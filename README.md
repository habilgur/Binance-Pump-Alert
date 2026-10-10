# 🚀 Binance Spike / Pump Alert Bot

Bu proje, **Binance** piyasasındaki tüm vadeli ve spot USDT işlem çiftlerini 10 dakikada bir tarar, en çok yükselenleri (Z-A) sıralar ve belirlediğiniz eşiği aşan koinleri **Telegram Botu** aracılığıyla telefonunuza anlık bildirim olarak gönderir.

GitHub Actions ile sunucu (VPS) masrafı olmadan tamamen **ücretsiz ve kesintisiz** çalışır.

---

## ✨ Öne Çıkan Özellikler

1. **📱 Telegram Üzerinden Canlı Kontrol:**
   * Eşik değiştirmek için koda veya ayarlara girmenize gerek yok!
   * Telegram'dan bota `/esik 80` veya doğrudan `80` yazmanız yeterlidir. Bot sonraki taramada eşiği otomatik günceller ve size teyit mesajı atar.
   * `/durum` yazarak aktif eşiği ve takipteki koinleri görebilirsiniz.

2. **🛡️ Akıllı Anti-Spam Koruması:**
   * Bir koin eşiği aştığında bildirilir ve hafızaya (`state.json`) alınır.
   * Aynı koin için **4 saat boyunca tekrar bildirim atılmaz**.
   * Ancak koin son bildirimden sonra **+%15 daha fırlarsa** (örn: %50'den %68'e çıkarsa), bot *"🔥 Zirve Tazeledi"* diyerek tek bir güncel bildirim daha gönderir.

3. **📊 Binance Uygulaması ile Birebir Sıralama:**
   * Binance mobil uygulamasındaki **Piyasalar -> 24s Değişim (Z-A / En Çok Yükselenler)** listesini baz alır.
   * Mesajlarda koinin Binance sayfasına doğrudan grafik/al-sat linki bulunur.

4. **⚡ Kesintisiz Çalışma (Bölgesel Kısıt / Fallback Koruması):**
   * GitHub Actions bulut sunucularındaki olası bölgesel kısıtlamalara karşı hem Binance Futures hem de Binance Global Data kaynaklarını akıllı şekilde yönetir.

---

## 🤖 Kullanabileceğiniz Telegram Komutları

| Komut | Açıklama | Örnek |
| :--- | :--- | :--- |
| `/esik <yüzde>` | Bildirim alarm eşiğini anında günceller | `/esik 70` veya `/esik 100` |
| `<sayı>` | Komut yazmadan sadece sayı da gönderebilirsiniz | `80` veya `%65` |
| `/durum` | Aktif eşik ve takipteki koin sayısını gösterir | `/durum` |
| `/yardim` | Komut listesini gösterir | `/yardim` |

---

## 📁 Proje Dosya Yapısı

```
Binance Pump Alert/
├── .github/
│   └── workflows/
│       └── checker.yml       # Her 10 dakikada bir çalışan iş akışı ve state senkronizasyonu
├── .env.example              # Lokal test ortam değişkenleri örneği
├── .gitignore                # Git dışı tutulacak dosyalar
├── main.py                   # Piyasa tarayıcı, Telegram komut işleyici ve anti-spam filtresi
├── requirements.txt          # Python bağımlılıkları (requests)
├── state.json                # Eşik değeri ve anti-spam hafıza dosyası
└── README.md                 # Detaylı kılavuz
```
