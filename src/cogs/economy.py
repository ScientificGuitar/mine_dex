from discord.ext import commands
from database.user import User
from database.inventory import Inventory
import discord
from constants import RARITY_EMOJIS, RARITY_COLORS


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

        embed.set_footer(text="Use $item <item_id> to view details")
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


async def setup(bot):
    await bot.add_cog(Economy(bot))
