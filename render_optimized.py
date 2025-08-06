#!/usr/bin/env python3
"""
Optimized Render.com deployment for Game of Thrones Discord Bot
Version 2.0 - Fixed for better reliability and error handling
"""

import os
import sys
import time
import signal
import subprocess
import threading
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot_process = None
start_time = time.time()
bot_restart_count = 0
max_restarts = 10

@app.route('/')
def home():
    uptime_hours = (time.time() - start_time) / 3600
    bot_status = "running" if bot_process and bot_process.poll() is None else "stopped"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏰 Game of Thrones Discord Bot - Render</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body style="font-family: Arial; background: #1a1a1a; color: #fff; padding: 40px; text-align: center;">
        <h1>🏰 Demir Taht RP - Discord Bot</h1>
        <h2>Status: <span style="color: {'#00ff00' if bot_status == 'running' else '#ff4444'};">{bot_status.upper()}</span></h2>
        <div style="background: #333; padding: 20px; margin: 20px 0; border-radius: 10px;">
            <p>🕒 Uptime: {uptime_hours:.1f} hours</p>
            <p>🔄 Restarts: {bot_restart_count}/{max_restarts}</p>
            <p>🏆 Features: 150+ Commands, War System, Economy</p>
            <p>🌍 Platform: Render.com Free Tier</p>
        </div>
        <div style="margin: 20px 0;">
            <a href="/health" style="color: #7289da; text-decoration: none; background: #7289da; color: white; padding: 10px 20px; border-radius: 5px;">Health Check</a>
        </div>
        <p><small>Game of Thrones Discord RP Bot by xxkaan44xx</small></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    global bot_process, bot_restart_count
    is_alive = bot_process and bot_process.poll() is None
    
    return jsonify({
        "status": "healthy" if is_alive else "unhealthy",
        "bot_process": "running" if is_alive else "stopped",
        "uptime_hours": round((time.time() - start_time) / 3600, 2),
        "restarts": bot_restart_count,
        "max_restarts": max_restarts,
        "discord_token_present": bool(os.environ.get('DISCORD_BOT_TOKEN')),
        "timestamp": int(time.time())
    })

@app.route('/restart')
def force_restart():
    """Force restart the bot (for debugging)"""
    global bot_process
    if bot_process:
        logger.info("Force restart requested")
        bot_process.terminate()
        return jsonify({"message": "Bot restart initiated"})
    else:
        return jsonify({"message": "Bot not running"})

def start_discord_bot():
    """Start the Discord bot process with better error handling"""
    try:
        # Validate environment
        if not os.environ.get('DISCORD_BOT_TOKEN'):
            logger.error("DISCORD_BOT_TOKEN environment variable not found!")
            return None
            
        logger.info("Starting Discord bot process...")
        
        # Create process environment
        env = os.environ.copy()
        
        # Start bot process
        process = subprocess.Popen(
            [sys.executable, '-u', 'main.py'],  # -u for unbuffered output
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            bufsize=0,
            universal_newlines=True
        )
        
        logger.info(f"Discord bot started with PID: {process.pid}")
        return process
        
    except Exception as e:
        logger.error(f"Failed to start Discord bot: {e}")
        return None

def monitor_bot():
    """Monitor and restart bot if needed with rate limiting"""
    global bot_process, bot_restart_count
    
    while True:
        try:
            # Check if bot process is alive
            if bot_process is None or bot_process.poll() is not None:
                if bot_restart_count >= max_restarts:
                    logger.error(f"Max restart limit ({max_restarts}) reached. Stopping auto-restart.")
                    time.sleep(300)  # Wait 5 minutes before trying again
                    bot_restart_count = 0  # Reset counter
                    continue
                
                logger.info(f"Bot not running, attempting restart {bot_restart_count + 1}/{max_restarts}")
                bot_process = start_discord_bot()
                
                if bot_process:
                    bot_restart_count += 1
                    # Wait longer after each restart to avoid rapid cycling
                    wait_time = min(60 + (bot_restart_count * 30), 300)
                    logger.info(f"Waiting {wait_time} seconds before next check...")
                    time.sleep(wait_time)
                else:
                    logger.error("Failed to start bot, waiting 60 seconds...")
                    time.sleep(60)
            else:
                # Bot is running, check every 30 seconds
                time.sleep(30)
                
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            time.sleep(60)

def signal_handler(signum, frame):
    """Graceful shutdown handler"""
    global bot_process
    logger.info("Received shutdown signal, cleaning up...")
    
    if bot_process:
        logger.info("Terminating bot process...")
        try:
            bot_process.terminate()
            bot_process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            logger.warning("Bot process didn't terminate gracefully, killing...")
            bot_process.kill()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    logger.info("Shutdown complete")
    sys.exit(0)

def main():
    """Main entry point"""
    global bot_process
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("🏰 Starting Game of Thrones Discord Bot on Render.com")
    
    # Validate environment
    if not os.environ.get('DISCORD_BOT_TOKEN'):
        logger.error("DISCORD_BOT_TOKEN not found! Please set it in Render environment variables.")
        sys.exit(1)
    
    logger.info("✅ Discord bot token found")
    
    # Start Discord bot
    bot_process = start_discord_bot()
    if not bot_process:
        logger.error("Failed to start bot on initial attempt")
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_bot, daemon=True)
    monitor_thread.start()
    logger.info("Bot monitoring thread started")
    
    # Start web server
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting web server on port {port}")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Web server failed to start: {e}")
        signal_handler(signal.SIGTERM, None)

if __name__ == "__main__":
    main()