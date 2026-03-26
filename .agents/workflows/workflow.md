---
description: AI HR Aday Eleme Sistemini Kurma
---

// turbo-all
1. Proje dizininde Python Sanal Ortamını oluştur ve aktif et(opsiyonel):
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Paketleri Yükle (fastapi, uvicorn, pdfplumber, gemini, google-sheets):
```bash
pip install fastapi "uvicorn[standard]" python-multipart pdfplumber google-generativeai python-dotenv gspread google-auth
```

3. Gerekli Çevre Değişkenleri (.env) Dosyasını Oluştur:
```bash
echo GEMINI_API_KEY="" > .env
echo SPREADSHEET_ID="" >> .env
```

4. Python Kod Kütüphanesini ve Frontend'i oluştur:
- `index.html` (Basit frontend arayüzü ve POST istek kodları)
- `pdf_parser.py` (pdfplumber ile text parse)
- `processor.py` (Metnin ad/soyad olarak GEMINi parse'ı)
- `ai_completion.py` (Google Gemini AI promptları)
- `sheets_integration.py` (Google Sheets'e gspread veri yazdırma / fallback CSV)
- `notification.py` (Slack webhook ile >90 puan aday bilgilendirme)
- `main.py` (FastAPI Endpoints)
- `credentials.json` (Manuel olarak Service Account'tan çekilecek)

5. Sistemi Web Sunucusunda Çalıştır:
```bash
.\.venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```