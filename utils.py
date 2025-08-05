import discord
import math
import random
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def create_embed(title, description, color=discord.Color.blue()):
    """Create a Discord embed with consistent styling"""
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="🏰 Game of Thrones RP Bot")
    embed.timestamp = datetime.utcnow()
    return embed

def format_number(number):
    """Format large numbers with commas"""
    if number is None:
        return "0"
    return f"{number:,}"

def format_currency(amount):
    """Format currency as Lannister Gold"""
    return f"{format_number(amount)} Lannister Altını"

def get_house_emoji(house_name):
    """Get emoji for a house"""
    house_emojis = {
        "Stark": "🐺",
        "Lannister": "🦁", 
        "Targaryen": "🐉",
        "Baratheon": "🦌",
        "Tyrell": "🌹",
        "Martell": "☀️",
        "Greyjoy": "🐙",
        "Arryn": "🦅",
        "Tully": "🐟",
        "Bolton": "❌",
        "Frey": "🏰",
        "Mormont": "🐻"
    }
    return house_emojis.get(house_name, "🏰")

def get_weather_emoji(weather):
    """Get emoji for weather condition"""
    weather_emojis = {
        "normal": "☀️",
        "yağmur": "🌧️",
        "kar": "❄️", 
        "fırtına": "⛈️",
        "sis": "🌫️"
    }
    return weather_emojis.get(weather, "🌤️")

def get_terrain_emoji(terrain):
    """Get emoji for terrain type"""
    terrain_emojis = {
        "ova": "🌾",
        "orman": "🌲",
        "dağ": "⛰️",
        "sahil": "🏖️",
        "çöl": "🏜️"
    }
    return terrain_emojis.get(terrain, "🌍")

def calculate_level_from_experience(experience):
    """Calculate level based on experience points"""
    if experience <= 0:
        return 1
    return int(math.sqrt(experience / 100)) + 1

def experience_needed_for_level(level):
    """Calculate experience needed for a specific level"""
    if level <= 1:
        return 0
    return (level - 1) ** 2 * 100

def experience_needed_for_next_level(current_exp):
    """Calculate experience needed for next level"""
    current_level = calculate_level_from_experience(current_exp)
    next_level_exp = experience_needed_for_level(current_level + 1)
    return next_level_exp - current_exp

def get_character_class_info(character_class):
    """Get information about character classes"""
    classes = {
        "Lord": {
            "description": "Soylu lider, politik güce sahip",
            "bonuses": {"attack": 5, "defense": 5, "health": 10},
            "emoji": "👑"
        },
        "Knight": {
            "description": "Profesyonel savaşçı, savaş eğitimli", 
            "bonuses": {"attack": 10, "defense": 8, "health": 5},
            "emoji": "⚔️"
        },
        "Maester": {
            "description": "Bilgin, şifa bilgisi olan",
            "bonuses": {"attack": 0, "defense": 3, "health": 15},
            "emoji": "📚"
        },
        "Assassin": {
            "description": "Gizli katil, ölümcül kesinlik",
            "bonuses": {"attack": 15, "defense": 2, "health": 0},
            "emoji": "🗡️"
        },
        "Sellsword": {
            "description": "Paralı asker",
            "bonuses": {"attack": 8, "defense": 5, "health": 3},
            "emoji": "💰"
        },
        "Merchant": {
            "description": "Tüccar, ekonomi uzmanı",
            "bonuses": {"attack": 2, "defense": 3, "health": 5},
            "emoji": "🏪"
        }
    }
    return classes.get(character_class, classes["Lord"])

def validate_house_name(name):
    """Validate house name format"""
    if not name or len(name.strip()) < 3:
        return False, "Hane adı en az 3 karakter olmalı!"

    name = name.strip()
    if len(name) > 20:
        return False, "Hane adı en fazla 20 karakter olmalı!"

    # Check for valid characters (allowing Turkish characters)
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 çÇğĞıİöÖşŞüÜ-'")
    if not all(c in allowed_chars for c in name):
        return False, "Hane adında geçersiz karakter var!"

    # Check for reserved names
    reserved_names = ["Admin", "Bot", "System", "Moderator"]
    if name.lower() in [r.lower() for r in reserved_names]:
        return False, "Bu isim kullanılamaz!"

    return True, ""

def create_progress_bar(current, maximum, length=10):
    """Create a text progress bar"""
    if maximum <= 0:
        return "▱" * length + " 0%"

    filled = int((current / maximum) * length)
    filled = max(0, min(filled, length))
    bar = "▰" * filled + "▱" * (length - filled)
    percentage = int((current / maximum) * 100)
    return f"{bar} {percentage}%"

def time_until_next_hour():
    """Get minutes until next hour for debt calculations"""
    now = datetime.now()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    diff = next_hour - now
    return int(diff.total_seconds() / 60)

