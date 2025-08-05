import discord
import asyncio
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AutoModerationSystem:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.spam_cache = {}
        self.warning_counts = {}
        
    def setup_automod_events(self):
        """Setup automatic moderation event listeners"""
        
        @self.bot.event
        async def on_message(message):
            # Skip if bot message or DM
            if message.author.bot or not message.guild:
                return
                
            # Process the message first (important for commands)
            await self.bot.process_commands(message)
            
            # Then check for violations
            await self.check_message_violations(message)
    
    async def check_message_violations(self, message):
        """Check message for various violations"""
        try:
            user_id = message.author.id
            guild_id = message.guild.id
            
            # Spam detection
            if await self.detect_spam(message):
                await self.handle_spam(message)
                return
            
            # Profanity filter
            if await self.detect_profanity(message):
                await self.handle_profanity(message)
                return
                
            # Excessive caps
            if await self.detect_excessive_caps(message):
                await self.handle_excessive_caps(message)
                return
                
            # Mass mentions
            if await self.detect_mass_mentions(message):
                await self.handle_mass_mentions(message)
                return
                
        except Exception as e:
            logger.error(f"Auto-moderation error: {e}")
    
    async def detect_spam(self, message):
        """Detect spam messages"""
        user_id = message.author.id
        now = datetime.now()
        
        # Initialize user spam cache
        if user_id not in self.spam_cache:
            self.spam_cache[user_id] = []
        
        # Clean old messages (older than 10 seconds)
        self.spam_cache[user_id] = [
            msg_time for msg_time in self.spam_cache[user_id] 
            if now - msg_time < timedelta(seconds=10)
        ]
        
        # Add current message
        self.spam_cache[user_id].append(now)
        
        # Check if more than 5 messages in 10 seconds
        return len(self.spam_cache[user_id]) > 5
    
    async def detect_profanity(self, message):
        """Detect profanity in messages"""
        # Turkish profanity words (basic list)
        profanity_words = [
            'amk', 'amq', 'orospu', 'piç', 'göt', 'sik', 'mal', 
            'salak', 'gerizekalı', 'aptal', 'cahil'
        ]
        
        content_lower = message.content.lower()
        return any(word in content_lower for word in profanity_words)
    
    async def detect_excessive_caps(self, message):
        """Detect excessive capital letters"""
        if len(message.content) < 10:
            return False
            
        caps_count = sum(1 for c in message.content if c.isupper())
        caps_ratio = caps_count / len(message.content)
        
        return caps_ratio > 0.7 and len(message.content) > 20
    
    async def detect_mass_mentions(self, message):
        """Detect mass mentions"""
        mention_count = len(message.mentions) + len(message.role_mentions)
        return mention_count > 5
    
    async def handle_spam(self, message):
        """Handle spam violation"""
        try:
            await message.delete()
            
            # Timeout user for 5 minutes
            await message.author.edit(
                timed_out_until=discord.utils.utcnow() + timedelta(minutes=5),
                reason="Spam tespit edildi"
            )
            
            # Send warning
            embed = discord.Embed(
                title="🚫 Otomatik Moderasyon",
                description=f"{message.author.mention} spam nedeniyle 5 dakika susturuldu!",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed, delete_after=10)
            
            # Log the action
            await self.log_moderation_action("Spam", message.author, "5 dakika susturma")
            
        except Exception as e:
            logger.error(f"Handle spam error: {e}")
    
    async def handle_profanity(self, message):
        """Handle profanity violation"""
        try:
            await message.delete()
            
            # Add warning
            await self.add_warning(message.author, "Küfür kullanımı")
            
            embed = discord.Embed(
                title="🚫 Otomatik Moderasyon", 
                description=f"{message.author.mention} küfür nedeniyle mesaj silindi!",
                color=discord.Color.orange()
            )
            await message.channel.send(embed=embed, delete_after=10)
            
            await self.log_moderation_action("Küfür", message.author, "Mesaj silindi")
            
        except Exception as e:
            logger.error(f"Handle profanity error: {e}")
    
    async def handle_excessive_caps(self, message):
        """Handle excessive caps violation"""
        try:
            await message.delete()
            
            embed = discord.Embed(
                title="🚫 Otomatik Moderasyon",
                description=f"{message.author.mention} aşırı büyük harf kullanımı nedeniyle mesaj silindi!",
                color=discord.Color.yellow()
            )
            await message.channel.send(embed=embed, delete_after=10)
            
        except Exception as e:
            logger.error(f"Handle caps error: {e}")
    
    async def handle_mass_mentions(self, message):
        """Handle mass mentions violation"""
        try:
            await message.delete()
            
            # Timeout for 10 minutes
            await message.author.edit(
                timed_out_until=discord.utils.utcnow() + timedelta(minutes=10),
                reason="Toplu mention spam"
            )
            
            embed = discord.Embed(
                title="🚫 Otomatik Moderasyon",
                description=f"{message.author.mention} toplu mention nedeniyle 10 dakika susturuldu!",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed, delete_after=10)
            
            await self.log_moderation_action("Toplu Mention", message.author, "10 dakika susturma")
            
        except Exception as e:
            logger.error(f"Handle mass mentions error: {e}")
    
    async def add_warning(self, user, reason):
        """Add warning to user"""
        user_id = user.id
        if user_id not in self.warning_counts:
            self.warning_counts[user_id] = 0
        
        self.warning_counts[user_id] += 1
        
        # Auto-punishment for multiple warnings
        if self.warning_counts[user_id] >= 3:
            try:
                await user.edit(
                    timed_out_until=discord.utils.utcnow() + timedelta(hours=1),
                    reason="3 uyarı sonrası otomatik ceza"
                )
                self.warning_counts[user_id] = 0  # Reset warnings
            except:
                pass
    
    async def log_moderation_action(self, violation_type, user, action):
        """Log moderation actions"""
        try:
            # Find moderation log channel
            for guild in self.bot.guilds:
                log_channel = discord.utils.get(guild.channels, name="moderasyon-log")
                if log_channel and user in guild.members:
                    embed = discord.Embed(
                        title="🤖 Otomatik Moderasyon",
                        color=discord.Color.red(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name="Kullanıcı", value=f"{user.mention} ({user.id})", inline=True)
                    embed.add_field(name="İhlal Türü", value=violation_type, inline=True)
                    embed.add_field(name="Aksiyon", value=action, inline=True)
                    
                    await log_channel.send(embed=embed)
                    break
                    
        except Exception as e:
            logger.error(f"Log moderation action error: {e}")