import discord
import logging
from datetime import datetime
from typing import Optional
from utils import create_embed, format_number

logger = logging.getLogger(__name__)

class AchievementsSystem:
    def __init__(self, database):
        self.db = database
        self.achievements = {
            # WAR ACHIEVEMENTS
            "first_war": {
                "name": "🗡️ İlk Kan",
                "description": "İlk savaşını başlat",
                "reward_gold": 1000,
                "reward_soldiers": 50,
                "icon": "⚔️"
            },
            "war_master": {
                "name": "🏆 Savaş Ustası", 
                "description": "10 savaş kazan",
                "reward_gold": 10000,
                "reward_soldiers": 500,
                "icon": "👑"
            },
            "conqueror": {
                "name": "🌍 Fatih",
                "description": "Bir haneyi tamamen yok et",
                "reward_gold": 25000,
                "reward_soldiers": 1000,
                "icon": "🔥"
            },
            
            # ECONOMIC ACHIEVEMENTS
            "first_gold": {
                "name": "💰 İlk Servet",
                "description": "10,000 altın biriktir",
                "reward_gold": 5000,
                "reward_soldiers": 100,
                "icon": "💎"
            },
            "millionaire": {
                "name": "💸 Milyoner",
                "description": "1,000,000 altın biriktir",
                "reward_gold": 100000,
                "reward_soldiers": 2000,
                "icon": "👑"
            },
            "debt_master": {
                "name": "🏦 Borç Kralı",
                "description": "100,000 altın borç ver",
                "reward_gold": 20000,
                "reward_soldiers": 300,
                "icon": "📈"
            },
            
            # SOCIAL ACHIEVEMENTS
            "marriage_master": {
                "name": "💒 Evlilik Ustası",
                "description": "5 evlilik düzenle",
                "reward_gold": 15000,
                "reward_soldiers": 200,
                "icon": "💍"
            },
            "diplomat": {
                "name": "🤝 Diplomat",
                "description": "10 ittifak kur",
                "reward_gold": 12000,
                "reward_soldiers": 300,
                "icon": "🕊️"
            },
            
            # TOURNAMENT ACHIEVEMENTS
            "tournament_champion": {
                "name": "🏆 Turnuva Şampiyonu",
                "description": "5 turnuva kazan",
                "reward_gold": 8000,
                "reward_soldiers": 150,
                "icon": "🎖️"
            },
            "duel_master": {
                "name": "⚔️ Düello Ustası",
                "description": "20 düello kazan",
                "reward_gold": 15000,
                "reward_soldiers": 400,
                "icon": "🥇"
            },
            
            # SPECIAL ACHIEVEMENTS
            "dragon_slayer": {
                "name": "🐲 Ejder Avcısı",
                "description": "Efsanevi ejder avı başar",
                "reward_gold": 50000,
                "reward_soldiers": 1500,
                "icon": "🔥"
            },
            "secret_agent": {
                "name": "🕵️ Gizli Ajan",
                "description": "10 gizli görev başar",
                "reward_gold": 30000,
                "reward_soldiers": 800,
                "icon": "🎭"
            },
            "magic_user": {
                "name": "🔮 Büyücü",
                "description": "5 büyü ritüeli yap",
                "reward_gold": 20000,
                "reward_soldiers": 500,
                "icon": "✨"
            }
        }
        
        # Create achievements table if not exists
        self.setup_achievements_table()
    
    def setup_achievements_table(self):
        """Create achievements table in database"""
        try:
            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_id TEXT NOT NULL,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, achievement_id)
            )
            ''')
            
            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS achievement_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_type TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                UNIQUE(user_id, achievement_type)
            )
            ''')
            
            self.db.conn.commit()
            logger.info("Achievements tables created successfully")
        except Exception as e:
            logger.error(f"Error creating achievements tables: {e}")
    
    def setup_achievement_commands(self, bot):
        """Setup achievement-related commands"""
        
        @bot.command(name='başarılar')
        async def view_achievements(ctx, member: Optional[discord.Member] = None):
            """View user achievements"""
            try:
                target = member or ctx.author
                user_id = target.id
                
                # Get user's achievements
                self.db.c.execute('''
                SELECT achievement_id, unlocked_at FROM achievements 
                WHERE user_id = ? ORDER BY unlocked_at DESC
                ''', (user_id,))
                
                user_achievements = self.db.c.fetchall()
                
                embed = create_embed(
                    f"🏆 {target.display_name} - Başarılar",
                    f"Toplam başarı: {len(user_achievements)}/{len(self.achievements)}",
                    discord.Color.gold()
                )
                
                if user_achievements:
                    unlocked_text = ""
                    for ach_id, unlocked_at in user_achievements:
                        if ach_id in self.achievements:
                            achievement = self.achievements[ach_id]
                            unlocked_text += f"{achievement['icon']} **{achievement['name']}**\n"
                            unlocked_text += f"   └ {achievement['description']}\n\n"
                    
                    embed.add_field(name="✅ Kazanılan Başarılar", value=unlocked_text[:1000], inline=False)
                
                # Show some locked achievements
                locked_achievements = []
                for ach_id, achievement in self.achievements.items():
                    if not any(ua[0] == ach_id for ua in user_achievements):
                        locked_achievements.append(f"🔒 {achievement['name']}")
                
                if locked_achievements:
                    embed.add_field(name="🔒 Kilitli Başarılar", 
                                  value="\n".join(locked_achievements[:5]), inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"View achievements error: {e}")
                embed = create_embed("❌ Hata", f"Başarılar görüntülenirken hata: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='başarı_sıralaması')
        async def achievement_leaderboard(ctx):
            """View achievement leaderboard"""
            try:
                self.db.c.execute('''
                SELECT user_id, COUNT(*) as achievement_count 
                FROM achievements 
                GROUP BY user_id 
                ORDER BY achievement_count DESC 
                LIMIT 10
                ''')
                
                leaderboard = self.db.c.fetchall()
                
                embed = create_embed(
                    "🏆 BAŞARI SIRALAMASI",
                    "En çok başarıya sahip oyuncular",
                    discord.Color.gold()
                )
                
                leaderboard_text = ""
                for i, (user_id, count) in enumerate(leaderboard, 1):
                    try:
                        user = bot.get_user(user_id)
                        username = user.display_name if user else f"User #{user_id}"
                        
                        if i == 1:
                            leaderboard_text += f"👑 **{username}** - {count} başarı\n"
                        elif i == 2:
                            leaderboard_text += f"🥈 **{username}** - {count} başarı\n"
                        elif i == 3:
                            leaderboard_text += f"🥉 **{username}** - {count} başarı\n"
                        else:
                            leaderboard_text += f"{i}. **{username}** - {count} başarı\n"
                    except:
                        continue
                
                embed.add_field(name="🏆 En İyiler", value=leaderboard_text or "Henüz başarı yok!", inline=False)
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Achievement leaderboard error: {e}")
                embed = create_embed("❌ Hata", f"Sıralama hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
    
    async def check_and_award_achievement(self, user_id, achievement_id, ctx=None):
        """Check and award achievement to user"""
        try:
            # Check if user already has this achievement
            self.db.c.execute('SELECT id FROM achievements WHERE user_id = ? AND achievement_id = ?', 
                            (user_id, achievement_id))
            
            if self.db.c.fetchone():
                return False  # Already has achievement
            
            if achievement_id not in self.achievements:
                return False  # Invalid achievement
            
            # Award achievement
            self.db.c.execute('''
            INSERT INTO achievements (user_id, achievement_id) 
            VALUES (?, ?)
            ''', (user_id, achievement_id))
            
            achievement = self.achievements[achievement_id]
            
            # Give rewards
            alliance = self.db.get_user_alliance(user_id)
            if alliance:
                alliance_id = alliance[0]
                self.db.update_alliance_resources(alliance_id, 
                                                achievement['reward_gold'], 
                                                achievement['reward_soldiers'])
            
            self.db.conn.commit()
            
            # Notify user if context available
            if ctx:
                embed = create_embed(
                    "🎉 BAŞARI KAZANILDI!",
                    f"{achievement['icon']} **{achievement['name']}**",
                    discord.Color.gold()
                )
                embed.add_field(name="📋 Açıklama", value=achievement['description'], inline=False)
                embed.add_field(name="🎁 Ödüller", 
                              value=f"💰 {format_number(achievement['reward_gold'])} altın\n⚔️ {format_number(achievement['reward_soldiers'])} asker", 
                              inline=False)
                await ctx.send(embed=embed)
            
            return True
            
        except Exception as e:
            logger.error(f"Award achievement error: {e}")
            return False
    
    def increment_progress(self, user_id, progress_type, amount=1):
        """Increment user's progress for specific achievement type"""
        try:
            self.db.c.execute('''
            INSERT OR REPLACE INTO achievement_progress (user_id, achievement_type, progress)
            VALUES (?, ?, COALESCE((SELECT progress FROM achievement_progress WHERE user_id = ? AND achievement_type = ?), 0) + ?)
            ''', (user_id, progress_type, user_id, progress_type, amount))
            
            self.db.conn.commit()
            
        except Exception as e:
            logger.error(f"Increment progress error: {e}")

logger.info("Achievements system initialized successfully")