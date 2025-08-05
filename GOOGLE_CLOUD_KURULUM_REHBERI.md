# 🤖 APTAL BİRİNE ANLATIR GİBİ GOOGLE CLOUD KURULUM REHBERİ

## Başlamadan Önce Hazırlık
1. **Gmail hesabın olması lazım** (yoksa yap)
2. **Kredi kartı** (para kesmiyor ama istiyor, $300 bedava veriyor)
3. **Telefon numarası** (doğrulama için)

---

## ADIM 1: GOOGLE CLOUD HESABI OLUŞTUR

### 1.1 Web Sitesine Git
- Telefonunda browser aç (Chrome, Safari, vs.)
- **console.cloud.google.com** yaz ve git
- Veya **"Google Cloud Console"** diye Google'da ara

### 1.2 Hesap Oluştur
- **"Ücretsiz başlayın"** butonuna bas
- Gmail hesabınla giriş yap
- **Ülke: Türkiye** seç
- **Şirket: Hayır, kişisel kullanım** seç
- **Kullanım koşullarını** kabul et

### 1.3 Kredi Kartı Bilgilerini Gir
- **ÖNEMLİ: PARA KESMİYOR!** Sadece doğrulama için
- Kredi kartı numaranı gir
- CVV ve son kullanma tarihini gir
- **$300 ücretsiz kredi** alacaksın

---

## ADIM 2: SANAL MAKİNE (VM) OLUŞTUR

### 2.1 Compute Engine'e Git
- Sol tarafta menü var, **"Compute Engine"** bul
- **"VM instances"** (Sanal Makineler) kısmına tıkla
- **"Create Instance"** (Makine Oluştur) butonuna bas

### 2.2 Makine Ayarları (ÇOK ÖNEMLİ!)
```
Name (İsim): discord-bot-server
Region: us-central1 (a, b, c herhangi biri)
Zone: us-central1-a
Machine type: e2-micro (ÜCRETSİZ OLAN BU!)
Boot disk: Ubuntu 20.04 LTS
```

### 2.3 Güvenlik Duvarı Ayarları
- **"Allow HTTP traffic"** kutusunu işaretle ✅
- **"Allow HTTPS traffic"** kutusunu işaretle ✅
- **"CREATE"** butonuna bas

### 2.4 Makine Başlatma Bekle
- 1-2 dakika bekle, makine hazırlanıyor
- Yeşil tik çıkınca hazır

---

## ADIM 3: MAKİNEYE BAĞLAN (SSH)

### 3.1 SSH Butonuna Bas
- Makinen listede görünecek
- Sağ tarafta **"SSH"** butonu var
- Ona bas, yeni pencere açılacak

### 3.2 Terminal Açıldı
- Siyah ekran geldi, komut yazabilirsin
- Bu Linux terminali, bot burada çalışacak

---

## ADIM 4: BOT KURULUMU

### 4.1 Sistem Güncelleme
Terminal'de şunu yaz (enter'a bas):
```bash
sudo apt update
```
Bekle, biter.

### 4.2 Python Kurulumu
```bash
sudo apt install python3 python3-pip git nano -y
```
Bu komut Python, pip ve gerekli araçları kurar.

### 4.3 Discord Kütüphanesi Kurulumu
```bash
pip3 install discord.py flask
```
Bu Discord bot için gerekli kütüphaneleri kurar.

---

## ADIM 5: BOT DOSYALARINI AKTAR

### 5.1 Bot Klasörü Oluştur
```bash
mkdir discord-bot
cd discord-bot
```

### 5.2 Ana Bot Dosyasını Oluştur
```bash
nano main.py
```
Terminal'de dosya editörü açıldı. Şimdi bot kodunu yapıştır:

