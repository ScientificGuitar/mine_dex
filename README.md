# Minecraft Mob Collection Game - Functional Design
## Overview
This Discord bot implements a Minecraft-themed collection game where players roll for mobs, collect them, trade duplicates, and progress through a village-based upgrade system using emeralds.  
The game is server-specific: each server maintains its own collections, progression, and economy.

## Core Gameplay Loop
1. Player rolls for a mob (once per hour)
2. Player claims the roll (once per day)
3. Mob is added to their collection
4. Player earns emeralds based on mob rarity
5. Duplicate mobs can be traded via villagers
6. Emeralds are used to upgrade systems and buy items
7. Progression unlocks new gameplay mechanics

## Rolling & Claiming
### $roll
- Can be used once per hour
- Randomly selects a mob based on rarity weights
- Displays the mob in an embed
- Includes a Claim button, can be claimed for 1 hour before expiring

### Claiming
- Players may claim only once per day
- Claiming:
    - Adds the mob to the player's collection
    - Awards emeralds based on rarity
    - Disables the claim button
    - Updates the embed to show it was claimed

## Mob Rarities
Each mob belongs to one of the following rarities:
- Common
- Uncommon
- Rare
- Epic
- Legendary
Rarity determines:
- Roll probability
- Emerald reward on claim
- Token type (if applicable)

## Player Economy
### Emeralds
- Primary currency
- Earned when claiming mobs
- Used for:
    - Trading Hall upgrades
    - Other shop items (future)

### $balance
- Displays the player's current emerald count

## Collection System
### $collection
- Displays the player's collected mobs
- Shows duplicates where applicable
- Collection is per-server

### $mob <mob_id>
- Shows detailed info about a specific mob

### $mobs
- Lists all mobs, grouped by rarity

### $mobs <rarity>
- Lists mobs of a specific rarity

## Shop System
### $shop
Displays available shop categories.
Currently available:
- 🏛️ Trading Hall

Future categories may include:
- Tokens & Boosts
- Special Items

### $shop <category>
- Shows detailed information about a specific shop category.

## Trading Hall (Progression System)
The Trading Hall is a tiered upgrade system that unlocks new mechanics.
### Upgrade Command
- `$shop upgrade trading`

Upgrades must be purchased in order.

### Trading Hall Tiers
**Tier 1 - Farmer (100 emeralds)**
- Unlocks trading duplicate mobs for emeralds
- Command:
    ```
    $trade farmer <mob_id> <amount>
    ```
**Tier 2 - Cleric (250 emeralds)**
- Unlocks converting duplicate mobs into roll tokens
- Tokens allow rarity-restricted rolls
- Command:
    ```
    $trade cleric <mob_id> <amount>
    ```
**Tier 3 - Toolsmith (500 emeralds)**
- Unlocks one reroll per day
- Reroll is not subject to the hourly cooldown
- Command:
    ```
    $reroll
    ```
**Tier 4 - Librarian (1000 emeralds)**
- Unlocks one focused roll per day
- Focused roll excludes Common mobs entirely
- Command:
    ```
    $roll focus
    ```

## Trading Flow
When a trade command is issued:
1. Bot responds with a trade breakdown:
    - What the player gives
    - What the player receives
2. Player confirms or cancels via buttons
3. On confirmation:
    - Inventory is updated
    - Rewards are granted

## Roll Tokens
- Obtained via Cleric trades or shop purchases (future)
- Token types correspond to rarities:
    - Uncommon Token
    - Rare Token
    - Epic Token

### Using Tokens
`$roll <token>`
- Consumes the token
- Rolls a mob only within that rarity band

## Villager Information
### $villager <villager_id>
Displays:
- Villager image
- Description
- Relevant commands