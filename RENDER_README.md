# Game of Thrones Discord Bot - Render Deployment Guide

## 🚀 Render'de 7/24 Ücretsiz Deployment

Bu bot artık Render'de tamamen ücretsiz çalışmaya hazır!

### Gerekli Dosyalar (Hazır)
✅ `render.yaml` - Render konfigürasyonu
✅ `main.py` - Bot ana dosyası  
✅ `Procfile` - Start komutu
✅ `runtime.txt` - Python versiyonu

### Adım Adım Kurulum:

#### 1. GitHub Repository Oluştur
- GitHub'da yeni repo oluştur: `got-discord-bot`
- Bu projedeki tüm dosyaları GitHub'a yükle

#### 2. Render'da Deployment
1. https://render.com adresine git
2. "New +" butonuna tıkla
3. "Web Service" seç
4. GitHub repository'ni bağla
5. Ayarlar:
   - **Name**: `got-rp-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install discord.py flask requests psutil`
   - **Start Command**: `python main.py`

#### 3. Environment Variables
Render dashboard'da Environment Variables bölümünde:
```
DISCORD_BOT_TOKEN = [Discord Bot Token'ınız]
```

#### 4. Deploy
"Create Web Service" butonuna tıkla!

### Keep-Alive Sistemi
Bot'ta keep-alive sistemi mevcut. Render'de 15 dakika boşta kalırsa uyur, ama:
- UptimeRobot ile her 5 dakikada ping atabilirsiniz
- Render URL'iniz: `https://got-rp-bot.onrender.com`

### Özellikler
🏆 **104+ Discord Komut**
⚔️ **Gelişmiş Savaş Sistemi**  
💰 **Ekonomi & Ticaret**
👑 **Evlilik & Turnuva**
🤖 **Otomatik Moderasyon**
📊 **Performans Optimizasyonu**

Bot Render'de deployed olduktan sonra tamamen ücretsiz 7/24 çalışacak!