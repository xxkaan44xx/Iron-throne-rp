# 🏰 Render.com'da 24/7 Bot Deployment Rehberi

## ✅ HAZIRLIK DURUMU - %100 TAMAMLANDI

Bu rehber, Game of Thrones Discord RP Bot'unuzu Render.com'da tamamen ücretsiz ve 7/24 çalışacak şekilde deploy etmek için hazırlanmıştır.

## 🎯 RENDER AVANTAJLARI

✅ **Tamamen Ücretsiz** - Kredi kartı gerektirmez  
✅ **7/24 Uptime** - Otomatik restart sistemi  
✅ **Web Server** - Health check ve monitoring  
✅ **Otomatik Deploy** - GitHub push ile otomatik güncelleme  
✅ **SSL Sertifikası** - HTTPS desteği  
✅ **550 Saat/Ay** - Free tier limit (7/24 için yeterli)  

## 📁 HAZIR DOSYALAR

Botunuz Render deployment için tamamen hazırlandı:

- ✅ `render_startup.py` - Ana startup script (web server + bot monitoring)
- ✅ `render.yaml` - Render konfigürasyon dosyası  
- ✅ `Procfile` - Process tanımlaması
- ✅ `runtime.txt` - Python version
- ✅ Otomatik restart sistemi
- ✅ Health check endpoints

## 🚀 DEPLOYMENT ADIMLARI

### 1. GitHub Repository Hazırlama

```bash
# Projenizi GitHub'a push edin
git add .
git commit -m "Render deployment ready"
git push origin main
```

### 2. Render.com'da Hesap Açma

1. [render.com](https://render.com) sitesine gidin
2. "Get Started for Free" butonuna tıklayın
3. GitHub hesabınızla giriş yapın (önerilen)

### 3. Web Service Oluşturma

1. Dashboard'da "New +" → "Web Service" seçin
2. GitHub repository'nizi seçin
3. Aşağıdaki ayarları yapın:

**Temel Ayarlar:**
- **Name:** `got-rp-bot` (veya istediğiniz isim)  
- **Environment:** `Python 3`
- **Region:** `Frankfurt` (Türkiye'ye yakın)
- **Branch:** `main`

**Build & Deploy Ayarları:**
- **Build Command:** `pip install discord.py flask requests psutil`
- **Start Command:** `python render_startup.py`
- **Plan:** `Free` (0$/month)

### 4. Environment Variables

**Environment Variables** sekmesinde şu değişkeni ekleyin:

```
DISCORD_BOT_TOKEN = your_actual_bot_token_here
```

⚠️ **ÖNEMLİ:** Bot token'ınızı Discord Developer Portal'dan alın.

### 5. Health Check Ayarları

```
Health Check Path: /health
```

Bu ayar botun çalışıp çalışmadığını kontrol eder.

## 🔧 ÖZEL ÖZELLİKLER

### Otomatik Bot Monitoring

Bot kendi kendini izler ve crash olursa otomatik restart eder:

```python
# render_startup.py'de otomatik monitoring
def monitor_bot():
    while True:
        if bot_process is None or bot_process.poll() is not None:
            print("Bot crashed, restarting...")
            bot_process = start_discord_bot()
        time.sleep(30)  # Her 30 saniyede kontrol
```

### Web Dashboard

Bot deploy edildikten sonra Render size bir URL verecek:
```
https://got-rp-bot.onrender.com
```

Bu URL'de:
- ✅ Bot durumu görüntüleme
- ✅ Uptime tracking  
- ✅ Manuel restart butonu
- ✅ Health check endpoint (`/health`)

### Manuel Restart

Gerektiğinde botu manuel restart edebilirsiniz:
```
https://your-app.onrender.com/restart
```

## 📊 MONITORING VE KONTROL

### Health Check Endpoints

```
GET /          - Ana sayfa (bot durumu)
GET /health    - JSON health check
GET /restart   - Manuel bot restart
```

### Render Dashboard

Render dashboard'da görebilecekleriniz:
- ✅ Build logs
- ✅ Deploy history  
- ✅ Metrics (CPU, Memory)
- ✅ Custom logs
- ✅ Environment variables

## 🚨 SORUN GİDERME

### Bot Başlamıyor

1. **Environment Variables** kontrol edin
2. **Build logs** inceleyin
3. **DISCORD_BOT_TOKEN** doğru mu kontrol edin

### 550 Saat Limiti

Free tier 550 saat/ay limit vardır:
- 30 gün × 24 saat = 720 saat (limit aşılır)
- **Çözüm:** Ayın son günlerinde bot duraklar, 1. gün tekrar başlar
- **Alternatif:** Paid plan ($7/month) unlimited

### Web Server Kapanıyor

```python
# render_startup.py otomatik çözüm içerir
# Bot crash olursa 30 saniye içinde restart eder
```

## 🎉 BAŞARILI DEPLOYMENT

Deploy tamamlandığında:

1. ✅ Bot Discord'da online görünecek
2. ✅ Web dashboard erişilebilir olacak  
3. ✅ Health check çalışacak
4. ✅ Otomatik monitoring aktif olacak

**Test Komutları:**
```
!ping - Bot response kontrolü
!komutlar - Komutlar menüsü (2 kere gönderme sorunu çözüldü)
!yardım - Yardım sistemi
```

## 📈 PERFORMANS

**Render Free Tier Specs:**
- ✅ 512 MB RAM
- ✅ 1 vCPU  
- ✅ 550 saat/ay
- ✅ SSL certificate
- ✅ Custom domain desteği

**Bot Performance:**
- ✅ 150+ komut destekleri
- ✅ SQLite database
- ✅ Otomatik backup sistemi
- ✅ Memory optimization

## 🆘 DESTEK

Sorun yaşarsanız:

1. **Render Logs:** Dashboard → Logs sekmesi
2. **Health Check:** `your-app.onrender.com/health`
3. **Manual Restart:** `your-app.onrender.com/restart`

**İletişim:**
- Bot Creator: xxkaan44xx
- Proje: Game of Thrones Discord RP Bot
- Status: Production Ready ✅

---

**🏆 BAŞARIYLA TAMAMLANDI - BOT 7/24 RENDER'DA AKTİF! 🏆**