import discord
from discord.ext import commands
import asyncio
import re
import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class AutoModerationSystem:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.spam_cache = defaultdict(list)
        self.warning_counts = defaultdict(int)

        # Profanity filter words (basic implementation)
        self.bad_words = ['spam', 'hack', 'cheat', 'bot', 'fake']

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
            logger.error(f"Auto moderation error: {e}")

    async def detect_spam(self, message):
        """Detect spam messages"""
        user_id = message.author.id
        current_time = time.time()

        # Clean old messages (older than 10 seconds)
        self.spam_cache[user_id] = [
            msg_time for msg_time in self.spam_cache[user_id] 
            if current_time - msg_time < 10
        ]

        # Add current message
        self.spam_cache[user_id].append(current_time)

        # Check if spam (5+ messages in 10 seconds)
        return len(self.spam_cache[user_id]) >= 5

    async def detect_profanity(self, message):
        """Detect profanity in message"""
        content = message.content.lower()
        return any(word in content for word in self.bad_words)

    async def detect_excessive_caps(self, message):
        """Detect excessive caps"""
        if len(message.content) < 10:
            return False

        caps_count = sum(1 for c in message.content if c.isupper())
        caps_ratio = caps_count / len(message.content)

        return caps_ratio > 0.7

    async def detect_mass_mentions(self, message):
        """Detect mass mentions"""
        return len(message.mentions) > 5

    async def handle_spam(self, message):
        """Handle spam violation"""
        try:
            await message.delete()

            embed = discord.Embed(
                title="🚫 Spam Detected",
                description=f"{message.author.mention} please slow down your messages!",
                color=discord.Color.red()
            )

            warning_msg = await message.channel.send(embed=embed)
            await warning_msg.delete(delay=5)

            # Add warning to database
            self.add_warning(message.author.id, message.guild.id, "Spam", self.bot.user.id)

        except discord.Forbidden:
            pass

    async def handle_profanity(self, message):
        """Handle profanity violation"""
        try:
            await message.delete()

            embed = discord.Embed(
                title="🚫 Inappropriate Language",
                description=f"{message.author.mention} please keep the chat clean!",
                color=discord.Color.red()
            )

            warning_msg = await message.channel.send(embed=embed)
            await warning_msg.delete(delay=5)

            self.add_warning(message.author.id, message.guild.id, "Profanity", self.bot.user.id)

        except discord.Forbidden:
            pass

    async def handle_excessive_caps(self, message):
        """Handle excessive caps violation"""
        try:
            embed = discord.Embed(
                title="📢 Please Lower Your Voice",
                description=f"{message.author.mention} please avoid excessive caps!",
                color=discord.Color.orange()
            )

            warning_msg = await message.channel.send(embed=embed)
            await warning_msg.delete(delay=3)

        except discord.Forbidden:
            pass

    async def handle_mass_mentions(self, message):
        """Handle mass mentions violation"""
        try:
            await message.delete()

            embed = discord.Embed(
                title="🚫 Mass Mentions",
                description=f"{message.author.mention} please avoid mass mentions!",
                color=discord.Color.red()
            )

            warning_msg = await message.channel.send(embed=embed)
            await warning_msg.delete(delay=5)

            self.add_warning(message.author.id, message.guild.id, "Mass Mentions", self.bot.user.id)

        except discord.Forbidden:
            pass

    def add_warning(self, user_id, guild_id, reason, moderator_id):
        """Add warning to database"""
        try:
            self.db.c.execute('''
            INSERT INTO warnings (user_id, moderator_id, reason)
            VALUES (?, ?, ?)
            ''', (user_id, moderator_id, reason))
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"Error adding warning to database: {e}")

logger.info("Auto moderation system initialized successfully")