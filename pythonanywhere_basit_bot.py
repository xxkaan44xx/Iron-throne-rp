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