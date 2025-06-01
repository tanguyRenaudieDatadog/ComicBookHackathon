'use client';
import { useEffect, useRef, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { getPDF } from '@/lib/storage';

// Remove pdfjs-dist imports for SSR safety

export default function BookPage() {
  const params = useParams();
  const id = params?.id as string;
  const [title, setTitle] = useState('');
  const [numPages, setNumPages] = useState<number>(0);
  const [page, setPage] = useState(1); // 1-based index
  const [pdfDoc, setPdfDoc] = useState<any>(null); // PDFDocumentProxy, but type only available after dynamic import
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [renderKey, setRenderKey] = useState(0); // for animation

  // No more canvasRefs; use callback ref for rendering
  // Track render tasks for each canvas
  const renderTaskRef = useRef<any>(null);
  // Track render session to prevent race conditions
  const renderSessionId = useRef(0);

  // Fixed page size
  const PAGE_WIDTH = 480;
  const PAGE_HEIGHT = 680;

  useEffect(() => {
    if (!id) return;
    const stored = localStorage.getItem('demo-books');
    if (stored) {
      const books = JSON.parse(stored);
      const book = books.find((b: any) => b.id === id);
      if (book) {
        setTitle(book.title);
      }
    }
  }, [id]);

  // Load PDF document (dynamically import pdfjsLib)
  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);

    let isMounted = true;

    getPDF(id)
      .then(async (pdfData) => {
        if (!pdfData) {
          if (isMounted) {
            setError('PDF not found');
            setLoading(false);
          }
          return;
        }

        try {
          // Dynamically import pdfjs-dist only on client
          const pdfjsLib = await import('pdfjs-dist/build/pdf');
          pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.mjs';

          // Convert base64 to Uint8Array
          const binaryString = window.atob(pdfData);
          const bytes = new Uint8Array(binaryString.length);
          for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
          }

          console.log('Loading PDF from IndexedDB...');
          const doc = await pdfjsLib.getDocument(bytes).promise;
          console.log('PDF loaded successfully, pages:', doc.numPages);
          if (isMounted) {
            setPdfDoc({ doc, pdfjsLib });
            setNumPages(doc.numPages);
            setPage(1);
            setLoading(false);
          }
        } catch (err) {
          console.error('Error loading PDF:', err);
          if (isMounted) {
            setError(`Failed to load PDF: ${err instanceof Error ? err.message : 'Unknown error'}`);
            setLoading(false);
          }
        }
      })
      .catch((err) => {
        console.error('Error retrieving PDF from IndexedDB:', err);
        if (isMounted) {
          setError('Failed to retrieve PDF from storage');
          setLoading(false);
        }
      });

    return () => { isMounted = false; };
  }, [id]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (pdfDoc) {
        setRenderKey(k => k + 1); // Trigger re-render with new scale
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [pdfDoc]);

  const isDesktop = typeof window !== 'undefined' && window.innerWidth >= 1024;
  const pagesToShow = isDesktop ? 2 : 1;
  // Clamp page to valid range
  const maxPage = Math.max(1, numPages - pagesToShow + 1);
  const clampedPage = Math.min(Math.max(1, page), maxPage);
  const pageNumbers = Array.from({ length: pagesToShow }, (_, i) => clampedPage + i).filter(p => p <= numPages);

  function goPrev() {
    setPage(p => Math.max(1, p - pagesToShow));
  }
  function goNext() {
    setPage(p => {
      const nextPage = p + pagesToShow;
      return Math.min(maxPage, nextPage);
    });
  }

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') {
        goPrev();
      } else if (e.key === 'ArrowRight') {
        goNext();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [maxPage, pagesToShow]);

  // Callback ref for canvas rendering (must be sync for React)
  const handleCanvasRef = (pageNum: number) => (canvas: HTMLCanvasElement | null) => {
    if (!canvas || !pdfDoc || !pdfDoc.doc || !pdfDoc.pdfjsLib) return;
    const { doc } = pdfDoc;
    // Cancel any previous render
    if (renderTaskRef.current && renderTaskRef.current[pageNum]) {
      try { renderTaskRef.current[pageNum].cancel(); } catch {}
      renderTaskRef.current[pageNum] = null;
    }
    if (!renderTaskRef.current) renderTaskRef.current = {};
    renderSessionId.current += 1;
    const session = renderSessionId.current;
    (async () => {
      try {
        const pageObj = await doc.getPage(pageNum);
        const viewport = pageObj.getViewport({ scale: 1.0 });
        const scale = Math.min(PAGE_WIDTH / viewport.width, PAGE_HEIGHT / viewport.height);
        const scaledViewport = pageObj.getViewport({ scale });
        canvas.width = PAGE_WIDTH;
        canvas.height = PAGE_HEIGHT;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        ctx.save();
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.clearRect(0, 0, PAGE_WIDTH, PAGE_HEIGHT);
        ctx.fillStyle = '#fff';
        ctx.fillRect(0, 0, PAGE_WIDTH, PAGE_HEIGHT);
        ctx.translate(
          (PAGE_WIDTH - scaledViewport.width) / 2,
          (PAGE_HEIGHT - scaledViewport.height) / 2
        );
        const renderTask = pageObj.render({ canvasContext: ctx, viewport: scaledViewport });
        renderTaskRef.current[pageNum] = renderTask;
        await renderTask.promise;
        ctx.restore();
      } catch (e) {
        // Ignore cancellation errors
      }
    })();
  };

  return (
    <main className="min-h-screen bg-background flex flex-col">
      {/* ComicTranslator logo top left */}
      <header className="fixed top-0 left-0 w-full h-20 flex items-center px-8 z-10">
        <Link href="/demo" className="text-xl font-bold text-primary select-none" style={{ letterSpacing: '-0.02em' }}>
          ComicTranslator
        </Link>
      </header>
      <div className="flex-1 flex flex-col items-center justify-center pt-24 pb-12 px-4">
        <h1 className="text-3xl font-bold mb-6">{title ? title : 'Book'}</h1>
        {loading ? (
          <div className="text-muted-foreground">Loading PDF…</div>
        ) : error ? (
          <div className="text-destructive">{error}</div>
        ) : pdfDoc ? (
          <div className="flex flex-col items-center">
            <div
              className="flex gap-4 transition-all duration-500"
              style={{ width: isDesktop ? `${PAGE_WIDTH * 2 + 32}px` : `${PAGE_WIDTH}px`, height: `${PAGE_HEIGHT}px` }}
              key={clampedPage + '-' + renderKey}
            >
              {pageNumbers.map((p) => (
                <canvas
                  key={p + '-' + renderKey}
                  ref={handleCanvasRef(p)}
                  width={PAGE_WIDTH}
                  height={PAGE_HEIGHT}
                  style={{
                    width: PAGE_WIDTH,
                    height: PAGE_HEIGHT,
                    boxShadow: '0 2px 16px rgba(0,0,0,0.08)',
                    borderRadius: 8,
                    background: '#fff',
                    transition: 'opacity 0.3s',
                    opacity: 1,
                  }}
                />
              ))}
            </div>
            <div className="flex gap-4 mt-6">
              <Button onClick={goPrev} disabled={clampedPage === 1} variant="outline">Previous</Button>
              <span className="text-muted-foreground">Page {clampedPage}{pagesToShow === 2 && clampedPage + 1 <= numPages ? `-${clampedPage + 1}` : ''} of {numPages}</span>
              <Button onClick={goNext} disabled={clampedPage >= maxPage} variant="outline">Next</Button>
            </div>
          </div>
        ) : (
          <div className="text-muted-foreground">No PDF found for this book.</div>
        )}
      </div>
    </main>
  );
} 