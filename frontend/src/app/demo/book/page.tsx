'use client';

import { useEffect, useState, useRef, useCallback, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { getPDF, getOriginalPDF } from '@/lib/storage';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ChevronLeft, ChevronRight, ArrowLeft } from 'lucide-react';

type ViewMode = 'translated' | 'original';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type PDFDocProxy = any;

function BookReader() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');

  const canvasRef = useRef<HTMLCanvasElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const pdfjsRef = useRef<any>(null);

  const [translatedDoc, setTranslatedDoc] = useState<PDFDocProxy>(null);
  const [originalDoc, setOriginalDoc] = useState<PDFDocProxy>(null);
  const [hasOriginal, setHasOriginal] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('translated');
  const [page, setPage] = useState(1);
  const [numPages, setNumPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load PDFs from IndexedDB
  useEffect(() => {
    if (!id) {
      setError('No book ID provided.');
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function loadPDFs() {
      try {
        // Dynamic import to avoid SSR issues with DOMMatrix
        const pdfjsLib = await import('pdfjs-dist');
        pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';
        pdfjsRef.current = pdfjsLib;

        const pdfData = await getPDF(id!);
        if (!pdfData || cancelled) {
          if (!cancelled) setError('Translated PDF not found in library.');
          setLoading(false);
          return;
        }
        const raw = atob(pdfData);
        const uint8 = new Uint8Array(raw.length);
        for (let i = 0; i < raw.length; i++) uint8[i] = raw.charCodeAt(i);

        const doc = await pdfjsLib.getDocument({ data: uint8 }).promise;
        if (cancelled) return;
        setTranslatedDoc(doc);
        setNumPages(doc.numPages);

        // Try loading original
        try {
          const origData = await getOriginalPDF(id!);
          if (origData && !cancelled) {
            const origRaw = atob(origData);
            const origUint8 = new Uint8Array(origRaw.length);
            for (let i = 0; i < origRaw.length; i++) origUint8[i] = origRaw.charCodeAt(i);

            const origDoc = await pdfjsLib.getDocument({ data: origUint8 }).promise;
            if (!cancelled) {
              setOriginalDoc(origDoc);
              setHasOriginal(true);
            }
          }
        } catch {
          // Original not available — that's fine
        }
      } catch (err) {
        if (!cancelled) setError('Failed to load PDF.');
        console.error(err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadPDFs();
    return () => { cancelled = true; };
  }, [id]);

  // Render current page
  const renderPage = useCallback(async () => {
    const doc = viewMode === 'original' ? originalDoc : translatedDoc;
    const canvas = canvasRef.current;
    if (!doc || !canvas) return;

    const pageNum = Math.min(page, doc.numPages);
    const pdfPage = await doc.getPage(pageNum);
    const scale = 1.5;
    const viewport = pdfPage.getViewport({ scale });

    canvas.height = viewport.height;
    canvas.width = viewport.width;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    await pdfPage.render({ canvasContext: ctx, viewport }).promise;
  }, [viewMode, translatedDoc, originalDoc, page]);

  useEffect(() => {
    renderPage();
  }, [renderPage]);

  // Update numPages when switching views
  useEffect(() => {
    const doc = viewMode === 'original' ? originalDoc : translatedDoc;
    if (doc) setNumPages(doc.numPages);
  }, [viewMode, translatedDoc, originalDoc]);

  const handleViewChange = (value: string) => {
    setViewMode(value as ViewMode);
    setPage(1);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-muted-foreground text-lg">Loading book...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background gap-4">
        <div className="text-destructive text-lg">{error}</div>
        <Button variant="outline" onClick={() => router.push('/demo')}>
          <ArrowLeft className="h-4 w-4 mr-2" /> Back to library
        </Button>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-background flex flex-col items-center">
      {/* Top bar */}
      <div className="w-full max-w-4xl flex items-center justify-between px-4 py-3">
        <Button variant="ghost" size="sm" onClick={() => router.push('/demo')}>
          <ArrowLeft className="h-4 w-4 mr-1" /> Library
        </Button>

        {hasOriginal && (
          <Tabs value={viewMode} onValueChange={handleViewChange}>
            <TabsList>
              <TabsTrigger value="translated">Translated</TabsTrigger>
              <TabsTrigger value="original">Original</TabsTrigger>
            </TabsList>
          </Tabs>
        )}

        <div className="text-sm text-muted-foreground">
          {page} / {numPages}
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 flex items-start justify-center w-full overflow-auto px-4 pb-24">
        <canvas ref={canvasRef} className="max-w-full h-auto shadow-lg rounded-lg" />
      </div>

      {/* Navigation */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-4 bg-background/80 backdrop-blur border rounded-full px-4 py-2 shadow-lg">
        <Button
          variant="ghost"
          size="icon"
          disabled={page <= 1}
          onClick={() => setPage(p => Math.max(1, p - 1))}
        >
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <span className="text-sm font-medium min-w-[60px] text-center">
          Page {page}
        </span>
        <Button
          variant="ghost"
          size="icon"
          disabled={page >= numPages}
          onClick={() => setPage(p => Math.min(numPages, p + 1))}
        >
          <ChevronRight className="h-5 w-5" />
        </Button>
      </div>
    </main>
  );
}

export default function BookReaderPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-muted-foreground text-lg">Loading book...</div>
      </div>
    }>
      <BookReader />
    </Suspense>
  );
}
