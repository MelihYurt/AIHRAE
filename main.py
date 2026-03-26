from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from pdf_parser import extract_text_from_pdf
from processor import process_candidate_text
from sheets_integration import save_to_sheets_mock
from ai_completion import generate_professional_summary
from notification import send_slack_notification

app = FastAPI(title="AI HR System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    # A simple way to serve the static HTML file
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_cv(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "Lütfen sadece PDF dosyası yükleyin."}
        
    temp_file_path = f"temp_{file.filename}"
    try:
        # Save file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 1. Triggered: PDF Upload Trigger ->
        # 2. Processing Function (PDF Parser & Evaluation) ->
        extracted_text = extract_text_from_pdf(temp_file_path)
        candidate_data = process_candidate_text(extracted_text)
        
        # 3. External API (Google Sheets Sync) ->
        save_to_sheets_mock(candidate_data, extracted_text)

        # 4. AI Completion (Gemini)
        ai_summary = generate_professional_summary(extracted_text, candidate_data)
        
        # 5. Conditional Slack Webhook (Score >= 90)
        send_slack_notification(candidate_data, ai_summary)
        
        return {
            "success": True,
            "filename": file.filename,
            "candidate": candidate_data,
            "ai_summary": ai_summary,
            "extracted_text_preview": extracted_text[:200] + "..." if extracted_text else "Metin bulunamadı."
        }
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/best-candidate")
async def get_best_candidate():
    try:
        from sheets_integration import get_all_candidates
        candidates = get_all_candidates()
        
        if not candidates:
            return {"error": "Google Sheets'te hiç aday bulunamadı veya bağlanılamadı."}
            
        best_candidate = None
        highest_score = -1
        
        for p in candidates:
            try:
                score = int(p.get("Teknik Puan", 0))
            except ValueError:
                score = 0
                
            if score > highest_score:
                highest_score = score
                best_candidate = p
        
        if best_candidate:
            analysis_text = (
                f"- 🏆 **En Yüksek Puanlı Aday**\n"
                f"- 👤 **Ad Soyad:** {best_candidate.get('Ad', '')} {best_candidate.get('Soyad', '')}\n"
                f"- 🎯 **Teknik Puan:** {best_candidate.get('Teknik Puan', 0)}/100\n"
                f"- 🎓 **Okul:** {best_candidate.get('Okul', '')}\n"
                f"- 💼 **Deneyim:** {best_candidate.get('Deneyim', '')} Yıl\n"
                f"- 💡 **Beceriler:** {best_candidate.get('Beceriler', '')}\n"
                f"- 📞 **İletişim:** {best_candidate.get('İletişim', '')}\n"
                f"- 📌 **Durum:** {best_candidate.get('Durum', '')}"
            )
            return {"success": True, "analysis": analysis_text}
        else:
            return {"error": "Geçerli puana sahip aday bulunamadı."}
            
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
