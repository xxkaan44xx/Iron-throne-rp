
import time
import psutil
import discord
from datetime import datetime
import asyncio

class PerformanceMonitor:
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.command_counts = {}
        self.error_counts = {}
        
    async def log_command(self, command_name):
        """Log command usage"""
        self.command_counts[command_name] = self.command_counts.get(command_name, 0) + 1
        
    async def log_error(self, error_type):
        """Log error occurrence"""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
    def get_uptime(self):
        """Get bot uptime"""
        return time.time() - self.start_time
        
    def get_memory_usage(self):
        """Get memory usage"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
        
    def get_performance_stats(self):
        """Get comprehensive performance stats"""
        return {
            "uptime": self.get_uptime(),
            "memory_mb": self.get_memory_usage(),
            "commands_used": sum(self.command_counts.values()),
            "errors": sum(self.error_counts.values()),
            "guilds": len(self.bot.guilds),
            "users": len(self.bot.users)
        }
