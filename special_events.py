import discord
import random
import asyncio
import logging
from datetime import datetime, timedelta
from utils import create_embed, format_number, get_house_emoji

logger = logging.getLogger(__name__)

class SpecialEventsSystem:
    def __init__(self, database):
        self.db = database
        self.active_events = {}

    def setup_special_events(self, bot):
        """Setup all special event commands"""

        @bot.command(name='ejder_avı')
        async def dragon_hunt(ctx):
            """Efsanevi ejder avı! Büyük ödüller veya büyük riskler"""
            try:
                user_id = ctx.author.id
                alliance = self.db.get_user_alliance(user_id)

                if not alliance:
                    embed = create_embed("❌ Hata", "Ejder avına çıkmak için bir haneye ait olmalısın!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return

                alliance_id = alliance[0]
                alliance_data = self.db.get_alliance_by_id(alliance_id)

                if alliance_data[4] < 500:  # soldiers
                    embed = create_embed("⚔️ Yetersiz Güç", "Ejder avı için en az 500 askerin olmalı!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return

                if alliance_data[3] < 1000:  # gold
                    embed = create_embed("💰 Yetersiz Altın", "Ejder avı için 1000 altın gerekli!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return

                # Dragon hunt mechanics
                hunt_success = random.randint(1, 100)

                # Deduct costs
                self.db.update_alliance_resources(alliance_id, -1000, -100)

                if hunt_success <= 15:  # 15% chance - HUGE SUCCESS
                    reward_gold = random.randint(10000, 25000)
                    reward_soldiers = random.randint(200, 500)
                    dragon_name = random.choice(["Balerion", "Vhagar", "Meraxes", "Syrax", "Caraxes"])

                    self.db.update_alliance_resources(alliance_id, reward_gold, reward_soldiers)

                    embed = create_embed("🐉 EFSANE BAŞARI!",
                                       f"🔥 {dragon_name} ejderini alt ettin!",
                                       discord.Color.from_rgb(255, 0, 0))
                    embed.add_field(name="💰 Ödül", value=f"{format_number(reward_gold)} altın", inline=True)
                    embed.add_field(name="⚔️ Bonus", value=f"{format_number(reward_soldiers)} asker", inline=True)
                    embed.add_field(name="👑 Prestij", value="LEGENDARY STATUS!", inline=False)
                    embed.set_thumbnail(url="https://i.imgur.com/dragon.png")

                elif hunt_success <= 40:  # 25% chance - SUCCESS
                    reward_gold = random.randint(3000, 8000)
                    reward_soldiers = random.randint(50, 150)

                    self.db.update_alliance_resources(alliance_id, reward_gold, reward_soldiers)

                    embed = create_embed("🐲 Başarılı Av!",
                                       "Genç bir ejderi yakaladın!",
                                       discord.Color.orange())
                    embed.add_field(name="💰 Ödül", value=f"{format_number(reward_gold)} altın", inline=True)
                    embed.add_field(name="⚔️ Bonus", value=f"{format_number(reward_soldiers)} asker", inline=True)

                elif hunt_success <= 70:  # 30% chance - PARTIAL SUCCESS
                    reward_gold = random.randint(500, 2000)

                    self.db.update_alliance_resources(alliance_id, reward_gold, 0)

                    embed = create_embed("🔥 Kısmi Başarı",
                                       "Ejder izlerini buldun ve hazineler keşfettin!",
                                       discord.Color.gold())
                    embed.add_field(name="💰 Ödül", value=f"{format_number(reward_gold)} altın", inline=True)

                else:  # 30% chance - FAILURE
                    loss_soldiers = random.randint(50, 200)

                    self.db.update_alliance_resources(alliance_id, 0, -loss_soldiers)

                    embed = create_embed("💀 Felaket!",
                                       "Ejder saldırısında askerler kaybettin!",
                                       discord.Color.dark_red())
                    embed.add_field(name="💀 Kayıp", value=f"{format_number(loss_soldiers)} asker", inline=True)
                    embed.add_field(name="🔥 Sonuç", value="Ejder kaçtı!", inline=True)

                await ctx.send(embed=embed)

            except Exception as e:
                logger.error(f"Dragon hunt error: {e}")
                embed = create_embed("❌ Hata", f"Ejder avı hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)

        @bot.command(name='gizli_görev')
        async def secret_mission(ctx):
            """Gizli istihbarat görevi - büyük riskler, büyük ödüller"""
            try:
                user_id = ctx.author.id
                alliance = self.db.get_user_alliance(user_id)

                if not alliance:
                    embed = create_embed("❌ Hata", "Gizli görev için bir haneye ait olmalısın!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return

                alliance_id = alliance[0]
                alliance_data = self.db.get_alliance_by_id(alliance_id)

                if alliance_data[3] < 2000:  # gold
                    embed = create_embed("💰 Yetersiz Altın", "Gizli görev için 2000 altın gerekli!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return

                # Mission types
                missions = [
                    {
                        "name": "🕵️ King's Landing Casusluğu",
                        "description": "Iron Throne'un sırlarını öğren",
                        "success_rate": 60,
                        "reward": (5000, 15000),
                        "punishment": (1000, 3000)
                    },
                    {
                        "name": "🏴‍☠️ Braavos Bankası Soygunu",
                        "description": "Iron Bank'tan gizlice altın al",
                        "success_rate": 30,
                        "reward": (15000, 40000),
                        "punishment": (3000, 8000)
                    },
                    {
                        "name": "📜 Citadel Gizli Bilgileri",
                        "description": "Oldtown'dan gizli bilgileri çal",
                        "success_rate": 70,
                        "reward": (3000, 8000),
                        "punishment": (500, 2000)
                    },
                    {
                        "name": "⚔️ Düşman Hane Sabotajı",
                        "description": "Rakip hanenin planlarını boz",
                        "success_rate": 50,
                        "reward": (8000, 20000),
                        "punishment": (2000, 5000)
                    }
                ]

                mission = random.choice(missions)
                success = random.randint(1, 100) <= mission["success_rate"]

                # Deduct mission cost
                self.db.update_alliance_resources(alliance_id, -2000, 0)

                if success:
                    reward = random.randint(mission["reward"][0], mission["reward"][1])
                    self.db.update_alliance_resources(alliance_id, reward, 0)

                    embed = create_embed("🎯 GÖREV BAŞARILI!",
                                       mission["name"],
                                       discord.Color.green())
                    embed.add_field(name="📋 Görev", value=mission["description"], inline=False)
                    embed.add_field(name="💰 Ödül", value=f"{format_number(reward)} altın", inline=True)
                    embed.add_field(name="🎖️ Statü", value="Gizli Operasyon Uzmanı", inline=True)
                else:
                    punishment = random.randint(mission["punishment"][0], mission["punishment"][1])
                    self.db.update_alliance_resources(alliance_id, -punishment, 0)

                    embed = create_embed("💀 GÖREV BAŞARISIZ!",
                                       mission["name"],
                                       discord.Color.red())
                    embed.add_field(name="📋 Görev", value=mission["description"], inline=False)
                    embed.add_field(name="💸 Ceza", value=f"{format_number(punishment)} altın kaybı", inline=True)
                    embed.add_field(name="⚠️ Sonuç", value="Yakalandın!", inline=True)

                await ctx.send(embed=embed)

            except Exception as e:
                logger.error(f"Secret mission error: {e}")
                embed = create_embed("❌ Hata", f"Gizli görev hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)

        @bot.command(name='büyü_ritüeli')
        async def magic_ritual(ctx):
            """Red Priestess büyü ritüeli - mistik güçler"""
            try:
                user_id = ctx.author.id
                alliance = self.db.get_user_alliance(user_id)

                if not alliance:
                    embed = create_embed("❌ Hata", "Büyü ritüeli için bir haneye ait olmalısın!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return

                alliance_id = alliance[0]
                alliance_data = self.db.get_alliance_by_id(alliance_id)

                if alliance_data[3] < 1500:  # gold
                    embed = create_embed("💰 Yetersiz Altın", "Büyü ritüeli için 1500 altın gerekli!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return

                # Magic ritual types
                rituals = [
                    "🔥 Lord of Light Blessing",
                    "❄️ Old Gods Protection",
                    "🌙 Faceless God Ritual",
                    "⚡ Storm God Power",
                    "🌊 Drowned God Blessing"
                ]

                ritual_name = random.choice(rituals)
                outcome = random.randint(1, 100)

                # Deduct ritual cost
                self.db.update_alliance_resources(alliance_id, -1500, 0)

                if outcome <= 20:  # 20% - DIVINE BLESSING
                    gold_bonus = random.randint(8000, 20000)
                    soldier_bonus = random.randint(100, 300)

                    self.db.update_alliance_resources(alliance_id, gold_bonus, soldier_bonus)

                    embed = create_embed("✨ İLAHİ BEREKET!",
                                       f"{ritual_name} başarılı!",
                                       discord.Color.from_rgb(255, 215, 0))
                    embed.add_field(name="🙏 Ritüel", value=ritual_name, inline=False)
                    embed.add_field(name="💰 Bereket", value=f"{format_number(gold_bonus)} altın", inline=True)
                    embed.add_field(name="⚔️ Güç", value=f"{format_number(soldier_bonus)} asker", inline=True)
                    embed.add_field(name="🌟 Durum", value="Tanrılar senin yanında!", inline=False)

                elif outcome <= 50:  # 30% - MINOR BLESSING
                    gold_bonus = random.randint(2000, 6000)

                    self.db.update_alliance_resources(alliance_id, gold_bonus, 0)

                    embed = create_embed("🌟 Küçük Bereket",
                                       f"{ritual_name} kısmen başarılı!",
                                       discord.Color.blue())
                    embed.add_field(name="💰 Bereket", value=f"{format_number(gold_bonus)} altın", inline=True)

                elif outcome <= 80:  # 30% - NO EFFECT
                    embed = create_embed("🌫️ Belirsizlik",
                                       f"{ritual_name} etkisiz kaldı!",
                                       discord.Color.light_grey())
                    embed.add_field(name="🤷 Sonuç", value="Tanrılar sessiz kaldı", inline=False)

                else:  # 20% - CURSE
                    gold_loss = random.randint(1000, 3000)
                    soldier_loss = random.randint(20, 100)

                    self.db.update_alliance_resources(alliance_id, -gold_loss, -soldier_loss)

                    embed = create_embed("🌑 LANETLENDİN!",
                                       f"{ritual_name} ters gitti!",
                                       discord.Color.dark_red())
                    embed.add_field(name="💸 Kayıp", value=f"{format_number(gold_loss)} altın", inline=True)
                    embed.add_field(name="💀 Kayıp", value=f"{format_number(soldier_loss)} asker", inline=True)
                    embed.add_field(name="😈 Lanet", value="Kötü ruhlar seni takip ediyor!", inline=False)

                await ctx.send(embed=embed)

            except Exception as e:
                logger.error(f"Magic ritual error: {e}")
                embed = create_embed("❌ Hata", f"Büyü ritüeli hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)

        # The original code had a duplicate command definition for 'görev_tamamla'.
        # This has been corrected by renaming one of them to 'özel_görev_tamamla'
        # to resolve the command conflict.
        @bot.command(name='özel_görev_tamamla')
        async def complete_task(ctx):
             """Özel bir görevi tamamla"""
             try:
                 user_id = ctx.author.id
                 alliance = self.db.get_user_alliance(user_id)

                 if not alliance:
                     embed = create_embed("❌ Hata", "Bu görevi tamamlamak için bir haneye ait olmalısın!", discord.Color.red())
                     await ctx.send(embed=embed)
                     return

                 alliance_id = alliance[0]
                 alliance_data = self.db.get_alliance_by_id(alliance_id)

                 # Sample task completion logic (replace with actual task logic)
                 task_reward_gold = random.randint(100, 500)
                 task_reward_soldiers = random.randint(10, 50)

                 self.db.update_alliance_resources(alliance_id, task_reward_gold, task_reward_soldiers)

                 embed = create_embed("✅ Görev Tamamlandı!",
                                    "Başarıyla bir özel görevi tamamladın!",
                                    discord.Color.green())
                 embed.add_field(name="💰 Ödül", value=f"{format_number(task_reward_gold)} altın", inline=True)
                 embed.add_field(name="⚔️ Bonus", value=f"{format_number(task_reward_soldiers)} asker", inline=True)

                 await ctx.send(embed=embed)

             except Exception as e:
                 logger.error(f"Task completion error: {e}")
                 embed = create_embed("❌ Hata", f"Görev tamamlama hatası: {str(e)}", discord.Color.red())
                 await ctx.send(embed=embed)


        logger.info("Special events system initialized successfully")