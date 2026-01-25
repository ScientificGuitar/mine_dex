import discord
from discord.ext import commands
import random
from discord import Colour
from db.collection import Collection
from db.user import User
import time
from collections import defaultdict

TRADING_HALL_ORDER = ["farmer", "cleric", "toolsmith", "librarian"]


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shop(self, ctx, category: str = None):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        category = category.lower() if category else None
        User.ensure_user(self.bot.db, guild_id, user_id)

        if category is None:
            row = User.get_emeralds(self.bot.db, guild_id, user_id)
            emeralds = row["emeralds"] if row else 0

            embed = discord.Embed(
                title="🏪 Marketplace", description=f"💎 **Emeralds:** {emeralds}", color=discord.Color.gold()
            )
            embed.add_field(name="🏛️ Trading Hall", value="Upgrade your village to unlock new services", inline=False)
            embed.set_footer(text="Use $shop <category> to browse")

            await ctx.send(embed=embed)
        if category == "trading":
            row = User.get_emeralds(self.bot.db, guild_id, user_id)
            emeralds = row["emeralds"] if row else 0

            embed = discord.Embed(
                title="🏛️ Trading Hall",
                description=f"Upgrade your village to unlock new services.\n\n💎 **Emeralds:** {emeralds}",
                color=discord.Color.gold(),
            )

            row = User.get_trading_hall_level(self.bot.db, guild_id, user_id)
            current_trading_level = row["trading_hall_level"] if row else 0
            for villager_id in TRADING_HALL_ORDER:
                villager = self.bot.villagers[villager_id]
                state = get_villager_state(current_trading_level, villager["level"])

                if state == "owned":
                    embed.add_field(
                        name=f"✅ {villager['name']} - Owned",
                        value=(f"• {villager['description']}"),
                        inline=False,
                    )
                elif state == "available":
                    embed.add_field(
                        name=f"🔓 {villager['name']} - Available",
                        value=(f"• {villager['description']}\n• **Cost:** 💎 {villager['price']} emeralds\n"),
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=f"🔒 {villager['name']} — Locked",
                        value=(f"• {villager['description']}"),
                        inline=False,
                    )

            embed.set_footer(
                text="Use `$shop upgrade trading` to upgrade your trading hall and unlock the next villager"
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Shop(bot))


def get_villager_state(current_level: int, villager_level: int) -> str:
    if villager_level <= current_level:
        return "owned"
    elif villager_level == current_level + 1:
        return "available"
    else:
        return "locked"
