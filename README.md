# BIST Sinyal Tarayıcı — MACD Strateji v2

MACD Histogram Dönüşü stratejisi ile BIST hisselerini tarayan, backtest eden ve Telegram bildirimi gönderen sistem.

---

## Strateji

| Kural | Detay |
|-------|-------|
| **Endeks Filtresi** | BIST100 kapanış > EMA200 olduğunda strateji aktif |
| **Trend** | EMA20 > EMA50 > EMA100 > EMA200 hizalaması |
| **Fiyat** | Kapanış fiyatı EMA20 üzerinde olmalı |
| **Hacim** | Günlük hacim > 20 günlük ortalama hacim × 1.5 |
| **Giriş** | MACD histogramı negatiften pozitife döndüğünde |
| **Stop** | Giriş − (ATR × 1.5) |
| **Hedef** | Giriş + (Stop mesafesi × R:R) |
| **Risk** | Portföyün %1'i her işlem için |

> Fiyat > EMA20 ve hacim filtresi v2 ile eklendi. Amaç sahte MACD geçişlerini ve düşük hacimli sinyalleri elemek.

---

## Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `bist_streamlit.py` | Web arayüzü — günlük tarayıcı (filtre istatistikleri, TradingView linkleri, grafik) |
| `bist_tarayici.py` | Komut satırı tarayıcı |
| `bist_telegram_bot.py` | Telegram otomatik bildirim botu |
| `bist_backtest_ui.py` | Streamlit backtest arayüzü (pozisyon yönetimli, portföy eğrisi) |
| `bist_kombinasyon_backtest.py` | ATR × R:R kombinasyon karşılaştırma backtesti (35 kombinasyon) |
| `requirements.txt` | Bağımlılıklar |

---

## Kurulum

```bash
pip install -r requirements.txt
```

`requirements.txt` içeriği:

```
streamlit>=1.30.0
yfinance>=0.2.40
pandas>=2.0.0
plotly>=5.0.0
python-telegram-bot>=20.0
```

---

## Kullanım

### Web Tarayıcı

```bash
streamlit run bist_streamlit.py
```

Açılan arayüzde:
- Sol menüden ATR, R:R, hacim çarpanı ve MACD parametrelerini ayarla
- **Tara** butonuna bas
- Filtre istatistiklerinden kaç hissenin hangi filtrede elendiğini gör
- Sinyalli hisselerin grafik ve işlem detaylarını incele

### Komut Satırı

```bash
python bist_tarayici.py
```

Tarama tamamlandığında sinyaller hem ekrana yazdırılır hem de `bist_sinyaller_YYYYMMDD_HHMM.csv` olarak kaydedilir.

### Backtest

```bash
streamlit run bist_backtest_ui.py
```

### Kombinasyon Backtest (ATR × R:R)

```bash
streamlit run bist_kombinasyon_backtest.py
```

5 ATR (1.0 – 3.0) × 7 R:R (1.0 – 4.0) = **35 kombinasyon** aynı anda test edilir. Sonuçlar karşılaştırmalı tablo ve ısıl harita olarak gösterilir, CSV olarak indirilebilir.

---

## GitHub Actions — Otomatik Telegram Bildirimi

`.github/workflows/bist_bot.yml` dosyası her hafta içi **17:00 UTC (20:00 TR)** çalışır ve sinyal varsa Telegram'a bildirim gönderir.

### Gerekli Secret'lar

Repo → **Settings → Secrets and variables → Actions** bölümüne ekle:

| Secret | Açıklama |
|--------|----------|
| `TELEGRAM_TOKEN` | BotFather'dan alınan bot token |
| `TELEGRAM_CHAT_ID` | Bildirimin gönderileceği chat ID |

---

## Notlar

- Tüm veriler [Yahoo Finance](https://finance.yahoo.com) üzerinden `yfinance` kütüphanesi ile çekilir
- Backtest geçmiş performansı gösterir, gelecek getiriyi garanti etmez
- Bu sistem yatırım tavsiyesi değildir
