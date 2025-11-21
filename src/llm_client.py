import lmstudio as lms
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import LLM_MODEL

class LLMClient:
    def __init__(self):
        self.model_name = LLM_MODEL
        # We don't initialize the client here as a persistent object because 
        # the SDK usage pattern suggests 'with lms.Client() as client:'.
        # However, to keep the class structure, we can initialize it in methods 
        # or keep a reference if the SDK supports it.
        # The docs show:
        # with lms.Client() as client:
        #     model = client.llm.model("...")
        #     ...
        pass

    def polish_text_safe(self, text: str) -> str:
        """
        Polishes the text using the LLM.
        Splits by paragraphs to avoid overlap duplication issues.
        """
        paragraphs = text.split("\n\n")
        polished_paragraphs = []
        
        # Group paragraphs into chunks of ~2000 chars
        current_chunk = []
        current_length = 0
        
        # We create the client once for the batch to avoid overhead?
        # Or per chunk? The SDK seems to handle connection.
        # Let's try to use a single client context for the whole process if possible,
        # but this method is called once per file.
        
        try:
            # Connect to LM Studio
            # Note: The user needs to have the model loaded or available.
            # The SDK might allow listing models or getting the loaded one.
            # For now we assume the user provided model name is correct or we try to find it.
            
            print(f"Connecting to LM Studio...")
            client = lms.Client()
            
            # Attempt to get the model. 
            # If the user has it loaded, we might need to query what's loaded or use the specific string.
            # The 'model' method usually loads it or gets the handle.
            # If we are unsure of the exact path, we can try to list.
            # But let's stick to the config.
            
            # If the user says "Qwen3 Vl 30B", that might be the display name.
            # The SDK usually needs the path-like ID (e.g. "qwen3-vl-30b").
            # Since we don't know the exact ID, we might face an issue.
            # However, let's try to use the config value.
            
            # To be safe, let's try to get *any* loaded model if possible, or the specific one.
            # The docs example: client.llm.model("openai/gpt-oss-20b")
            
            # Let's assume the user put the correct ID in config.py.
            model = client.llm.model(self.model_name)
            
            for p in paragraphs:
                if current_length + len(p) > 2000:
                    chunk_text = "\n\n".join(current_chunk)
                    if chunk_text.strip():
                        polished_paragraphs.append(self._process_chunk(model, chunk_text))
                    current_chunk = [p]
                    current_length = len(p)
                else:
                    current_chunk.append(p)
                    current_length += len(p)
            
            if current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                if chunk_text.strip():
                    polished_paragraphs.append(self._process_chunk(model, chunk_text))
                    
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
