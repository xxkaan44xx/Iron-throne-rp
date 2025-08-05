import os
import discord
from discord.ext import commands, tasks
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, jsonify
from threading import Thread
import json

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

@app.route('/status')
def status():
    return jsonify({
        "service": "Discord Bot",
        "platform": "Cyclic.sh",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    })

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
            description='Game of Thrones Roleplay Bot - Cyclic.sh Edition'
        )
        
        # Database setup
        self.setup_database()
        
    def setup_database(self):
        """Initialize SQLite database"""
        try:
            self.db = sqlite3.connect('got_rp.db', check_same_thread=False)
            self.db.execute("PRAGMA foreign_keys = ON")
            
            # Create alliances table
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
            
            # Create members table
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
            
            # Create wars table
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS wars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attacker_id INTEGER NOT NULL,
                    defender_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'active',
                    attacker_losses INTEGER DEFAULT 0,
                    defender_losses INTEGER DEFAULT 0,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(attacker_id) REFERENCES alliances(id),
                    FOREIGN KEY(defender_id) REFERENCES alliances(id)
                )
            ''')
            
            self.db.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            
    async def setup_hook(self):
        """Setup background tasks"""
        logger.info("Bot is ready for 24/7 operation on Cyclic.sh!")
        
    async def on_ready(self):
        """Bot ready event"""
        logger.info(f'{self.user} has logged in!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        logger.info("Running on Cyclic.sh platform")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="🏰 GoT RP | Cyclic.sh'de 7/24")
        )
        
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Eksik parametre: {error.param.name}")
        else:
            logger.error(f"Unhandled error in {ctx.command}: {error}")
            await ctx.send("❌ Bir hata oluştu!")

# Bot instance
bot = GameOfThronesBot()

# Commands
@bot.command(name='test')
async def test_command(ctx):
    """Test command"""
    embed = discord.Embed(
        title="🏰 Game of Thrones RP Bot",
        description="Cyclic.sh'de başarıyla çalışıyor!",
        color=discord.Color.blue()
    )
    embed.add_field(name="Platform", value="Cyclic.sh", inline=True)
    embed.add_field(name="Durum", value="✅ Aktif", inline=True)
    embed.add_field(name="Sunucu Sayısı", value=str(len(bot.guilds)), inline=True)
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    """Ping command"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! {latency}ms')

@bot.command(name='yardım', aliases=['help'])
async def help_command(ctx):
    """Help command"""
    embed = discord.Embed(
        title="🏰 Game of Thrones RP Bot - Yardım",
        description="Bot komutları (Cyclic.sh Edition):",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Temel Komutlar",
        value="`!test` - Bot durumunu test et\n"
              "`!ping` - Bot gecikmesini ölç\n"
              "`!yardım` - Bu yardım mesajını göster",
        inline=False
    )
    embed.add_field(
        name="Platform",
        value="Cyclic.sh'de 7/24 çalışıyor",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command(name='haneler')
async def houses_command(ctx):
    """List all houses"""
    try:
        cursor = bot.db.execute('SELECT name, gold, soldiers FROM alliances ORDER BY gold DESC')
        houses = cursor.fetchall()
        
        if not houses:
            await ctx.send("❌ Henüz hane oluşturulmamış!")
            return
            
        embed = discord.Embed(
            title="🏰 Haneler",
            description="Westeros'taki tüm haneler:",
            color=discord.Color.gold()
        )
        
        for name, gold, soldiers in houses:
            embed.add_field(
                name=f"🏰 {name}",
                value=f"💰 {gold:,} altın\n⚔️ {soldiers:,} asker",
                inline=True
            )
            
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Houses command error: {e}")
        await ctx.send("❌ Haneler listelenirken hata oluştu!")

@bot.command(name='katıl')
async def join_house(ctx, *, house_name):
    """Join a house"""
    try:
        # Check if house exists
        cursor = bot.db.execute('SELECT id FROM alliances WHERE name = ?', (house_name,))
        house = cursor.fetchone()
        
        if not house:
            await ctx.send(f"❌ '{house_name}' adında bir hane bulunamadı!")
            return
            
        # Check if user is already in a house
        cursor = bot.db.execute('SELECT alliance_id FROM members WHERE user_id = ?', (ctx.author.id,))
        existing = cursor.fetchone()
        
        if existing:
            await ctx.send("❌ Zaten bir haneye üyesiniz!")
            return
            
        # Join the house
        bot.db.execute(
            'INSERT OR REPLACE INTO members (user_id, alliance_id) VALUES (?, ?)',
            (ctx.author.id, house[0])
        )
        bot.db.commit()
        
        await ctx.send(f"✅ {house_name} hanesine katıldınız!")
        
    except Exception as e:
        logger.error(f"Join house error: {e}")
        await ctx.send("❌ Haneye katılırken hata oluştu!")

# Note: This file is deprecated. Use main.py instead.
# The Flask server is now handled by keep_alive.py
# This file is kept for reference only.

if __name__ == '__main__':
    logger.warning("This file is deprecated. Please use main.py to run the bot.")
    print("⚠️ Bu dosya artık kullanılmıyor. Botu çalıştırmak için main.py kullanın.")