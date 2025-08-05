# 🚀 Cyclic.sh Detaylı Kurulum Rehberi

## ADIM 1: GITHUB HESABI HAZIRLAMA

### 1.1 GitHub'a Git
- **github.com** adresine git
- Hesabın yoksa **"Sign up"** ile hesap oluştur
- Varsa **"Sign in"** ile giriş yap

### 1.2 Yeni Repository Oluştur
- Sağ üstte **"+"** butonuna tıkla
- **"New repository"** seç
- Repository adı: **got-discord-bot**
- **Public** seç (ücretsiz için)
- **"Create repository"** butonuna bas

---

## ADIM 2: BOT KODLARINI HAZIRLA

### 2.1 Ana Bot Dosyası (main.py)
GitHub repository'nde **"Create new file"** butonuna bas, dosya adı **main.py** yaz ve şu kodu yapıştır:

```python
import os
import discord
from discord.ext import commands
import asyncio
import logging
import sqlite3
from datetime import datetime
from flask import Flask, jsonify
from threading import Thread

# Flask uygulaması (Cyclic.sh için gerekli)
app = Flask(__name__)

@app.route('/')
def home():
    return "🏰 Game of Thrones Discord Bot - Cyclic.sh'de 7/24 çalışıyor!"

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "platform": "cyclic.sh",
        "bot": "Game of Thrones RP Bot",
        "uptime": "24/7"
    })

# Bot setup
class GameOfThronesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='Game of Thrones RP Bot'
        )
        
        self.setup_database()
        
    def setup_database(self):
        """Database kurulumu"""
        try:
            self.db = sqlite3.connect('got_rp.db', check_same_thread=False)
            self.db.execute("PRAGMA foreign_keys = ON")
            
            # Haneler tablosu
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS alliances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    leader_id INTEGER,
                    gold INTEGER DEFAULT 1000,
                    soldiers INTEGER DEFAULT 100,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Üyeler tablosu
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    user_id INTEGER PRIMARY KEY,
                    alliance_id INTEGER,
                    role TEXT DEFAULT 'Üye',
                    level INTEGER DEFAULT 1,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(alliance_id) REFERENCES alliances(id)
                )
            ''')
            
            self.db.commit()
            print("✅ Database hazırlandı")
            
        except Exception as e:
            print(f"❌ Database hatası: {e}")
            
    async def on_ready(self):
        print(f'✅ {self.user} çalışmaya başladı!')
        print(f'📊 Bot {len(self.guilds)} sunucuda aktif')
        
        await self.change_presence(
            activity=discord.Game(name="🏰 GoT RP | Cyclic.sh'de 7/24")
        )

# Bot instance
bot = GameOfThronesBot()

# Komutlar
@bot.command(name='test')
async def test_command(ctx):
    embed = discord.Embed(
        title="🏰 Game of Thrones RP Bot",
        description="Cyclic.sh'de başarıyla çalışıyor!",
        color=discord.Color.blue()
    )
    embed.add_field(name="Platform", value="Cyclic.sh", inline=True)
    embed.add_field(name="Durum", value="✅ Aktif", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! {latency}ms')

@bot.command(name='yardım')
async def help_command(ctx):
    embed = discord.Embed(
        title="🏰 Game of Thrones RP Bot",
        description="Bot komutları:",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Komutlar",
        value="`!test` - Bot durumunu test et\n"
              "`!ping` - Gecikme ölç\n"
              "`!yardım` - Bu mesajı göster",
        inline=False
    )
    await ctx.send(embed=embed)

# Flask ve Bot çalıştırma
def run_flask():
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)

def run_bot():
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ DISCORD_BOT_TOKEN bulunamadı!")
        return
    
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Bot hatası: {e}")

if __name__ == '__main__':
    # Flask arka planda
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("🚀 Game of Thrones RP Bot başlatılıyor...")
    run_bot()
```

### 2.2 Package.json Dosyası
**"Create new file"** → **package.json** → şu içeriği yapıştır:

```json
{
  "name": "got-discord-bot",
  "version": "1.0.0",
  "description": "Game of Thrones Discord RP Bot",
  "main": "main.py",
  "scripts": {
    "start": "python main.py"
  },
  "engines": {
    "python": "3.9"
  }
}
```

### 2.3 Requirements.txt
**"Create new file"** → **requirements.txt** → şu içeriği yapıştır:

```
discord.py==2.3.2
flask==2.3.3
```

---

## ADIM 3: CYCLIC.SH HESABI OLUŞTUR

