
import os
import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
import logging
import asyncio
import time

# Logging setup for PythonAnywhere
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/xxkaan44xx/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PythonAnywhereBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='🏰 Demir Taht RP - 7/24 PythonAnywhere | Created by xxkaan44xx'
        )
        
        self.setup_database()
        
    def setup_database(self):
        """Initialize SQLite database for PythonAnywhere"""
        try:
            # PythonAnywhere için mutlak dosya yolu
            db_path = '/home/xxkaan44xx/got_rp.db'
            self.db = sqlite3.connect(db_path, check_same_thread=False)
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
                    username TEXT,
                    alliance_id INTEGER,
                    role TEXT DEFAULT 'Üye',
                    level INTEGER DEFAULT 1,
                    gold INTEGER DEFAULT 100,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(alliance_id) REFERENCES alliances(id)
                )
            ''')
            
            # Bot durumu tablosu
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS bot_status (
                    id INTEGER PRIMARY KEY,
                    last_restart TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    uptime_count INTEGER DEFAULT 0
                )
            ''')
            
            self.db.commit()
            logger.info("✅ Database PythonAnywhere'de hazırlandı")
            
            # Bot restart sayısını güncelle
            self.update_restart_count()
            
        except Exception as e:
            logger.error(f"❌ Database hatası: {e}")
            
    def update_restart_count(self):
        """Bot restart sayısını güncelle"""
        try:
            cursor = self.db.execute("SELECT uptime_count FROM bot_status WHERE id = 1")
            result = cursor.fetchone()
            
            if result:
                new_count = result[0] + 1
                self.db.execute("UPDATE bot_status SET last_restart = ?, uptime_count = ? WHERE id = 1", 
                               (datetime.now(), new_count))
            else:
                self.db.execute("INSERT INTO bot_status (id, uptime_count) VALUES (1, 1)")
                
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Restart count hatası: {e}")
            
    async def on_ready(self):
        """Bot hazır olduğunda çalışır"""
        logger.info(f'✅ {self.user} PythonAnywhere\'de 7/24 çalışıyor!')
        logger.info(f'📊 Bot {len(self.guilds)} sunucuda aktif')
        
        # Bot durumunu güncelle
        await self.change_presence(
            activity=discord.Game(name="🏰 Westeros'ta Hüküm Sürüyor | 7/24 PythonAnywhere | !yardım")
        )
        
        # Başlangıç bilgilerini logla
        try:
            cursor = self.db.execute("SELECT uptime_count FROM bot_status WHERE id = 1")
            result = cursor.fetchone()
            if result:
                logger.info(f"🔄 Bot restart sayısı: {result[0]}")
        except Exception as e:
            logger.error(f"Status check hatası: {e}")

    async def on_command_error(self, ctx, error):
        """Hata yönetimi"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Eksik parametre! Doğru kullanım için `!yardım` yazın.")
        else:
            logger.error(f"Command error: {error}")
            await ctx.send("❌ Bir hata oluştu! Lütfen daha sonra tekrar deneyin.")

# Bot'u başlat
bot = PythonAnywhereBot()

# ==================== KOMUTLAR ====================

@bot.command(name='test')
async def test_command(ctx):
    """PythonAnywhere test komutu"""
    try:
        # Database connection test
        cursor = bot.db.execute("SELECT COUNT(*) FROM alliances")
        house_count = cursor.fetchone()[0]
        
        cursor = bot.db.execute("SELECT uptime_count FROM bot_status WHERE id = 1")
        restart_count = cursor.fetchone()
        restart_num = restart_count[0] if restart_count else 0
        
        embed = discord.Embed(
            title="🏰 Demir Taht RP Bot - PythonAnywhere",
            description="Bot başarıyla çalışıyor!",
            color=discord.Color.gold()
        )
        embed.add_field(name="Platform", value="PythonAnywhere 7/24", inline=True)
        embed.add_field(name="Durum", value="✅ Aktif", inline=True)
        embed.add_field(name="Creator", value="xxkaan44xx", inline=True)
        embed.add_field(name="Haneler", value=f"{house_count} hane", inline=True)
        embed.add_field(name="Restart", value=f"{restart_num}. kez", inline=True)
        embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Test komutu hatası: {e}")
        await ctx.send("❌ Test sırasında hata oluştu!")

@bot.command(name='ping')
async def ping_command(ctx):
    """Ping komutu"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Gecikme: **{latency}ms**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='yardım', aliases=['help'])
async def help_command(ctx):
    """Yardım komutu"""
    embed = discord.Embed(
        title="🏰 Demir Taht RP - Komutlar",
        description="PythonAnywhere'de 7/24 çalışan bot komutları:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🔧 Temel Komutlar",
        value="`!test` - Bot durumu\n`!ping` - Gecikme\n`!yardım` - Bu mesaj",
        inline=False
    )
    embed.add_field(
        name="🏰 Hane Komutları",
        value="`!haneler` - Haneleri listele\n`!katıl <hane>` - Haneye katıl\n`!profil` - Profilini gör",
        inline=False
    )
    embed.set_footer(text="Created by xxkaan44xx | PythonAnywhere 7/24")
    await ctx.send(embed=embed)

