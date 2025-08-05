import os

# Bot Configuration
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "your_bot_token_here")
DATABASE_PATH = os.getenv("DATABASE_PATH", "got_rp.db")

# Game Configuration
MAX_ALLIANCE_MEMBERS = 50
STARTING_GOLD = 1000
STARTING_SOLDIERS = 100
MAX_WAR_TURNS = 50
INCOME_INTERVAL_MINUTES = 1
DEBT_INTEREST_INTERVAL_HOURS = 1

# Combat Configuration
BASE_CASUALTY_RATE = 0.1  # 10% max casualties per turn
VICTORY_THRESHOLD = 0.1   # 10% soldiers remaining to lose

# Economy Configuration
DEFAULT_INTEREST_RATE = 0.1  # 10% interest rate
LOAN_DEFAULT_DURATION_DAYS = 30

# Character Configuration
BASE_HEALTH = 100
BASE_ATTACK = 20
BASE_DEFENSE = 15
EXPERIENCE_PER_LEVEL = 100
