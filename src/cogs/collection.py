from collections import defaultdict
from discord.ext import commands
from database.user import User
import discord
from database.collection import Collection
from constants import RARITY_EMOJIS, RARITY_COLORS


class CollectionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def collection(self, ctx):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        User.ensure_user(self.bot.db, guild_id, user_id)
        rows = Collection.get_collection(self.bot.db, guild_id, user_id)

        if not rows:
            await ctx.send("📭 Your collection is empty. Try `/roll`!")
            return

        embed = self.build_collection_embed(ctx, rows)
        await ctx.send(embed=embed)

    @commands.command()
    async def mobs(self, ctx, rarity: str = None):
        if rarity:
            await self._mobs_by_rarity(ctx, rarity)
            return

        self._all_mobs(ctx)

    @commands.command()
    async def mob(self, ctx, mob_id: str):
        mob_id = mob_id.lower()
        mob = self.bot.mobs.get(mob_id)
        if not mob:
            await ctx.send("❌ That mob does not exist.")
            return

        rarity = mob["rarity"]
        color = RARITY_COLORS[rarity]

        embed = discord.Embed(title=f"{mob['name']}", color=color)
        embed.set_image(url=mob["image"])
        embed.set_footer(text=f"Mob ID: {mob_id}")

        await ctx.send(embed=embed)

    def build_collection_embed(self, ctx, rows):
        mobs_by_rarity = defaultdict(list)

        for row in rows:
            mob = self.bot.mobs[row["mob_id"]]
            mobs_by_rarity[mob["rarity"]].append(f"{mob['name']} x{row['amount']}")

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Collection", colour=discord.Colour.green())

        for rarity in [
            ":orange_circle: Legendary",
            ":purple_circle: Epic",
            ":blue_circle: Rare",
            ":green_circle: Uncommon",
            ":white_circle: Common",
        ]:
            symbol, rarity = rarity.split(" ")
            if rarity in mobs_by_rarity:
                embed.add_field(name=f"{symbol} {rarity}", value="\n".join(mobs_by_rarity[rarity]), inline=False)

        return embed

    async def _all_mobs(self, ctx):
        embed = discord.Embed(
            title="📘 Mob Bestiary", description="All known mobs, grouped by rarity.", color=discord.Color.dark_gray()
        )

        for rarity_name, mob_ids in self.bot.mobs_by_rarity.items():
            if not mob_ids:
                continue

            mob_names = [self.bot.mobs[mob_id]["name"] for mob_id in mob_ids]

            embed.add_field(
                name=f"{RARITY_EMOJIS[rarity_name]} {rarity_name}", value="• " + "\n• ".join(mob_names), inline=False
            )

        embed.set_footer(
            text="Use $mobs <rarity> to filter by rarity\nUser $mob <mob_name> for more information about a specific mob"
        )
        await ctx.send(embed=embed)

    async def _mobs_by_rarity(self, ctx, rarity: str):
        rarity = rarity.capitalize()

        if rarity not in self.bot.mobs_by_rarity:
            valid = ", ".join(self.bot.mobs_by_rarity.keys())
            await ctx.send(f"❌ Invalid rarity. Valid options: {valid}")
            return

        mob_ids = self.bot.mobs_by_rarity[rarity]
        if not mob_ids:
            await ctx.send(f"❌ No mobs found for rarity: {rarity}")
            return

        mob_names = [self.bot.mobs[mob_id]["name"] for mob_id in mob_ids]

        embed = discord.Embed(
            title=f"{RARITY_EMOJIS[rarity]} {rarity} Mobs",
            description="• " + "\n• ".join(mob_names),
            color=RARITY_COLORS[rarity],
        )

        embed.set_footer(text=f"Total: {len(mob_names)} mobs")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CollectionCog(bot))