### 3.1 Cyclic.sh'ye Git
- **cyclic.sh** adresine git
- **"Sign up with GitHub"** butonuna bas
- GitHub hesabınla giriş yapmasına izin ver

### 3.2 Dashboard'u İncele
- Giriş yaptıktan sonra ana dashboard açılır
- **"Deploy"** butonu görünecek

---

## ADIM 4: BOT'U DEPLOY ET

### 4.1 Deployment Başlat
- Dashboard'da **"Deploy"** butonuna bas
- **"Link your own"** seçeneğini seç
- **"Import from GitHub"** butonuna bas

### 4.2 Repository Seç
- GitHub'daki **got-discord-bot** repository'nizi seç
- **"Connect"** butonuna bas
- Otomatik olarak dosyalarınızı tarar

### 4.3 Deployment Ayarları
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`
- **"Deploy"** butonuna bas

---

## ADIM 5: ENVIRONMENT VARIABLES AYARLA

### 5.1 Settings'e Git
- Deployment tamamlandıktan sonra **"Settings"** sekmesine tıkla
- **"Environment Variables"** bölümünü bul

### 5.2 Discord Token Ekle
- **"Add Variable"** butonuna bas
- **Key:** `DISCORD_BOT_TOKEN`
- **Value:** Discord bot token'ınızı yapıştır
- **"Save"** butonuna bas

### 5.3 Port Variable (Otomatik)
Cyclic.sh otomatik olarak PORT variable'ı ekler, siz eklemeyiniz.

---

## ADIM 6: DEPLOYMENT'I KONTROL ET

### 6.1 Logs Kontrol
- **"Logs"** sekmesine git
- Şu mesajları görmelisiniz:
```
🚀 Game of Thrones RP Bot başlatılıyor...
✅ [Bot Name] çalışmaya başladı!
📊 Bot X sunucuda aktif
```

### 6.2 Web Endpoint Test
- **"Overview"** sekmesinde URL'nizi bulun
- Browser'da açın
- "Game of Thrones Discord Bot - Cyclic.sh'de 7/24 çalışıyor!" mesajını görmelisiniz

### 6.3 Discord'da Test
- Discord'da bot'unuza `!test` komutu gönderin
- "Cyclic.sh'de başarıyla çalışıyor!" mesajını almalısınız

---

## ADIM 7: OTOMATİK DEPLOYMENT AYARLA

### 7.1 GitHub Webhook (Otomatik)
Cyclic.sh otomatik olarak GitHub webhook'u kurar. GitHub'da kod değiştirdiğinizde otomatik deploy olur.

### 7.2 Auto-Deploy Test
- GitHub'da main.py dosyasında küçük bir değişiklik yapın
- Commit edin
- Cyclic.sh otomatik olarak yeniden deploy edecek

---

## ADIM 8: MONİTORİNG VE YÖNETİM

### 8.1 Metrics
- **"Metrics"** sekmesinde:
  - CPU kullanımı
  - Memory kullanımı
  - Request sayısı
  - Response times

### 8.2 Custom Domain (İsteğe Bağlı)
- **"Settings"** → **"Domains"**
- Kendi domain'inizi bağlayabilirsiniz

### 8.3 Environment Variables Güncelleme
- Settings'den istediğiniz zaman environment variable'ları güncelleyebilirsiniz
- Değişiklik sonrası otomatik restart olur

---

## SORU GİDERME

### Bot Çalışmıyor?
1. **Logs kontrol edin**
2. **DISCORD_BOT_TOKEN** doğru mu?
3. **requirements.txt** eksik mi?

### Deployment Başarısız?
1. **package.json** doğru mu?
2. **Python version** 3.9 mu?
3. **Start command** `python main.py` mi?

### Web Endpoint Açılmıyor?
1. **Flask port** ayarları doğru mu?
2. **Thread** başlatılıyor mu?
3. **PORT environment variable** var mı?

---

## AVANTAJLAR

### ✅ Tamamen Ücretsiz
- Sınırsız hosting
- Aylık maliyet yok
- Bandwidth limiti yok

### ✅ Kolay Yönetim
- Web dashboard
- Real-time logs
- Metrics monitoring

### ✅ Otomatik Features
- Auto-deployment
- SSL certificate
- Custom domains

### ✅ Güvenilirlik
- 99.9% uptime
- Auto-scaling
- Error recovery

Bot'unuz Cyclic.sh'de 7/24 kesintisiz çalışacak!