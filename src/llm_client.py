import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL

class LLMClient:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
            model=LLM_MODEL,
            temperature=0.1, # Low temperature for cleaning tasks
            max_tokens=4096
        )
        
        # Prompt for semantic cleaning in Turkish
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Sen profesyonel bir redaktör ve editörsün. Görevin, OCR (Optik Karakter Tanıma) işleminden geçmiş bozuk metinleri düzeltmek."),
            ("user", """Aşağıdaki metin bir kitaptan taranmıştır ve OCR hataları, yanlış satır kesmeleri ve bozuk cümleler içerebilir.
Lütfen metni anlamını değiştirmeden aşağıdaki kurallara göre düzenle:
1. Bölünmüş kelimeleri birleştir (tire ile ayrılmış satır sonları).
2. Gereksiz satır sonlarını kaldır ve paragrafları düzgün hale getir.
3. OCR kaynaklı harf hatalarını (örn. 'l' yerine '1', 'rn' yerine 'm') bağlama göre düzelt.
4. Asla yorum ekleme, sadece düzeltilmiş metni ver.
5. Markdown formatını koru (başlıklar vs.).

Metin:
{text}
""")
        ])
        
        self.chain = self.prompt | self.llm

    def polish_text(self, text: str) -> str:
        """
        Polishes the text using the LLM.
        Uses RecursiveCharacterTextSplitter to handle long texts.
        """
        # Split text into chunks to fit context window
        # We use a large chunk size to keep context, but small enough for the model
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200, # Overlap to maintain context
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        polished_chunks = []
        
        print(f"Processing {len(chunks)} chunks with LLM...")
        
        for i, chunk in enumerate(chunks):
            print(f"  - Chunk {i+1}/{len(chunks)}")
            try:
                response = self.chain.invoke({"text": chunk})
                polished_chunks.append(response.content)
            except Exception as e:
                print(f"Error processing chunk {i+1}: {e}")
                # Fallback: append original chunk if LLM fails
                polished_chunks.append(chunk)
        
        # Join chunks
        # Note: Simple join might duplicate overlap content if not handled carefully.
        # The user warned about this: "temizleme aşamasında örtüşme kullanırsanız aynı cümleler tekrar edebilir."
        # However, RecursiveCharacterTextSplitter creates overlaps.
        # Ideally, we should use a method that doesn't overlap for *processing* if we just concatenate,
        # OR we rely on the LLM to output exactly what was input (minus errors) and we try to merge.
        # Given the complexity of merging overlapped corrected text, and the user's suggestion:
        # "temizleme aşamasında sayfa bazlı veya paragraf bazlı ilerlemek daha güvenlidir."
        
        # Let's switch strategy: Split by paragraphs (double newline) without overlap for safety in concatenation,
        # UNLESS the paragraph is too huge.
        
        return "\n\n".join(polished_chunks)

    def polish_text_safe(self, text: str) -> str:
        """
        Alternative strategy: Split by paragraphs to avoid overlap duplication issues.
        """
        paragraphs = text.split("\n\n")
        polished_paragraphs = []
        
        # Group paragraphs into chunks of ~2000 chars
        current_chunk = []
        current_length = 0
        
        for p in paragraphs:
            if current_length + len(p) > 2000:
                # Process current chunk
                chunk_text = "\n\n".join(current_chunk)
                if chunk_text.strip():
                    polished_paragraphs.append(self._process_chunk(chunk_text))
                current_chunk = [p]
                current_length = len(p)
            else:
                current_chunk.append(p)
                current_length += len(p)
        
        # Process last chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            if chunk_text.strip():
                polished_paragraphs.append(self._process_chunk(chunk_text))
                
        return "\n\n".join(polished_paragraphs)

    def _process_chunk(self, text):
        try:
            response = self.chain.invoke({"text": text})
            return response.content
        except Exception as e:
            print(f"Error invoking LLM: {e}")
            return text
