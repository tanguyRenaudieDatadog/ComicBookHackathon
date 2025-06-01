"""
Multi-page Comic Translation with Multimodal Context Preservation

This script demonstrates how to translate multiple comic pages
while maintaining rich visual and textual context across pages 
using Llama4's multimodal capabilities.
"""

import os
from translation_context import MultimodalTranslationContext
from llama_api_client import LlamaAPIClient
from dotenv import load_dotenv

def translate_comic_series_multimodal(page_files, output_prefix="translated_page", debug=False, 
                                    source_lang="English", target_lang="Russian"):
    """
    Translate a series of comic pages with continuous multimodal context
    
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
        print("Please add either 'api_key' or 'LLAMA_API_KEY' to your .env file")
        return None
    
    # Initialize Llama client and multimodal context manager
    client = LlamaAPIClient(api_key=api_key)
    context_manager = MultimodalTranslationContext(client)
    
    if debug:
        print(f"🧠 Initialized multimodal context manager with Llama4 vision capabilities")
    
    for i, page_file in enumerate(page_files):
        page_num = i + 1
        if debug:
            print(f"\n{'='*60}")
            print(f"📖 Processing Page {page_num}: {page_file}")
            print(f"🌐 Translation: {source_lang} → {target_lang}")
            print(f"🧠 Using multimodal AI context analysis")
            print(f"{'='*60}")
        else:
            print(f"\n📖 Processing page {page_num}/{len(page_files)}: {os.path.basename(page_file)}")
        
        # Load previous context if available
        if i > 0:
            prev_context_file = f"{output_prefix}_{i}_context.json"
            if os.path.exists(prev_context_file):
                context_manager.load_context(prev_context_file)
                if debug:
                    print(f"✓ Loaded context from {len(context_manager.bubble_contexts)} previous bubbles")
                    print(f"✓ Known characters: {', '.join(context_manager.characters.keys())}")
                    print(f"✓ Current genre: {context_manager.genre}")
        
        # Process current page with multimodal context
        output_file = f"{output_prefix}_{page_num}.png"
        
        # Import and use the multimodal processing function
        from translate_and_fill_bubbles_multilang import process_comic_page_multimodal
        
        # Process page and get updated context
        context_manager = process_comic_page_multimodal(
            page_file, 
            output_file, 
            api_key=api_key,
            source_lang=source_lang, 
            target_lang=target_lang,
            page_number=page_num,
            context_manager=context_manager
        )
        
        # Save context for next page
        context_file = f"{output_prefix}_{page_num}_context.json"
        context_manager.save_context(context_file)
        
        if debug:
            print(f"\n📊 Page {page_num} Context Summary:")
            print(f"   Characters discovered: {len(context_manager.characters)}")
            print(f"   Total dialogue bubbles: {len(context_manager.bubble_contexts)}")
            print(f"   Current genre: {context_manager.genre}")
            print(f"   Context saved to: {context_file}")
            print(f"\n✅ Completed Page {page_num}")
    
    if debug:
        print(f"\n{'='*60}")
        print("🎉 All pages translated successfully with multimodal context!")
        print(f"📊 Final Statistics:")
        print(f"   Total pages processed: {len(page_files)}")
        print(f"   Total characters identified: {len(context_manager.characters)}")
        print(f"   Total dialogue bubbles: {len(context_manager.bubble_contexts)}")
        print(f"   Story genre: {context_manager.genre}")
        print(f"   Context files: {output_prefix}_*_context.json")
        print(f"{'='*60}")
    else:
        print(f"\n🎉 All pages translated successfully!")
        print(f"📊 Processed {len(page_files)} pages with {len(context_manager.characters)} characters")
    
    return context_manager

# Backward compatibility function
def translate_comic_series(page_files, output_prefix="translated_page", debug=False, 
                          source_lang="English", target_lang="Russian"):
    """
    Backward compatibility wrapper - now uses multimodal context by default
    """
    print("ℹ️  Using enhanced multimodal translation (upgrade from simple context)")
    return translate_comic_series_multimodal(page_files, output_prefix, debug, source_lang, target_lang)

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
        translate_comic_series_multimodal(existing_pages, debug=debug_mode, 
                                        source_lang=source_lang, target_lang=target_lang)
    else:
        print("ℹ️  Enhanced Multi-page Comic Translation with Multimodal AI")
        print("This version uses Llama4's vision capabilities for better context understanding.")
        print("\nUsage:")
        print("  python translate_multipage.py [--debug] [--source=English] [--target=Russian]")
        print("\nTo use it, add your comic page files (page1.png, page2.png, etc.)")
        print("\nFor single page translation, use:")
        print("  python translate_and_fill_bubbles_multimodal.py [image_path]")
        print("\nFor debug mode, add --debug flag:")
        print("  python translate_multipage.py --debug")
        print("\nLanguage options:")
        print("  --source=English --target=Spanish")
        print("  --source=Japanese --target=English") 