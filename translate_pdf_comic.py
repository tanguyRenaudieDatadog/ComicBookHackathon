"""
PDF Comic Translation with Context Preservation

This script extracts all pages from a PDF comic book and applies
translate_comic_series to process them with continuous context.
"""

import os
import tempfile
import shutil
from pathlib import Path
from translate_and_fill_bubbles_multilang import process_comic_page_with_languages
from dotenv import load_dotenv
import fitz
from PIL import Image
import glob
import asyncio


def extract_pdf_pages(pdf_path, output_dir="temp_pdf_pages", dpi=300, debug=False):
    """
    Extract all pages from a PDF file as high-quality images
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted images
        dpi: Resolution for image extraction (higher = better quality)
        debug: Enable detailed output
    
    Returns:
        List of extracted image file paths
    """
    method = "pymupdf" 
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    if debug:
        print(f"📄 Extracting pages from {pdf_path} using {method}...")
    else:
        print(f"📄 Extracting pages from PDF...")
    extracted_files = []
            
    # Use PyMuPDF
    try:
        doc = fitz.open(pdf_path)
        if debug:
            print(f"✅ Found {len(doc)} pages in PDF")
        else:
            print(f"✅ Found {len(doc)} pages")
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Calculate zoom factor for desired DPI
            zoom = dpi / 72.0  # 72 is default DPI
            mat = fitz.Matrix(zoom, zoom)
            
            # Render page as image
            pix = page.get_pixmap(matrix=mat)
            output_path = os.path.join(output_dir, f"page_{page_num + 1:03d}.png")
            pix.save(output_path)
            extracted_files.append(output_path)
            if debug:
                print(f"📖 Extracted page {page_num + 1} → {output_path}")
        
        doc.close()
        
    except Exception as e:
        print(f"❌ Error with PyMuPDF: {e}")
        return []
    
    if not debug:
        print(f"✅ Successfully extracted {len(extracted_files)} pages")
    return extracted_files

def translate_pdf_comic(pdf_path, output_prefix="translated_pdf_page", 
                       temp_dir="temp_pdf_pages", dpi=300, cleanup=True, debug=False,
                       source_lang="English", target_lang="Russian"):
    """
    Complete pipeline to translate a PDF comic book
    
    Args:
        pdf_path: Path to the PDF comic file
        output_prefix: Prefix for translated output files
        temp_dir: Temporary directory for extracted pages
        dpi: Resolution for page extraction
        cleanup: Whether to delete temporary files after processing
        debug: Enable detailed output
        source_lang: Source language name (e.g., "English")
        target_lang: Target language name (e.g., "Spanish")
    
    Returns:
        List of translated image file paths
    """
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("api_key")
    
    if not api_key:
        print("❌ Error: api_key not found in .env file")
        print("Please create a .env file with your API key:")
        print("api_key=your_llama_api_key_here")
        return []
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return []
    
    if debug:
        print(f"\n{'='*80}")
        print(f"🚀 Starting PDF Comic Translation Pipeline")
        print(f"📁 Input PDF: {pdf_path}")
        print(f"🎯 Output prefix: {output_prefix}")
        print(f"🌐 Translation: {source_lang} → {target_lang}")
        print(f"{'='*80}\n")
    else:
        print(f"🚀 Starting PDF comic translation: {os.path.basename(pdf_path)}")
        print(f"🌐 Translation: {source_lang} → {target_lang}")
    
    try:
        # Step 1: Extract pages from PDF
        if debug:
            print("📋 Step 1: Extracting pages from PDF...")
        page_files = extract_pdf_pages(pdf_path, temp_dir, dpi, debug)
        
        if not page_files:
            print("❌ Failed to extract pages from PDF")
            return []
        
        # Step 2: Translate all pages with context preservation
        if debug:
            print(f"\n📋 Step 2: Translating {len(page_files)} pages with context preservation...")
        
        # Process each page with the multilang version
        translated_files = []
        for i, page_file in enumerate(page_files):
            output_file = f"{output_prefix}_{i + 1}.png"
            asyncio.run(process_comic_page_with_languages(
                page_file,
                output_file,
                api_key,
                source_lang=source_lang,
                target_lang=target_lang,
                debug=debug
            ))
            translated_files.append(output_file)
        
        if debug:
            print(f"\n{'='*80}")
            print(f"🎉 PDF Comic Translation Complete!")
            print(f"📊 Processed: {len(page_files)} pages")
            print(f"📁 Generated: {len(translated_files)} translated images")
            print(f"💾 Output files: {output_prefix}_1.png to {output_prefix}_{len(translated_files)}.png")
            print(f"{'='*80}")
        else:
            print(f"🎉 Translation complete! Generated {len(translated_files)} translated pages")
            print(f"💾 Files: {output_prefix}_1.png to {output_prefix}_{len(translated_files)}.png")
        
        # Step 4: Cleanup temporary files
        if cleanup and os.path.exists(temp_dir):
            if debug:
                print(f"\n🧹 Cleaning up temporary files in {temp_dir}...")
            shutil.rmtree(temp_dir)
            if debug:
                print("✅ Cleanup complete")
        
        return translated_files
        
    except Exception as e:
        print(f"❌ Error during PDF translation: {e}")
        return []

