from flask import Flask, jsonify
from threading import Thread
import time
import os
import random
import socket
import psutil
import subprocess
import sys
import signal

app = Flask('')

# Bot'un başlangıç zamanını kaydet
start_time = time.time()
bot_process = None

@app.route('/')
def home():
    return """
    <html>
    <head><title>🏰 Iron Throne RP Bot</title></head>
    <body style="font-family: Arial; background: #2c2f33; color: #ffffff; text-align: center; padding: 50px;">
        <h1>🏰 Game of Thrones Discord Bot</h1>
        <h2>⚔️ Iron Throne RP - Demir Taht Roleplay</h2>
        <p>✅ Bot is alive and running 24/7!</p>
        <p>🏆 104+ Commands | 🏰 10 Houses | ⚔️ Advanced War System</p>
        <p>💰 Economy System | 👑 Marriage System | 🛡️ Auto Moderation</p>
        <hr>
        <p><a href="/status" style="color: #7289da;">Bot Status</a> | <a href="/health" style="color: #7289da;">Health Check</a></p>
        <p><small>Created by xxkaan44xx | Running on Replit</small></p>
    </body>
    </html>
    """

@app.route('/status')
def status():
    uptime_seconds = time.time() - start_time
    uptime_hours = uptime_seconds / 3600

    return jsonify({
        "status": "running",
        "service": "Iron Throne RP Discord Bot",
        "version": "3.0 Professional Edition",
        "uptime_seconds": round(uptime_seconds),
        "uptime_hours": round(uptime_hours, 2),
        "features": {
            "commands": "104+",
            "houses": 10,
            "systems": ["War", "Economy", "Marriage", "Tournament", "Trade"],
            "moderation": "Advanced Auto-Mod"
        },
        "timestamp": time.time(),
        "memory_usage": f"{psutil.Process().memory_info().rss / 1024 / 1024:.1f} MB" if 'psutil' in globals() else "N/A"
    })

@app.route('/health')
def health():
    global bot_process
    bot_status = "active" if bot_process and bot_process.poll() is None else "inactive"
    
    return jsonify({
        "health": "ok",
        "bot": bot_status,
        "database": "connected",
        "systems": "operational",
        "process_alive": bot_process is not None and bot_process.poll() is None,
        "last_check": time.time()
    })

@app.route('/restart-bot')
def restart_bot():
    """Restart the Discord bot if it crashes"""
    global bot_process
    try:
        if bot_process:
            bot_process.terminate()
            bot_process.wait(timeout=10)
        
        bot_process = subprocess.Popen([sys.executable, 'main.py'])
        return jsonify({"status": "bot restarted", "pid": bot_process.pid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def find_free_port():
    """Find a free port to use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def run():
    try:
        # Replit requires port 5000 for web server
        port = int(os.environ.get('PORT', 5000))
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        print(f"Flask server error: {e}")

def keep_alive():
    """Start Flask server in a separate thread"""
    server = Thread(target=run)
    server.daemon = True
    server.start()

def start_bot():
    """Start the Discord bot as a subprocess"""
    global bot_process
    try:
        bot_process = subprocess.Popen([sys.executable, 'main.py'])
        return bot_process
    except Exception as e:
        print(f"Failed to start bot: {e}")
        return None

def monitor_bot():
    """Monitor bot process and restart if crashed"""
    global bot_process
    while True:
        if bot_process is None or bot_process.poll() is not None:
            print("Bot process not running, starting...")
            bot_process = start_bot()
            if bot_process:
                print(f"Bot started with PID: {bot_process.pid}")
            else:
                print("Failed to start bot, retrying in 30 seconds...")
                time.sleep(30)
                continue
        
        time.sleep(60)  # Check every minute

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global bot_process
    print("Shutting down gracefully...")
    if bot_process:
        bot_process.terminate()
        bot_process.wait()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start Flask web server
    keep_alive()
    print("Web server started on port 5000")
    
    # Start bot monitoring
    monitor_thread = Thread(target=monitor_bot)
    monitor_thread.daemon = True
    monitor_thread.start()
    print("Bot monitoring started")
    
    # Keep the main process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)