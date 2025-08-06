#!/bin/bash
# Render.com startup script for Game of Thrones Discord Bot

echo "🏰 Starting Game of Thrones Discord Bot on Render..."

# Check if Discord bot token exists
if [ -z "$DISCORD_BOT_TOKEN" ]; then
    echo "❌ ERROR: DISCORD_BOT_TOKEN environment variable is not set!"
    exit 1
fi

echo "✅ Discord bot token found"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r render_requirements.txt

# Start the bot with monitoring
echo "🚀 Starting Discord bot with monitoring..."
python render_main.py