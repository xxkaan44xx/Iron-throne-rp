import os
import discord
from discord.ext import commands, tasks
import asyncio
import logging
from database import Database
from war_system import WarSystem
from economy import EconomySystem
from army_management import ArmyManagement
from tournament_system import TournamentSystem
from commands import setup_commands
# keep_alive is now handled by separate web server
from special_events import SpecialEventsSystem
from achievements_system import AchievementsSystem
from daily_challenges import DailyChallengesSystem
from enhanced_entertainment import EnhancedEntertainmentSystem
from economy_enhancements import EconomyEnhancements
from advanced_moderation import AdvancedModerationSystem
from lore_economic_system import LoreEconomicSystem
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GameOfThronesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='🏰 Demir Taht RP - Premium Game of Thrones Roleplay Bot | 50+ Komut | Profesyonel Savaş & Ekonomi Sistemi | Created by xxkaan44xx'
        )
        
        # Initialize systems
        self.db = Database()
        self.war_system = WarSystem(self.db)
        self.economy_system = EconomySystem(self.db)
        
        # Initialize new systems
        self.special_events = SpecialEventsSystem(self.db)
        self.achievements = AchievementsSystem(self.db)
        self.daily_challenges = DailyChallengesSystem(self.db)
        self.enhanced_entertainment = EnhancedEntertainmentSystem(self.db)
        self.economy_enhancements = EconomyEnhancements(self.db)
        self.advanced_moderation = AdvancedModerationSystem(self.db)
        self.lore_economy = LoreEconomicSystem(self.db)
        
        # Initialize user friendly system
        from user_friendly_enhancements import UserFriendlySystem
        self.user_friendly = UserFriendlySystem(self.db)
        
        # Prevent duplicate command registration with global flag
        self._commands_loaded = False
        self._prevent_duplicate_response = set()  # Track which commands have responded
        
        # Initialize performance optimizer
        from performance_optimizer import PerformanceOptimizer
        self.perf_optimizer = PerformanceOptimizer(self.db)
        
        # Initialize auto-moderation
        from auto_moderation import AutoModerationSystem
        self.auto_mod = AutoModerationSystem(self, self.db)
        self.auto_mod.setup_automod_events()
        
        # Initialize bot improvements
        from bot_improvements import BotImprovements
        self.improvements = BotImprovements(self, self.db)
        
    async def setup_hook(self):
        """Setup background tasks"""
        logger.info("Setting up background tasks...")
        
        # Load commands only once to prevent duplication
        if not self._commands_loaded:
            await self._load_commands()
            self._commands_loaded = True
        
        # Sync slash commands only once per session
        try:
            # Check if we've already synced recently
            import os
            sync_file = 'last_sync.txt'
            should_sync = True
            
            if os.path.exists(sync_file):
                with open(sync_file, 'r') as f:
                    last_sync = float(f.read())
                    import time
                    if time.time() - last_sync < 3600:  # Don't sync more than once per hour
                        should_sync = False
                        logger.info("Skipping slash command sync (already synced recently)")
            
            if should_sync:
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} slash commands")
                with open(sync_file, 'w') as f:
                    import time
                    f.write(str(time.time()))
            
        except discord.HTTPException as e:
            if "rate limited" in str(e).lower():
                logger.warning("Rate limited during slash command sync, will retry later")
            else:
                logger.error(f"Failed to sync slash commands: {e}")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")
        
        self.income_task.start()
        self.debt_task.start()
        self.maintenance_task.start()
        logger.info("Bot is ready for 24/7 operation!")
    
    async def _load_commands(self):
        """Load all commands once to prevent duplication"""
        try:
            logger.info("Loading bot commands...")
            
            # Setup main commands
            setup_commands(self, self.db, self.war_system, self.economy_system)
            
            # Setup easy commands
            from easy_commands import setup_easy_commands
            setup_easy_commands(self, self.db)
            
            # Setup new system commands
            self.special_events.setup_special_events(self)
            self.achievements.setup_achievement_commands(self)
            self.daily_challenges.setup_daily_challenges_commands(self)
            self.enhanced_entertainment.setup_entertainment_commands(self)
            self.economy_enhancements.setup_economy_commands(self)
            self.advanced_moderation.setup_moderation_commands(self)
            self.lore_economy.setup_lore_commands(self)
            self.user_friendly.setup_user_friendly_commands(self)
            
            # Setup quick improvements (lightweight)
            from quick_improvements import setup_quick_improvements, setup_admin_improvements
            setup_quick_improvements(self)
            setup_admin_improvements(self)
            
            logger.info(f"Successfully loaded {len(self.commands)} commands")
            
        except Exception as e:
            logger.error(f"Error loading commands: {e}")
            raise
        
    async def on_ready(self):
        """Bot ready event"""
        logger.info(f'{self.user} has logged in!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="🏰 Westeros'ta Hüküm Sürüyor | 👨‍💻 xxkaan44xx tarafından | !yardım")
        )
        
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Eksik Parametre",
                description=f"Gerekli parametre: `{error.param.name}`",
                color=discord.Color.red()
            )
            embed.add_field(name="Yardım", value=f"`!yardım {ctx.command.name}` komutunu kullanın")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏱️ Cooldown",
                description=f"Bu komutu {error.retry_after:.1f} saniye sonra tekrar kullanabilirsin!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="🚫 Yetkisiz",
                description="Bu komutu kullanmak için yeterli yetkin yok!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="🤖 Bot Yetkisiz",
                description="Bot'un bu işlemi yapması için gereken yetkiler eksik!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            logger.error(f"Unhandled error in {ctx.command}: {error}", exc_info=True)
            embed = discord.Embed(
                title="❌ Beklenmeyen Hata",
                description="Bir hata oluştu! Lütfen daha sonra tekrar deneyin.",
                color=discord.Color.red()
            )
            embed.add_field(name="Hata Kodu", value=f"`{type(error).__name__}`")
            await ctx.send(embed=embed)
    
    @tasks.loop(minutes=1)
    async def income_task(self):
        """Generate income every minute"""
        try:
            await self.economy_system.generate_income()
        except Exception as e:
            logger.error(f"Income generation error: {e}")
    
    @tasks.loop(hours=1)
    async def debt_task(self):
        """Calculate debt interest every hour"""
        try:
            await self.economy_system.calculate_debt_interest()
        except Exception as e:
            logger.error(f"Debt calculation error: {e}")
    
    @tasks.loop(hours=24)
    async def maintenance_task(self):
        """Daily maintenance and optimization"""
        try:
            # Optimize database performance
            self.perf_optimizer.optimize_database()
            
            # Clean old data
            self.perf_optimizer.cleanup_old_data()
            
            # Log statistics
            stats = self.perf_optimizer.get_performance_stats()
            logger.info(f"Daily maintenance completed. DB stats: {stats}")
            
        except Exception as e:
            logger.error(f"Maintenance task error: {e}")
    
    @income_task.before_loop
    @debt_task.before_loop
    @maintenance_task.before_loop
    async def before_tasks(self):
        """Wait for bot to be ready before starting tasks"""
        await self.wait_until_ready()

async def main():
    """Main function to run the bot"""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not bot_token:
        logger.error("DISCORD_BOT_TOKEN environment variable not set!")
        logger.info("Please add your Discord bot token in the Secrets tab with key: DISCORD_BOT_TOKEN")
        return
    
    if len(bot_token) < 50:
        logger.error("Invalid Discord bot token format!")
        logger.info("Discord bot tokens should be around 70+ characters long")
        return
    
    bot = GameOfThronesBot()
    
    try:
        logger.info("Starting Discord bot...")
        await bot.start(bot_token)
    except discord.LoginFailure:
        logger.error("Invalid Discord bot token! Please check DISCORD_BOT_TOKEN secret.")
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
        if "görev_tamamla" in str(e):
            logger.error("Command name conflict detected. Please restart the bot.")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
