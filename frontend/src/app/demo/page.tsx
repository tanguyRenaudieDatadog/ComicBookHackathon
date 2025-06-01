'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Plus, BookOpen, Languages, Upload, X, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { useDropzone } from 'react-dropzone';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Book {
  id: string;
  title: string;
  language: string;
}

const features = [
  {
    icon: <BookOpen className="h-7 w-7 text-primary" />,
    title: 'Read any comic',
    desc: 'Enjoy your favorite comics and manga in your chosen language with a beautiful reader.'
  },
  {
    icon: <Languages className="h-7 w-7 text-primary" />,
    title: 'Translate instantly',
    desc: 'AI-powered translation preserves the art and layout of your comics.'
  },
  {
    icon: <Upload className="h-7 w-7 text-primary" />,
    title: 'Easy upload',
    desc: 'Drag & drop or select files to add new books to your library.'
  },
];

const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'it', name: 'Italian' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'ru', name: 'Russian' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'zh', name: 'Chinese' },
  { code: 'ar', name: 'Arabic' },
  { code: 'hi', name: 'Hindi' },
];

const MAX_SIZE_MB = 16;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

function AddBookModal({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('es');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) {
      setFile(null);
      setTitle('');
      setSourceLang('en');
      setTargetLang('es');
      setError(null);
      setLoading(false);
    }
  }, [open]);

  const onDrop = (acceptedFiles: File[]) => {
    if (!acceptedFiles.length) return;
    const f = acceptedFiles[0];
    if (f.size > MAX_SIZE_BYTES) {
      setError('File is too large (max 16MB)');
      setFile(null);
      return;
    }
    setFile(f);
    setError(null);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    maxSize: MAX_SIZE_BYTES,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
  });

  // Backend logic: handle submit
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !title || !sourceLang || !targetLang) {
      setError('Please fill out all fields and upload a file.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('source_lang', sourceLang);
      formData.append('target_lang', targetLang);
      // Optionally send title as well (not used by backend, but for future use)
      formData.append('title', title);
      const res = await fetch('/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok || !data.job_id) {
        setError(data.error || 'Failed to start translation');
        setLoading(false);
        return;
      }
      // Poll status
      let status = 'processing';
      let jobId = data.job_id;
      while (status !== 'completed') {
        await new Promise(r => setTimeout(r, 2000));
        const statusRes = await fetch(`/status/${jobId}`);
        const statusData = await statusRes.json();
        if (statusData.status === 'failed') {
          setError(statusData.error || 'Translation failed');
          setLoading(false);
          return;
        }
        status = statusData.status;
      }
      // Download PDF
      const pdfRes = await fetch(`/download/all/${jobId}`);
      if (!pdfRes.ok) {
        setError('Failed to download translated PDF');
        setLoading(false);
        return;
      }
      const blob = await pdfRes.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title || 'translated_comic'}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setLoading(false);
      onOpenChange(false);
    } catch (err) {
      setError('Network or server error.');
      setLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg p-0 overflow-visible">
        <DialogTitle className="sr-only">Add a Book</DialogTitle>
        {loading ? (
          <div className="flex flex-col items-center justify-center min-h-[350px] w-full">
            <Loader2 className="h-12 w-12 text-primary animate-spin mb-6" />
            <div className="text-lg font-semibold text-foreground mb-2">Translating…</div>
            <div className="text-muted-foreground text-sm text-center max-w-xs">
              This may take a minute for large comics. Please do not close this window.
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="relative bg-background rounded-xl shadow-xl p-8 pt-6 flex flex-col items-center">
            <div className="flex flex-col items-center w-full">
              <Upload className="h-10 w-10 text-primary mb-2" />
              <h2 className="text-xl font-semibold mb-1">Upload source</h2>
              <p className="text-muted-foreground mb-6 text-center text-sm">
                Drag & drop or <span className="text-primary underline cursor-pointer">choose file</span> to upload
              </p>
              {/* Book Title Field */}
              <div className="w-full mb-4">
                <Label htmlFor="book-title" className="mb-1 block">Book Title</Label>
                <Input
                  id="book-title"
                  placeholder="Enter a title for your book"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                  className="w-full"
                />
              </div>
              {/* Language Row */}
              <div className="w-full flex items-center gap-2 mb-6">
                <div className="flex-1">
                  <Label htmlFor="source-lang" className="mb-1 block">Source Language</Label>
                  <Select value={sourceLang} onValueChange={setSourceLang}>
                    <SelectTrigger id="source-lang" className="w-full">
                      <SelectValue placeholder="Source language" />
                    </SelectTrigger>
                    <SelectContent>
                      {LANGUAGES.map(l => (
                        <SelectItem key={l.code} value={l.code}>{l.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <span className="mx-2 text-muted-foreground">to</span>
                <div className="flex-1">
                  <Label htmlFor="target-lang" className="mb-1 block">Target Language</Label>
                  <Select value={targetLang} onValueChange={setTargetLang}>
                    <SelectTrigger id="target-lang" className="w-full">
                      <SelectValue placeholder="Target language" />
                    </SelectTrigger>
                    <SelectContent>
                      {LANGUAGES.map(l => (
                        <SelectItem key={l.code} value={l.code}>{l.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div
                {...getRootProps()}
                className={`w-full border-2 border-dashed rounded-lg flex flex-col items-center justify-center py-10 px-4 mb-4 transition-colors ${isDragActive ? 'border-primary bg-primary/5' : 'border-muted'}`}
                style={{ cursor: 'pointer' }}
              >
                <input {...getInputProps()} />
                {file ? (
                  <div className="flex flex-col items-center">
                    <span className="font-medium text-foreground mb-1">{file.name}</span>
                    <span className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                ) : (
                  <span className="text-muted-foreground">Drop a PDF, JPG, or PNG file here</span>
                )}
              </div>
              <div className="text-xs text-muted-foreground mb-2">Supported file types: PDF, JPG, PNG</div>
              {error && <div className="text-sm text-destructive mb-2">{error}</div>}
              {/* Source limit bar */}
              <div className="w-full flex items-center gap-2 mt-2">
                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-2 bg-primary rounded-full transition-all"
                    style={{ width: file ? `${Math.min(100, (file.size / MAX_SIZE_BYTES) * 100)}%` : '0%' }}
                  />
                </div>
                <span className="text-xs text-muted-foreground whitespace-nowrap">
                  {file ? `${(file.size / 1024 / 1024).toFixed(2)} / ${MAX_SIZE_MB} MB` : `0 / ${MAX_SIZE_MB} MB`}
                </span>
              </div>
              <Button type="submit" size="lg" className="w-full mt-6" disabled={loading}>
                {loading ? 'Translating...' : 'Translate & Download'}
              </Button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default function DemoPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [modalOpen, setModalOpen] = useState(false);

  // Load books from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('demo-books');
    if (stored) setBooks(JSON.parse(stored));
  }, []);

  // Save books to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('demo-books', JSON.stringify(books));
  }, [books]);

  return (
    <main className="min-h-screen bg-background flex flex-col">
      {/* Fixed header, styled and animated like landing page */}
      <motion.header
        className="fixed top-0 left-0 w-full h-20 flex items-center px-8 z-10"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Link
          href="/"
          className="text-xl font-bold text-primary select-none"
          style={{ letterSpacing: '-0.02em' }}
        >
          ComicTranslator
        </Link>
      </motion.header>
      <AddBookModal open={modalOpen} onOpenChange={setModalOpen} />
      <div className="flex-1 flex flex-col items-center justify-center pt-24 pb-12 px-4">
        {books.length === 0 ? (
          <>
            <motion.h1 
              className="text-4xl sm:text-5xl font-bold text-foreground text-center mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              Welcome to ComicTranslator
            </motion.h1>
            <motion.h2 
              className="text-2xl font-semibold text-foreground text-center mb-2"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              Create your first book
            </motion.h2>
            <motion.p 
              className="text-lg text-muted-foreground text-center max-w-xl mb-10"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7 }}
            >
              ComicTranslator lets you translate and read comics or manga in your chosen language. Get started by adding your first book.
            </motion.p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16 w-full max-w-4xl">
              {features.map((f, i) => (
                <motion.div
                  key={f.title}
                  className="flex-1 bg-card rounded-xl shadow-md p-6 flex flex-col items-center text-center"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 + i * 0.1 }}
                >
                  <div className="mb-3">{f.icon}</div>
                  <div className="font-semibold text-lg mb-1">{f.title}</div>
                  <div className="text-muted-foreground text-sm">{f.desc}</div>
                </motion.div>
              ))}
            </div>
            <div className="flex flex-col items-center mt-8">
              <Button size="lg" className="flex items-center gap-2 text-base px-6 py-3" onClick={() => setModalOpen(true)}>
                <Plus className="h-5 w-5" />
                Add a Book
              </Button>
            </div>
          </>
        ) : (
          <div className="w-full max-w-4xl flex flex-col items-center mt-20">
            <h1 className="text-3xl font-bold mb-10 mt-2">Your Library</h1>
            <Button size="lg" className="mb-10 flex items-center gap-2" onClick={() => setModalOpen(true)}>
              <Plus className="h-5 w-5" />
              Add a Book
            </Button>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 w-full">
              {books.map((book, i) => (
                <motion.div
                  key={book.id}
                  className="bg-card rounded-lg shadow-sm overflow-hidden flex flex-col"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: i * 0.1 }}
                >
                  <div className="aspect-[3/4] bg-muted flex items-center justify-center text-muted-foreground">
                    Comic Preview
                  </div>
                  <div className="p-4 flex-1 flex flex-col">
                    <h3 className="font-semibold mb-1">{book.title}</h3>
                    <p className="text-sm text-muted-foreground mb-4">Language: {book.language}</p>
                    <Button variant="outline" className="w-full mt-auto">
                      Read Now
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
} 