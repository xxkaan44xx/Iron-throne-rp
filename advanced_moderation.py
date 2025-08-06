import discord
from discord.ext import commands
import logging
from datetime import datetime, timedelta
from utils import create_embed, format_number

logger = logging.getLogger(__name__)

class AdvancedModerationSystem:
    def __init__(self, database):
        self.db = database
        self.setup_moderation_tables()
    
    def setup_moderation_tables(self):
        """Create advanced moderation tables"""
        try:
            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS user_infractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                infraction_type TEXT NOT NULL,
                reason TEXT,
                moderator_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NULL,
                active BOOLEAN DEFAULT TRUE
            )
            ''')
            
            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS moderation_config (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER,
                mute_role_id INTEGER,
                auto_mod_enabled BOOLEAN DEFAULT TRUE,
                warn_threshold INTEGER DEFAULT 3,
                auto_ban_enabled BOOLEAN DEFAULT FALSE
            )
            ''')
            
            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER UNIQUE,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP NULL
            )
            ''')
            
            self.db.conn.commit()
            logger.info("Advanced moderation tables created successfully")
        except Exception as e:
            logger.error(f"Error creating moderation tables: {e}")
    
    def setup_moderation_commands(self, bot):
        """Setup advanced moderation commands"""
        
        @bot.command(name='gelişmiş_uyarı')
        @commands.has_permissions(moderate_members=True)
        async def advanced_warn(ctx, member: discord.Member, *, reason: str = "Sebep belirtilmemiş"):
            """Gelişmiş uyarı sistemi - otomatik takip"""
            try:
                # Add infraction
                self.db.c.execute('''
                INSERT INTO user_infractions (user_id, guild_id, infraction_type, reason, moderator_id)
                VALUES (?, ?, 'warn', ?, ?)
                ''', (member.id, ctx.guild.id, reason, ctx.author.id))
                
                # Count total warnings
                self.db.c.execute('''
                SELECT COUNT(*) FROM user_infractions 
                WHERE user_id = ? AND guild_id = ? AND infraction_type = 'warn' AND active = TRUE
                ''', (member.id, ctx.guild.id))
                
                warning_count = self.db.c.fetchone()[0]
                self.db.conn.commit()
                
                embed = create_embed(
                    "⚠️ UYARI VERİLDİ",
                    f"{member.mention} kullanıcısına uyarı verildi",
                    discord.Color.orange()
                )
                
                embed.add_field(name="👤 Kullanıcı", value=member.display_name, inline=True)
                embed.add_field(name="👮 Moderatör", value=ctx.author.display_name, inline=True)
                embed.add_field(name="📊 Toplam Uyarı", value=f"{warning_count}/3", inline=True)
                embed.add_field(name="📝 Sebep", value=reason, inline=False)
                
                # Auto-moderation based on warning count
                if warning_count >= 3:
                    # Auto-mute for 1 hour
                    mute_until = datetime.now() + timedelta(hours=1)
                    
                    self.db.c.execute('''
                    INSERT INTO user_infractions (user_id, guild_id, infraction_type, reason, moderator_id, expires_at)
                    VALUES (?, ?, 'mute', 'Otomatik susturma - 3 uyarı', ?, ?)
                    ''', (member.id, ctx.guild.id, bot.user.id, mute_until))
                    
                    try:
                        await member.timeout(mute_until, reason="3 uyarı - otomatik susturma")
                        embed.add_field(name="🔇 Otomatik İşlem", value="1 saat susturuldu (3 uyarı)", inline=False)
                    except discord.Forbidden:
                        embed.add_field(name="❌ Hata", value="Susturma yetkisi yok", inline=False)
                
                await ctx.send(embed=embed)
                
                # DM user
                try:
                    dm_embed = create_embed(
                        f"⚠️ {ctx.guild.name} - Uyarı",
                        f"Size bir uyarı verildi",
                        discord.Color.orange()
                    )
                    dm_embed.add_field(name="📝 Sebep", value=reason, inline=False)
                    dm_embed.add_field(name="📊 Toplam Uyarı", value=f"{warning_count}/3", inline=True)
                    await member.send(embed=dm_embed)
                except:
                    pass  # User has DMs disabled
                
            except Exception as e:
                logger.error(f"Advanced warn error: {e}")
                embed = create_embed("❌ Hata", f"Uyarı hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='sil_toplu')
        @commands.has_permissions(manage_messages=True)
        async def bulk_delete(ctx, amount: int, member: discord.Member = None):
            """Toplu mesaj silme - opsiyonel kullanıcı filtresi"""
            try:
                if amount > 100:
                    embed = create_embed("❌ Hata", "En fazla 100 mesaj silebilirsin!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                if member:
                    # Delete messages from specific user
                    def check(m):
                        return m.author == member
                    
                    deleted = await ctx.channel.purge(limit=amount*3, check=check)  # Check more messages to find target user's messages
                    deleted = deleted[:amount]  # Limit to requested amount
                else:
                    # Delete recent messages
                    deleted = await ctx.channel.purge(limit=amount)
                
                embed = create_embed(
                    "🗑️ MESAJLAR SİLİNDİ",
                    f"{len(deleted)} mesaj başarıyla silindi",
                    discord.Color.green()
                )
                
                embed.add_field(name="📊 Miktar", value=len(deleted), inline=True)
                embed.add_field(name="📍 Kanal", value=ctx.channel.mention, inline=True)
                
                if member:
                    embed.add_field(name="👤 Kullanıcı", value=member.display_name, inline=True)
                
                embed.add_field(name="👮 Moderatör", value=ctx.author.display_name, inline=True)
                
                # Send temporary message
                temp_msg = await ctx.send(embed=embed)
                await temp_msg.delete(delay=5)  # Auto-delete after 5 seconds
                
            except Exception as e:
                logger.error(f"Bulk delete error: {e}")
                embed = create_embed("❌ Hata", f"Silme hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='kullanıcı_bilgi')
        @commands.has_permissions(moderate_members=True)
        async def user_info(ctx, member: discord.Member):
            """Detaylı kullanıcı bilgileri ve ihlal geçmişi"""
            try:
                # Get user infractions
                self.db.c.execute('''
                SELECT infraction_type, reason, created_at FROM user_infractions
                WHERE user_id = ? AND guild_id = ? AND active = TRUE
                ORDER BY created_at DESC
                LIMIT 5
                ''', (member.id, ctx.guild.id))
                
                infractions = self.db.c.fetchall()
                
                embed = create_embed(
                    f"👤 {member.display_name} - Kullanıcı Bilgisi",
                    f"Detaylı profil ve moderasyon geçmişi",
                    discord.Color.blue()
                )
                
                # Basic info
                embed.add_field(name="🆔 ID", value=member.id, inline=True)
                embed.add_field(name="📅 Hesap Oluşturma", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
                embed.add_field(name="📅 Sunucuya Katılma", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "Bilinmiyor", inline=True)
                
                # Role info
                roles = [role.name for role in member.roles[1:]]  # Skip @everyone
                embed.add_field(name="🎭 Roller", value=", ".join(roles) if roles else "Rol yok", inline=False)
                
                # Permissions
                perms = []
                if member.guild_permissions.administrator:
                    perms.append("🔴 Yönetici")
                if member.guild_permissions.moderate_members:
                    perms.append("🟡 Moderatör")
                if member.guild_permissions.manage_messages:
                    perms.append("🟢 Mesaj Yönetimi")
                
                embed.add_field(name="🛡️ Yetkiler", value=", ".join(perms) if perms else "Özel yetki yok", inline=False)
                
                # Infraction history
                if infractions:
                    infraction_text = ""
                    warn_count = sum(1 for inf in infractions if inf[0] == 'warn')
                    mute_count = sum(1 for inf in infractions if inf[0] == 'mute')
                    
                    infraction_text += f"⚠️ Uyarı: {warn_count}\n🔇 Susturma: {mute_count}\n\n"
                    
                    infraction_text += "**Son İhlaller:**\n"
                    for inf_type, reason, date in infractions[:3]:
                        date_str = datetime.fromisoformat(date).strftime("%d/%m %H:%M")
                        emoji = "⚠️" if inf_type == "warn" else "🔇" if inf_type == "mute" else "🚫"
                        infraction_text += f"{emoji} {date_str}: {reason[:50]}...\n"
                    
                    embed.add_field(name="📋 İhlal Geçmişi", value=infraction_text, inline=False)
                else:
                    embed.add_field(name="✅ İhlal Geçmişi", value="Temiz kayıt! Hiç ihlal yok.", inline=False)
                
                # Status indicators
                status_indicators = []
                if warn_count >= 2:
                    status_indicators.append("🟡 Uyarı Sınırında")
                if mute_count > 0:
                    status_indicators.append("🔇 Susturma Geçmişi")
                if not infractions:
                    status_indicators.append("✅ Temiz Kayıt")
                
                embed.add_field(name="🚦 Durum", value=", ".join(status_indicators), inline=False)
                
                embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"User info error: {e}")
                embed = create_embed("❌ Hata", f"Kullanıcı bilgi hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='mod_istatistik')
        @commands.has_permissions(moderate_members=True)
        async def mod_stats(ctx):
            """Sunucu moderasyon istatistikleri"""
            try:
                # Get stats from last 30 days
                thirty_days_ago = datetime.now() - timedelta(days=30)
                
                self.db.c.execute('''
                SELECT infraction_type, COUNT(*) FROM user_infractions
                WHERE guild_id = ? AND created_at > ?
                GROUP BY infraction_type
                ''', (ctx.guild.id, thirty_days_ago))
                
                stats = dict(self.db.c.fetchall())
                
                # Get most warned users
                self.db.c.execute('''
                SELECT user_id, COUNT(*) as count FROM user_infractions
                WHERE guild_id = ? AND infraction_type = 'warn' AND created_at > ?
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT 5
                ''', (ctx.guild.id, thirty_days_ago))
                
                top_warned = self.db.c.fetchall()
                
                embed = create_embed(
                    "📊 MODERASYON İSTATİSTİKLERİ",
                    f"Son 30 günün moderasyon özeti",
                    discord.Color.blue()
                )
                
                # Action stats
                warns = stats.get('warn', 0)
                mutes = stats.get('mute', 0)
                bans = stats.get('ban', 0)
                
                embed.add_field(name="⚠️ Toplam Uyarı", value=warns, inline=True)
                embed.add_field(name="🔇 Toplam Susturma", value=mutes, inline=True)
                embed.add_field(name="🚫 Toplam Ban", value=bans, inline=True)
                
                # Top warned users
                if top_warned:
                    warned_text = ""
                    for user_id, count in top_warned:
                        try:
                            user = bot.get_user(user_id)
                            username = user.display_name if user else f"User #{user_id}"
                            warned_text += f"• {username}: {count} uyarı\n"
                        except:
                            continue
                    
                    embed.add_field(name="👥 En Çok Uyarı Alanlar", value=warned_text, inline=False)
                
                # Active moderators
                self.db.c.execute('''
                SELECT moderator_id, COUNT(*) as count FROM user_infractions
                WHERE guild_id = ? AND created_at > ?
                GROUP BY moderator_id
                ORDER BY count DESC
                LIMIT 5
                ''', (ctx.guild.id, thirty_days_ago))
                
                active_mods = self.db.c.fetchall()
                
                if active_mods:
                    mod_text = ""
                    for mod_id, count in active_mods:
                        try:
                            mod = bot.get_user(mod_id)
                            mod_name = mod.display_name if mod else "Bot"
                            mod_text += f"• {mod_name}: {count} işlem\n"
                        except:
                            continue
                    
                    embed.add_field(name="👮 Aktif Moderatörler", value=mod_text, inline=False)
                
                # Overall health
                total_actions = warns + mutes + bans
                member_count = ctx.guild.member_count
                action_rate = (total_actions / member_count) * 100 if member_count > 0 else 0
                
                if action_rate < 5:
                    health = "🟢 Çok İyi"
                elif action_rate < 10:
                    health = "🟡 Normal"
                else:
                    health = "🔴 Yoğun"
                
                embed.add_field(name="🏥 Sunucu Sağlığı", value=f"{health} (Aksiyon oranı: %{action_rate:.1f})", inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Mod stats error: {e}")
                embed = create_embed("❌ Hata", f"İstatistik hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='uyarı_temizle')
        @commands.has_permissions(moderate_members=True)
        async def clear_warnings(ctx, member: discord.Member):
            """Kullanıcının tüm uyarılarını temizle"""
            try:
                # Get current warning count
                self.db.c.execute('''
                SELECT COUNT(*) FROM user_infractions
                WHERE user_id = ? AND guild_id = ? AND infraction_type = 'warn' AND active = TRUE
                ''', (member.id, ctx.guild.id))
                
                warning_count = self.db.c.fetchone()[0]
                
                if warning_count == 0:
                    embed = create_embed("ℹ️ Bilgi", f"{member.display_name} kullanıcısının aktif uyarısı yok!", discord.Color.blue())
                    await ctx.send(embed=embed)
                    return
                
                # Deactivate warnings
                self.db.c.execute('''
                UPDATE user_infractions SET active = FALSE
                WHERE user_id = ? AND guild_id = ? AND infraction_type = 'warn' AND active = TRUE
                ''', (member.id, ctx.guild.id))
                
                self.db.conn.commit()
                
                embed = create_embed(
                    "🧹 UYARILAR TEMİZLENDİ",
                    f"{member.display_name} kullanıcısının uyarıları temizlendi",
                    discord.Color.green()
                )
                
                embed.add_field(name="👤 Kullanıcı", value=member.display_name, inline=True)
                embed.add_field(name="🗑️ Temizlenen", value=f"{warning_count} uyarı", inline=True)
                embed.add_field(name="👮 Moderatör", value=ctx.author.display_name, inline=True)
                
                await ctx.send(embed=embed)
                
                # DM user
                try:
                    dm_embed = create_embed(
                        f"✅ {ctx.guild.name} - Uyarılar Temizlendi",
                        "Tüm uyarılarınız temizlendi! Yeni bir başlangıç yapabilirsiniz.",
                        discord.Color.green()
                    )
                    await member.send(embed=dm_embed)
                except:
                    pass
                
            except Exception as e:
                logger.error(f"Clear warnings error: {e}")
                embed = create_embed("❌ Hata", f"Uyarı temizleme hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)

logger.info("Advanced moderation system initialized successfully")