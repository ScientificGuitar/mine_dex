import discord
from discord.ext import commands
from database.user import User
from views.upgrade_confirm import UpgradeTradingView
from constants import TRADING_HALL_ORDER


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shop(self, ctx, action: str = None, target: str = None):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        category = action.lower() if action else None
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

        if category == "upgrade":
            if target == "trading":
                row = User.get_trading_hall_level(self.bot.db, guild_id, user_id)
                current_level = row["trading_hall_level"]
                row = User.get_emeralds(self.bot.db, guild_id, user_id)
                emeralds = row["emeralds"]
                next_level = current_level + 1

                villager = get_villager_by_level(self.bot.villagers, next_level)
                if not villager:
                    await ctx.send("✅ Your Trading Hall is already fully upgraded.")
                    return

                price = villager["price"]

                if emeralds < price:
                    await ctx.send(f"❌ You need **{price} emeralds**, but you only have **{emeralds}**.")
                    return

                embed = discord.Embed(
                    title="⬆️ Upgrade Trading Hall",
                    description=(
                        f"**Current Tier:** {get_villager_by_level(self.bot.villagers, current_level)['name'] if current_level > 0 else 'None'}\n"
                        f"**Next Tier:** {villager['name']}\n\n"
                        f"**Unlocks:**\n• {villager['description']}\n\n"
                        f"💎 **Price:** {price} emeralds"
                    ),
                    color=discord.Color.gold(),
                )

                view = UpgradeTradingView(bot=self.bot, guild_id=guild_id, user_id=user_id, villager=villager)

                embed.set_footer(text="Confirm to upgrade your Trading Hall")
                await ctx.send(embed=embed, view=view)

            else:
                await ctx.send("❌ Unknown upgrade target.")
                return

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
                        value=(f"• {villager['description']}\n• **Price:** 💎 {villager['price']} emeralds\n"),
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

def get_villager_by_level(villagers: dict, level: int):
    for key, villager in villagers.items():
        if villager["level"] == level:
            return villager
        return None
