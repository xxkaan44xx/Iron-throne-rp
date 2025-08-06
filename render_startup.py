#!/usr/bin/env python3
"""
Render.com 24/7 Startup Script for Game of Thrones Discord Bot
Handles both web server and bot process management for reliable uptime
"""

import os
import sys
import time
import signal
import subprocess
import threading
from flask import Flask, jsonify
import psutil

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
    <head><title>🏰 Game of Thrones Discord Bot - Render Status</title></head>
    <body style="font-family: Arial; background: #1a1a1a; color: #fff; padding: 40px; text-align: center;">
        <h1>🏰 Demir Taht RP - Discord Bot</h1>
        <h2>✅ Bot Status: {bot_status.upper()}</h2>
        <p>🕒 Uptime: {uptime_hours:.1f} hours</p>
        <p>🏆 104+ Commands | ⚔️ Advanced War System | 💰 Economy</p>
        <hr style="margin: 30px 0;">
        <p><a href="/health" style="color: #7289da;">Health Check</a> | 
           <a href="/restart" style="color: #7289da;">Restart Bot</a></p>
        <p><small>Running on Render.com | Created by xxkaan44xx</small></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    global bot_process
    is_alive = bot_process and bot_process.poll() is None
    
    health_data = {
        "status": "healthy" if is_alive else "unhealthy",
        "bot_process": "running" if is_alive else "stopped",
        "uptime_hours": round((time.time() - start_time) / 3600, 2),
        "memory_mb": round(psutil.Process().memory_info().rss / 1024 / 1024, 1),
        "timestamp": int(time.time()),
        "restart_available": True
    }
    
    return jsonify(health_data)

@app.route('/restart')
def restart_bot():
    """Manual bot restart endpoint"""
    global bot_process
    
    try:
        if bot_process:
            bot_process.terminate()
            bot_process.wait(timeout=10)
        
        bot_process = start_discord_bot()
        
        if bot_process:
            return jsonify({
                "status": "success",
                "message": "Bot restarted successfully",
                "pid": bot_process.pid
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "Failed to start bot process"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Restart failed: {str(e)}"
        }), 500

def start_discord_bot():
    """Start the Discord bot process"""
    try:
        # Check if Discord token is available
        if not os.environ.get('DISCORD_BOT_TOKEN'):
            print("ERROR: DISCORD_BOT_TOKEN environment variable not set!")
            return None
            
        env = os.environ.copy()
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            env=env,
            bufsize=1,
            universal_newlines=True
        )
        print(f"Discord bot started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"Failed to start Discord bot: {e}")
        return None

def monitor_bot():
    """Monitor bot process and restart if it crashes"""
    global bot_process
    
    while True:
        try:
            # Check if bot process is alive
            if bot_process is None or bot_process.poll() is not None:
                print("Bot process not running, attempting restart...")
                bot_process = start_discord_bot()
                
                if bot_process:
                    print(f"Bot successfully restarted with PID: {bot_process.pid}")
                else:
                    print("Failed to restart bot, will retry in 60 seconds")
                    time.sleep(60)
                    continue
            
            # Check every 30 seconds
            time.sleep(30)
            
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(60)

def signal_handler(signum, frame):
    """Graceful shutdown handler"""
    global bot_process
    print("Received shutdown signal, terminating...")
    
    if bot_process:
        bot_process.terminate()
        try:
            bot_process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            bot_process.kill()
    
    sys.exit(0)

def main():
    """Main application entry point"""
    global bot_process
    
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting Game of Thrones Discord Bot on Render...")
    print("Web server will be available on port 5000")
    
    # Start Discord bot
    bot_process = start_discord_bot()
    
    # Start bot monitoring in background thread
    monitor_thread = threading.Thread(target=monitor_bot, daemon=True)
    monitor_thread.start()
    print("Bot monitoring thread started")
    
    # Start Flask web server (Render requires this for health checks)
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting web server on port {port}")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False  # Important: disable reloader in production
        )
    except Exception as e:
        print(f"Web server error: {e}")
        signal_handler(signal.SIGTERM, None)

if __name__ == "__main__":
    main()