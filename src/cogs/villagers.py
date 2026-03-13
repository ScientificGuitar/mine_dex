import discord
from discord.ext import commands


class Villagers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def villager(self, ctx, villager_id: str):
        villager_id = villager_id.lower()
        villager = self.bot.villagers.get(villager_id)

        if not villager:
            await ctx.send("❌ That villager does not exist.")
            return

        embed = discord.Embed(
            title=f"{villager['name']}",
            description=villager["description"],
            color=discord.Color.gold(),
        )

        embed.add_field(name="🏛️ Trading Hall Level", value=f"Tier {villager['level']}", inline=False)
        embed.add_field(name="💎 Price", value=f"{villager['price']} emeralds", inline=False)
        embed.add_field(name="📜 Commands", value="\n".join(f"`{cmd}`" for cmd in villager["commands"]), inline=False)
        embed.set_footer(text=f"Villager ID: {villager_id}")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Villagers(bot))
