# 🚀 Binance Futures Pump / Spike Alert Bot

Bu proje, **Binance Futures** piyasasındaki tüm USDT vadeli işlem çiftlerini düzenli aralıklarla tarar ve belirlediğiniz değişim eşiğini (varsayılan: **%50**) aşan koinleri **Telegram Botu** aracılığıyla anlık bildirim olarak gönderir.

GitHub Actions sayesinde herhangi bir sunucu (VPS) kiralamadan tamamen ücretsiz çalışır.

---

## 📁 Proje Dosya Yapısı

```
Binance Pump Alert/
├── .github/
│   └── workflows/
│       └── checker.yml       # GitHub Actions zamanlayıcısı (her 10 dakikada bir)
├── .env.example              # Lokal test ortam değişkenleri örneği
├── .gitignore                # Git dışı tutulacak dosyalar
├── main.py                   # Binance tarayıcı ve Telegram gönderici script
├── requirements.txt          # Python bağımlılıkları (requests)
└── README.md                 # Kurulum ve kullanım kılavuzu
```

---

## 🛠️ Kurulum Adımları

### 1. Telegram Botu Oluşturma
1. Telegram uygulamasında [@BotFather](https://t.me/botfather) botunu bulun ve açın.
2. `/newbot` komutunu gönderin.
3. Botunuz için bir isim ve kullanıcı adı belirleyin (örn: `BinanceSpikeAlertBot`).
4. `@BotFather` size `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ` formatında bir **HTTP API Token** verecektir. Bu token'ı saklayın (`TELEGRAM_TOKEN`).
5. Yeni açtığınız botunuza gidin ve `/start` mesajı atarak sohbeti başlatın (botun size mesaj gönderebilmesi için şarttır).

### 2. Chat ID Öğrenme
1. Telegram'da [@userinfobot](https://t.me/userinfobot) botunu bulun ve `/start` yapın.
2. Botun size döneceği `Id:` alanındaki sayısal değer sizin **Chat ID**'nizdir (`CHAT_ID`).

---

### 3. GitHub Deposuna Yükleme ve Secret Tanımlama
Projeyi GitHub'a push ettikten sonra:

1. GitHub deponuzda **Settings** sekmesine gidin.
2. Sol menüden **Secrets and variables** -> **Actions** yolunu izleyin.
3. **New repository secret** butonuna tıklayarak aşağıdaki gizli anahtarları ekleyin:

| Secret Adı | Değer Açıklaması | Zorunlu mu? |
| :--- | :--- | :--- |
| `TELEGRAM_TOKEN` | @BotFather'dan aldığınız token | **Evet** |
| `CHAT_ID` | @userinfobot'tan aldığınız kullanıcı/grup ID | **Evet** |
| `THRESHOLD_PERCENT` | Değişim yüzdesi eşiği (örn: `30` veya `50`). Girilmezse `50.0` kullanılır. | Hayır |

---

### 4. Test Etme (Manuel Çalıştırma)
Otomatik 10 dakikalık cron beklemeden önce botu hemen test etmek için:
1. GitHub deponuzda **Actions** sekmesine gidin.
2. Sol tarafta **Binance Futures Spike Alert** iş akışını seçin.
3. Sağ üstteki **Run workflow** butonuna tıklayın.
4. Çalışmanın tamamlanmasını bekleyin ve logları inceleyin.

---

## 💻 Lokal Test (Kendi Bilgisayarınızda Çalıştırma)

1. Python paketlerini yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. Ortam değişkenlerini vererek scripti çalıştırın (PowerShell örneği):
   ```powershell
   $env:TELEGRAM_TOKEN="BOT_TOKENINIZ"
   $env:CHAT_ID="CHAT_IDNIZ"
   $env:THRESHOLD_PERCENT="10"   # Test amaçlı düşük eşik verebilirsiniz
   python main.py
   ```
