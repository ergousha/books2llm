# Books2LLM: OCR to Markdown to LLM Polish

Bu proje, PDF kitapları okuyup, Marker ile Markdown'a çeviren, ardından yerel LLM (LM Studio - Qwen3 Vl 30B) kullanarak metni temizleyen ve düzelten bir Python uygulamasıdır.

## Mimari

1.  **PDF Ingestion**: `input/` klasöründeki PDF dosyaları okunur.
2.  **OCR & Conversion**: `marker-pdf` kütüphanesi kullanılarak PDF'ler Markdown formatına çevrilir. Görseller ve tablolar korunur.
3.  **Pre-processing**: Bariz OCR hataları regex ve heuristic yöntemlerle temizlenir.
4.  **LLM Polishing**: Metin, LM Studio üzerinde çalışan Qwen3 Vl 30B modeline gönderilir. "Semantic Cleaning" yapılarak cümleler birleştirilir ve düzeltilir.
5.  **Output**: Temizlenmiş metin `output/` klasörüne, her kitap için tek bir Markdown dosyası olarak kaydedilir.

## Gereksinimler

- Python 3.10+
- LM Studio (Qwen3 Vl 30B modeli yüklü ve server modu aktif: `http://localhost:1234/v1`)
- GPU (Marker ve LLM için önerilir)

## Kurulum

Bu proje, bağımlılıkları izole etmek için Python sanal ortamı (venv) kullanır. `make install` komutu otomatik olarak bir `.venv` klasörü oluşturur.

```bash
make install
```

## Kullanım

1.  PDF dosyalarınızı `input/` klasörüne koyun.
2.  Uygulamayı çalıştırın (Sanal ortam otomatik olarak kullanılır):
    ```bash
    make run
    ```
3.  Sonuçları `output/` klasöründe bulabilirsiniz.

## Yapılandırma

- `src/config.py`: LLM ayarları, model adı ve diğer parametreler buradan değiştirilebilir.
