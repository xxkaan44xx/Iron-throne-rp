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
from keep_alive import keep_alive
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
        
        # Setup commands
        setup_commands(self, self.db, self.war_system, self.economy_system)
        
        # Initialize performance optimizer
        from performance_optimizer import PerformanceOptimizer
        self.perf_optimizer = PerformanceOptimizer(self.db)
        
        # Initialize auto-moderation
        from auto_moderation import AutoModerationSystem
        self.auto_mod = AutoModerationSystem(self, self.db)
        self.auto_mod.setup_automod_events()
        
    async def setup_hook(self):
        """Setup background tasks"""
        logger.info("Setting up background tasks...")
        # Note: Flask server is handled by separate Web Server workflow
        
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
            await ctx.send(f"❌ Eksik parametre: {error.param.name}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ Bu komutu {error.retry_after:.1f} saniye sonra tekrar kullanabilirsin!")
        else:
            logger.error(f"Unhandled error in {ctx.command}: {error}")
            await ctx.send("❌ Bir hata oluştu! Lütfen daha sonra tekrar deneyin.")
    
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
        logger.info("Please set your Discord bot token in the Secrets tab")
        return
    
    bot = GameOfThronesBot()
    
    try:
        logger.info("Starting Discord bot...")
        await bot.start(bot_token)
    except discord.LoginFailure:
        logger.error("Invalid Discord bot token!")
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
