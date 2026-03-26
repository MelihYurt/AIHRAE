import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY and API_KEY != "your_gemini_api_key_here":
    genai.configure(api_key=API_KEY)

def process_candidate_text(text: str) -> dict:
    """
    Uses Gemini to extract structured data and evaluate technical score.
    Returns: name, surname, school, contact, experience, skills, technical_score, status
    """
    if not API_KEY or API_KEY == "your_gemini_api_key_here":
        # Fallback dummy logic
        return {
            "name": text[:50].replace('\\n', ' '),
            "surname": "",
            "school": "Örnek Üniversite",
            "contact": "ornek@mail.com",
            "experience": "2",
            "skills": "Python, SQL",
            "technical_score": 60,
            "status": "Uygun"
        }

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Aşağıdaki CV metninden şu bilgileri çıkarıp sadece geçerli bir JSON formatında döndür:
        - "name": Ad (eğer net anlaşılamıyorsa boş bırak)
        - "surname": Soyad
        - "school": Mezun olunan üniversite/bölüm (yoksa boş string)
        - "contact": Eposta veya Telefon
        - "experience": Kaç yıl deneyimi olduğu (yoksa "0")
        - "skills": Teknik becerileri (virgülle ayrılmış string)
        - "technical_score": CV'nin genel yazılım yetkinliklerine (Örn: Python, modern kütüphaneler) göre 100 üzerinden değerlendirme puanı (X/100 şekli değil, sadece sayı olarak). EĞER BİR CV DEĞİLSE VEYA YETERSİZSE 0 ver.
        
        CV Metni:
        {text[:2000]}
        
        Sadece JSON objesini döndür. Markdown etiketleri kullanmadan direkt json dizesi de olabilir ancak geçerli JSON olmalı.
        Örnek:
        {{ "name": "Ali", "surname": "Yılmaz", "school": "X Üni", "contact": "ali@...", "experience": "3", "skills": "Python, SQL", "technical_score": 85 }}
        """
        response = model.generate_content(prompt)
        content = response.text.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        data = json.loads(content.strip())
        
        # Ensure correct types
        score = int(data.get("technical_score", 0))
        data["technical_score"] = score
        data["status"] = "Uygun" if score >= 50 else "Uygun Değil"
        
        # Make sure essential fields exist
        for k in ["name", "surname", "school", "contact", "experience", "skills"]:
            if k not in data:
                data[k] = ""
                
        return data
        
    except Exception as e:
        print(f"Extraction error: {e}")
        return {
            "name": "Format Hatası",
            "surname": "",
            "school": "",
            "contact": "",
            "experience": "",
            "skills": "",
            "technical_score": 0,
            "status": "Hata: AI Parse Edemedi"
        }
