from typing import List
import discord
import logging
import logging.handlers
from discord.ext import commands
import asyncio
from utils import villager_loader, mob_loader
from database.db import get_connection, init_db


class MyBot(commands.Bot):
    def __init__(self, *args, extentions: List[str], mobs, mobs_by_rarity, villagers, db, **kwargs):
        super().__init__(*args, command_prefix="$", **kwargs)
        self.extentions = extentions
        self.mobs = mobs
        self.mobs_by_rarity = mobs_by_rarity
        self.villagers = villagers
        self.db = db

    async def setup_hook(self) -> None:
        for extentions in self.extentions:
            await self.load_extension(extentions)
            print(f"loaded {extentions}")

    async def on_ready(self) -> None:
        print(f"We have logged in as {self.user}")


async def main():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)

    handler = logging.handlers.RotatingFileHandler(
        filename="discord.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=3,  # Rotate through 3 files
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    mobs, mobs_by_rarity = mob_loader.load_mob_data()
    villagers = villager_loader.load_villagers()
    conn = get_connection()
    init_db(conn)

    extentions = ["cogs.rolls", "cogs.shop", "cogs.collection", "cogs.economy", "cogs.villagers", "cogs.trade"]
    intents = discord.Intents.default()
    intents.message_content = True
    async with MyBot(
        extentions=extentions, intents=intents, mobs=mobs, mobs_by_rarity=mobs_by_rarity, villagers=villagers, db=conn
    ) as bot:
        await bot.start("token")


asyncio.run(main())
