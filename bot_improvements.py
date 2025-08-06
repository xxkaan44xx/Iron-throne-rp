import discord
from discord.ext import commands
import asyncio
import random
import json
from datetime import datetime, timedelta
from utils import create_embed, format_number
import logging

logger = logging.getLogger(__name__)

class BotImprovements:
    """
    Game of Thrones Discord Bot İyileştirmeleri
    Yeni özellikler ve gelişmiş komutlar
    """
    
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.create_tables()
    
    def create_tables(self):
        """İyileştirme sistemleri için yeni tablolar oluştur"""
        conn = self.db.conn
        cursor = conn.cursor()
        
        # Gelişmiş görev sistemi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS advanced_quests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_name TEXT NOT NULL,
                description TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                reward_gold INTEGER DEFAULT 0,
                reward_soldiers INTEGER DEFAULT 0,
                reward_power INTEGER DEFAULT 0,
                requirements TEXT,
                duration_hours INTEGER DEFAULT 24,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Karakter gelişim sistemi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS character_progression (
                user_id INTEGER PRIMARY KEY,
                character_class TEXT DEFAULT 'Noble',
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                skill_points INTEGER DEFAULT 0,
                strength INTEGER DEFAULT 10,
                intelligence INTEGER DEFAULT 10,
                charisma INTEGER DEFAULT 10,
                diplomacy INTEGER DEFAULT 10,
                warfare INTEGER DEFAULT 10,
                stealth INTEGER DEFAULT 10,
                last_training TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Gelişmiş ekonomi sistemi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS advanced_economy (
                user_id INTEGER PRIMARY KEY,
                trading_reputation INTEGER DEFAULT 0,
                merchant_level INTEGER DEFAULT 1,
                trade_routes INTEGER DEFAULT 0,
                ships INTEGER DEFAULT 0,
                caravans INTEGER DEFAULT 0,
                market_shares TEXT DEFAULT '{}',
                investment_portfolio TEXT DEFAULT '{}',
                last_trade TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Savaş geçmişi ve başarılar
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS war_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                battle_type TEXT NOT NULL,
                opponent TEXT,
                result TEXT NOT NULL,
                soldiers_lost INTEGER DEFAULT 0,
                gold_gained INTEGER DEFAULT 0,
                experience_gained INTEGER DEFAULT 0,
                battle_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Gelişmiş evlilik sistemi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS marriage_enhancements (
                marriage_id INTEGER PRIMARY KEY,
                wedding_date TIMESTAMP,
                ceremony_type TEXT DEFAULT 'Simple',
                dowry_gold INTEGER DEFAULT 0,
                alliance_bonus INTEGER DEFAULT 0,
                children_count INTEGER DEFAULT 0,
                relationship_status TEXT DEFAULT 'Happy',
                anniversary_rewards TEXT DEFAULT '[]',
                FOREIGN KEY (marriage_id) REFERENCES marriages (id)
            )
        ''')
        
        # Kraliyet sistemi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS royal_system (
                kingdom_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kingdom_name TEXT NOT NULL,
                king_user_id INTEGER,
                queen_user_id INTEGER,
                hand_user_id INTEGER,
                treasury INTEGER DEFAULT 10000,
                army_size INTEGER DEFAULT 1000,
                stability INTEGER DEFAULT 50,
                popularity INTEGER DEFAULT 50,
                laws TEXT DEFAULT '[]',
                founded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Bot improvements tables created successfully")

def setup_improved_commands(bot):
    """Gelişmiş komutları bot'a ekle"""
    improvements = BotImprovements(bot, bot.db)
    
    @bot.command(name='karakter-sınıfı', aliases=['class', 'sınıf'])
    async def character_class(ctx, new_class=None):
        """Karakter sınıfınızı görün veya değiştirin"""
        classes = {
            'Lord': {'desc': 'Güçlü lider, yüksek karizma ve diplomasi', 'bonus': '+3 Karizma, +2 Diplomasi'},
            'Knight': {'desc': 'Elit savaşçı, yüksek güç ve savaş', 'bonus': '+3 Güç, +2 Savaş'},
            'Maester': {'desc': 'Bilge danışman, yüksek zeka', 'bonus': '+3 Zeka, +2 Diplomasi'},
            'Spy': {'desc': 'Gizli ajan, yüksek gizlilik ve zeka', 'bonus': '+3 Gizlilik, +2 Zeka'},
            'Merchant': {'desc': 'Zengin tüccar, ekonomi uzmanı', 'bonus': '+50% Altın, +2 Karizma'},
            'Assassin': {'desc': 'Ölümcül suikastçı, yüksek gizlilik', 'bonus': '+3 Gizlilik, +2 Güç'},
            'Diplomat': {'desc': 'Usta diplomat, yüksek karizma', 'bonus': '+3 Diplomasi, +2 Karizma'}
        }
        
        conn = bot.db.conn
        cursor = conn.cursor()
        
        if new_class is None:
            # Mevcut sınıfı göster
            cursor.execute('SELECT character_class, level, experience FROM character_progression WHERE user_id = ?', (ctx.author.id,))
            result = cursor.fetchone()
            
            if result:
                current_class, level, exp = result
                embed = create_embed(
                    f"⚔️ {ctx.author.display_name}'in Karakteri",
                    f"**Sınıf:** {current_class}\n**Seviye:** {level}\n**Deneyim:** {exp}\n\n"
                    f"**Sınıf Bonusu:** {classes.get(current_class, {}).get('bonus', 'Bilinmiyor')}"
                )
            else:
                embed = create_embed("⚔️ Karakter Bulunamadı", "Henüz bir karakteriniz yok. Bir sınıf seçin!")
        else:
            # Sınıf değiştir
            if new_class not in classes:
                available = ', '.join(classes.keys())
                embed = create_embed("❌ Geçersiz Sınıf", f"Mevcut sınıflar: {available}")
            else:
                cursor.execute('''
                    INSERT OR REPLACE INTO character_progression 
                    (user_id, character_class, level, experience) 
                    VALUES (?, ?, 1, 0)
                ''', (ctx.author.id, new_class))
                
                embed = create_embed(
                    f"✅ Sınıf Değiştirildi!",
                    f"**Yeni Sınıfınız:** {new_class}\n"
                    f"**Açıklama:** {classes[new_class]['desc']}\n"
                    f"**Bonus:** {classes[new_class]['bonus']}"
                )
        
        conn.commit()
        conn.close()
        await ctx.send(embed=embed)
    
    @bot.command(name='antrenman', aliases=['train', 'eğitim'])
    async def character_training(ctx, skill=None):
        """Karakterinizi antrenman yaparak geliştirin"""
        skills = ['strength', 'intelligence', 'charisma', 'diplomacy', 'warfare', 'stealth']
        
        if skill is None:
            embed = create_embed(
                "⚔️ Antrenman Sistemi",
                f"**Kullanım:** `!antrenman <beceri>`\n"
                f"**Beceriler:** {', '.join(skills)}\n"
                f"**Cooldown:** 2 saat\n"
                f"**Maliyet:** 100 altın"
            )
            await ctx.send(embed=embed)
            return
        
        if skill not in skills:
            embed = create_embed("❌ Geçersiz Beceri", f"Mevcut beceriler: {', '.join(skills)}")
            await ctx.send(embed=embed)
            return
        
        conn = bot.db.conn
        cursor = conn.cursor()
        
        # Cooldown kontrolü
        cursor.execute('SELECT last_training FROM character_progression WHERE user_id = ?', (ctx.author.id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            last_training = datetime.fromisoformat(result[0])
            if datetime.now() - last_training < timedelta(hours=2):
                remaining = timedelta(hours=2) - (datetime.now() - last_training)
                embed = create_embed("⏰ Cooldown Aktif", f"Bir sonraki antrenman: {remaining}")
                await ctx.send(embed=embed)
                conn.close()
                return
        
        # Altın kontrolü
        cursor.execute('SELECT gold FROM alliances WHERE user_id = ?', (ctx.author.id,))
        gold_result = cursor.fetchone()
        
        if not gold_result or gold_result[0] < 100:
            embed = create_embed("💰 Yetersiz Altın", "Antrenman için 100 altın gerekli!")
            await ctx.send(embed=embed)
            conn.close()
            return
        
        # Antrenman yap
        improvement = random.randint(1, 3)
        exp_gain = random.randint(10, 25)
        
        cursor.execute(f'''
            UPDATE character_progression 
            SET {skill} = {skill} + ?, experience = experience + ?, last_training = ?
            WHERE user_id = ?
        ''', (improvement, exp_gain, datetime.now().isoformat(), ctx.author.id))
        
        cursor.execute('UPDATE alliances SET gold = gold - 100 WHERE user_id = ?', (ctx.author.id,))
        
        embed = create_embed(
            "⚔️ Antrenman Tamamlandı!",
            f"**{skill.title()}** +{improvement}\n"
            f"**Deneyim** +{exp_gain}\n"
            f"**Maliyet:** 100 altın"
        )
        
        conn.commit()
        conn.close()
        await ctx.send(embed=embed)
    
    @bot.command(name='krallık-kur', aliases=['found-kingdom'])
    async def found_kingdom(ctx, *, kingdom_name):
        """Yeni bir krallık kurun"""
        if len(kingdom_name) < 3 or len(kingdom_name) > 30:
            embed = create_embed("❌ Geçersiz İsim", "Krallık ismi 3-30 karakter arası olmalı!")
            await ctx.send(embed=embed)
            return
        
        conn = bot.db.conn
        cursor = conn.cursor()
        
        # Kullanıcının yeterli kaynağı var mı?
        cursor.execute('SELECT gold, soldiers, power FROM alliances WHERE user_id = ?', (ctx.author.id,))
        result = cursor.fetchone()
        
        if not result:
            embed = create_embed("❌ İttifak Bulunamadı", "Önce bir ittifak kurmalısınız!")
            await ctx.send(embed=embed)
            conn.close()
            return
        
        gold, soldiers, power = result
        required_gold = 50000
        required_soldiers = 5000
        required_power = 100
        
        if gold < required_gold or soldiers < required_soldiers or power < required_power:
            embed = create_embed(
                "❌ Yetersiz Kaynak",
                f"**Gereksinimler:**\n"
                f"Altın: {format_number(required_gold)} (Mevcut: {format_number(gold)})\n"
                f"Asker: {format_number(required_soldiers)} (Mevcut: {format_number(soldiers)})\n"
                f"Güç: {format_number(required_power)} (Mevcut: {format_number(power)})"
            )
            await ctx.send(embed=embed)
            conn.close()
            return
        
        # Krallık kur
        try:
            cursor.execute('''
                INSERT INTO royal_system (kingdom_name, king_user_id, treasury, army_size)
                VALUES (?, ?, ?, ?)
            ''', (kingdom_name, ctx.author.id, required_gold, required_soldiers))
            
            cursor.execute('''
                UPDATE alliances 
                SET gold = gold - ?, soldiers = soldiers - ?, power = power - ?
                WHERE user_id = ?
            ''', (required_gold, required_soldiers, required_power, ctx.author.id))
            
            embed = create_embed(
                f"👑 {kingdom_name} Krallığı Kuruldu!",
                f"**Kral:** {ctx.author.display_name}\n"
                f"**Hazine:** {format_number(required_gold)} altın\n"
                f"**Ordu:** {format_number(required_soldiers)} asker\n"
                f"**Kuruluş:** {datetime.now().strftime('%d/%m/%Y')}"
            )
            
            conn.commit()
            conn.close()
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = create_embed("❌ Hata", "Krallık kurulurken bir hata oluştu!")
            await ctx.send(embed=embed)
            conn.close()
    
    @bot.command(name='ticaret-yolu', aliases=['trade-route'])
    async def establish_trade_route(ctx, target_user: discord.Member):
        """Başka bir oyuncuyla ticaret yolu kurun"""
        if target_user is None or target_user == ctx.author:
            embed = create_embed("❌ Geçersiz Hedef", "Geçerli bir oyuncu etiketleyin!")
            await ctx.send(embed=embed)
            return
        
        conn = bot.db.conn
        cursor = conn.cursor()
        
        # Her iki oyuncunun da ittifakı var mı?
        cursor.execute('SELECT COUNT(*) FROM alliances WHERE user_id IN (?, ?)', (ctx.author.id, target_user.id))
        if cursor.fetchone()[0] != 2:
            embed = create_embed("❌ Geçersiz İşlem", "Her iki oyuncunun da ittifakı olmalı!")
            await ctx.send(embed=embed)
            conn.close()
            return
        
        # Ticaret yolu maliyeti
        cost = 1000
        cursor.execute('SELECT gold FROM alliances WHERE user_id = ?', (ctx.author.id,))
        gold = cursor.fetchone()[0]
        
        if gold < cost:
            embed = create_embed("💰 Yetersiz Altın", f"Ticaret yolu için {cost} altın gerekli!")
            await ctx.send(embed=embed)
            conn.close()
            return
        
        # Ticaret yolu kur
        cursor.execute('''
            INSERT OR IGNORE INTO advanced_economy (user_id, trade_routes, last_trade)
            VALUES (?, 0, ?)
        ''', (ctx.author.id, datetime.now().isoformat()))
        
        cursor.execute('''
            UPDATE advanced_economy 
            SET trade_routes = trade_routes + 1, last_trade = ?
            WHERE user_id = ?
        ''', (datetime.now().isoformat(), ctx.author.id))
        
        cursor.execute('UPDATE alliances SET gold = gold - ? WHERE user_id = ?', (cost, ctx.author.id))
        
        # Günlük gelir bonusu ekle
        daily_bonus = random.randint(50, 150)
        cursor.execute('UPDATE alliances SET gold = gold + ? WHERE user_id = ?', (daily_bonus, ctx.author.id))
        
        embed = create_embed(
            "🚢 Ticaret Yolu Kuruldu!",
            f"**Hedef:** {target_user.display_name}\n"
            f"**Maliyet:** {cost} altın\n"
            f"**Günlük Bonus:** {daily_bonus} altın\n"
            f"**Ticaret Geliriniz artacak!**"
        )
        
        conn.commit()
        conn.close()
        await ctx.send(embed=embed)
    
    logger.info("Advanced bot improvements commands loaded successfully")

def setup_premium_features(bot):
    """Premium özellikler ekle"""
    
    @bot.command(name='ejder-avı', aliases=['dragon-hunt'])
    async def dragon_hunt(ctx):
        """Efsanevi ejder avına çıkın!"""
        conn = bot.db.conn
        cursor = conn.cursor()
        
        # Minimum gereksinimler
        cursor.execute('SELECT gold, soldiers, power FROM alliances WHERE user_id = ?', (ctx.author.id,))
        result = cursor.fetchone()
        
        if not result:
            embed = create_embed("❌ İttifak Bulunamadı", "Önce bir ittifak kurmalısınız!")
            await ctx.send(embed=embed)
            conn.close()
            return
        
        gold, soldiers, power = result
        
        if soldiers < 1000 or power < 50:
            embed = create_embed(
                "⚔️ Yetersiz Güç",
                f"**Ejder avı için gereksinimler:**\n"
                f"Asker: 1000+ (Mevcut: {soldiers})\n"
                f"Güç: 50+ (Mevcut: {power})"
            )
            await ctx.send(embed=embed)
            conn.close()
            return
        
        # Ejder avı simülasyonu
        dragons = [
            {"name": "Balerion", "difficulty": "Legendary", "reward_multiplier": 5},
            {"name": "Vhagar", "difficulty": "Epic", "reward_multiplier": 3},
            {"name": "Meraxes", "difficulty": "Rare", "reward_multiplier": 2},
            {"name": "Syrax", "difficulty": "Common", "reward_multiplier": 1}
        ]
        
        dragon = random.choice(dragons)
        success_rate = min(90, (soldiers // 100) + (power * 2))
        
        if random.randint(1, 100) <= success_rate:
            # Başarı!
            gold_reward = random.randint(5000, 15000) * dragon["reward_multiplier"]
            power_reward = random.randint(10, 30) * dragon["reward_multiplier"]
            soldiers_lost = random.randint(50, 200)
            
            cursor.execute('''
                UPDATE alliances 
                SET gold = gold + ?, power = power + ?, soldiers = soldiers - ?
                WHERE user_id = ?
            ''', (gold_reward, power_reward, soldiers_lost, ctx.author.id))
            
            embed = create_embed(
                f"🐉 {dragon['name']} Ejderi Yenildi!",
                f"**Zorluk:** {dragon['difficulty']}\n"
                f"**Kazanılan Altın:** {format_number(gold_reward)}\n"
                f"**Kazanılan Güç:** {power_reward}\n"
                f"**Kaybedilen Asker:** {soldiers_lost}\n\n"
                f"🏆 **Efsanevi zafer!**"
            )
        else:
            # Başarısızlık
            soldiers_lost = random.randint(200, 500)
            gold_lost = random.randint(1000, 3000)
            
            cursor.execute('''
                UPDATE alliances 
                SET soldiers = soldiers - ?, gold = gold - ?
                WHERE user_id = ?
            ''', (soldiers_lost, gold_lost, ctx.author.id))
            
            embed = create_embed(
                f"💀 {dragon['name']} Ejderi Kaçtı!",
                f"**Zorluk:** {dragon['difficulty']}\n"
                f"**Kaybedilen Asker:** {soldiers_lost}\n"
                f"**Kaybedilen Altın:** {format_number(gold_lost)}\n\n"
                f"💔 **Daha güçlü olup tekrar deneyin!**"
            )
        
        conn.commit()
        conn.close()
        await ctx.send(embed=embed)
    
    @bot.command(name='büyük-turnuva', aliases=['grand-tournament'])
    async def grand_tournament(ctx):
        """Büyük turnuvaya katılın!"""
        conn = bot.db.conn
        cursor = conn.cursor()
        
        # Turnuva katılım ücreti
        entry_fee = 5000
        cursor.execute('SELECT gold FROM alliances WHERE user_id = ?', (ctx.author.id,))
        result = cursor.fetchone()
        
        if not result or result[0] < entry_fee:
            embed = create_embed("💰 Yetersiz Altın", f"Turnuva katılım ücreti: {entry_fee} altın")
            await ctx.send(embed=embed)
            conn.close()
            return
        
        # Turnuva simülasyonu
        opponents = [
            "Ser Jaime Lannister",
            "Ser Barristan Selmy", 
            "Oberyn Martell",
            "Gregor Clegane",
            "Sandor Clegane",
            "Ser Loras Tyrell"
        ]
        
        rounds = 3
        total_winnings = 0
        survived_rounds = 0
        
        for round_num in range(1, rounds + 1):
            opponent = random.choice(opponents)
            win_chance = random.randint(30, 70)
            
            if random.randint(1, 100) <= win_chance:
                # Kazandı
                round_reward = entry_fee * round_num
                total_winnings += round_reward
                survived_rounds += 1
                
                embed = create_embed(
                    f"⚔️ {round_num}. Tur Kazanıldı!",
                    f"**Rakip:** {opponent}\n"
                    f"**Ödül:** {format_number(round_reward)} altın\n"
                    f"**Toplam:** {format_number(total_winnings)} altın"
                )
                await ctx.send(embed=embed)
                await asyncio.sleep(2)
            else:
                # Kaybetti
                embed = create_embed(
                    f"💀 {round_num}. Turda Elendi!",
                    f"**Rakip:** {opponent}\n"
                    f"**Toplam Kazanç:** {format_number(total_winnings)} altın\n"
                    f"**Turnuva Sona Erdi**"
                )
                await ctx.send(embed=embed)
                break
        
        if survived_rounds == rounds:
            # Şampiyon!
            champion_bonus = 20000
            total_winnings += champion_bonus
            
            embed = create_embed(
                "👑 TURNUVA ŞAMPİYONU!",
                f"**Tüm turları geçtiniz!**\n"
                f"**Şampiyonluk Bonusu:** {format_number(champion_bonus)} altın\n"
                f"**Toplam Kazanç:** {format_number(total_winnings)} altın\n\n"
                f"🏆 **Efsanevi başarı!**"
            )
            await ctx.send(embed=embed)
        
        # Kazançları hesaba ekle
        net_gain = total_winnings - entry_fee
        cursor.execute('UPDATE alliances SET gold = gold + ? WHERE user_id = ?', (net_gain, ctx.author.id))
        
        conn.commit()
        conn.close()
    
    logger.info("Premium features loaded successfully")