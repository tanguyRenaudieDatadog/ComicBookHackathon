"""
PDF Comic Translation with Multimodal Context Preservation

This script extracts all pages from a PDF comic book and applies
multimodal translation with Llama4's vision capabilities to process 
them with comprehensive visual and textual context understanding.
"""

import os
import tempfile
import shutil
from pathlib import Path
from translate_multipage import translate_comic_series_multimodal
from translation_context import MultimodalTranslationContext
from llama_api_client import LlamaAPIClient
from dotenv import load_dotenv
import fitz
from PIL import Image
import glob


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

def translate_pdf_comic_multimodal(pdf_path, output_prefix="translated_pdf_page", 
                                 temp_dir="temp_pdf_pages", dpi=300, cleanup=True, debug=False,
                                 source_lang="English", target_lang="Russian"):
    """
    Complete pipeline to translate a PDF comic book using multimodal AI context
    
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
        Tuple of (translated_files, context_manager)
    """
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("api_key") or os.getenv("LLAMA_API_KEY")
    
    if not api_key:
        print("❌ Error: api_key not found in .env file")
        print("Please create a .env file with your API key:")
        print("api_key=your_llama_api_key_here")
        print("or")
        print("LLAMA_API_KEY=your_llama_api_key_here")
        return [], None
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return [], None
    
    if debug:
        print(f"\n{'='*80}")
        print(f"🚀 Starting Enhanced PDF Comic Translation Pipeline")
        print(f"🧠 Using Llama4's multimodal vision capabilities")
        print(f"📁 Input PDF: {pdf_path}")
        print(f"🎯 Output prefix: {output_prefix}")
        print(f"🌐 Translation: {source_lang} → {target_lang}")
        print(f"🔍 DPI: {dpi}")
        print(f"{'='*80}\n")
    else:
        print(f"🚀 Starting enhanced PDF comic translation: {os.path.basename(pdf_path)}")
        print(f"🧠 Using multimodal AI for context understanding")
        print(f"🌐 Translation: {source_lang} → {target_lang}")
    
    try:
        # Step 1: Extract pages from PDF
        if debug:
            print("📋 Step 1: Extracting pages from PDF...")
        page_files = extract_pdf_pages(pdf_path, temp_dir, dpi, debug)
        
        if not page_files:
            print("❌ Failed to extract pages from PDF")
            return [], None
        
        # Step 2: Translate all pages with multimodal context preservation
        if debug:
            print(f"\n📋 Step 2: Translating {len(page_files)} pages with multimodal context...")
            print("🧠 AI will analyze visual context, characters, and scenes")
        
        context_manager = translate_comic_series_multimodal(
            page_files, 
            output_prefix, 
            debug, 
            source_lang=source_lang, 
            target_lang=target_lang
        )
        
        # Step 3: Generate list of output files
        translated_files = []
        for i in range(len(page_files)):
            output_file = f"{output_prefix}_{i + 1}.png"
            if os.path.exists(output_file):
                translated_files.append(output_file)
        
        # Step 4: Generate final context summary
        context_summary_file = f"{output_prefix}_final_context.json"
        if context_manager:
            context_manager.save_context(context_summary_file)
        
        if debug:
            print(f"\n{'='*80}")
            print(f"🎉 Enhanced PDF Comic Translation Complete!")
            print(f"🧠 Multimodal AI Analysis Results:")
            if context_manager:
                print(f"   📊 Characters identified: {len(context_manager.characters)}")
                for char_name, char_info in context_manager.characters.items():
                    print(f"      - {char_name}: {len(char_info.speech_patterns)} speech patterns")
                print(f"   🎭 Story genre: {context_manager.genre}")
                print(f"   💬 Total dialogue bubbles: {len(context_manager.bubble_contexts)}")
                print(f"   🏞️  Scenes analyzed: {len(context_manager.scenes)}")
            print(f"📊 Processing Results:")
            print(f"   📁 Processed: {len(page_files)} pages")
            print(f"   📁 Generated: {len(translated_files)} translated images")
            print(f"   💾 Output files: {output_prefix}_1.png to {output_prefix}_{len(translated_files)}.png")
            print(f"   🧠 Context saved: {context_summary_file}")
            print(f"{'='*80}")
        else:
            print(f"🎉 Enhanced translation complete! Generated {len(translated_files)} translated pages")
            if context_manager:
                print(f"🧠 AI identified {len(context_manager.characters)} characters in {context_manager.genre} genre")
            print(f"💾 Files: {output_prefix}_1.png to {output_prefix}_{len(translated_files)}.png")
            print(f"🧠 Context: {context_summary_file}")
        
        # Step 5: Cleanup temporary files
        if cleanup and os.path.exists(temp_dir):
            if debug:
                print(f"\n🧹 Cleaning up temporary files in {temp_dir}...")
            shutil.rmtree(temp_dir)
            if debug:
                print("✅ Cleanup complete")
        
        return translated_files, context_manager
        
    except Exception as e:
        print(f"❌ Error during PDF translation: {e}")
        return [], None