def batch_translate_pdfs(pdf_directory, output_directory="translated_comics", debug=False):
    """
    Translate multiple PDF files in a directory
    
    Args:
        pdf_directory: Directory containing PDF files
        output_directory: Directory to save translated comics
        debug: Enable detailed output
    """
    pdf_files = list(Path(pdf_directory).glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_directory}")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files to translate")
    os.makedirs(output_directory, exist_ok=True)
    
    for i, pdf_file in enumerate(pdf_files):
        if debug:
            print(f"\n{'='*60}")
            print(f"📖 Processing PDF {i+1}/{len(pdf_files)}: {pdf_file.name}")
            print(f"{'='*60}")
        else:
            print(f"\n📖 Processing PDF {i+1}/{len(pdf_files)}: {pdf_file.name}")
        
        # Create output prefix with comic name
        comic_name = pdf_file.stem
        output_prefix = os.path.join(output_directory, f"{comic_name}_page")
        
        # Translate this PDF
        translated_files = translate_pdf_comic(
            str(pdf_file), 
            output_prefix,
            temp_dir=f"temp_{comic_name}_pages",
            debug=debug
        )
        
        if translated_files:
            print(f"✅ Successfully translated {pdf_file.name}")
        else:
            print(f"❌ Failed to translate {pdf_file.name}")

def images_to_pdf(image_pattern, output_pdf="translated_manga.pdf", page_order=None):
    """
    Convert a list of images to a PDF file
    
    Args:
        image_pattern: Glob pattern like "translated_pdf_page_*.png" or list of files
        output_pdf: Output PDF filename
        page_order: Optional list to specify custom page order
    """
    # Get list of image files
    if isinstance(image_pattern, str):
        image_files = glob.glob(image_pattern)
        # Sort by page number if they follow your naming convention
        image_files.sort(key=lambda x: int(x.split('_page_')[1].split('.')[0]))
    else:
        image_files = image_pattern
    
    if page_order:
        # Reorder according to specified order
        ordered_files = []
        for page_num in page_order:
            matching_files = [f for f in image_files if f"page_{page_num}" in f]
            if matching_files:
                ordered_files.append(matching_files[0])
        image_files = ordered_files
    
    if not image_files:
        print("No image files found!")
        return
    
    # Convert first image to RGB and prepare for PDF
    images = []
    for img_path in image_files:
        img = Image.open(img_path)
        # Convert to RGB if necessary (PDF requires RGB)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)
        print(f"Added: {os.path.basename(img_path)}")
    
    # Save as PDF
    if images:
        images[0].save(
            output_pdf, 
            save_all=True, 
            append_images=images[1:], 
            format='PDF'
        )
        print(f"✅ Successfully created PDF: {output_pdf}")
        print(f"📄 {len(images)} pages combined")
    
# Example usage and CLI interface
if __name__ == "__main__":
    import sys
    
    # Check for debug flag
    debug_mode = "--debug" in sys.argv
    if debug_mode:
        sys.argv.remove("--debug")
    
    if len(sys.argv) < 2:
        print("📖 PDF Comic Translation Tool")
        print("\nUsage:")
        print("  python translate_pdf_comic.py <pdf_file> [--debug]")
        print("  python translate_pdf_comic.py <pdf_file> <output_prefix> [--debug]")
        print("  python translate_pdf_comic.py --batch <pdf_directory> [--debug]")
        print("\nExamples:")
        print("  python translate_pdf_comic.py comic.pdf")
        print("  python translate_pdf_comic.py comic.pdf my_comic_page --debug")
        print("  python translate_pdf_comic.py --batch ./comic_pdfs/ --debug")
        print("\nFlags:")
        print("  --debug    Show detailed output including bubble contents and translations")
        print("\nRequired dependencies:")
        print("  pip install PyMuPDF")
        sys.exit(1)
    
    if debug_mode:
        print("🐛 Debug mode enabled")
    
    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("❌ Please specify directory containing PDF files")
            sys.exit(1)
        batch_translate_pdfs(sys.argv[2], debug=debug_mode)
    else:
        pdf_path = sys.argv[1]
        output_prefix = sys.argv[2] if len(sys.argv) > 2 else "translated_pdf_page"
        translated_files = translate_pdf_comic(pdf_path, output_prefix, debug=debug_mode) 
        images_to_pdf(translated_files, output_pdf=f"translated_{pdf_path}")
