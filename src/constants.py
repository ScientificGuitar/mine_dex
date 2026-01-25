from discord import Colour

RARITY_WEIGHTS = {"Common": 55, "Uncommon": 25, "Rare": 13, "Epic": 6, "Legendary": 1}
RARITY_EMERALD_REWARDS = {
    "Common": 1,
    "Uncommon": 2,
    "Rare": 4,
    "Epic": 8,
    "Legendary": 15,
}
RARITY_EMOJIS = {
    "Common": ":white_circle:",
    "Uncommon": ":green_circle:",
    "Rare": ":blue_circle:",
    "Epic": ":purple_circle:",
    "Legendary": ":orange_circle:",
}
RARITY_COLORS = {
    "Common": Colour.light_grey(),
    "Uncommon": Colour.green(),
    "Rare": Colour.blue(),
    "Epic": Colour.purple(),
    "Legendary": Colour.orange(),
}

TRADING_HALL_ORDER = ["farmer", "cleric", "toolsmith", "librarian"]

VALID_TOKEN_RARITIES = ["uncommon", "rare", "epic"]
