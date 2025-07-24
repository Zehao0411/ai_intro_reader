"""
Step 1: Generate JSON file for manual annotation of introduction boundaries
This script scans PDF files in the papers_to_read folder and creates a JSON file
where users can manually specify the start and end of introduction sections.
"""

import os
import json
import PyPDF2
from pathlib import Path
import re

def extract_title_from_pdf(pdf_path):
    """
    Use filename (without extension) as the title.
    """
    return Path(pdf_path).stem

def scan_papers_and_generate_json():
    """
    Scan papers_to_read folder and generate JSON file for manual annotation.
    """
    papers_folder = Path("papers_to_read")
    
    if not papers_folder.exists():
        print("Error: papers_to_read folder not found!")
        return
    
    # Find all PDF files
    pdf_files = list(papers_folder.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in papers_to_read folder.")
        return
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Generate data structure
    papers_data = {}
    
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        
        # Extract title
        title = extract_title_from_pdf(pdf_file)
        
        # Create entry
        papers_data[pdf_file.name] = {
            "title": title,
            "type": "",            # To be filled manually: "theoretical" or "empirical"
            "start_of_intro": "",  # To be filled manually
            "end_of_intro": "",    # To be filled manually
            "notes": ""            # Optional field for additional notes
        }
    
    # Save to JSON file
    output_file = "papers_annotation.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(papers_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nGenerated {output_file} with {len(papers_data)} papers")
    print("\nPlease fill in the following fields manually:")
    print("1. 'type': Either 'theoretical' or 'empirical'")
    print("2. 'start_of_intro' and 'end_of_intro': Text patterns that identify the introduction section")
    print("\nExample:")
    print("  'type': 'theoretical'")
    print("  'start_of_intro': '1. Introduction'")
    print("  'end_of_intro': '2. Literature Review'")
    print("  or")
    print("  'type': 'empirical'")
    print("  'start_of_intro': 'Introduction'")
    print("  'end_of_intro': 'Data and Methodology'")

if __name__ == "__main__":
    scan_papers_and_generate_json() 