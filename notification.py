import os
import re
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_slack_notification(candidate_data: dict, summary: str):
    """
    Sends a message to a Slack Webhook if the candidate's score is >= 90.
    """
    # Eğer url formata uygun değilse (veya içi boşsa) hiçbir şey yapma
    if not SLACK_WEBHOOK_URL or not SLACK_WEBHOOK_URL.startswith("http"):
        return
        
    try:
        score = int(candidate_data.get("technical_score", 0))
    except ValueError:
        score = 0
        
    if score >= 80:
        name = candidate_data.get("name", "Bilinmiyor")
        surname = candidate_data.get("surname", "")
        school = candidate_data.get("school", "")
        
        payload = {
            "text": f"🎉 *Yıldız Aday Alarmı (Puan: {score}/100)*\n\n*Aday:* {name} {surname}\n*Üniversite:* {school}\n\n*Yapay Zeka Özeti:*\n{summary}"
        }
        
        try:
            requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
            print(f"Slack notification sent for {name}.")
        except Exception as e:
            print(f"Slack Notification Error: {e}")

def send_candidate_email(candidate_data: dict, email_content: str):
    """
    Sends a real email to the candidate using SMTP (Gmail).
    Requires SMTP_EMAIL and SMTP_PASSWORD to be set in .env.
    """
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("SMTP_EMAIL or SMTP_PASSWORD not set in .env. Skipping real email dispatch.")
        return
        
    raw_contact = candidate_data.get("contact", "")
    
    # E-posta adresini regex ile ayrıştır (telefon veya diğer metinlerden temizle)
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', str(raw_contact))
    recipient = email_match.group(0) if email_match else ""

    # Çok basit bir mail kontrolü
    if not recipient or "@" not in str(recipient):
        print(f"Invalid email address extracted: {raw_contact}. Cannot send email.")
        return
        
    status = candidate_data.get("status", "Reject")
    score = int(candidate_data.get("technical_score", 0))
    if status == "Interview" or score >= 80:
        subject = "Mülakat Daveti - İnsan Kaynakları"
    else:
        subject = "Başvurunuz Hakkında - İnsan Kaynakları"
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject
        
        msg.attach(MIMEText(email_content, 'plain', 'utf-8'))
        
        # Setup SMTP (varsayılan olarak Gmail üzerinden yapıyoruz)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Real email sent successfully to {recipient}")
    except Exception as e:
        print(f"Failed to send email to {recipient}: {e}")
