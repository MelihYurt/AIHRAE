import os
import gspread
from google.oauth2.service_account import Credentials
import csv
from datetime import datetime

CREDENTIALS_FILE = "credentials.json"
CSV_FILE = "candidates.csv"

def get_sheet():
    # Fallback to local CSV if user didn't create Service Account JSON
    if not os.path.exists(CREDENTIALS_FILE):
        return None 
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    
    from dotenv import load_dotenv
    load_dotenv()
    sheet_id = os.getenv("SPREADSHEET_ID")
    if not sheet_id or sheet_id == "your_sheet_id_here":
         raise Exception("Lütfen .env dosyasına SPREADSHEET_ID=... değerini kendi Spreadsheet ID'niz ile ekleyin.")
         
    try:
        sheet = client.open_by_key(sheet_id).sheet1
        return sheet
    except Exception as e:
        raise Exception(f"Tabloya ulaşılamadı. Service account mail adresini Sheets dosyasına 'Editor' olarak eklediğinizden emin olun: {str(e)}")

def save_to_sheets_mock(candidate_data: dict, extracted_text: str):
    """
    Save structured candidate data to Google Sheets.
    Falls back to local candidates.csv if credentials.json is not provided.
    """
    try:
        sheet = get_sheet()
        
        row = [
            candidate_data.get("name", ""),
            candidate_data.get("surname", ""),
            candidate_data.get("school", ""),
            candidate_data.get("contact", ""),
            str(candidate_data.get("experience", "")),
            candidate_data.get("skills", ""),
            candidate_data.get("technical_score", 0),
            candidate_data.get("status", "")
        ]
        
        if sheet:
            # Check if headers exist
            headers = sheet.row_values(1)
            expected_headers = ["Ad", "Soyad", "Okul", "İletişim", "Deneyim", "Beceriler", "Teknik Puan", "Durum"]
            if not headers or headers[0] != "Ad":
                sheet.insert_row(expected_headers, index=1)
                
            sheet.append_row(row)
        else:
            # YEDEK SİSTEM: CSV'ye kaydet
            file_exists = os.path.isfile(CSV_FILE)
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Ad", "Soyad", "Okul", "İletişim", "Deneyim", "Beceriler", "Teknik Puan", "Durum"])
                writer.writerow(row)
                
        return True
    except Exception as e:
        raise Exception(f"Google Sheets Kayıt Hatası: {str(e)}")

def get_all_candidates():
    try:
        sheet = get_sheet()
        if sheet:
            records = sheet.get_all_records()
            return records
        else:
            # YEDEK SİSTEM: CSV'den oku
            if not os.path.isfile(CSV_FILE):
                return []
            with open(CSV_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
    except Exception as e:
        raise Exception(f"Google Sheets Okuma Hatası: {str(e)}")
