# 🌐 Web Üzerinden Ücretsiz 7/24 Bot Hosting

## 1. Render.com (Önerilen)
- **750 saat/ay ücretsiz**
- Web arayüzünden kolay kurulum
- GitHub ile otomatik deploy
- dashboard.render.com

### Kurulum:
1. render.com'a git
2. GitHub hesabı ile giriş yap
3. "New Web Service" oluştur
4. Bot repository'sini bağla
5. Otomatik deploy olur

## 2. Railway.app
- **500 saat/ay ücretsiz**
- Modern web dashboard
- railway.app

### Kurulum:
1. railway.app'e git  
2. GitHub ile giriş
3. "Deploy from GitHub repo" seç
4. Bot'u seç ve deploy et

## 3. Fly.io
- **Shared CPU ücretsiz**
- Web terminali var
- fly.io

## 4. Cyclic.sh
- **Tamamen ücretsiz**
- Serverless hosting
- cyclic.sh

## 5. Glitch.com
- **Web editörü**
- Ücretsiz hosting
- glitch.com

---

# 🔧 UptimeRobot Düzeltme

## Sorunu Tespit Et

Şu anda bot'unuz çalışıyor ve web sunucusu aktif:
- Port 5000: Web Server workflow
- Port 8080: Discord Bot workflow içinde Flask

## UptimeRobot Doğru Ayarları

### 1. URL Kontrolü
Replit proje URL'niz:
```
https://[proje-adınız].[kullanıcı-adınız].replit.app
```

### 2. UptimeRobot Monitor Ayarları
```
Monitor Type: HTTP(s)
URL: https://[proje-adınız].[kullanıcı-adınız].replit.app
Port: 443 (HTTPS için)
Monitoring Interval: 5 dakika
Keyword: "Game of Thrones" (opsiyonel)
```

### 3. Test Et
Browser'da URL'nizi açın:
- Çalışıyorsa: "🏰 Game of Thrones Discord Bot is alive and running 24/7!"
- Çalışmıyorsa: UptimeRobot çalışmaz

## UptimeRobot Alternatif Endpoints

### Health Check Endpoint
```
https://[proje-adınız].[kullanıcı-adınız].replit.app/health
```

### Status Endpoint  
```
https://[proje-adınız].[kullanıcı-adınız].replit.app/status
```

---

# 🚀 En Kolay Çözüm: Render.com

1. **render.com'a git**
2. **GitHub hesabı ile giriş yap**
3. **Bot kodlarını GitHub'a yükle**
4. **"New Web Service" oluştur**
5. **Repository'yi seç**
6. **Otomatik deploy olur**

750 saat/ay = günde 25 saat (7/24 için yeterli)

Hangi yöntemi denemek istiyorsunuz?