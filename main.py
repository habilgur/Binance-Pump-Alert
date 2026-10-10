import os
import sys
import json
import time
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
STATE_FILE = "state.json"
FUTURES_SYMBOLS_FILE = "futures_symbols.json"

# Anti-Spam Yapılandırması
COOLDOWN_SECONDS = 4 * 3600   # 4 saat (Aynı koin için 4 saat boyunca tekrar bildirim atılmaz)
STEP_UP_PERCENT = 15.0        # 4 saat dolmasa bile koin +%15 daha fazla yükselirse "Yeni Zirve" bildirimi atılır

def load_state() -> dict:
    default_state = {
        "threshold": float(os.getenv("THRESHOLD_PERCENT", "50.0") or "50.0"),
        "last_update_id": 0,
        "history": {}
    }
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key, val in default_state.items():
                    if key not in data:
                        data[key] = val
                return data
        except Exception as e:
            print(f"[UYARI] {STATE_FILE} okunamadı ({e}), varsayılan durum kullanılıyor.")
    return default_state

def save_state(state: dict):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print("[BİLGİ] Durum (state.json) başarıyla kaydedildi.")
    except Exception as e:
        print(f"[HATA] {STATE_FILE} kaydedilemedi: {e}")

def load_futures_symbols() -> set:
    """Yalnızca aktif Binance Vadeli İşlemler (Futures) paritelerini yükler/günceller."""
    symbols = set()
    if os.path.exists(FUTURES_SYMBOLS_FILE):
        try:
            with open(FUTURES_SYMBOLS_FILE, "r", encoding="utf-8") as f:
                symbols = set(json.load(f))
        except Exception:
            pass

    # Eğer API erişilebilir durumdaysa vadeli işlem paritelerini canlı güncelle
    try:
        res = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo", timeout=5)
        if res.status_code == 200:
            api_symbols = [
                s["symbol"] for s in res.json().get("symbols", [])
                if s.get("contractType") == "PERPETUAL" and s.get("status") == "TRADING"
            ]
            if api_symbols:
                symbols = set(api_symbols)
                with open(FUTURES_SYMBOLS_FILE, "w", encoding="utf-8") as f:
                    json.dump(sorted(api_symbols), f, indent=2)
                print(f"[BİLGİ] Vadeli işlemler parite listesi güncellendi ({len(symbols)} adet).")
    except Exception:
        pass

    return symbols

def send_telegram(message: str) -> bool:
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[UYARI] TELEGRAM_TOKEN veya CHAT_ID tanımlı değil!")
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
        print("[BİLGİ] Telegram bildirimi iletildi.")
        return True
    except Exception as e:
        print(f"[HATA] Telegram mesajı gönderilemedi: {e}")
        return False

