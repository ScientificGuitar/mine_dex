from discord.ext import commands
from database.user import User
import discord
from database.collection import Collection
from constants import FARMER_EMERALD_VALUES
from views.trade_confirm import TradeConfirm


class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def trade(self, ctx, villager: str, mob_id: str, amount: int):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        User.ensure_user(self.bot.db, guild_id, user_id)
        user = User.get_user(self.bot.db, guild_id, user_id)

        if villager.lower() == "farmer":
            user_trading_hall_level = user["trading_hall_level"] if user else 0
            if user_trading_hall_level < self.bot.villagers["farmer"]["level"]:
                await ctx.send(
                    "❌ Your village doesn't have a Farmer yet! Upgrade your Trading Hall to trade your duplicate mobs for emeralds!"
                )
                return

            mob = self.bot.mobs.get(mob_id)
            if not mob:
                await ctx.send("❌ That mob does not exist.")
                return

            row = Collection.get_mob_count(self.bot.db, guild_id, user_id, mob_id)
            user_mob_count = row["amount"] if row else 0
            if user_mob_count <= 1:
                await ctx.send("❌ You do not have duplicates of this mob.")
                return
            if amount >= user_mob_count:
                await ctx.send(f"❌ You can only sell {user_mob_count - 1} of this mob.")
                return

            rarity = mob["rarity"]
            value_per = FARMER_EMERALD_VALUES[rarity]
            emeralds = amount * value_per

            embed = discord.Embed(
                title="Farmer Trade Offer",
                colour=discord.Colour.green(),
            )
            embed.add_field(
                name="You Give",
                value=f"🃏 **{mob['name']}** ×{amount}",
                inline=False,
            )
            embed.add_field(
                name="You Receive",
                value=f"💎 **Emeralds** ×{emeralds}",
                inline=False,
            )
            embed.add_field(
                name="Rarity",
                value=mob["rarity"],
                inline=True,
            )

            embed.set_thumbnail(url=mob["image"])
            embed.set_footer(text="Confirming this trade will permanently remove the mobs.")

            view = TradeConfirm(
                bot=self.bot, guild_id=guild_id, user_id=user_id, mob_id=mob_id, amount=amount, emeralds=emeralds
            )

            await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Trade(bot))
