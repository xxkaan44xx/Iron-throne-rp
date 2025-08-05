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