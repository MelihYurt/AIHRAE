import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY and API_KEY != "your_gemini_api_key_here":
    genai.configure(api_key=API_KEY)

def generate_professional_summary(text: str, candidate_data: dict) -> str:
    """
    Calls Google Gemini API to summarize the candidate's profile.
    Fallback to mock if API key is not set.
    """
    score = candidate_data.get("technical_score", 0)
    name = candidate_data.get("name", "Aday")
    
    if not API_KEY or API_KEY == "your_gemini_api_key_here":
        # Fallback Mock logic
        summary = f"[MOCK - .env dosyasına GEMINI_API_KEY girilmedi] {name} adlı adayın CV'si incelendi. "
        if score >= 70:
            summary += "Teknik yetkinlikleri güçlü, kesinlikle değerlendirilmeli."
        elif score >= 50:
            summary += "Temel düzeyde beklentileri karşılıyor. Mülakata alınması önerilir."
        else:
            summary += "Anahtar teknik yetkinliklere yeterince rastlanmadı."
        return summary
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Sen tecrübeli bir IK uzmanısın. Aşağıdaki adayın CV metnini incele ve yöneticine sunmak üzere ÇOK KISA, okuması kolay ve maddeler halinde yapılandırılmış, net bir özet sun. Destan veya uzun paragraflar KESİNLİKLE yazma.
        
        Aşağıdaki formata birebir uy:
        - 🎯 Sistem Puanı: {score}/100
        - 👤 Profil: (Adayın kim olduğu, eğitim/deneyim durumu. Max 2 açık cümle)
        - 💡 Güçlü Yönler: (En belirgin teknik ve sosyal yetkinlikleri)
        - 📌 Karar/Öneri: (İşe alım için uygunluk veya mülakat önerisi. Max 1 cümle)

        CV Metni:
        {text[:3000]}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Hatası: {str(e)}"