def batch_translate_pdfs_multimodal(pdf_directory, output_directory="translated_comics", debug=False,
                                  source_lang="English", target_lang="Russian"):
    """
    Translate multiple PDF files in a directory using multimodal AI
    
    Args:
        pdf_directory: Directory containing PDF files
        output_directory: Directory to save translated comics
        debug: Enable detailed output
        source_lang: Source language
        target_lang: Target language
    """
    pdf_files = list(Path(pdf_directory).glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_directory}")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files to translate with multimodal AI")
    print(f"🌐 Translation: {source_lang} → {target_lang}")
    os.makedirs(output_directory, exist_ok=True)
    
    all_contexts = []
    
    for i, pdf_file in enumerate(pdf_files):
        if debug:
            print(f"\n{'='*60}")
            print(f"📖 Processing PDF {i+1}/{len(pdf_files)}: {pdf_file.name}")
            print(f"🧠 Using multimodal AI context analysis")
            print(f"{'='*60}")
        else:
            print(f"\n📖 Processing PDF {i+1}/{len(pdf_files)}: {pdf_file.name}")
        
        # Create output prefix with comic name
        comic_name = pdf_file.stem
        output_prefix = os.path.join(output_directory, f"{comic_name}_page")
        
        # Translate this PDF
        translated_files, context_manager = translate_pdf_comic_multimodal(
            str(pdf_file), 
            output_prefix,
            temp_dir=f"temp_{comic_name}_pages",
            debug=debug,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        if translated_files and context_manager:
            print(f"✅ Successfully translated {pdf_file.name}")
            all_contexts.append((comic_name, context_manager))
        else:
            print(f"❌ Failed to translate {pdf_file.name}")
    
    # Generate batch summary
    if all_contexts:
        summary_file = os.path.join(output_directory, "batch_translation_summary.json")
        batch_summary = {
            "total_comics": len(pdf_files),
            "successful_translations": len(all_contexts),
            "source_language": source_lang,
            "target_language": target_lang,
            "comics": []
        }
        
        for comic_name, context in all_contexts:
            batch_summary["comics"].append({
                "name": comic_name,
                "characters": len(context.characters),
                "genre": context.genre,
                "total_bubbles": len(context.bubble_contexts)
            })
        
        import json
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(batch_summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 Batch translation summary saved to: {summary_file}")

# Backward compatibility functions
def translate_pdf_comic(pdf_path, output_prefix="translated_pdf_page", 
                       temp_dir="temp_pdf_pages", dpi=300, cleanup=True, debug=False,
                       source_lang="English", target_lang="Russian"):
    """Backward compatibility wrapper - now uses multimodal AI"""
    print("ℹ️  Using enhanced multimodal translation (upgrade from simple context)")
    translated_files, _ = translate_pdf_comic_multimodal(
        pdf_path, output_prefix, temp_dir, dpi, cleanup, debug, source_lang, target_lang
    )
    return translated_files

def batch_translate_pdfs(pdf_directory, output_directory="translated_comics", debug=False):
    """Backward compatibility wrapper"""
    print("ℹ️  Using enhanced multimodal translation (upgrade from simple context)")
    return batch_translate_pdfs_multimodal(pdf_directory, output_directory, debug)

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
    
    # Check for language flags
    source_lang = "English"
    target_lang = "Russian"
    
    for arg in sys.argv[1:]:
        if arg.startswith("--source="):
            source_lang = arg.split("=")[1]
            sys.argv.remove(arg)
        elif arg.startswith("--target="):
            target_lang = arg.split("=")[1]
            sys.argv.remove(arg)
    
    if len(sys.argv) < 2:
        print("📖 Enhanced PDF Comic Translation Tool with Multimodal AI")
        print("🧠 Uses Llama4's vision capabilities for comprehensive context understanding")
        print("\nUsage:")
        print("  python translate_pdf_comic.py <pdf_file> [--debug] [--source=lang] [--target=lang]")
        print("  python translate_pdf_comic.py <pdf_file> <output_prefix> [options]")
        print("  python translate_pdf_comic.py --batch <pdf_directory> [options]")
        print("\nExamples:")
        print("  python translate_pdf_comic.py comic.pdf")
        print("  python translate_pdf_comic.py comic.pdf my_comic_page --debug")
        print("  python translate_pdf_comic.py --batch ./comic_pdfs/ --debug")
        print("  python translate_pdf_comic.py comic.pdf --source=Japanese --target=English")
        print("\nFlags:")
        print("  --debug           Show detailed output including AI analysis")
        print("  --source=lang     Source language (default: English)")
        print("  --target=lang     Target language (default: Russian)")
        print("\nEnhancements in this version:")
        print("  🧠 Multimodal AI analyzes visual context")
        print("  👥 Character identification and tracking")
        print("  🎭 Genre and mood detection")
        print("  💬 Speaker identification")
        print("  🏞️  Scene and setting analysis")
        print("\nRequired dependencies:")
        print("  pip install PyMuPDF pillow ultralytics")
        sys.exit(1)
    
    if debug_mode:
        print("🐛 Debug mode enabled")
        print("🧠 Multimodal AI analysis will be detailed")
    
    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("❌ Please specify directory containing PDF files")
            sys.exit(1)
        batch_translate_pdfs_multimodal(sys.argv[2], debug=debug_mode, 
                                      source_lang=source_lang, target_lang=target_lang)
    else:
        pdf_path = sys.argv[1]
        output_prefix = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "translated_pdf_page"
        
        translated_files, context_manager = translate_pdf_comic_multimodal(
            pdf_path, output_prefix, debug=debug_mode, 
            source_lang=source_lang, target_lang=target_lang
        )
        
        if translated_files:
            # Optionally create a combined PDF
            output_pdf_name = f"translated_{os.path.splitext(os.path.basename(pdf_path))[0]}.pdf"
            images_to_pdf(translated_files, output_pdf=output_pdf_name)
        else:
            print("❌ Translation failed")
