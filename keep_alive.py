from flask import Flask, jsonify
from threading import Thread
import time
import os
import random
import socket

app = Flask('')

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>🏰 Iron Throne RP Bot - 24/7 Active</title>
        <style>
            body { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 { color: #FFD700; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏰 Iron Throne RP Bot</h1>
            <h2>✅ Bot is ONLINE & Active 24/7</h2>
            <p>Game of Thrones Roleplay Discord Bot</p>
            <p>🎯 Serving <strong>3 Discord Servers</strong></p>
            <p>⚔️ 104+ Commands Available</p>
            <p>🔥 Zero Downtime - Professional Grade</p>
            <hr>
            <p><em>Valar Morghulis - All Men Must Die</em></p>
            <p><em>But this bot will live forever! 👑</em></p>
        </div>
    </body>
    </html>
    """

@app.route('/status')
def status():
    return jsonify({
        "status": "running",
        "service": "Game of Thrones Discord Bot", 
        "uptime": "24/7",
        "timestamp": time.time()
    })

@app.route('/health')
def health():
    return jsonify({"health": "ok", "bot": "active"})

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
    server = Thread(target=run)
    server.daemon = True
    server.start()

if __name__ == "__main__":
    keep_alive()
    while True:
        time.sleep(1)