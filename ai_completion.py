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

def generate_tailored_email(candidate_data: dict) -> str:
    """
    Calls Google Gemini API to generate a tailored email for the candidate.
    """
    score = candidate_data.get("technical_score", 0)
    name = candidate_data.get("name", "Aday")
    surname = candidate_data.get("surname", "")
    school = candidate_data.get("school", "")
    skills = candidate_data.get("skills", "")
    status = candidate_data.get("status", "Reject")
    
    if not API_KEY or API_KEY == "your_gemini_api_key_here":
        if status == "Interview" or score >= 80:
            return f"Sayın {name} {surname},\n\nŞirketimize yaptığınız başvuru için teşekkür ederiz. Profiliniz olumlu değerlendirilmiştir. En kısa sürede sizinle mülakat planlaması için iletişime geçeceğiz.\n\nİyi günler dileriz."
        else:
            return f"Sayın {name} {surname},\n\nŞirketimize yaptığınız başvuru için teşekkür ederiz. Profiliniz şu anki açık pozisyonlarımızla tam olarak eşleşmemiştir. Özgeçmişinizi gelecekteki fırsatlar için veritabanımızda saklayacağız.\n\nİyi günler dileriz."
            
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        if status == "Interview" or score >= 80:
            prompt = f"""
            Sen bir İnsan Kaynakları uzmanısın. Aşağıdaki adaya bir İK mülakatı daveti e-postası yaz. 
            Şirket adı olarak "TechNova Solutions" kullan. Pozisyon adı olarak "Full Stack Developer" kullan.
            E-postada kesinlikle köşeli parantezli boşluklar (örn: [Şirket Adı], [Tarih], vb.) bırakma, hayali mantıklı detaylar ekle.
            E-posta profesyonel, samimi ve motive edici olmalı. Adayın okulundan ({school}) veya yeteneklerinden ({skills}) kısa ve nazikçe bahsederek e-postayı özelleştir.
            Sadece e-posta metnini yaz (konu başlığı hariç).

            Adayın Adı Soyadı: {name} {surname}
            """
        else:
            prompt = f"""
            Sen bir İnsan Kaynakları uzmanısın. Aşağıdaki adaya nazik, yapıcı ve profesyonel bir ret (olumsuz sonuç) e-postası yaz. 
            Şirket adı olarak "TechNova Solutions" kullan. Pozisyon adı olarak "Full Stack Developer" kullan.
            E-postada kesinlikle köşeli parantezli boşluklar (örn: [Şirket Adı]) bırakma, direkt bu bilgileri kullan.
            Adayın zaman ayırıp başvurduğu için teşekkür et ve yeteneklerinin ({skills}) değerli olduğunu ancak şu anki pozisyonla eşleşmediğini belirt.
            Sadece e-posta metnini yaz (konu başlığı hariç).

            Adayın Adı Soyadı: {name} {surname}
            """
            
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Sayın {name},\nSistemde oluşan bir hatadan dolayı e-postanız otomatik oluşturulamadı. Lütfen İK ile iletişime geçiniz."