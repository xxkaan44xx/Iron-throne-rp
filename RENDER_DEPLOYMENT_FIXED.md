# 🏰 Game of Thrones Discord Bot - Render Deployment Guide (Fixed)

Bu rehber, Game of Thrones Discord bot'unu Render.com'da başarıyla deploy etmek için güncellenmiş ve düzeltilmiş adımları içerir.

## ✅ Düzeltilen Sorunlar

1. **IndentationError düzeltildi** - commands.py dosyasındaki girinti hatası çözüldü
2. **Eksik komutlar eklendi** - `savaş_büyüklük` komutu geri yüklendi
3. **Render konfigürasyonu optimize edildi** - Daha güvenilir deployment
4. **Dependency'ler güncellendi** - Tüm gerekli kütüphaneler eklendi

## 📋 Gerekli Dosyalar

### 1. render.yaml (✅ GÜNCEL)
```yaml
services:
  - type: web
    name: got-rp-bot
    env: python
    buildCommand: pip install --upgrade pip && pip install -r render_requirements.txt
    startCommand: python render_optimized.py
    plan: free
    healthCheckPath: /health
    region: frankfurt
    autoDeploy: true
    envVars:
      - key: PORT
        value: 5000
      - key: DISCORD_BOT_TOKEN
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
```

### 2. render_requirements.txt (✅ GÜNCEL)
```
discord.py==2.3.2
flask==2.3.3
requests==2.31.0
psutil==5.9.5
aiohttp==3.8.5
```

### 3. runtime.txt (✅ MEVCUT)
```
python-3.11.0
```

## 🚀 Deployment Adımları

### Adım 1: Repository Hazırlığı
- Tüm dosyaların GitHub repo'nuzda olduğundan emin olun
- `render_optimized.py` dosyasının root'ta olduğunu kontrol edin

### Adım 2: Render.com'da Service Oluşturma
1. [render.com](https://render.com) hesabınıza giriş yapın
2. "New +" → "Web Service"
3. GitHub repo'nuzu bağlayın
4. Branch: `main` seçin
5. Root Directory: boş bırakın

### Adım 3: Service Ayarları
```
Name: got-rp-bot (veya istediğiniz isim)
Environment: Python
Region: Frankfurt (düşük gecikme için)
Branch: main
Build Command: pip install --upgrade pip && pip install -r render_requirements.txt
Start Command: python render_optimized.py
Plan: Free
```

### Adım 4: Environment Variables (ÖNEMLİ!)
Environment Variables kısmına şu değişkenleri ekleyin:
```
DISCORD_BOT_TOKEN = [Discord bot token'ınız]
PORT = 5000
PYTHON_VERSION = 3.11.0
```

### Adım 5: Deploy
- "Create Web Service" butonuna tıklayın
- Build loglarını takip edin

## 🔧 Monitoring ve Health Check

### Health Check Endpoint
- URL: `https://your-app-name.onrender.com/health`
- Bu endpoint bot durumunu JSON formatında döner

### Bot Monitoring
- Ana sayfa: `https://your-app-name.onrender.com/`
- Bu sayfada bot durumu, uptime ve restart sayısını görebilirsiniz

### Restart Endpoint (Debug için)
- URL: `https://your-app-name.onrender.com/restart`
- Bu endpoint bot'u manuel olarak restart eder

## ⚠️ Önemli Notlar

### Free Tier Limitler
- 750 saat/ay (yaklaşık 24/7 çalışır)
- 15 dakika inaktiflik sonrası sleep
- Cold start gecikmesi olabilir

### Bot Token Güvenliği
- Discord bot token'ınızı asla kod içinde yazmayın
- Sadece Render environment variables'da saklayın

### Database
- SQLite dosyası her deployment'ta sıfırlanır
- Kalıcı data için PostgreSQL kullanmanız önerilir

## 🐛 Sorun Giderme

### Deployment Failed
1. Build loglarını kontrol edin
2. `render_requirements.txt` dosyasının doğru olduğundan emin olun
3. Python version'ın 3.11.0 olduğunu kontrol edin

### Bot Çalışmıyor
1. Environment variables'ı kontrol edin
2. Discord token'ın doğru olduğundan emin olun
3. Health check endpoint'ini ziyaret edin

### Memory/CPU Sorunları
- Free tier limited resources
- Bot restart sayısını /health endpoint'inden kontrol edin

## 📞 Destek

Sorun yaşarsanız:
1. Render deployment loglarını kontrol edin
2. Health check endpoint'ini ziyaret edin
3. GitHub Issues'da sorunuzu paylaşın

---

**Başarılı deployment sonrası bot'unuz 24/7 çalışacak ve Discord sunucularınızda aktif olacaktır!** 🏆