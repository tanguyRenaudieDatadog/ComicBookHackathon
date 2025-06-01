declare module 'pdfjs-dist/build/pdf' {
  export const GlobalWorkerOptions: {
    workerSrc: string;
  };

  export function getDocument(source: string | Uint8Array): {
    promise: Promise<PDFDocumentProxy>;
  };

  export interface PDFDocumentProxy {
    numPages: number;
    getPage(pageNumber: number): Promise<PDFPageProxy>;
  }

  export interface PDFPageProxy {
    getViewport(params: { scale: number }): PDFPageViewport;
    render(params: {
      canvasContext: CanvasRenderingContext2D;
      viewport: PDFPageViewport;
    }): {
      promise: Promise<void>;
    };
  }

  export interface PDFPageViewport {
    width: number;
    height: number;
  }
} 