"""
Multi-page Comic Translation

This script demonstrates how to translate multiple comic pages
independently without context management.
"""

import os
from translate_and_fill_bubbles_multilang import process_comic_page_with_languages
from dotenv import load_dotenv

def translate_comic_series(page_files, output_prefix="translated_page", debug=False, source_lang="English", target_lang="Russian"):
    """
    Translate a series of comic pages independently
    
    Args:
        page_files: List of input image filenames
        output_prefix: Prefix for output files
        debug: Enable detailed output
        source_lang: Source language name (e.g., "English")
        target_lang: Target language name (e.g., "Spanish")
    """
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("api_key") or os.getenv("LLAMA_API_KEY")
    
    if not api_key:
        print("❌ Error: api_key not found in .env file")
        return
    
    for i, page_file in enumerate(page_files):
        page_num = i + 1
        if debug:
            print(f"\n{'='*60}")
            print(f"📖 Processing Page {page_num}: {page_file}")
            print(f"🌐 Translation: {source_lang} → {target_lang}")
            print(f"{'='*60}")
        else:
            print(f"\n📖 Processing page {page_num}/{len(page_files)}: {os.path.basename(page_file)}")
        
        # Process current page
        output_file = f"{output_prefix}_{page_num}.png"
        
        # Use the multilang version
        process_comic_page_with_languages(page_file, output_file, api_key, source_lang, target_lang, debug)
        
        if debug:
            print(f"\n✅ Completed Page {page_num}")
    
    if debug:
        print(f"\n{'='*60}")
        print("🎉 All pages translated successfully!")
        print(f"Processed {len(page_files)} pages")
        print(f"{'='*60}")
    else:
        print(f"\n🎉 All pages translated successfully!")
        print(f"Processed {len(page_files)} pages")

# Example usage
if __name__ == "__main__":
    import sys
    
    # Check for debug flag
    debug_mode = "--debug" in sys.argv
    if debug_mode:
        sys.argv.remove("--debug")
    
    # Check for languages
    source_lang = "English"
    target_lang = "Russian"
    
    for arg in sys.argv[1:]:
        if arg.startswith("--source="):
            source_lang = arg.split("=")[1]
            sys.argv.remove(arg)
        elif arg.startswith("--target="):
            target_lang = arg.split("=")[1]
            sys.argv.remove(arg)
    
    # Example for translating multiple pages
    comic_pages = [
        "page1.png",
        "page2.png", 
        "page3.png"
    ]
    
    # Check if files exist
    existing_pages = [page for page in comic_pages if os.path.exists(page)]
    
    if existing_pages:
        print(f"Found {len(existing_pages)} pages to translate")
        if debug_mode:
            print("🐛 Debug mode enabled")
        print(f"🌐 Translation: {source_lang} → {target_lang}")
        translate_comic_series(existing_pages, debug=debug_mode, 
                              source_lang=source_lang, target_lang=target_lang)
    else:
        print("ℹ️  Multi-page Comic Translation Tool")
        print("\nUsage:")
        print("  python translate_multipage.py [--debug] [--source=English] [--target=Russian]")
        print("\nTo use it, add your comic page files (page1.png, page2.png, etc.)")
        print("\nFor single page translation, use:")
        print("  python translate_and_fill_bubbles_multilang.py [image_path]")
        print("\nFor debug mode, add --debug flag:")
        print("  python translate_multipage.py --debug")
        print("\nLanguage options:")
        print("  --source=English --target=Spanish")
        print("  --source=Japanese --target=English") 