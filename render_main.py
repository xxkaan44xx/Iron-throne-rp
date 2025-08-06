#!/usr/bin/env python3
"""
Simple Render.com startup script for Game of Thrones Discord Bot
Optimized for free tier with minimal resource usage
"""

import os
import sys
import time
import signal
import subprocess
import threading
from flask import Flask, jsonify

app = Flask(__name__)
bot_process = None
start_time = time.time()

@app.route('/')
def home():
    uptime_hours = (time.time() - start_time) / 3600
    bot_status = "running" if bot_process and bot_process.poll() is None else "stopped"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>🏰 Game of Thrones Discord Bot</title></head>
    <body style="font-family: Arial; background: #1a1a1a; color: #fff; padding: 40px; text-align: center;">
        <h1>🏰 Demir Taht RP - Discord Bot</h1>
        <h2>✅ Status: {bot_status.upper()}</h2>
        <p>🕒 Uptime: {uptime_hours:.1f} hours</p>
        <p>🏆 146+ Commands | ⚔️ War System | 💰 Economy</p>
        <p><a href="/health" style="color: #7289da;">Health Check</a></p>
        <p><small>Running on Render.com</small></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    global bot_process
    is_alive = bot_process and bot_process.poll() is None
    
    return jsonify({
        "status": "healthy" if is_alive else "unhealthy",
        "bot_process": "running" if is_alive else "stopped",
        "uptime_hours": round((time.time() - start_time) / 3600, 2),
        "timestamp": int(time.time())
    })

def start_discord_bot():
    """Start the Discord bot process"""
    try:
        if not os.environ.get('DISCORD_BOT_TOKEN'):
            print("ERROR: DISCORD_BOT_TOKEN not found!")
            return None
            
        env = os.environ.copy()
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            bufsize=1,
            universal_newlines=True
        )
        print(f"Discord bot started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"Failed to start bot: {e}")
        return None

def monitor_bot():
    """Monitor and restart bot if needed"""
    global bot_process
    
    while True:
        try:
            if bot_process is None or bot_process.poll() is not None:
                print("Bot not running, starting...")
                bot_process = start_discord_bot()
                if not bot_process:
                    time.sleep(60)
                    continue
            
            time.sleep(30)
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(60)

def signal_handler(signum, frame):
    """Graceful shutdown"""
    global bot_process
    print("Shutting down...")
    
    if bot_process:
        bot_process.terminate()
        try:
            bot_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            bot_process.kill()
    
    sys.exit(0)

if __name__ == "__main__":
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting Discord Bot on Render...")
    
    # Start Discord bot
    bot_process = start_discord_bot()
    
    # Start monitoring in background
    monitor_thread = threading.Thread(target=monitor_bot, daemon=True)
    monitor_thread.start()
    
    # Start web server
    port = int(os.environ.get('PORT', 5000))
    print(f"Web server starting on port {port}")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False
        )
    except Exception as e:
        print(f"Web server error: {e}")
        signal_handler(signal.SIGTERM, None)