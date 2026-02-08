from discord.ext import commands
from database.user import User
from database.inventory import Inventory
from database.collection import Collection
import discord
from constants import RARITY_EMOJIS, RARITY_COLORS, RARITY_WEIGHTS
import random
from datetime import datetime, timezone
import time


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def balance(self, ctx):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        User.ensure_user(self.bot.db, guild_id, user_id)
        row = User.get_emeralds(self.bot.db, guild_id, user_id)
        emeralds = row["emeralds"] if row else 0

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Balance", colour=discord.Colour.green())

        embed.add_field(name="💎 Emeralds", value=str(emeralds), inline=False)
        embed.set_footer(text="Collect mobs to earn more emeralds!")

        await ctx.send(embed=embed)

    @commands.command()
    async def inventory(self, ctx):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        User.ensure_user(self.bot.db, guild_id, user_id)
        inventory = Inventory.get_items(self.bot.db, guild_id, user_id)

        grouped = {}

        for item in inventory or []:
            item_id = item["item_id"]
            amount = item["amount"]

            if amount <= 0:
                continue

            item = self.bot.items.get(item_id)
            if not item:
                continue

            item_type = item.get("type", "misc")
            grouped.setdefault(item_type, []).append((item, amount))

        if not grouped:
            await ctx.send("🎒 Your inventory is empty.")
            return

        embed = discord.Embed(title=f"🎒 {ctx.author.display_name}'s Inventory", colour=discord.Colour.dark_gold())

        for item_type, items in grouped.items():
            lines = []

            for item, amount in items:
                rarity = item.get("rarity", "Common")
                emoji = RARITY_EMOJIS[rarity]

                lines.append(f"{emoji} **{item['name']}** x{amount}")

            embed.add_field(
                name=item_type.title(),
                value="\n".join(lines),
                inline=False,
            )

        embed.set_footer(text=f"Use {self.bot.command_prefix}item <item_id> to view details")
        await ctx.send(embed=embed)

    @commands.command()
    async def item(self, ctx, item_id: str):
        item = self.bot.items.get(item_id)
        if not item:
            await ctx.send("❌ Unknown item.")
            return

        rarity = item.get("rarity", "Common")
        colour = RARITY_COLORS.get(rarity, discord.Colour.dark_grey())

        embed = discord.Embed(title=item["name"], description=item.get("description", "No description."), colour=colour)

        embed.add_field(name="Type", value=item.get("type", "Unknown").title(), inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def daily(self, ctx):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        now = time.time()
        User.ensure_user(self.bot.db, guild_id, user_id)

        user = User.get_user(self.bot.db, guild_id, user_id)
        last_daily_claim_at = user["last_daily_at"] if user else None
        if same_utc_day(last_daily_claim_at, now):
            await ctx.send("❌ You've already claimed today.")
            return

        emeralds = random.randint(2, 5)
        mob_id, mob = self.roll_random_mob(allowed={"Common"})

        User.update_last_daily_at(self.bot.db, guild_id, user_id, now)
        User.add_emeralds(self.bot.db, guild_id, user_id, emeralds)
        Collection.add_to_collection(self.bot.db, guild_id, user_id, mob_id)

        embed = discord.Embed(
            title="🎁 Daily Reward",
            description=("You checked in today and received your daily reward!\nCome back tomorrow for more."),
            colour=discord.Colour.green(),
        )

        embed.add_field(
            name="💎 Emeralds",
            value=f"+{emeralds}",
            inline=False,
        )

        embed.add_field(
            name="🪨 Common Mob",
            value=f"**{mob['name']}**",
            inline=False,
        )

        await ctx.send(embed=embed)

    def roll_random_mob(self, exclude=None, allowed=None):
        rarity = Economy.roll_rarity(exclude, allowed)
        mob = random.choice(self.bot.mobs_by_rarity[rarity])
        return mob, self.bot.mobs[mob]

    @staticmethod
    def roll_rarity(exclude=None, allowed=None):
        exclude = exclude or set()
        if allowed:
            rarities = [r for r in allowed if r in RARITY_WEIGHTS]
        else:
            rarities = [r for r in RARITY_WEIGHTS if r not in exclude]
        weights = [RARITY_WEIGHTS[r] for r in rarities]

        return random.choices(rarities, weights=weights, k=1)[0]


async def setup(bot):
    await bot.add_cog(Economy(bot))


def same_utc_day(ts1: int, ts2: int) -> bool:
    if ts1 is None:
        return False
    d1 = datetime.fromtimestamp(ts1, tz=timezone.utc).date()
    d2 = datetime.fromtimestamp(ts2, tz=timezone.utc).date()
    return d1 == d2