def process_telegram_commands(state: dict) -> dict:
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return state

    last_update_id = state.get("last_update_id", 0)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"offset": last_update_id + 1, "timeout": 5}

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        updates = res.json().get("result", [])
    except Exception as e:
        print(f"[UYARI] Telegram komutları alınamadı: {e}")
        return state

    for update in updates:
        update_id = update.get("update_id", 0)
        if update_id > state.get("last_update_id", 0):
            state["last_update_id"] = update_id

        message = update.get("message", {})
        sender_chat_id = str(message.get("chat", {}).get("id", ""))
        text = message.get("text", "").strip()

        # Güvenlik Kontrolü: Yalnızca yetkili Chat ID'den gelen komutları işle
        if sender_chat_id != str(CHAT_ID):
            continue

        if not text:
            continue

        text_lower = text.lower()
        print(f"[BİLGİ] Telegram'dan yeni mesaj alındı: {text}")

        # Eşik değiştirme komutları: /esik 70, /threshold 80, /set 60
        if text_lower.startswith(("/esik", "/threshold", "/set")):
            parts = text.split()
            if len(parts) >= 2:
                try:
                    val_str = parts[1].replace("%", "").replace(",", ".")
                    new_val = float(val_str)
                    state["threshold"] = new_val
                    send_telegram(f"✅ *Futures Alarm Eşiği Güncellendi!*\n\nYeni Eşik: *%{new_val:.1f}*\nArtık Futures 24s artışı bu oranın üzerinde olan koinler bildirilecek.")
                except ValueError:
                    send_telegram("❌ Geçersiz sayı formatı. Örnek kullanım: `/esik 60` veya `/esik 100`")
            else:
                send_telegram(f"ℹ️ Mevcut alarm eşiği: *%{state.get('threshold', 50.0):.1f}*\nDeğiştirmek için: `/esik 80` yazabilirsiniz.")

        elif text_lower in ["/durum", "/status"]:
            th = state.get("threshold", 50.0)
            hist_count = len(state.get("history", {}))
            send_telegram(
                f"📊 *Binance Futures Bot Durumu:*\n\n"
                f"• Aktif Alarm Eşiği: *%{th:.1f}*\n"
                f"• Takipteki (önceden bildirilmiş) Futures koinler: *{hist_count}*\n"
                f"• Filtre: *Sadece Binance Futures (Vadeli İşlemler)*\n"
                f"• Tarama Aralığı: *Her 5 dakikada bir*\n"
                f"• Anti-Spam Koruması: *Aktif (4 saat cooldown / +%15 kademeli zirve)*\n\n"
                f"Eşiği değiştirmek için: `/esik <yüzde>` (Örn: `/esik 75`)"
            )

        elif text_lower in ["/yardim", "/help", "/start"]:
            th = state.get("threshold", 50.0)
            send_telegram(
                f"🤖 *Binance Futures Spike Alert Botu*\n\n"
                f"Kullanabileceğiniz komutlar:\n"
                f"• `/esik 80` : Alarm eşiğini %80 yapar\n"
                f"• `/durum` : Mevcut ayarları ve bot durumunu gösterir\n"
                f"• `/yardim` : Bu mesajı gösterir\n\n"
                f"Mevcut Eşik: *%{th:.1f}*"
            )

        # Kullanıcı komutsuz doğrudan sayı yazdıysa (örn: "80" veya "%80")
        elif text.replace("%", "").replace(",", ".").replace(".", "", 1).isdigit():
            try:
                new_val = float(text.replace("%", "").replace(",", "."))
                state["threshold"] = new_val
                send_telegram(f"✅ *Futures Alarm Eşiği Güncellendi!*\nYeni Eşik: *%{new_val:.1f}*")
            except ValueError:
                pass

    return state

def fetch_tickers():
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

def match_futures_symbol(symbol: str, futures_set: set) -> str | None:
    """Spot sembolünü Futures paritesi ile eşleştirir (örn: 1000PEPEUSDT vb.)."""
    if symbol in futures_set:
        return symbol
    thousand_sym = "1000" + symbol
    if thousand_sym in futures_set:
        return thousand_sym
    return None

