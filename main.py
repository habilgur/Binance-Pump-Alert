import os
import sys
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD_PERCENT = float(os.getenv("THRESHOLD_PERCENT", "50.0"))

def send_telegram(message: str) -> bool:
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[UYARI] TELEGRAM_TOKEN veya CHAT_ID ortam değişkeni tanımlanmamış!")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        print("[BİLGİ] Telegram mesajı başarıyla iletildi.")
        return True
    except Exception as e:
        print(f"[HATA] Telegram mesajı gönderilemedi: {e}")
        return False

def fetch_tickers():
    # GitHub Actions sunucuları (ABD merkezli) Binance Futures (fapi) için 451 dönebilir.
    # Bu nedenle önce Futures, bölgesel kısıt varsa Global Vision API denenir.
    endpoints = [
        ("Binance Futures", "https://fapi.binance.com/fapi/v1/ticker/24hr"),
        ("Binance Global Data", "https://data-api.binance.vision/api/v3/ticker/24hr"),
    ]

    for source_name, url in endpoints:
        try:
            print(f"[BİLGİ] {source_name} verileri alınıyor...")
            response = requests.get(url, timeout=15)
            if response.status_code == 451:
                print(f"[UYARI] {source_name} bölgesel kısıt (HTTP 451) döndü. Alternatif uç noktaya geçiliyor...")
                continue
            response.raise_for_status()
            data = response.json()
            print(f"[BİLGİ] {source_name} üzerinden veriler başarıyla alındı.")
            return source_name, data
        except Exception as e:
            print(f"[UYARI] {source_name} isteği başarısız oldu: {e}")
            continue

    print("[HATA] Hiçbir Binance veri kaynağına erişilemedi!")
    sys.exit(1)

def check_binance_spikes():
    source_name, tickers = fetch_tickers()

    alerts = []
    total_usdt_pairs = 0

    for ticker in tickers:
        symbol = ticker.get("symbol", "")
        # Sadece USDT çiftlerini tara
        if symbol.endswith("USDT"):
            total_usdt_pairs += 1
            try:
                price_change_percent = float(ticker.get("priceChangePercent", 0.0))
                last_price = ticker.get("lastPrice", "0")

                # Eşiği geçen koinleri topla
                if price_change_percent >= THRESHOLD_PERCENT:
                    alerts.append(f"🚀 *{symbol}*: +%{price_change_percent:.2f}\n💵 Fiyat: `{last_price} USDT`")
            except (ValueError, TypeError):
                continue

    print(f"[BİLGİ] Toplam {total_usdt_pairs} USDT çifti tarandı ({source_name}). Eşiği (>={THRESHOLD_PERCENT}%) geçen: {len(alerts)}")

    if alerts:
        msg = (
            f"🔥 *Binance Yüksek Performans Uyarısı (>=%{THRESHOLD_PERCENT:.1f})* [{source_name}]\n\n"
            + "\n\n".join(alerts)
        )
        send_telegram(msg)
    else:
        print(f"[BİLGİ] Eşiği geçen (>=%{THRESHOLD_PERCENT:.1f}) koin bulunamadı. Telegram mesajı gönderilmedi.")

if __name__ == "__main__":
    check_binance_spikes()
