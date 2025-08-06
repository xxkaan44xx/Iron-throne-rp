
import discord
from discord.ext import commands
import asyncio
import random
from utils import create_embed, format_number, get_house_emoji

def setup_easy_commands(bot, db):
    """Setup additional easy-to-use commands"""
    
    @bot.command(name='ticaret_kolay', aliases=['easy_trade'])
    async def easy_trade(ctx):
        """Super simple trading system"""
        user_id = ctx.author.id
        alliance = db.get_user_alliance(user_id)
        
        if not alliance:
            embed = create_embed("❌ Hata", "Önce bir haneye katıl! `!hızlı_hane`", discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        gold = alliance[3]
        
        if gold < 100:
            embed = create_embed("💸 Para Yok", "En az 100 altına ihtiyacın var!", discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        # Simple random trade
        trade_options = [
            {"item": "Kuzey Kürkleri", "cost": 100, "profit": 150, "chance": 80},
            {"item": "Dorne Şarabı", "cost": 200, "profit": 320, "chance": 70},
            {"item": "Valyrian Çelik", "cost": 500, "profit": 800, "chance": 60},
            {"item": "Ejder Yumurtası", "cost": 1000, "profit": 1600, "chance": 50}
        ]
        
        # Filter affordable options
        affordable = [t for t in trade_options if t["cost"] <= gold]
        
        if not affordable:
            embed = create_embed("💰 Daha Fazla Para Gerek", 
                               "En az 100 altınla ticaret yapabilirsin!", 
                               discord.Color.orange())
            await ctx.send(embed=embed)
            return
        
        embed = create_embed("🏪 KOLAY TİCARET",
                           "Basit ve karlı ticaret seçenekleri:",
                           discord.Color.gold())
        
        for i, trade in enumerate(affordable, 1):
            profit = trade["profit"] - trade["cost"]
            embed.add_field(
                name=f"{i}️⃣ {trade['item']}",
                value=f"**Maliyet:** {trade['cost']} altın\n"
                      f"**Kar:** {profit} altın\n"
                      f"**Başarı:** %{trade['chance']}\n"
                      f"**Komut:** `!ticaret_yap {i}`",
                inline=True
            )
        
        embed.set_footer(text="Numara yazarak ticaret yap! Örnek: !ticaret_yap 1")
        await ctx.send(embed=embed)

    @bot.command(name='ticaret_yap')
    async def do_trade(ctx, option: int):
        """Execute a trade"""
        user_id = ctx.author.id
        alliance = db.get_user_alliance(user_id)
        
        if not alliance:
            return
        
        trade_options = [
            {"item": "Kuzey Kürkleri", "cost": 100, "profit": 150, "chance": 80},
            {"item": "Dorne Şarabı", "cost": 200, "profit": 320, "chance": 70},
            {"item": "Valyrian Çelik", "cost": 500, "profit": 800, "chance": 60},
            {"item": "Ejder Yumurtası", "cost": 1000, "profit": 1600, "chance": 50}
        ]
        
        if option < 1 or option > len(trade_options):
            await ctx.send("❌ Geçersiz seçenek! 1-4 arası numara seç.")
            return
        
        trade = trade_options[option - 1]
        gold = alliance[3]
        
        if gold < trade["cost"]:
            await ctx.send(f"❌ Yetersiz altın! {trade['cost']} altın gerekli.")
            return
        
        # Execute trade
        success = random.randint(1, 100) <= trade["chance"]
        
        if success:
            profit = trade["profit"] - trade["cost"]
            db.update_alliance_resources(alliance[0], profit, 0)
            
            embed = create_embed("🎉 TİCARET BAŞARILI!",
                               f"**{trade['item']}** ticareti başarılı!",
                               discord.Color.green())
            embed.add_field(name="Kar", value=f"+{profit} altın", inline=True)
            embed.add_field(name="Yeni Bakiye", value=f"{gold + profit:,} altın", inline=True)
        else:
            db.update_alliance_resources(alliance[0], -trade["cost"], 0)
            
            embed = create_embed("💔 TİCARET BAŞARISIZ",
                               f"**{trade['item']}** ticareti başarısız!",
                               discord.Color.red())
            embed.add_field(name="Kayıp", value=f"-{trade['cost']} altın", inline=True)
            embed.add_field(name="Yeni Bakiye", value=f"{gold - trade['cost']:,} altın", inline=True)
        
        await ctx.send(embed=embed)

    @bot.command(name='kolay_savaş', aliases=['easy_war'])
    async def easy_war(ctx):
        """Simple war declaration system"""
        user_id = ctx.author.id
        alliance = db.get_user_alliance(user_id)
        
        if not alliance:
            embed = create_embed("❌ Hata", "Önce bir haneye katıl! `!hızlı_hane`", discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        # Get other houses
        db.c.execute('SELECT name, soldiers FROM alliances WHERE id != ? AND name NOT IN ("System", "Admin")', (alliance[0],))
        other_houses = db.c.fetchall()
        
        if not other_houses:
            embed = create_embed("😅 Savaş Yok", "Şu anda savaşılabilecek hane yok!", discord.Color.orange())
            await ctx.send(embed=embed)
            return
        
        my_soldiers = alliance[4]
        
        embed = create_embed("⚔️ KOLAY SAVAŞ SİSTEMİ",
                           f"**{alliance[1]}** hanesi savaş seçenekleri:",
                           discord.Color.red())
        
        for i, (house_name, enemy_soldiers) in enumerate(other_houses[:5], 1):
            if my_soldiers > enemy_soldiers * 1.5:
                difficulty = "🟢 Kolay"
                color = "🟢"
            elif my_soldiers > enemy_soldiers:
                difficulty = "🟡 Orta"
                color = "🟡"
            else:
                difficulty = "🔴 Zor"
                color = "🔴"
            
            embed.add_field(
                name=f"{get_house_emoji(house_name)} {house_name}",
                value=f"**Asker:** {enemy_soldiers:,}\n"
                      f"**Zorluk:** {difficulty}\n"
                      f"**Komut:** `!savaş_başlat {house_name}`",
                inline=True
            )
        
        embed.add_field(
            name="💡 İPUCU",
            value="🟢 Kolay = Büyük ihtimalle kazanırsın\n"
                  "🟡 Orta = 50-50 şans\n"
                  "🔴 Zor = Kaybedebilirsin",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @bot.command(name='günlük_görev', aliases=['daily_quest'])
    async def daily_quest(ctx):
        """Simple daily quest system"""
        user_id = ctx.author.id
        alliance = db.get_user_alliance(user_id)
        
        if not alliance:
            embed = create_embed("❌ Hata", "Önce bir haneye katıl! `!hızlı_hane`", discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        # Check if already completed today
        from datetime import datetime, date
        today = date.today().isoformat()
        
        db.c.execute('SELECT last_quest_date FROM user_progress WHERE user_id = ?', (user_id,))
        result = db.c.fetchone()
        
        if result and result[0] == today:
            embed = create_embed("✅ Görev Tamamlandı",
                               "Bugünün görevini zaten tamamladın!\nYarın yeni görev alabilirsin.",
                               discord.Color.blue())
            await ctx.send(embed=embed)
            return
        
        # Random daily quest
        quests = [
            {"task": "Zar oyunu oyna", "command": "!zar 6 2", "reward": 200},
            {"task": "Durumunu kontrol et", "command": "!durum", "reward": 150},
            {"task": "Basit ticaret yap", "command": "!ticaret_kolay", "reward": 300},
            {"task": "İpucu al", "command": "!ipucu", "reward": 100},
            {"task": "Roleplay yap", "command": "!roleplay merhaba der", "reward": 250}
        ]
        
        quest = random.choice(quests)
        
        embed = create_embed("📋 GÜNLÜK GÖREV",
                           "Bugünün basit görevi:",
                           discord.Color.purple())
        
        embed.add_field(name="🎯 Görev", value=quest["task"], inline=False)
        embed.add_field(name="💡 Komut", value=quest["command"], inline=False)
        embed.add_field(name="🎁 Ödül", value=f"{quest['reward']} altın", inline=False)
        embed.add_field(name="✅ Tamamlama", value="`!görev_tamamla` - Komutu çalıştırdıktan sonra", inline=False)
        
        # Store quest in database
        db.c.execute('''
        INSERT OR REPLACE INTO user_progress 
        (user_id, last_quest_date, current_quest_reward)
        VALUES (?, ?, ?)
        ''', (user_id, today, quest["reward"]))
        db.conn.commit()
        
        await ctx.send(embed=embed)

    @bot.command(name='görev_tamamla', aliases=['complete_quest'])
    async def complete_quest(ctx):
        """Complete daily quest"""
        user_id = ctx.author.id
        alliance = db.get_user_alliance(user_id)
        
        if not alliance:
            return
        
        db.c.execute('SELECT current_quest_reward FROM user_progress WHERE user_id = ?', (user_id,))
        result = db.c.fetchone()
        
        if not result or not result[0]:
            await ctx.send("❌ Aktif görevin yok! `!günlük_görev` ile görev al.")
            return
        
        reward = result[0]
        
        # Give reward
        db.update_alliance_resources(alliance[0], reward, 0)
        
        # Clear quest
        db.c.execute('UPDATE user_progress SET current_quest_reward = NULL WHERE user_id = ?', (user_id,))
        db.conn.commit()
        
        embed = create_embed("🎉 GÖREV TAMAMLANDI!",
                           f"Tebrikler! Günlük görevi tamamladın!",
                           discord.Color.green())
        embed.add_field(name="🎁 Ödül", value=f"+{reward} altın", inline=True)
        embed.add_field(name="📅 Sonraki Görev", value="Yarın yeni görev alabilirsin!", inline=True)
        
        await ctx.send(embed=embed)
