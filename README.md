# Minecraft Mob Collection Discord Bot
A Minecraft-themed Discord bot where players roll for mobs, collect them, trade them, and upgrade their village to unlock new mechanics.  
Players build their collection over time by rolling mobs, claiming rewards, and trading duplicates for emeralds and special items.
## Features
- Mob Rolling - Roll for mobs with rarity-based probabilities.
- Collection System - Track collected mobs and duplicates.
- Emerald Economy - Earn emeralds from claiming mobs.
- Villager Trading - Trade duplicate mobs for emeralds or tokens
- Village Progression - Upgrade your Trading Hall to unlock features
- Daily Rewards - Claim emeralds and a free mob each day.

## Getting Started
### Invite the Bot
Once deployed, invite the bot to a server and start playing with:
```
&help
```
Some useful commands:
```
&roll           Roll for a mob (once per hour)
&daily          Claim your daily reward
&collection     View your mob collection
&balance        Check your emeralds
&shop           View available upgrades 
```
## Running Locally:
### 1. Clone the Repository
```
git clone https://github.com/ScientificGuitar/mine_dex.git
cd mine_dex
```
### 2. Install Dependencies
This project uses uv for dependency management and local development.
If you don't have `uv` installed yet:
```
pip install uv
```
Then install the project dependencies:
```
uv sync
```
This will create a vertual environment and install all dependencies automatically.
### 3. Configure Environment Variables
Create a `.env` file in the project root:
```
DISCORD_TOKEN=your_bot_token_here
```
You can obtain a bot token from the Discord Developer Portal
### 4. Run the Bot
Start the bot with:
```
uv run src/bot.py
```
The bot should now connect to Discord.
## Development Notes
- The bot uses SQLite for sersistent storage
- All player data is server-specific
- Mobs and items are defined via JSON configuration files.