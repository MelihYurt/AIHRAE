from sheets_integration import get_sheet
import traceback

def test():
    try:
        sheet = get_sheet()
        if sheet:
            headers = sheet.row_values(1)
            print("BAŞARILI! Tabloya bağlanıldı. İlk satır:", headers)
            
            # Try a dummy append
            row = ["TestAd", "TestSoyad", "TestOkul", "Testİletişim", "1", "TestBeceriler", 100, "TestDurum"]
            sheet.append_row(row)
            print("BAŞARILI! Test satırı eklendi.")
        else:
            print("HATA: get_sheet() None döndürdü. credentials.json yok mu?")
    except Exception as e:
        print("HATA OLUŞTU:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