def format_time_duration(seconds):
    """Format duration in seconds to readable format"""
    if seconds < 60:
        return f"{seconds}s"

    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m") 
    if seconds > 0 and hours == 0:  # Only show seconds if less than an hour
        parts.append(f"{seconds}s")

    return " ".join(parts) if parts else "0s"

def get_random_battle_flavor_text(result_type):
    """Get random flavor text for battle results"""
    texts = {
        "attacker_major": [
            "Düşman hatları çöktü!",
            "Zafer yakındır!",
            "Düşman ordusunda panik var!",
            "Kahramanca ilerleme!",
            "Saldırı başarılı!"
        ],
        "attacker_minor": [
            "İlerleyiş devam ediyor.",
            "Küçük bir avantaj elde edildi.",
            "Düşman geri çekiliyor.",
            "Pozisyon kazanıldı.",
            "Yavaş ama kararlı ilerleme."
        ],
        "defender_major": [
            "Kahramanca savunma!",
            "Düşman püskürtüldü!",
            "Kale sağlam duruyor!",
            "Savunma hatları korunuyor!",
            "Başarılı karşı saldırı!"
        ],
        "defender_minor": [
            "Savunma hatları tutuyor.",
            "Düşman saldırısı karşılandı.",
            "Pozisyonlar korunuyor.",
            "Direniş devam ediyor.",
            "Savunma başarılı."
        ],
        "draw": [
            "Çetin bir çarpışma!",
            "Her iki taraf da direniyor.",
            "Savaş dengelerde.",
            "Kimse üstünlük sağlayamıyor.",
            "Dengeli mücadele."
        ]
    }

    return random.choice(texts.get(result_type, ["Savaş devam ediyor."]))

def get_random_weather():
    """Get random weather condition"""
    weather_conditions = ["normal", "yağmur", "kar", "fırtına", "sis"]
    weights = [0.4, 0.2, 0.15, 0.15, 0.1]  # Normal weather is most common
    return random.choices(weather_conditions, weights=weights)[0]

def get_random_terrain():
    """Get random terrain type"""
    terrain_types = ["ova", "orman", "dağ", "sahil", "çöl"]
    return random.choice(terrain_types)

def calculate_war_score(alliance_data):
    """Calculate war readiness score for an alliance"""
    if not alliance_data:
        return 0

    gold = alliance_data[3] or 0
    soldiers = alliance_data[4] or 0

    # Basic score calculation
    score = (gold * 0.1) + (soldiers * 2)

    # Bonus for special abilities
    special_ability = alliance_data[7] or ""
    if "Savaş" in special_ability:
        score *= 1.2
    elif "Altın" in special_ability:
        score *= 1.1

    return int(score)

def get_income_source_emoji(source_type):
    """Get emoji for income source type"""
    emojis = {
        "mine": "⛏️",
        "farm": "🌾",
        "port": "⚓",
        "castle": "🏰",
        "market": "🏪",
        "forest": "🌲",
        "quarry": "🪨",
        "vineyard": "🍇"
    }
    return emojis.get(source_type, "💰")

def validate_character_name(name):
    """Validate character name format"""
    if not name or len(name.strip()) < 2:
        return False, "Karakter adı en az 2 karakter olmalı!"

    name = name.strip()
    if len(name) > 30:
        return False, "Karakter adı en fazla 30 karakter olmalı!"

    # Allow letters, spaces, apostrophes, and Turkish characters
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ çÇğĞıİöÖşŞüÜ'-")
    if not all(c in allowed_chars for c in name):
        return False, "Karakter adında geçersiz karakter var!"

    return True, ""

def format_alliance_display(alliance_data):
    """Format alliance data for display"""
    if not alliance_data:
        return "Bilinmeyen Hane"

    name = alliance_data[1]
    emoji = get_house_emoji(name)
    return f"{emoji} {name}"

def calculate_marriage_compatibility(user1_data, user2_data):
    """Calculate compatibility score for marriage (simple implementation)"""
    if not user1_data or not user2_data:
        return 0

    # Base compatibility
    compatibility = 50

    # Same house bonus
    if user1_data[1] == user2_data[1]:  # alliance_id
        compatibility += 20

    # Level difference penalty
    level_diff = abs((user1_data[5] or 1) - (user2_data[5] or 1))
    compatibility -= level_diff * 2

    # Experience bonus
    total_exp = (user1_data[6] or 0) + (user2_data[6] or 0)
    compatibility += min(total_exp // 1000, 30)

    return max(0, min(100, compatibility))

class BotError(Exception):
    """Custom bot error class"""
    def __init__(self, message, user_friendly=True):
        self.message = message
        self.user_friendly = user_friendly
        super().__init__(message)

def safe_execute(func, *args, **kwargs):
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs), None
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}")
        return None, str(e)

def chunks(lst, n):
    """Yield successive n-sized chunks from list"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]