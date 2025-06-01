#!/usr/bin/env python3
"""
Script to extract the last 6 pages from avatar_test.pdf and save as avatar_test_cropped.pdf
"""

import PyPDF2
import sys
import os

def crop_last_pages(input_pdf_path, output_pdf_path, num_pages=6):
    """
    Extract the last num_pages from input PDF and save to output PDF
    
    Args:
        input_pdf_path (str): Path to the input PDF file
        output_pdf_path (str): Path to save the cropped PDF
        num_pages (int): Number of pages to extract from the end
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_pdf_path):
            print(f"Error: Input file '{input_pdf_path}' not found!")
            return False
        
        # Open the input PDF
        with open(input_pdf_path, 'rb') as input_file:
            pdf_reader = PyPDF2.PdfReader(input_file)
            total_pages = len(pdf_reader.pages)
            
            print(f"Total pages in '{input_pdf_path}': {total_pages}")
            
            if total_pages < num_pages:
                print(f"Warning: PDF only has {total_pages} pages, extracting all pages")
                start_page = 0
            else:
                start_page = total_pages - num_pages
                
            print(f"Extracting pages {start_page + 1} to {total_pages}")
            
            # Create a PDF writer object
            pdf_writer = PyPDF2.PdfWriter()
            
            # Add the last num_pages to the writer
            for page_num in range(start_page, total_pages):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)
            
            # Write the output PDF
            with open(output_pdf_path, 'wb') as output_file:
                pdf_writer.write(output_file)
                
            print(f"Successfully created '{output_pdf_path}' with {len(pdf_writer.pages)} pages")
            return True
            
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return False

def main():
    input_pdf = "avatar_test.pdf"
    output_pdf = "avatar_test_cropped.pdf"
    pages_to_extract = 6
    
    print(f"Extracting last {pages_to_extract} pages from '{input_pdf}'...")
    
    success = crop_last_pages(input_pdf, output_pdf, pages_to_extract)
    
    if success:
        print("✅ PDF cropping completed successfully!")
    else:
        print("❌ PDF cropping failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 