def filter_alerts_anti_spam(raw_alerts: list, state: dict) -> tuple[list, dict]:
    history = state.get("history", {})
    now = time.time()
    filtered_messages = []

    # 24 saatten eski kayıtları temizle
    history = {
        sym: data for sym, data in history.items()
        if (now - data.get("time", 0)) < 24 * 3600
    }
    state["history"] = history

    for item in raw_alerts:
        futures_symbol = item["futures_symbol"]
        percent = item["percent"]
        price = item["price"]

        last_record = history.get(futures_symbol)
        should_alert = False
        status_note = ""

        if not last_record:
            # 1. Durum: Koin ilk kez eşiği aşıyor
            should_alert = True
            history[futures_symbol] = {"time": now, "percent": percent, "price": price}
        else:
            time_since_last = now - last_record.get("time", 0)
            last_percent = last_record.get("percent", 0.0)

            if time_since_last >= COOLDOWN_SECONDS:
                # 2. Durum: 4 saatlik cooldown süresi dolmuş, koin hala yüksek
                should_alert = True
                status_note = " *(🔄 Devam Ediyor)*"
                history[futures_symbol] = {"time": now, "percent": percent, "price": price}
            elif percent >= (last_percent + STEP_UP_PERCENT):
                # 3. Durum: 4 saat dolmamış ama koin +%15 daha fırlamış (Yeni Zirve!)
                should_alert = True
                diff = percent - last_percent
                status_note = f" *(🔥 Zirve Tazeledi: +%{diff:.1f} daha arttı)*"
                history[futures_symbol] = {"time": now, "percent": percent, "price": price}
            else:
                # 4. Durum: Kısa süre önce bildirilmiş, yeni ek yükseliş yok -> SPAM'I ENGELLE
                print(f"[SPAM ENGELİ] {futures_symbol} daha önce %{last_percent:.1f} ile bildirilmişti (Şu an: %{percent:.1f}). Tekrar bildirilmedi.")

        if should_alert:
            trade_link = f"https://www.binance.com/tr/futures/{futures_symbol}"
            filtered_messages.append(
                f"🚀 *{futures_symbol}*{status_note}: *+%{percent:.2f}*\n"
                f"💵 Fiyat: `{price} USDT` | [📱 Grafiği Aç]({trade_link})"
            )

    return filtered_messages, state

def check_binance_spikes():
    # 1. Mevcut durumu yükle
    state = load_state()

    # 2. Aktif Binance Futures parite listesini al (Sadece Vadeli İşlemlerde Olanlar)
    futures_symbols = load_futures_symbols()
    print(f"[BİLGİ] Takip edilen aktif Binance Futures parite sayısı: {len(futures_symbols)}")

    # 3. Telegram'dan gelen komutları kontrol et (/esik 80 vb.)
    state = process_telegram_commands(state)
    active_threshold = state.get("threshold", 50.0)
    print(f"[BİLGİ] Aktif Futures alarm eşiği: %{active_threshold:.1f}")

    # 4. Binance piyasa verilerini çek
    source_name, tickers = fetch_tickers()

    raw_candidates = []
    total_usdt_pairs = 0
    futures_matched = 0

    for ticker in tickers:
        symbol = ticker.get("symbol", "")
        if symbol.endswith("USDT"):
            total_usdt_pairs += 1

            # KRİTİK: Sadece Binance Futures (Vadeli İşlemler) listesinde olanları dahil et!
            # Spotta olup vadeli işlemlerde olmayan koinler (örn: CREAM) burada elenir.
            futures_symbol = match_futures_symbol(symbol, futures_symbols)
            if not futures_symbol:
                continue

            futures_matched += 1

            try:
                price_change_percent = float(ticker.get("priceChangePercent", 0.0))
                last_price = ticker.get("lastPrice", "0")

                if price_change_percent >= active_threshold:
                    raw_candidates.append({
                        "futures_symbol": futures_symbol,
                        "percent": price_change_percent,
                        "price": last_price,
                    })
            except (ValueError, TypeError):
                continue

    # Değişime göre Z-A (en çok artandan az artana) sırala
    raw_candidates.sort(key=lambda x: x["percent"], reverse=True)

    print(f"[BİLGİ] Toplam {futures_matched} adet Futures USDT çifti tarandı. Eşiği (>={active_threshold}%) aşan: {len(raw_candidates)}")

    # 5. Anti-Spam filtresinden geçir
    alerts, state = filter_alerts_anti_spam(raw_candidates, state)

    # 6. Yeni bildirim varsa gönder
    if alerts:
        msg = (
            f"🔥 *Binance Futures Yüksek Performans Uyarısı (>=%{active_threshold:.1f})*\n\n"
            + "\n\n".join(alerts)
        )
        send_telegram(msg)
        print(f"[BİLGİ] {len(alerts)} adet filtrelenmiş Futures bildirimi Telegram'a gönderildi.")
    else:
        print("[BİLGİ] Gönderilecek yeni/spam olmayan Futures bildirimi bulunamadı.")

    # 7. Güncellenmiş durumu kaydet
    save_state(state)

if __name__ == "__main__":
    check_binance_spikes()
