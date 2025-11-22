import lmstudio as lms
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import LLM_MODEL, LLM_BASE_URL

class LLMClient:
    def __init__(self):
        self.model_name = LLM_MODEL
        self.api_host = LLM_BASE_URL.replace("http://", "").replace("https://", "").replace("/v1", "")
        if self.api_host.endswith("/"):
            self.api_host = self.api_host[:-1]
        
    def polish_text_safe(self, text: str) -> str:
        """
        Polishes the text using the LLM.
        Splits by paragraphs to avoid overlap duplication issues.
        """
        paragraphs = text.split("\n\n")
        polished_paragraphs = []
        
        # Group paragraphs into chunks of ~2000 chars
        chunks = []
        current_chunk = []
        current_length = 0
        
        for p in paragraphs:
            if current_length + len(p) > 2000:
                chunk_text = "\n\n".join(current_chunk)
                if chunk_text.strip():
                    chunks.append(chunk_text)
                current_chunk = [p]
                current_length = len(p)
            else:
                current_chunk.append(p)
                current_length += len(p)
        
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)
        
        total_chunks = len(chunks)
        print(f"Total chunks to process: {total_chunks}")

        try:
            print(f"Connecting to LM Studio at {self.api_host}...")
            client = lms.Client(api_host=self.api_host)
            
            model = client.llm.model(self.model_name)
            
            for i, chunk in enumerate(chunks):
                progress_pct = ((i + 1) / total_chunks) * 100
                print(f"Processing chunk {i + 1}/{total_chunks} ({progress_pct:.1f}%)")
                polished_paragraphs.append(self._process_chunk(model, chunk))
                    
        except Exception as e:
            print(f"Error initializing LM Studio client: {e}")
            return text # Return original text on failure
                
        return "\n\n".join(polished_paragraphs)

    def _process_chunk(self, model, text):
        system_prompt = "Sen profesyonel bir redaktör ve editörsün. Görevin, OCR (Optik Karakter Tanıma) işleminden geçmiş bozuk metinleri düzeltmek."
        user_prompt = f"""Aşağıdaki metin bir kitaptan taranmıştır ve OCR hataları, yanlış satır kesmeleri ve bozuk cümleler içerebilir.
Lütfen metni anlamını değiştirmeden aşağıdaki kurallara göre düzenle:
1. Bölünmüş kelimeleri birleştir (tire ile ayrılmış satır sonları).
2. Gereksiz satır sonlarını kaldır ve paragrafları düzgün hale getir.
3. OCR kaynaklı harf hatalarını (örn. 'l' yerine '1', 'rn' yerine 'm') bağlama göre düzelt.
4. Asla yorum ekleme, sadece düzeltilmiş metni ver.
5. Markdown formatını koru (başlıklar vs.).

Metin:
{text}
"""
        try:
            # The SDK's model.respond() takes a string prompt.
            # To include system prompt, we might need to format it.
            # Or use a chat structure if supported. 
            # Based on docs: result = model.respond("...")
            # We will combine them.
            
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Using predict or respond. Docs said respond.
            result = model.respond(full_prompt)
            
            # result might be an object with .content or just a string?
            # Docs: print(result) -> implies it has a string representation or is a string.
            # JS example: console.info(result.content). Python example: print(result).
            # Let's assume result is the string or has a __str__.
            # But to be safe, let's check if it has .content
            
            if hasattr(result, 'content'):
                return result.content
            return str(result)
            
        except Exception as e:
            print(f"Error processing chunk with LM Studio: {e}")
            return text
