import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

# Mock lmstudio before importing llm_client
sys.modules['lmstudio'] = MagicMock()
sys.modules['langchain_text_splitters'] = MagicMock()

from src.llm_client import LLMClient

class TestLLMClient(unittest.TestCase):
    @patch('builtins.print')
    def test_polish_text_progress_logging(self, mock_print):
        client = LLMClient()
        
        # Create text that will result in 2 chunks (chunk size is ~2000)
        # We need > 2000 chars.
        paragraph = "A" * 1500
        text = f"{paragraph}\n\n{paragraph}"
        
        # Mock the model and response
        mock_model = MagicMock()
        mock_model.respond.return_value = "Polished"
        
        with patch('lmstudio.Client') as MockClient:
            MockClient.return_value.llm.model.return_value = mock_model
            
            client.polish_text_safe(text)
            
            # Verify print calls
            # We expect:
            # 1. "Total chunks to process: 2"
            # 2. "Connecting..."
            # 3. "Processing chunk 1/2 (50.0%)"
            # 4. "Processing chunk 2/2 (100.0%)"
            
            # Check if expected strings are in any of the print calls
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            
            self.assertIn("Total chunks to process: 2", print_calls)
            self.assertIn("Processing chunk 1/2 (50.0%)", print_calls)
            self.assertIn("Processing chunk 2/2 (100.0%)", print_calls)

if __name__ == '__main__':
    unittest.main()
