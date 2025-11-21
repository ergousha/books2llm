import os
import sys
from pathlib import Path
from .config import INPUT_DIR, OUTPUT_DIR
from .converter import PDFConverter
from .cleaner import TextCleaner
from .llm_client import LLMClient

def main():
    # Ensure directories exist
    if not INPUT_DIR.exists():
        print(f"Input directory not found: {INPUT_DIR}")
        return
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Initialize components
    converter = PDFConverter()
    cleaner = TextCleaner()
    try:
        llm_client = LLMClient()
        llm_available = True
    except Exception as e:
        print(f"Warning: LLM Client could not be initialized ({e}). Skipping LLM polish.")
        llm_available = False

    # Process PDFs
    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in input directory.")
        return

    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}")
        
        # 1. Convert
        try:
            print("Step 1: Converting PDF to Markdown...")
            raw_md, metadata = converter.convert(pdf_path)
        except Exception as e:
            print(f"Failed to convert {pdf_path.name}: {e}")
            continue
            
        # 2. Clean
        print("Step 2: Heuristic Cleaning...")
        cleaned_md = cleaner.clean_raw_ocr(raw_md)
        
        # 3. LLM Polish
        final_md = cleaned_md
        if llm_available:
            print("Step 3: LLM Polishing (Semantic Cleaning)...")
            # Use the safe method to avoid overlap duplication
            final_md = llm_client.polish_text_safe(cleaned_md)
        
        # 4. Save
        output_file = OUTPUT_DIR / f"{pdf_path.stem}.md"
        print(f"Step 4: Saving to {output_file}...")
        output_file.write_text(final_md, encoding="utf-8")
        
        print(f"Done: {pdf_path.name}")

if __name__ == "__main__":
    main()
