# Game of Thrones Discord RP Bot

## Overview

This is the ultimate Discord role-playing bot themed around Game of Thrones/A Song of Ice and Fire. The bot allows users to create alliances (houses), engage in warfare, manage economies, and roleplay as characters from the series. It features a command-based architecture with modular systems for combat, economics, character progression, and auto-moderation. The project aims to provide a comprehensive and immersive GoT role-playing experience with advanced game mechanics and a stable, performant platform.

## User Preferences

Preferred communication style: Simple, everyday language.

**Key Requirement:** Every system that has an "opening" command MUST have a corresponding "closing" command. Always implement complete command pairs without exceptions. After every change, fix all errors completely.

**24/7 Hosting Preference:** User wants completely free, unlimited hosting solutions for Discord bot. Explored Replit Deployments (paid), Railway (500h limit), Oracle Cloud (app won't install), Google Cloud (interested), UptimeRobot integration, and **Render.com (750h/month free tier - CURRENT SOLUTION)**. Fixed deployment issues including IndentationError in commands.py and missing war commands.

## System Architecture

### Backend Architecture
- **Framework**: Discord.py (Python Discord library) for bot functionality.
- **Database**: SQLite for local data persistence with foreign key constraints.
- **Architecture Pattern**: Command-based bot with modular system components.
- **Background Tasks**: Asynchronous task loops for automated income generation and debt interest calculation.
- **Error Handling**: Comprehensive logging system with file and console output.
- **Hosting**: Implemented a Keep-Alive Server workflow for 24/7 uptime on Replit, including automatic crash detection and restart.

### Core Design Principles
- **Modularity**: Separate modules for different game systems (war, economy, database).
- **Persistence**: All game state stored in SQLite database.
- **Real-time Processing**: Background tasks handle time-based game mechanics.
- **Rich Interactions**: Discord embeds for enhanced user experience, with a professional, gold-themed 2x3 grid command menu.
- **Command System**: Primarily uses prefix commands (`!`) with a hybrid system for Active Developer Badge (`/ping`).

### Key Components

- **Database Layer**: Comprehensive SQLite schema for alliances, members, wars, income sources, and battle logs, with foreign key constraints and transaction management.
- **Command System**: Extensive pre-defined ASOIAF characters and houses, input validation, and consistent rich embeds.
- **War System**: Turn-based strategic battle system with environmental effects, five distinct combat strategies, and complex damage calculation.
- **Economy System**: Automated income generation from controlled territories, debt management with interest calculation, and resource types (gold, soldiers, power points).
- **Utility Functions**: Consistent Discord embeds, number formatting, house emojis, weather/terrain systems, and character progression with experience-based leveling.

## External Dependencies

### Core Libraries
- **discord.py**: Discord API integration and bot framework.
- **sqlite3**: Built-in Python SQLite database interface.
- **asyncio**: Asynchronous programming for background tasks.
- **logging**: Comprehensive error tracking and debugging.
- **Flask**: Used for web dashboard (although removed for simplicity, components may remain for internal server operations like `keep_alive.py`).

### Data Sources
- **Pre-defined Content**: Extensive ASOIAF character and house database.
- **Environmental Systems**: Libraries for weather and terrain effects.
- **Combat Mechanics**: Libraries for battle action and damage calculation systems.