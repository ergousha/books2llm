import re

class TextCleaner:
    def __init__(self):
        pass

    def clean_raw_ocr(self, text: str) -> str:
        """
        Performs heuristic cleaning on raw OCR output.
        """
        # 1. Fix hyphenation at end of lines (e.g. "pro-\ngram" -> "program")
        # This is conservative: only joins if the next line starts with a lowercase letter
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        
        # 2. Remove multiple newlines (more than 2)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 3. Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # 3. Remove common OCR artifacts (optional, depends on observation)
        # Example: isolated single characters that are not words (excluding a, I, o, etc in Turkish context)
        # text = re.sub(r' \W ', ' ', text) 
        
        return text
