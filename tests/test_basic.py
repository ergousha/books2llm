import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.cleaner import TextCleaner
# We mock converter and llm_client because they have external dependencies
sys.modules['src.converter'] = MagicMock()
sys.modules['src.llm_client'] = MagicMock()

class TestBooks2LLM(unittest.TestCase):
    def test_cleaner(self):
        cleaner = TextCleaner()
        raw_text = "This is a pro-\ngram."
        cleaned = cleaner.clean_raw_ocr(raw_text)
        self.assertEqual(cleaned, "This is a program.")

    def test_cleaner_newlines(self):
        cleaner = TextCleaner()
        raw_text = "Line 1\n\n\nLine 2"
        cleaned = cleaner.clean_raw_ocr(raw_text)
        self.assertEqual(cleaned, "Line 1\n\nLine 2")

    def test_cleaner_html_tags(self):
        cleaner = TextCleaner()
        raw_text = "This is <b>bold</b> and this is <i>italic</i>."
        cleaned = cleaner.clean_raw_ocr(raw_text)
        self.assertEqual(cleaned, "This is bold and this is italic.")

if __name__ == '__main__':
    unittest.main()