@bot.command(name='haneler')
async def list_alliances(ctx):
    """Haneleri listele"""
    try:
        cursor = bot.db.execute("SELECT name, gold, soldiers FROM alliances ORDER BY gold DESC LIMIT 10")
        alliances = cursor.fetchall()
        
        if not alliances:
            embed = discord.Embed(
                title="🏰 Westeros Haneleri",
                description="Henüz hane bulunmuyor! İlk haneyi sen kur!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
            
        embed = discord.Embed(
            title="🏰 Westeros Haneleri",
            description="En güçlü haneler:",
            color=discord.Color.gold()
        )
        
        for i, (name, gold, soldiers) in enumerate(alliances, 1):
            embed.add_field(
                name=f"{i}. {name}",
                value=f"💰 {gold:,} altın\n⚔️ {soldiers:,} asker",
                inline=True
            )
            
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Haneler komutu hatası: {e}")
        await ctx.send("❌ Haneleri listelerken hata oluştu!")

@bot.command(name='profil')
async def profile_command(ctx):
    """Kullanıcı profili"""
    try:
        user_id = ctx.author.id
        cursor = bot.db.execute("""
            SELECT m.level, m.gold, m.role, a.name as alliance_name 
            FROM members m 
            LEFT JOIN alliances a ON m.alliance_id = a.id 
            WHERE m.user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if not result:
            embed = discord.Embed(
                title="👤 Profil",
                description=f"{ctx.author.mention} henüz oyuna katılmamış!",
                color=discord.Color.red()
            )
        else:
            level, gold, role, alliance_name = result
            embed = discord.Embed(
                title="👤 Profil",
                description=f"{ctx.author.mention} profili:",
                color=discord.Color.green()
            )
            embed.add_field(name="Level", value=f"{level}", inline=True)
            embed.add_field(name="Altın", value=f"{gold:,}", inline=True)
            embed.add_field(name="Hane", value=alliance_name or "Hanesiz", inline=True)
            embed.add_field(name="Rol", value=role, inline=True)
            
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Profil komutu hatası: {e}")
        await ctx.send("❌ Profil görüntülenirken hata oluştu!")

@bot.command(name='durum')
async def status_command(ctx):
    """Bot durumu"""
    try:
        cursor = bot.db.execute("SELECT last_restart, uptime_count FROM bot_status WHERE id = 1")
        result = cursor.fetchone()
        
        if result:
            last_restart, uptime_count = result
            embed = discord.Embed(
                title="📊 Bot Durumu",
                color=discord.Color.green()
            )
            embed.add_field(name="Platform", value="PythonAnywhere", inline=True)
            embed.add_field(name="Durum", value="🟢 7/24 Aktif", inline=True)
            embed.add_field(name="Restart Sayısı", value=f"{uptime_count}", inline=True)
            embed.add_field(name="Son Restart", value=last_restart, inline=False)
        else:
            embed = discord.Embed(title="📊 Bot Durumu", description="Durum bilgisi bulunamadı", color=discord.Color.orange())
            
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Durum komutu hatası: {e}")
        await ctx.send("❌ Durum bilgisi alınırken hata oluştu!")

# ==================== ANA ÇALIŞMA DÖNGÜSÜ ====================

async def main():
    """Ana çalışma döngüsü - PythonAnywhere için optimize edilmiş"""
    try:
        # Bot'u başlat
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            logger.error("❌ DISCORD_BOT_TOKEN bulunamadı!")
            logger.info("Environment variables'a (.bashrc) token ekleyin:")
            logger.info('export DISCORD_BOT_TOKEN="your_token_here"')
            return
            
        logger.info("🚀 PythonAnywhere'de bot başlatılıyor...")
        await bot.start(token)
        
    except Exception as e:
        logger.error(f"❌ Bot başlatma hatası: {e}")
        
        # Hata durumunda 30 saniye bekle ve tekrar dene
        logger.info("🔄 30 saniye bekleyip tekrar denenecek...")
        await asyncio.sleep(30)
        
        # Yeniden başlatmayı dene
        try:
            await bot.start(token)
        except Exception as retry_error:
            logger.error(f"❌ Yeniden başlatma da başarısız: {retry_error}")

if __name__ == '__main__':
    # PythonAnywhere için sonsuz döngü
    while True:
        try:
            # Bot'u çalıştır
            asyncio.run(main())
            
        except KeyboardInterrupt:
            logger.info("👋 Bot kapatılıyor...")
            break
            
        except Exception as e:
            logger.error(f"❌ Beklenmeyen hata: {e}")
            logger.info("🔄 5 saniye bekleyip yeniden başlatılıyor...")
            time.sleep(5)
            
        # Kısa bekleme
        time.sleep(2)
