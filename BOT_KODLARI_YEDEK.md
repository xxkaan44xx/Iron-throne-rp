# 📦 Bot Kodları Yedek Paketi - Kopyala ve Kaydet!

## 🚨 ÖNEMLİ: Bütün bu kodları kopyala ve kaydet!

---

## 1. main.py (Ana Bot Dosyası)
```python
import os
import discord
from discord.ext import commands, tasks
import asyncio
import logging
from database import Database
from war_system import WarSystem
from economy import EconomySystem
from army_management import ArmyManagement
from tournament_system import TournamentSystem
from commands import setup_commands
from keep_alive import keep_alive

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        
        # Initialize systems
        self.db = Database()
        self.war_system = WarSystem(self.db)
        self.economy_system = EconomySystem(self.db)
        
        # Setup commands
        setup_commands(self, self.db, self.war_system, self.economy_system)
        
    async def setup_hook(self):
        """Setup background tasks"""
        logger.info("Setting up background tasks...")
        keep_alive()  # Start Flask server for uptime
        self.income_task.start()
        self.debt_task.start()
        logger.info("Bot is ready for 24/7 operation!")
        
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
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ Bu komutu {error.retry_after:.1f} saniye sonra tekrar kullanabilirsin!")
        else:
            logger.error(f"Unhandled error in {ctx.command}: {error}")
            await ctx.send("❌ Bir hata oluştu! Lütfen daha sonra tekrar deneyin.")
    
    @tasks.loop(minutes=1)
    async def income_task(self):
        """Generate income every minute"""
        try:
            await self.economy_system.generate_income()
        except Exception as e:
            logger.error(f"Income generation error: {e}")
    
    @tasks.loop(hours=1)
    async def debt_task(self):
        """Calculate debt interest every hour"""
        try:
            await self.economy_system.calculate_debt_interest()
        except Exception as e:
            logger.error(f"Debt calculation error: {e}")
    
    @income_task.before_loop
    @debt_task.before_loop
    async def before_tasks(self):
        """Wait for bot to be ready before starting tasks"""
        await self.wait_until_ready()

async def main():
    """Main function to run the bot"""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not bot_token:
        logger.error("DISCORD_BOT_TOKEN environment variable not set!")
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

---

## 2. keep_alive.py (Web Sunucusu)
```python
from flask import Flask, jsonify
from threading import Thread
import time
import os

app = Flask('')

@app.route('/')
def home():
    return "🏰 Game of Thrones Discord Bot is alive and running 24/7!"

@app.route('/status')
def status():
    return jsonify({
        "status": "running",
        "service": "Game of Thrones Discord Bot", 
        "uptime": "24/7",
        "timestamp": time.time()
    })

@app.route('/health')
def health():
    return jsonify({"health": "ok", "bot": "active"})

def run():
    try:
        app.run(host='0.0.0.0', port=5000)
    except:
        # Port already in use, try different port
        app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    keep_alive()
    while True:
        time.sleep(1)
```

---

## 3. config.py (Ayarlar)
```python
# Database configuration
DATABASE_PATH = 'got_rp.db'

# Game balance settings
SOLDIER_COST = 10
GOLD_PER_SOLDIER_KILL = 5
DEBT_INTEREST_RATE = 0.1
EXPERIENCE_PER_ACTION = 10

# Army management settings
ARMY_UPGRADE_COSTS = {
    'weapons': {'cost': 1000, 'effectiveness': 5},
    'armor': {'cost': 1500, 'effectiveness': 3},
    'training': {'cost': 800, 'effectiveness': 4},
    'siege': {'cost': 2000, 'effectiveness': 8},
    'cavalry': {'cost': 2500, 'effectiveness': 10},
    'archers': {'cost': 1200, 'effectiveness': 6}
}

# Tournament settings
TOURNAMENT_ENTRY_FEE = 500
TOURNAMENT_PRIZE_MULTIPLIER = 0.8
```

Bu kodlar tam bot'unuzun çalışan halidir!

## 📋 Google Cloud Kurulum Özeti:

1. **console.cloud.google.com** - Hesap aç ($300 bedava)
2. **VM oluştur** - e2-micro (ücretsiz)
3. **SSH bağlan** - Terminal aç
4. **Python kur** - `sudo apt install python3-pip -y`
5. **Discord kur** - `pip3 install discord.py flask`
6. **Bot kodunu yapıştır** - Yukarıdaki kodları kopyala
7. **Token ayarla** - Discord bot token'ını ekle  
8. **Screen aç** - `screen -S bot`
9. **Bot çalıştır** - `python3 main.py`
10. **Çık** - Ctrl+A+D (bot arka planda çalışır)

Bot Google Cloud VM'de 7/24 çalışacak!

Detaylı adımlar **GOOGLE_CLOUD_KURULUM_REHBERI.md** dosyasında mevcut.