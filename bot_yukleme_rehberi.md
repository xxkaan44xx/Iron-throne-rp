# 📁 Bot Dosyalarını Yükleme Rehberi

## 🐍 PythonAnywhere - Detaylı Adımlar

### Adım 1: Hesap Oluştur
1. **pythonanywhere.com** → **"Create a Beginner account"**
2. Username, email, şifre gir
3. Email doğrulama yap

### Adım 2: Files Bölümüne Git
- Dashboard'da **"Files"** sekmesine tıkla
- `/home/kullaniciadin/` klasöründesin

### Adım 3: Bot Dosyası Oluştur
1. **"New file"** butonuna bas
2. Dosya adı: **main.py** 
3. Şu kodu yapıştır:

```python
import os
import discord
from discord.ext import commands
import sqlite3
from datetime import datetime

class GameOfThronesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='Game of Thrones RP Bot - PythonAnywhere'
        )
        
        self.setup_database()
        
    def setup_database(self):
        try:
            self.db = sqlite3.connect('got_rp.db', check_same_thread=False)
            self.db.execute("PRAGMA foreign_keys = ON")
            
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS alliances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    gold INTEGER DEFAULT 1000,
                    soldiers INTEGER DEFAULT 100
                )
            ''')
            
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    user_id INTEGER PRIMARY KEY,
                    alliance_id INTEGER,
                    role TEXT DEFAULT 'Üye',
                    level INTEGER DEFAULT 1,
                    FOREIGN KEY(alliance_id) REFERENCES alliances(id)
                )
            ''')
            
            self.db.commit()
            print("✅ Database hazırlandı")
            
        except Exception as e:
            print(f"❌ Database hatası: {e}")
            
    async def on_ready(self):
        print(f'✅ {self.user} PythonAnywhere\'de çalışıyor!')
        print(f'📊 Bot {len(self.guilds)} sunucuda aktif')
        
        await self.change_presence(
            activity=discord.Game(name="🏰 GoT RP | PythonAnywhere 7/24")
        )

bot = GameOfThronesBot()

@bot.command(name='test')
async def test_command(ctx):
    embed = discord.Embed(
        title="🏰 Game of Thrones RP Bot",
        description="PythonAnywhere'de çalışıyor!",
        color=discord.Color.blue()
    )
    embed.add_field(name="Platform", value="PythonAnywhere", inline=True)
    embed.add_field(name="Durum", value="✅ Aktif", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! {latency}ms')

@bot.command(name='yardım')
async def help_command(ctx):
    embed = discord.Embed(
        title="🏰 Yardım",
        description="Bot komutları:",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Komutlar",
        value="`!test` - Bot testi\n`!ping` - Gecikme\n`!yardım` - Bu mesaj",
        inline=False
    )
    await ctx.send(embed=embed)

if __name__ == '__main__':
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ DISCORD_BOT_TOKEN bulunamadı!")
        print("Environment variables'a token ekleyin.")
    else:
        bot.run(token)
```

### Adım 4: Token Environment Variable Ekle
1. **"Files"** → **.bashrc** dosyasını aç
2. En altına ekle:
```bash
export DISCORD_BOT_TOKEN="YOUR_DISCORD_TOKEN_HERE"
```
3. **"Save"** butonuna bas

### Adım 5: Always-On Task Oluştur
1. **"Tasks"** sekmesine git
2. **"Create scheduled task"** butonu
3. **Command:** `python3.10 /home/kullaniciadin/main.py`
4. **Hour:** `*` (her saat)
5. **Minute:** `*` (her dakika)
6. **"Create"** butonu

Bot sürekli çalışmaya başlar!

---

## ✨ Glitch.com - Detaylı Adımlar

### Adım 1: Proje Oluştur
1. **glitch.com** → **"New Project"**
2. **"hello-express"** template seç (sonra değiştireceğiz)

### Adım 2: Ana Dosyaları Değiştir
**server.js dosyasını sil** ve yerine **main.py** oluştur:

1. Sol panelde **server.js** → sağ tık → **Delete**
2. **"New File"** → **main.py**
3. Şu kodu yapıştır:

```python
import os
import discord
from discord.ext import commands
import sqlite3
from flask import Flask
import threading

# Flask app (Glitch için gerekli)
app = Flask(__name__)

@app.route('/')
def home():
    return "🏰 Game of Thrones Bot - Glitch'de çalışıyor!"

def run_flask():
    app.run(host='0.0.0.0', port=3000)

# Discord Bot
class GameOfThronesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='GoT Bot - Glitch Edition'
        )
        
    async def on_ready(self):
        print(f'✅ {self.user} Glitch\'de çalışıyor!')
        await self.change_presence(
            activity=discord.Game(name="🏰 GoT RP | Glitch 7/24")
        )

bot = GameOfThronesBot()

@bot.command(name='test')
async def test_command(ctx):
    embed = discord.Embed(
        title="🏰 Game of Thrones Bot",
        description="Glitch'de çalışıyor!",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

# Flask ve Bot'u birlikte çalıştır
if __name__ == '__main__':
    # Flask arka planda
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Bot'u çalıştır
    token = os.getenv('DISCORD_BOT_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ Token bulunamadı!")
```

### Adım 3: Package.json Düzenle
**package.json** dosyasını şöyle değiştir:

```json
{
  "name": "got-discord-bot",
  "version": "1.0.0",
  "main": "main.py",
  "scripts": {
    "start": "python main.py"
  },
  "dependencies": {
    "discord.py": "^2.3.2",
    "flask": "^2.3.3"
  },
  "engines": {
    "python": "3.9"
  }
}
```

### Adım 4: Environment Variables (.env)
1. Sol panelde **".env"** dosyası oluştur
2. İçine yaz:
```
DISCORD_BOT_TOKEN=YOUR_DISCORD_TOKEN_HERE
```

### Adım 5: Requirements.txt
**"New File"** → **requirements.txt**:
```
discord.py==2.3.2
flask==2.3.3
```

### Adım 6: Çalıştır
- Glitch otomatik olarak bot'u başlatır
- **"Show"** butonuna basarak web sayfasını görebilirsiniz
- **"Logs"** panelinde bot durumunu kontrol edin

---

## 📋 Hangi Platform Daha Kolay?

### PythonAnywhere ✅
- **Artıları:** Tamamen ücretsiz, sınırsız, Python için optimize
- **Eksileri:** Biraz daha teknik kurulum

### Glitch.com ✅  
- **Artıları:** Web editörü, canlı kod değiştirme, çok kolay
- **Eksileri:** Bazen yavaş olabilir

## Önerim: PythonAnywhere
Daha stabil ve Python botlar için özel olarak tasarlanmış.

Hangi platformda deneyelim?