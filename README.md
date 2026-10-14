# 🚀 Binance Spike / Pump Alert Bot

Bu proje, **Binance** piyasasındaki tüm vadeli USDT işlem çiftlerini periyodik olarak tarar, en çok yükselenleri (Z-A) sıralar ve belirlediğiniz eşiği aşan koinleri **Telegram Botu** aracılığıyla telefonunuza anlık bildirim olarak gönderir.

GitHub Actions ve `cron-job.org` entegrasyonu sayesinde herhangi bir sunucu (VPS) kiralamadan ve bilgisayarınızı açık tutmaya gerek kalmadan tamamen **ücretsiz ve 7/24 kesintisiz** çalışır.

---

## ✨ Öne Çıkan Özellikler

1. **📱 Telegram Üzerinden Canlı Kontrol:**
   * Eşik değiştirmek için koda veya ayarlara girmenize gerek yok!
   * Telegram'dan bota `/esik 80` veya doğrudan `80` yazmanız yeterlidir. Bot sonraki taramada eşiği otomatik günceller ve size teyit mesajı atar.
   * `/durum` yazarak aktif eşiği, takipteki koinleri ve tarama aralığını görebilirsiniz.

2. **🛡️ Akıllı Anti-Spam Koruması:**
   * Bir koin eşiği aştığında bildirilir ve hafızaya (`state.json`) alınır.
   * Aynı koin için **4 saat boyunca tekrar bildirim atılmaz**.
   * Ancak koin son bildirimden sonra **+%15 daha fırlarsa** (örn: %50'den %68'e çıkarsa), bot *"🔥 Zirve Tazeledi"* diyerek tek bir güncel bildirim daha gönderir.

3. **📊 Binance Futures ile Birebir Uyum:**
   * Binance mobil uygulamasındaki **Piyasalar -> Vadeli (Futures) -> 24s Değişim (Z-A / En Çok Yükselenler)** listesini baz alır.
   * Yalnızca vadeli işlemlerde aktif olan kontratları (`futures_symbols.json`) filtreler, spot-only koinleri eler.
   * Sade, temiz ve hızlı okunabilir metin formatında bildirim gönderir.

4. **🎯 Short Fırsat Analizi & Dashboard Bildirimleri:**
   * Hiçbir parite elenmeden tüm adaylar bildirilir; ancak anında karar verebilmeniz için analiz parametreleri eklenir:
     - **Zirveden Ret (Pullback):** Günün en yüksek fiyatından ne kadar çekildiği (en az %1.5 çekilme `✅ DÜZELTME` kabul edilir).
     - **24s Vadeli Hacim:** Likidite derinliği (`92M$`, `1.2B$` vb.).
     - **Fonlama (Funding):** Anlık fonlama oranı ve saat aralığı (`%-2.2 1(h)` vb.).
     - **Sinyal:** `✅ DÜZELTME`, `⚠️ HALA TEPEDE`, `🚨 SQUEEZE RİSKİ`.
   * Mobil bildirimlerde 1 saniyede okunabilecek ultra-clean dashboard formatı kullanılır.

5. **⚡ Kesintisiz Çalışma (Bölgesel Kısıt / Fallback Koruması):**
   * GitHub Actions bulut sunucularındaki olası bölgesel kısıtlamalara (HTTP 451) karşı Binance Futures ve Global Data kaynaklarını akıllı şekilde yönetir.

---

## 🤖 Kullanabileceğiniz Telegram Komutları

| Komut | Açıklama | Örnek |
| :--- | :--- | :--- |
| `/esik <yüzde>` | Bildirim alarm eşiğini anında günceller | `/esik 70` veya `/esik 100` |
| `<sayı>` | Komut yazmadan sadece sayı da gönderebilirsiniz | `80` veya `%65` |
| `/durum` | Aktif eşik ve takipteki koin sayısını gösterir | `/durum` |
| `/yardim` | Komut listesini gösterir | `/yardim` |

---

## ⏱️ Hassas Zamanlayıcı: cron-job.org Entegrasyonu (Önerilen)

GitHub Actions'ın dahili cron mekanizması yoğun saatlerde gecikebilir. **cron-job.org** entegrasyonu ile GitHub'ın zamanlayıcısını bypass edebilir, tam 5 (veya 2-3) dakikada bir **saniyesi şaşmadan** çalışmasını sağlayabilirsiniz.

### Kurulum Adımları:
1. [cron-job.org](https://cron-job.org/) adresinde ücretsiz bir hesap açın.
2. **CREATE CRONJOB** butonuna tıklayın.
3. Ayarları şu şekilde yapılandırın:

* **Title:** `Binance Pump Alert`
* **URL:**
  ```text
  https://api.github.com/repos/habilgur/Binance-Pump-Alert/actions/workflows/checker.yml/dispatches
  ```
* **Execution schedule:** `Every 5 minutes` (İsteğe göre 2 veya 3 dakika da seçilebilir)
* **Request method:** `POST`

#### Headers (Başlıklar):
| Key | Value |
| :--- | :--- |
| `Authorization` | `Bearer <GITHUB_PERSONAL_ACCESS_TOKEN>` |
| `Accept` | `application/vnd.github+json` |
| `User-Agent` | `CronJob` |

#### Request Body (Gövde):
```json
{"ref": "main"}
```

4. **CREATE** butonuna tıklayarak kaydedin. Sistem artık bilgisayarınız kapalıyken bile 7/24 dakikası dakikasına tetiklenecektir.

---

## 🌐 Hızlı Erişim & Yönetim Panelleri

Botun bulut servislerini izlemek ve yönetmek için kullanılan kontrol panelleri:

* ⏱️ **Cron-Job Tetikleyici Paneli:** [console.cron-job.org/dashboard](https://console.cron-job.org/dashboard)  
  *İşlerin 5 dakikada bir başarıyla yürütüldüğünü ve `204 No Content` teyitlerini buradan izleyebilirsiniz.*

* 🛡️ **Webshare Proxy Paneli:** [dashboard.webshare.io/dashboard](https://dashboard.webshare.io/dashboard)  
  *Binance Futures bölge kısıtını (HTTP 451) aşan Avrupa (Almanya, İspanya vb.) döner proxy hattını ve 1 GB ücretsiz bant genişliği kullanımını buradan takip edebilirsiniz.*

---

## 📁 Proje Dosya Yapısı

```
Binance Pump Alert/
├── .github/
│   └── workflows/
│       └── checker.yml       # GitHub Actions iş akışı ve state senkronizasyonu
├── .env.example              # Lokal test ortam değişkenleri örneği
├── .gitignore                # Git dışı tutulacak dosyalar
├── futures_symbols.json      # Aktif Binance Futures kontratları listesi
├── main.py                   # Piyasa tarayıcı, Telegram komut işleyici ve anti-spam filtresi
├── requirements.txt          # Python bağımlılıkları (requests)
├── state.json                # Eşik değeri ve anti-spam hafıza dosyası
└── README.md                 # Detaylı kılavuz
```
