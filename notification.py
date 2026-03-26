import os
import requests
from dotenv import load_dotenv

load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

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
        
    if score >= 90:
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
