import discord
import random
import logging
from datetime import datetime, timedelta
from utils import create_embed, format_number

logger = logging.getLogger(__name__)

class DailyChallengesSystem:
    def __init__(self, database):
        self.db = database
        self.challenges = {
            "war_challenge": {
                "name": "⚔️ Savaşçı Görevi",
                "description": "Bugün bir savaş başlat",
                "reward_gold": 3000,
                "reward_soldiers": 100,
                "difficulty": "Orta"
            },
            "economy_challenge": {
                "name": "💰 Ekonomist Görevi",
                "description": "50 asker satın al",
                "reward_gold": 2000,
                "reward_soldiers": 50,
                "difficulty": "Kolay"
            },
            "trade_challenge": {
                "name": "🛒 Tüccar Görevi",
                "description": "Başka bir haneyle ticaret yap",
                "reward_gold": 4000,
                "reward_soldiers": 75,
                "difficulty": "Orta"
            },
            "social_challenge": {
                "name": "👥 Sosyal Görevi",
                "description": "Bir evlilik teklifi yap",
                "reward_gold": 2500,
                "reward_soldiers": 60,
                "difficulty": "Kolay"
            },
            "tournament_challenge": {
                "name": "🏆 Turnuva Görevi",
                "description": "Bir turnuvaya katıl",
                "reward_gold": 3500,
                "reward_soldiers": 80,
                "difficulty": "Orta"
            },
            "adventure_challenge": {
                "name": "🗺️ Macera Görevi",
                "description": "Özel bir görev tamamla",
                "reward_gold": 5000,
                "reward_soldiers": 150,
                "difficulty": "Zor"
            }
        }
        
        self.setup_challenges_table()
    
    def setup_challenges_table(self):
        """Create daily challenges table"""
        try:
            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS daily_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                challenge_id TEXT NOT NULL,
                assigned_date DATE NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP NULL,
                UNIQUE(user_id, challenge_id, assigned_date)
            )
            ''')
            
            self.db.conn.commit()
            logger.info("Daily challenges table created successfully")
        except Exception as e:
            logger.error(f"Error creating daily challenges table: {e}")
    
    def setup_daily_challenges_commands(self, bot):
        """Setup daily challenges commands"""
        
        @bot.command(name='günlük_görevler')
        async def daily_challenges(ctx):
            """View today's daily challenges"""
            try:
                user_id = ctx.author.id
                today = datetime.now().date()
                
                # Check if user has challenges for today
                self.db.c.execute('''
                SELECT challenge_id, completed FROM daily_challenges 
                WHERE user_id = ? AND assigned_date = ?
                ''', (user_id, today))
                
                existing_challenges = self.db.c.fetchall()
                
                # If no challenges for today, assign new ones
                if not existing_challenges:
                    self.assign_daily_challenges(user_id, today)
                    
                    # Fetch newly assigned challenges
                    self.db.c.execute('''
                    SELECT challenge_id, completed FROM daily_challenges 
                    WHERE user_id = ? AND assigned_date = ?
                    ''', (user_id, today))
                    
                    existing_challenges = self.db.c.fetchall()
                
                embed = create_embed(
                    "📅 GÜNLÜK GÖREVLER",
                    f"🗓️ {today.strftime('%d/%m/%Y')} - {ctx.author.display_name}",
                    discord.Color.blue()
                )
                
                completed_count = 0
                total_rewards_gold = 0
                total_rewards_soldiers = 0
                
                for challenge_id, completed in existing_challenges:
                    if challenge_id in self.challenges:
                        challenge = self.challenges[challenge_id]
                        status = "✅ Tamamlandı" if completed else "⏳ Devam Ediyor"
                        
                        if completed:
                            completed_count += 1
                        else:
                            total_rewards_gold += challenge['reward_gold']
                            total_rewards_soldiers += challenge['reward_soldiers']
                        
                        difficulty_icon = "🟢" if challenge['difficulty'] == "Kolay" else "🟡" if challenge['difficulty'] == "Orta" else "🔴"
                        
                        embed.add_field(
                            name=f"{difficulty_icon} {challenge['name']}",
                            value=f"📋 {challenge['description']}\n"
                                  f"💰 Ödül: {format_number(challenge['reward_gold'])} altın, {format_number(challenge['reward_soldiers'])} asker\n"
                                  f"📊 {status}",
                            inline=False
                        )
                
                # Progress bar
                progress = completed_count / len(existing_challenges) if existing_challenges else 0
                progress_bar = "🟩" * int(progress * 10) + "⬜" * (10 - int(progress * 10))
                
                embed.add_field(
                    name="📊 İlerleme",
                    value=f"{progress_bar}\n{completed_count}/{len(existing_challenges)} tamamlandı",
                    inline=False
                )
                
                if total_rewards_gold > 0:
                    embed.add_field(
                        name="🎁 Kalan Ödüller",
                        value=f"💰 {format_number(total_rewards_gold)} altın\n⚔️ {format_number(total_rewards_soldiers)} asker",
                        inline=True
                    )
                
                embed.set_footer(text="💡 Görevleri tamamlayarak ödüller kazan! Günlük saat 00:00'da yenilenir.")
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Daily challenges error: {e}")
                embed = create_embed("❌ Hata", f"Günlük görevler hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='görev_bitir')
        async def complete_challenge(ctx, *, challenge_name: str = ""):
            """Manually complete a daily challenge (for testing)"""
            try:
                if not challenge_name:
                    embed = create_embed("❌ Hata", "Tamamlamak istediğin görev adını belirt!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                user_id = ctx.author.id
                today = datetime.now().date()
                
                # Find challenge by name
                challenge_id = None
                for cid, challenge in self.challenges.items():
                    if challenge_name.lower() in challenge['name'].lower():
                        challenge_id = cid
                        break
                
                if not challenge_id:
                    embed = create_embed("❌ Hata", "Bu isimde bir görev bulunamadı!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                # Check if challenge exists and is not completed
                self.db.c.execute('''
                SELECT completed FROM daily_challenges 
                WHERE user_id = ? AND challenge_id = ? AND assigned_date = ?
                ''', (user_id, challenge_id, today))
                
                result = self.db.c.fetchone()
                
                if not result:
                    embed = create_embed("❌ Hata", "Bu görev bugün sana atanmamış!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                if result[0]:  # already completed
                    embed = create_embed("❌ Hata", "Bu görev zaten tamamlanmış!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                # Complete the challenge
                await self.complete_daily_challenge(user_id, challenge_id, ctx)
                
            except Exception as e:
                logger.error(f"Complete challenge error: {e}")
                embed = create_embed("❌ Hata", f"Görev tamamlama hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='günlük_sıralama')
        async def daily_leaderboard(ctx):
            """View daily challenges leaderboard"""
            try:
                today = datetime.now().date()
                
                self.db.c.execute('''
                SELECT user_id, COUNT(*) as completed_count
                FROM daily_challenges 
                WHERE assigned_date = ? AND completed = TRUE
                GROUP BY user_id 
                ORDER BY completed_count DESC 
                LIMIT 10
                ''', (today,))
                
                leaderboard = self.db.c.fetchall()
                
                embed = create_embed(
                    "🏆 GÜNLÜK GÖREV SIRALAMASI",
                    f"📅 {today.strftime('%d/%m/%Y')} - Bugünün en aktif oyuncuları",
                    discord.Color.gold()
                )
                
                if leaderboard:
                    leaderboard_text = ""
                    for i, (user_id, count) in enumerate(leaderboard, 1):
                        try:
                            user = bot.get_user(user_id)
                            username = user.display_name if user else f"User #{user_id}"
                            
                            if i == 1:
                                leaderboard_text += f"👑 **{username}** - {count} görev\n"
                            elif i == 2:
                                leaderboard_text += f"🥈 **{username}** - {count} görev\n"
                            elif i == 3:
                                leaderboard_text += f"🥉 **{username}** - {count} görev\n"
                            else:
                                leaderboard_text += f"{i}. **{username}** - {count} görev\n"
                        except:
                            continue
                    
                    embed.add_field(name="🏆 Bugünün En İyileri", value=leaderboard_text, inline=False)
                else:
                    embed.add_field(name="📝 Sonuç", value="Bugün henüz kimse görev tamamlamamış!", inline=False)
                
                embed.set_footer(text="💪 Sen de görevleri tamamlayarak sıralamaya gir!")
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Daily leaderboard error: {e}")
                embed = create_embed("❌ Hata", f"Sıralama hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
    
    def assign_daily_challenges(self, user_id, date):
        """Assign random daily challenges to user"""
        try:
            # Select 3 random challenges
            challenge_ids = random.sample(list(self.challenges.keys()), 3)
            
            for challenge_id in challenge_ids:
                self.db.c.execute('''
                INSERT OR IGNORE INTO daily_challenges (user_id, challenge_id, assigned_date)
                VALUES (?, ?, ?)
                ''', (user_id, challenge_id, date))
            
            self.db.conn.commit()
            logger.info(f"Assigned daily challenges to user {user_id}")
            
        except Exception as e:
            logger.error(f"Assign daily challenges error: {e}")
    
    async def complete_daily_challenge(self, user_id, challenge_id, ctx=None):
        """Complete a daily challenge and give rewards"""
        try:
            today = datetime.now().date()
            
            # Mark as completed
            self.db.c.execute('''
            UPDATE daily_challenges 
            SET completed = TRUE, completed_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND challenge_id = ? AND assigned_date = ?
            ''', (user_id, challenge_id, today))
            
            if self.db.c.rowcount == 0:
                return False  # Challenge not found or already completed
            
            challenge = self.challenges[challenge_id]
            
            # Give rewards
            alliance = self.db.get_user_alliance(user_id)
            if alliance:
                alliance_id = alliance[0]
                self.db.update_alliance_resources(alliance_id, 
                                                challenge['reward_gold'], 
                                                challenge['reward_soldiers'])
            
            self.db.conn.commit()
            
            # Notify user if context available
            if ctx:
                embed = create_embed(
                    "✅ GÖREV TAMAMLANDI!",
                    f"🎯 **{challenge['name']}**",
                    discord.Color.green()
                )
                embed.add_field(name="📋 Görev", value=challenge['description'], inline=False)
                embed.add_field(name="🎁 Ödüller", 
                              value=f"💰 {format_number(challenge['reward_gold'])} altın\n⚔️ {format_number(challenge['reward_soldiers'])} asker", 
                              inline=False)
                embed.add_field(name="🌟 Tebrikler!", value="Günlük görevinde başarılı oldun!", inline=False)
                await ctx.send(embed=embed)
            
            return True
            
        except Exception as e:
            logger.error(f"Complete challenge error: {e}")
            return False

logger.info("Daily challenges system initialized successfully")