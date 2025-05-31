"""
Multi-page Comic Translation with Context Preservation

This script demonstrates how to translate multiple comic pages
while maintaining context across pages for consistent translations.
"""

import os
from translation_context import TranslationContext
from translate_and_fill_bubbles import process_comic_page
from dotenv import load_dotenv

def translate_comic_series(page_files, output_prefix="translated_page", debug=False, source_lang="English", target_lang="Russian"):
    """
    Translate a series of comic pages with continuous context
    
    Args:
        page_files: List of input image filenames
        output_prefix: Prefix for output files
        debug: Enable detailed output
        source_lang: Source language name (e.g., "English")
        target_lang: Target language name (e.g., "Spanish")
    """
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("api_key")
    
    if not api_key:
        print("❌ Error: api_key not found in .env file")
        return
    
    # Initialize persistent context
    context_manager = TranslationContext()
    
    for i, page_file in enumerate(page_files):
        page_num = i + 1
        if debug:
            print(f"\n{'='*60}")
            print(f"📖 Processing Page {page_num}: {page_file}")
            print(f"🌐 Translation: {source_lang} → {target_lang}")
            print(f"{'='*60}")
        else:
            print(f"\n📖 Processing page {page_num}/{len(page_files)}: {os.path.basename(page_file)}")
        
        # Check if we have previous context
        if i > 0:
            # Load context from previous page
            prev_context_file = f"{output_prefix}_{i}_context.json"
            if os.path.exists(prev_context_file):
                context_manager.load_context(prev_context_file)
                if debug:
                    print(f"✓ Loaded context from {len(context_manager.context_window)} previous bubbles")
                    print(f"✓ Known characters: {', '.join(context_manager.character_names)}")
        
        # Process current page
        output_file = f"{output_prefix}_{page_num}.png"
        
        # Use the multilang version of process_comic_page
        from translate_and_fill_bubbles_multilang import process_comic_page_with_languages
        process_comic_page_with_languages(page_file, output_file, api_key, source_lang, target_lang)
        
        if debug:
            print(f"\n✅ Completed Page {page_num}")
    
    if debug:
        print(f"\n{'='*60}")
        print("🎉 All pages translated successfully!")
        print(f"Total context accumulated: {len(context_manager.context_window)} dialogue bubbles")
    else:
        print("\n🎉 All pages translated successfully!")


# Example usage
if __name__ == "__main__":
    import sys
    
    # Check for debug flag
    debug_mode = "--debug" in sys.argv
    if debug_mode:
        sys.argv.remove("--debug")
    
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
        translate_comic_series(existing_pages, debug=debug_mode)
    else:
        print("ℹ️  This is an example script for multi-page translation.")
        print("To use it, add your comic page files (page1.png, page2.png, etc.)")
        print("\nFor single page translation, use:")
        print("  python translate_and_fill_bubbles.py [--debug]")
        print("\nFor debug mode, add --debug flag:")
        print("  python translate_multipage.py --debug") 