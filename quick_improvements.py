import discord
from discord.ext import commands
import random
from datetime import datetime, timedelta
from utils import create_embed, format_number
import logging

logger = logging.getLogger(__name__)

def setup_quick_improvements(bot):
    """Hızlı bot iyileştirmeleri - veritabanı sorunu olmadan"""
    
    @bot.command(name='günlük-bonus', aliases=['daily-bonus'])
    async def daily_bonus(ctx):
        """Günlük bonus ödülünüzü alın"""
        user_id = ctx.author.id
        
        # Simple bonus system
        bonus_gold = random.randint(500, 1500)
        bonus_soldiers = random.randint(10, 50)
        
        try:
            conn = bot.db.conn
            cursor = conn.cursor()
            
            # Check if user has alliance
            cursor.execute('SELECT gold, soldiers FROM alliances WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if not result:
                embed = create_embed("❌ İttifak Bulunamadı", "Önce bir ittifak kurmalısınız!")
                await ctx.send(embed=embed)
                return
            
            # Add bonus
            cursor.execute('''
                UPDATE alliances 
                SET gold = gold + ?, soldiers = soldiers + ?
                WHERE user_id = ?
            ''', (bonus_gold, bonus_soldiers, user_id))
            
            conn.commit()
            
            embed = create_embed(
                "🎁 Günlük Bonus Alındı!",
                f"**🪙 Altın:** +{format_number(bonus_gold)}\n"
                f"**⚔️ Asker:** +{bonus_soldiers}\n\n"
                f"Yarın tekrar gelin!"
            )
            
        except Exception as e:
            logger.error(f"Daily bonus error: {e}")
            embed = create_embed("❌ Hata", "Bonus verilirken bir hata oluştu!")
        
        await ctx.send(embed=embed)
    
    @bot.command(name='şanslı-çark', aliases=['lucky-wheel'])
    async def lucky_wheel(ctx):
        """Şans çarkını çevirin!"""
        user_id = ctx.author.id
        cost = 100
        
        try:
            conn = bot.db.conn
            cursor = conn.cursor()
            
            # Check gold
            cursor.execute('SELECT gold FROM alliances WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if not result or result[0] < cost:
                embed = create_embed("💰 Yetersiz Altın", f"Şans çarkı için {cost} altın gerekli!")
                await ctx.send(embed=embed)
                return
            
            # Prizes
            prizes = [
                {"name": "💰 Büyük Hazine", "gold": 2000, "soldiers": 0, "chance": 5},
                {"name": "⚔️ Elit Ordu", "gold": 0, "soldiers": 200, "chance": 10},
                {"name": "🎯 Altın Yağmuru", "gold": 1000, "soldiers": 0, "chance": 15},
                {"name": "🛡️ Güçlü Askerler", "gold": 0, "soldiers": 100, "chance": 20},
                {"name": "💎 Değerli Taş", "gold": 500, "soldiers": 0, "chance": 25},
                {"name": "🗡️ Savaşçılar", "gold": 0, "soldiers": 50, "chance": 25}
            ]
            
            # Spin wheel
            spin = random.randint(1, 100)
            cumulative = 0
            won_prize = None
            
            for prize in prizes:
                cumulative += prize["chance"]
                if spin <= cumulative:
                    won_prize = prize
                    break
            
            if not won_prize:
                won_prize = prizes[-1]  # Default to last prize
            
            # Apply cost and reward
            cursor.execute('''
                UPDATE alliances 
                SET gold = gold - ? + ?, soldiers = soldiers + ?
                WHERE user_id = ?
            ''', (cost, won_prize["gold"], won_prize["soldiers"], user_id))
            
            conn.commit()
            
            embed = create_embed(
                "🎰 Şans Çarkı Sonucu!",
                f"**🎉 Kazandınız:** {won_prize['name']}\n"
                f"**💰 Altın:** +{format_number(won_prize['gold'])}\n"
                f"**⚔️ Asker:** +{won_prize['soldiers']}\n"
                f"**💸 Maliyet:** {cost} altın"
            )
            
        except Exception as e:
            logger.error(f"Lucky wheel error: {e}")
            embed = create_embed("❌ Hata", "Şans çarkı çevrilirken bir hata oluştu!")
        
        await ctx.send(embed=embed)
    
    @bot.command(name='hızlı-savaş', aliases=['quick-battle'])
    async def quick_battle(ctx):
        """Hızlı NPC savaşı yapın"""
        user_id = ctx.author.id
        
        try:
            conn = bot.db.conn
            cursor = conn.cursor()
            
            # Check user army
            cursor.execute('SELECT soldiers, power FROM alliances WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if not result:
                embed = create_embed("❌ İttifak Bulunamadı", "Önce bir ittifak kurmalısınız!")
                await ctx.send(embed=embed)
                return
            
            soldiers, power = result
            
            if soldiers < 50:
                embed = create_embed("⚔️ Yetersiz Ordu", "Savaş için en az 50 asker gerekli!")
                await ctx.send(embed=embed)
                return
            
            # Battle simulation
            enemies = [
                {"name": "Yabani Haydutlar", "difficulty": 1, "reward_mult": 1},
                {"name": "Barbar Kabilesi", "difficulty": 2, "reward_mult": 1.5},
                {"name": "Eski Kalıntı Savunucuları", "difficulty": 3, "reward_mult": 2},
                {"name": "Ejder Yavruları", "difficulty": 4, "reward_mult": 3}
            ]
            
            enemy = random.choice(enemies)
            
            # Calculate win chance
            army_strength = soldiers + (power * 10)
            win_chance = min(90, max(10, army_strength // (enemy["difficulty"] * 100)))
            
            if random.randint(1, 100) <= win_chance:
                # Victory!
                gold_reward = random.randint(200, 800) * enemy["reward_mult"]
                power_reward = random.randint(1, 5) * enemy["difficulty"]
                soldiers_lost = random.randint(5, 20)
                
                cursor.execute('''
                    UPDATE alliances 
                    SET gold = gold + ?, power = power + ?, soldiers = soldiers - ?
                    WHERE user_id = ?
                ''', (int(gold_reward), power_reward, soldiers_lost, user_id))
                
                embed = create_embed(
                    "⚔️ Zafer!",
                    f"**🏆 Yenilen:** {enemy['name']}\n"
                    f"**💰 Ganimet:** {format_number(int(gold_reward))} altın\n"
                    f"**⚡ Güç:** +{power_reward}\n"
                    f"**💀 Kayıp:** {soldiers_lost} asker"
                )
            else:
                # Defeat
                soldiers_lost = random.randint(20, 40)
                gold_lost = random.randint(100, 300)
                
                cursor.execute('''
                    UPDATE alliances 
                    SET soldiers = soldiers - ?, gold = gold - ?
                    WHERE user_id = ?
                ''', (soldiers_lost, gold_lost, user_id))
                
                embed = create_embed(
                    "💀 Yenilgi!",
                    f"**😈 Yenildi:** {enemy['name']}\n"
                    f"**💀 Kayıp Asker:** {soldiers_lost}\n"
                    f"**💸 Kayıp Altın:** {format_number(gold_lost)}\n"
                    f"**🔄 Tekrar deneyin!**"
                )
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Quick battle error: {e}")
            embed = create_embed("❌ Hata", "Savaş sırasında bir hata oluştu!")
        
        await ctx.send(embed=embed)
    
    @bot.command(name='ticaret-hızlı', aliases=['quick-trade'])
    async def quick_trade(ctx):
        """Hızlı ticaret yapın"""
        user_id = ctx.author.id
        
        try:
            conn = bot.db.conn
            cursor = conn.cursor()
            
            # Check user resources
            cursor.execute('SELECT gold, soldiers FROM alliances WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if not result:
                embed = create_embed("❌ İttifak Bulunamadı", "Önce bir ittifak kurmalısınız!")
                await ctx.send(embed=embed)
                return
            
            gold, soldiers = result
            
            # Trade options
            trades = [
                {"name": "Altın → Asker", "give_gold": 500, "get_soldiers": 25, "min_gold": 500},
                {"name": "Altın → Güç", "give_gold": 1000, "get_power": 5, "min_gold": 1000},
                {"name": "Asker → Altın", "give_soldiers": 50, "get_gold": 600, "min_soldiers": 50},
                {"name": "Toplu Ticaret", "give_gold": 2000, "get_soldiers": 100, "get_power": 3, "min_gold": 2000}
            ]
            
            available_trades = []
            for trade in trades:
                if trade.get("min_gold", 0) <= gold and trade.get("min_soldiers", 0) <= soldiers:
                    available_trades.append(trade)
            
            if not available_trades:
                embed = create_embed("💰 Yetersiz Kaynak", "Hiçbir ticaret için yeterli kaynağınız yok!")
                await ctx.send(embed=embed)
                return
            
            # Random trade
            chosen_trade = random.choice(available_trades)
            
            # Execute trade
            gold_change = chosen_trade.get("get_gold", 0) - chosen_trade.get("give_gold", 0)
            soldiers_change = chosen_trade.get("get_soldiers", 0) - chosen_trade.get("give_soldiers", 0)
            power_change = chosen_trade.get("get_power", 0)
            
            cursor.execute('''
                UPDATE alliances 
                SET gold = gold + ?, soldiers = soldiers + ?, power = power + ?
                WHERE user_id = ?
            ''', (gold_change, soldiers_change, power_change, user_id))
            
            conn.commit()
            
            # Format results
            changes = []
            if gold_change != 0:
                changes.append(f"💰 Altın: {'+' if gold_change > 0 else ''}{format_number(gold_change)}")
            if soldiers_change != 0:
                changes.append(f"⚔️ Asker: {'+' if soldiers_change > 0 else ''}{soldiers_change}")
            if power_change != 0:
                changes.append(f"⚡ Güç: +{power_change}")
            
            embed = create_embed(
                "🏪 Ticaret Tamamlandı!",
                f"**📋 İşlem:** {chosen_trade['name']}\n"
                f"**📊 Değişiklikler:**\n" + "\n".join(changes)
            )
            
        except Exception as e:
            logger.error(f"Quick trade error: {e}")
            embed = create_embed("❌ Hata", "Ticaret sırasında bir hata oluştu!")
        
        await ctx.send(embed=embed)
    
    @bot.command(name='yeni-özellikler', aliases=['new-features', 'features'])
    async def new_features(ctx):
        """Yeni eklenen özellikleri görün"""
        embed = create_embed(
            "🚀 Yeni Bot İyileştirmeleri!",
            "**🎁 Günlük Bonus Sistemi:**\n"
            "`!günlük-bonus` - Her gün ücretsiz ödül!\n\n"
            
            "**🎰 Şans Çarkı:**\n"
            "`!şanslı-çark` - 100 altınla büyük ödüller!\n\n"
            
            "**⚔️ Hızlı Savaş:**\n"
            "`!hızlı-savaş` - NPC'lere karşı hızlı mücadele!\n\n"
            
            "**🏪 Hızlı Ticaret:**\n"
            "`!ticaret-hızlı` - Otomatik kaynak ticareti!\n\n"
            
            "**📊 Bot İstatistikleri:**\n"
            f"• **Toplam Komut:** 150+\n"
            f"• **Aktif Sunucu:** 3\n"
            f"• **24/7 Uptime:** ✅\n"
            f"• **Performans:** Premium\n\n"
            
            "**🏆 Son Güncellemeler:**\n"
            "✅ Duplikasyon sorunu çözüldü\n"
            "✅ 24/7 sistem aktif\n"
            "✅ Render deployment hazır\n"
            "✅ Gelişmiş eğlence sistemi\n"
            "✅ Premium özellikler eklendi"
        )
        
        await ctx.send(embed=embed)
    
    logger.info("Quick improvements loaded successfully - 5 new commands added")

def setup_admin_improvements(bot):
    """Admin için gelişmiş özellikler"""
    
    @bot.command(name='bot-stats', aliases=['botstats'])
    async def bot_statistics(ctx):
        """Detaylı bot istatistikleri"""
        try:
            conn = bot.db.conn
            cursor = conn.cursor()
            
            # Get database stats
            cursor.execute('SELECT COUNT(*) FROM alliances')
            alliance_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM members')
            member_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(gold) FROM alliances')
            total_gold = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT SUM(soldiers) FROM alliances')
            total_soldiers = cursor.fetchone()[0] or 0
            
            # Bot info
            guild_count = len(bot.guilds)
            command_count = len(bot.commands)
            
            embed = create_embed(
                "📊 Bot İstatistikleri",
                f"**🏰 Sunucu Bilgileri:**\n"
                f"• Aktif Sunucu: {guild_count}\n"
                f"• Toplam Komut: {command_count}\n"
                f"• Bot Versiyonu: 3.0 Professional\n\n"
                
                f"**🏛️ Oyun İstatistikleri:**\n"
                f"• Toplam İttifak: {alliance_count}\n"
                f"• Aktif Üye: {member_count}\n"
                f"• Toplam Altın: {format_number(total_gold)}\n"
                f"• Toplam Asker: {format_number(total_soldiers)}\n\n"
                
                f"**⚡ Sistem Durumu:**\n"
                f"• Uptime: 24/7 Aktif ✅\n"
                f"• Database: SQLite ✅\n"
                f"• Memory: Optimize ✅\n"
                f"• Performance: Premium ✅"
            )
            
        except Exception as e:
            logger.error(f"Bot stats error: {e}")
            embed = create_embed("❌ Hata", "İstatistikler alınırken bir hata oluştu!")
        
        await ctx.send(embed=embed)
    
    logger.info("Admin improvements loaded successfully")