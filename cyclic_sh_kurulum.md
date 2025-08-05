# 🚀 Cyclic.sh ile Ücretsiz 7/24 Bot Hosting

## Neden Cyclic.sh?
- **Tamamen ücretsiz** (sınır yok)
- **Serverless** (otomatik scale)
- **Web dashboard** (kolay yönetim)
- **GitHub entegrasyonu**
- **Environment variables** desteği

## Adım Adım Kurulum

### 1. GitHub'a Bot Kodlarını Yükle
Bot kodlarınızı GitHub repository'sine yüklememiz gerekiyor.

### 2. Cyclic.sh Hesabı Oluştur
- **cyclic.sh** adresine git
- **"Sign up with GitHub"** butonuna bas
- GitHub hesabınla giriş yap

### 3. Yeni Uygulama Oluştur
- Dashboard'da **"Deploy"** butonuna bas
- **"Link your own"** seç
- GitHub repository'nizi seç

### 4. Environment Variables Ayarla
- **Settings > Environment Variables**
- **DISCORD_BOT_TOKEN** ekle
- Token değerini gir

### 5. Deploy Et
- **"Deploy"** butonuna bas
- Otomatik deployment başlar

## Cyclic.sh için Bot Kodu Düzenlemesi

Bot kodunuzda küçük bir değişiklik gerekli:

```python
# main.py - Cyclic.sh için optimize edilmiş versiyon
import os
import discord
from discord.ext import commands, tasks
import asyncio
import logging
from flask import Flask, jsonify
from threading import Thread

# Flask uygulaması (Cyclic.sh requirement)
app = Flask(__name__)

@app.route('/')
def home():
    return "🏰 Game of Thrones Discord Bot - Cyclic.sh'de çalışıyor!"

@app.route('/health')  
def health():
    return jsonify({"status": "healthy", "platform": "cyclic.sh"})

# Discord Bot
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
        
    async def on_ready(self):
        print(f'{self.user} çalışmaya başladı!')
        print(f'Bot {len(self.guilds)} sunucuda aktif')
        
        await self.change_presence(
            activity=discord.Game(name="🏰 GoT RP | Cyclic.sh'de 7/24")
        )

# Temel komutlar
@bot.command(name='test')
async def test_command(ctx):
    embed = discord.Embed(
        title="🏰 Game of Thrones Bot",
        description="Cyclic.sh'de başarıyla çalışıyor!",
        color=discord.Color.blue()
    )
    embed.add_field(name="Platform", value="Cyclic.sh", inline=True)
    embed.add_field(name="Durum", value="✅ Aktif", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

# Flask ve Bot'u birlikte çalıştır
def run_flask():
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

def run_bot():
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("DISCORD_BOT_TOKEN bulunamadı!")
        return
    bot.run(token)

if __name__ == '__main__':
    # Flask'ı arka planda başlat
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Bot'u çalıştır
    run_bot()
```

## package.json Dosyası (Gerekli)
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

## requirements.txt (Python Dependencies)
```
discord.py==2.3.2
flask==2.3.3
aiohttp==3.9.1
```

## Avantajları
- **Ücretsiz sınırsız** hosting
- **Otomatik deployment** (GitHub push = yeniden deploy)
- **Environment variables** güvenli
- **Custom domain** desteği
- **Logs** görüntüleme
- **SSL sertifikası** otomatik

Kodları hazırlayıp GitHub'a yükleyip Cyclic.sh'ye deploy etmek istiyor musunuz?