**BOT KODUNU TAMAMEN KOPYALA VE YAPIŞTIR:**
```python
import os
import discord
from discord.ext import commands, tasks
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, jsonify
from threading import Thread
import time

# Flask web server for uptime
app = Flask('')

@app.route('/')
def home():
    return "🏰 Game of Thrones Discord Bot is alive and running 24/7!"

@app.route('/health')
def health():
    return jsonify({"health": "ok", "bot": "active"})

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# Bot logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Discord bot setup
class GameOfThronesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='Game of Thrones Roleplay Bot'
        )
        
        # Database setup
        self.setup_database()
        
    def setup_database(self):
        """Initialize SQLite database"""
        self.db = sqlite3.connect('got_rp.db', check_same_thread=False)
        self.db.execute("PRAGMA foreign_keys = ON")
        
        # Create basic tables
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS alliances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                leader_id INTEGER,
                gold INTEGER DEFAULT 1000,
                soldiers INTEGER DEFAULT 100,
                power_points INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS members (
                user_id INTEGER PRIMARY KEY,
                alliance_id INTEGER,
                role TEXT DEFAULT 'Üye',
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(alliance_id) REFERENCES alliances(id)
            )
        ''')
        
        self.db.commit()
        logger.info("Database initialized successfully")
        
    async def setup_hook(self):
        """Setup background tasks"""
        logger.info("Bot is ready for 24/7 operation!")
        keep_alive()  # Start Flask server
        
    async def on_ready(self):
        """Bot ready event"""
        logger.info(f'{self.user} has logged in!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="🏰 Game of Thrones RP | !yardım")
        )
        
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Eksik parametre: {error.param.name}")
        else:
            logger.error(f"Unhandled error in {ctx.command}: {error}")
            await ctx.send("❌ Bir hata oluştu! Lütfen daha sonra tekrar deneyin.")

# Bot commands
@bot.command(name='test')
async def test_command(ctx):
    """Test command"""
    embed = discord.Embed(
        title="🏰 Game of Thrones RP Bot",
        description="Bot başarıyla çalışıyor! 7/24 aktif durumda.",
        color=discord.Color.blue()
    )
    embed.add_field(name="Durum", value="✅ Aktif", inline=True)
    embed.add_field(name="Sunucu", value="Google Cloud VM", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='yardım', aliases=['help'])
async def help_command(ctx):
    """Help command"""
    embed = discord.Embed(
        title="🏰 Game of Thrones RP Bot - Yardım",
        description="Bot komutları:",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Temel Komutlar",
        value="`!test` - Bot durumunu test et\n"
              "`!yardım` - Bu yardım mesajını göster",
        inline=False
    )
    await ctx.send(embed=embed)

# Run the bot
async def main():
    """Main function to run the bot"""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not bot_token:
        print("❌ DISCORD_BOT_TOKEN bulunamadı!")
        print("Token'ı şu komutla ekle:")
        print("export DISCORD_BOT_TOKEN='your_token_here'")
        return
    
    bot = GameOfThronesBot()
    
    try:
        await bot.start(bot_token)
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### 5.3 Dosyayı Kaydet
- **Ctrl + X** (çıkış)
- **Y** (kaydet)
- **Enter** (onayla)

---

## ADIM 6: DISCORD TOKEN AYARLA

### 6.1 Environment Variable Ayarla
```bash
nano ~/.bashrc
```

### 6.2 Dosyanın En Altına Ekle
Aşağıdaki satırı dosyanın en altına ekle:
```bash
export DISCORD_BOT_TOKEN="SENIN_DISCORD_TOKEN_IN_BURAYA"
```

**ÖNEMLİ:** `SENIN_DISCORD_TOKEN_IN_BURAYA` yazan yere gerçek Discord bot token'ını yaz!

### 6.3 Kaydet ve Çık
- **Ctrl + X**, **Y**, **Enter**

### 6.4 Ayarları Yükle
```bash
source ~/.bashrc
```

---

## ADIM 7: BOT'U ÇALIŞTIR

### 7.1 Screen Oturumu Aç
```bash
screen -S discord-bot
```
Bu komut arka planda çalışacak oturum açar.

### 7.2 Bot'u Başlat
```bash
python3 main.py
```

Bot çalışmaya başladı! Şu mesajları göreceksin:
```
Bot is ready for 24/7 operation!
[Bot Name] has logged in!
Bot is in X guilds
```

### 7.3 Screen'den Çık (Bot Çalışmaya Devam Eder)
- **Ctrl + A** basılı tut
- **D** bas
- Bot arka planda çalışmaya devam eder

---

## ADIM 8: BOT KONTROLÜ

### 8.1 Bot Durumunu Kontrol Et
```bash
screen -r discord-bot
```
Bu komutla bot ekranına geri dönebilirsin.

### 8.2 Web Kontrolü
Browser'da şu adresi aç:
```
http://[VM_EXTERNAL_IP]:8080
```
"Game of Thrones Discord Bot is alive" mesajını göreceksin.

### 8.3 Discord'da Test Et
Discord'da bot'una `!test` komutu gönder.

---

## ADIM 9: KALICI ÇALIŞMA GARANTİSİ

### 9.1 Otomatik Yeniden Başlatma
```bash
nano start_bot.sh
```

Şu içeriği ekle:
```bash
#!/bin/bash
cd /home/[KULLANICI_ADIN]/discord-bot
export DISCORD_BOT_TOKEN="SENIN_TOKEN_IN"
python3 main.py
```

### 9.2 Çalıştırılabilir Yap
```bash
chmod +x start_bot.sh
```

### 9.3 Crontab Ekle (Her 5 Dakikada Kontrol)
```bash
crontab -e
```

En alta ekle:
```
*/5 * * * * screen -S discord-bot -X quit; screen -dmS discord-bot /home/[KULLANICI_ADIN]/discord-bot/start_bot.sh
```

---

## MOBİL KONTROL

### Google Cloud Console App
1. **Play Store/App Store**: "Google Cloud Console" indir
2. Hesabınla giriş yap
3. VM'ini görebilir, başlatabilirsin

### SSH Mobil Apps
1. **Termius** (iOS/Android)
2. **JuiceSSH** (Android)
3. VM'e bağlanıp komut çalıştırabilirsin

---

## SORUN GİDERME

### Bot Çalışmıyor?
```bash
screen -r discord-bot
# Hata mesajlarını oku
```

### VM Restart Oldu?
```bash
cd discord-bot
screen -S discord-bot
python3 main.py
# Ctrl+A+D ile çık
```

### Token Hatası?
```bash
echo $DISCORD_BOT_TOKEN
# Token'ı kontrol et
```

---

## MALIYET DETAYI

- **e2-micro VM**: Sürekli ücretsiz
- **Network trafiği**: 1GB/ay ücretsiz (bot için yeterli)
- **Storage**: 30GB ücretsiz (fazlasıyla yeterli)
- **$300 kredi**: 90 gün süreyle geçerli

**SONUÇ: TAMAMEN ÜCRETSİZ 7/24 BOT!**

---

Bu adımları takip edersen bot'un Google Cloud'da sürekli çalışacak. Herhangi bir adımda takılırsan bana sor!