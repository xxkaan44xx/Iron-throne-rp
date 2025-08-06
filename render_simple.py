#!/usr/bin/env python3
"""
Ultra Simple Render Startup - Test Version
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>🏰 GoT Bot Test</title></head>
    <body style="font-family: Arial; background: #1a1a1a; color: #fff; text-align: center; padding: 50px;">
        <h1>🏰 Game of Thrones Discord Bot</h1>
        <h2>✅ TEST PAGE - Render Working</h2>
        <p>Bot Token Present: {'YES' if os.environ.get('DISCORD_BOT_TOKEN') else 'NO'}</p>
        <p><a href="/health" style="color: #7289da;">Health Check</a></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "service": "Game of Thrones Bot",
        "token_present": bool(os.environ.get('DISCORD_BOT_TOKEN'))
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting test server on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )