# ☁️ Google Cloud Ücretsiz Bot Hosting Rehberi

## Google Cloud Always Free Tier

### Ücretsiz Sınırlar:
- **$300 kredi** (ilk 90 gün)
- **Always Free** VM (sürekli ücretsiz)
- e2-micro instance (1 vCPU, 1GB RAM)
- **Süre sınırı yok**

## Adım Adım Kurulum

### 1. Hesap Oluşturma
- console.cloud.google.com'a git
- Gmail hesabı ile giriş yap
- Kredi kartı bilgisi iste (ama ücret kesmiyor)
- $300 kredi alıyorsun

### 2. VM Instance Oluşturma
```
Compute Engine > VM instances > Create Instance

Ayarlar:
- Name: discord-bot
- Region: us-central1 (Always Free)
- Machine type: e2-micro (Always Free)
- Boot disk: Ubuntu 20.04 LTS
- Firewall: HTTP ve HTTPS'i aç
```

### 3. SSH Bağlantısı
- VM'e SSH ile bağlan
- Terminal açılır

### 4. Bot Kurulumu
```bash
# Python ve pip kurulumu
sudo apt update
sudo apt install python3 python3-pip git -y

# Discord.py kurulumu
pip3 install discord.py flask

# Bot dosyalarını indir
git clone [bot-repo-url]
cd discord-bot

# Bot'u çalıştır
python3 main.py
```

### 5. Sürekli Çalıştırma
```bash
# Screen kullan (bot arka planda çalsın)
sudo apt install screen
screen -S discord-bot
python3 main.py

# Ctrl+A+D ile çık (bot çalışmaya devam eder)
```

## Mobil Kontrol

### Google Cloud Console App
- Play Store/App Store: "Google Cloud Console"
- VM durumunu kontrol et
- SSH bağlantısı
- Start/stop işlemleri

### SSH Apps
- **Termius** (mobil SSH client)
- **JuiceSSH** (Android)
- VM'e mobil bağlantı

## Avantajları
- **Gerçekten ücretsiz** (Always Free tier)
- **Sınırsız çalışma**
- **Google güvenilirliği**
- **Mobil kontrol**

## Dikkat Edilecekler
- e2-micro seç (Always Free)
- us-central1 region seç
- Network trafiği sınırı var ama bot için yeterli

Always Free tier sürekli devam ediyor - $300 kredi bitince de VM ücretsiz çalışmaya devam eder!