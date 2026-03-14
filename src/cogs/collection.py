from collections import defaultdict

import discord
from discord.ext import commands

from constants import RARITY_COLORS, RARITY_EMOJIS
from database.collection import Collection
from database.user import User


class CollectionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def collection(self, ctx, collection_filter: int | str = 1):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        User.ensure_user(self.bot.db, guild_id, user_id)
        rows = Collection.get_collection(self.bot.db, guild_id, user_id)

        if not rows:
            await ctx.send(f"📭 Your collection is empty. Try `{self.bot.command_prefix}roll`!")
            return

        if isinstance(collection_filter, int):
            embed = self.build_collection_embed(ctx, rows, page=collection_filter)
        else:
            embed = self.build_collection_embed(ctx, rows, rarity=collection_filter)

        await ctx.send(embed=embed)

    @commands.command()
    async def missing(self, ctx):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        User.ensure_user(self.bot.db, guild_id, user_id)
        rows = Collection.get_collection(self.bot.db, guild_id, user_id)

        owned_mobs = {row["mob_id"] for row in rows}
        all_mobs = set(self.bot.mobs.keys())
        missing_mobs = all_mobs - owned_mobs

        if not missing_mobs:
            await ctx.send("🎉 You have collected all mobs! Congratulations!")
            return

        missing_by_rarity = defaultdict(list)
        for mob_id in missing_mobs:
            mob = self.bot.mobs[mob_id]
            missing_by_rarity[mob["rarity"]].append(f"{mob['name']}")

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Missing Collection", colour=discord.Colour.red())

        for rarity in [
            ":orange_circle: Legendary",
            ":purple_circle: Epic",
            ":blue_circle: Rare",
            ":green_circle: Uncommon",
            ":white_circle: Common",
        ]:
            symbol, rarity = rarity.split(" ")
            if rarity in missing_by_rarity:
                mob_list = missing_by_rarity[rarity]
                if len(", ".join(mob_list)) > 1000:
                    mob_list = mob_list[:10] + [f"... and {len(mob_list) - 10} more"]
                embed.add_field(name=f"{symbol} {rarity}", value=", ".join(mob_list), inline=False)

        embed.set_footer(text=f"Total missing: {len(missing_mobs)} mobs")
        await ctx.send(embed=embed)

    @commands.command()
    async def mobs(self, ctx, mob_filter: int | str = 1):
        if isinstance(mob_filter, int):
            await self._all_mobs(ctx, mob_filter)
            return

        await self._mobs_by_rarity(ctx, mob_filter)

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

    def build_collection_embed(
        self,
        ctx,
        rows,
        page: int = 1,
        per_page: int = 3,
        rarity: str | None = None,
    ):
        rarity_order = ["Legendary", "Epic", "Rare", "Uncommon", "Common"]
        entries = []
        for r in rarity_order:
            if rarity is not None and r.lower() != rarity.lower():
                continue
            for row in rows:
                mob = self.bot.mobs[row["mob_id"]]
                if mob["rarity"] == r:
                    entries.append((r, f"{mob['name']} x{row['amount']}"))

        if rarity is not None and not entries:
            valid = ", ".join(rarity_order)
            embed = discord.Embed(
                title="❌ Invalid or empty rarity",
                description=f"No mobs found for rarity '{rarity}'. Valid options: {valid}",
                colour=discord.Colour.red(),
            )
            return embed

        total_entries = len(entries)
        total_pages = (total_entries + per_page - 1) // per_page
        if total_pages == 0:
            total_pages = 1

        if page < 1 or page > total_pages:
            embed = discord.Embed(
                title="❌ Invalid page",
                description=f"Page must be between 1 and {total_pages}.",
                colour=discord.Colour.red(),
            )
            return embed

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_entries = entries[start_idx:end_idx]

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Collection",
            colour=discord.Colour.green(),
            description=f"Page {page}/{total_pages} ({total_entries} mobs total)",
        )

        current_rarity = None
        rarity_entries = []
        for rarity_name, entry in page_entries:
            if rarity_name != current_rarity:
                if current_rarity and rarity_entries:
                    embed.add_field(
                        name=f"{RARITY_EMOJIS[current_rarity]} {current_rarity}",
                        value="\n".join(rarity_entries),
                        inline=False,
                    )
                current_rarity = rarity_name
                rarity_entries = [entry]
            else:
                rarity_entries.append(entry)

        if current_rarity and rarity_entries:
            embed.add_field(
                name=f"{RARITY_EMOJIS[current_rarity]} {current_rarity}",
                value="\n".join(rarity_entries),
                inline=False,
            )

        footer_text = f"Use {self.bot.command_prefix}collection <page> to navigate"
        if rarity:
            footer_text += f" | Filtering by rarity: {rarity.capitalize()}"
        embed.set_footer(text=footer_text)
        return embed

    async def _all_mobs(self, ctx, page: int = 1):
        mobs_per_page = 10
        all_mobs = []
        for rarity_name, mob_ids in self.bot.mobs_by_rarity.items():
            for mob_id in mob_ids:
                all_mobs.append((rarity_name, self.bot.mobs[mob_id]["name"]))

        total_mobs = len(all_mobs)
        total_pages = (total_mobs + mobs_per_page - 1) // mobs_per_page

        if page < 1 or page > total_pages:
            await ctx.send(f"❌ Invalid page number. Valid pages: 1-{total_pages}")
            return

        start_idx = (page - 1) * mobs_per_page
        end_idx = start_idx + mobs_per_page
        page_mobs = all_mobs[start_idx:end_idx]

        embed = discord.Embed(
            title="📘 Mob Bestiary", description="All known mobs, grouped by rarity.", color=discord.Color.dark_gray()
        )

        current_rarity = None
        rarity_mobs = []
        for rarity, mob_name in page_mobs:
            if rarity != current_rarity:
                if current_rarity and rarity_mobs:
                    embed.add_field(
                        name=f"{RARITY_EMOJIS[current_rarity]} {current_rarity}",
                        value="• " + "\n• ".join(rarity_mobs),
                        inline=False,
                    )
                current_rarity = rarity
                rarity_mobs = [mob_name]
            else:
                rarity_mobs.append(mob_name)

        if current_rarity and rarity_mobs:
            embed.add_field(
                name=f"{RARITY_EMOJIS[current_rarity]} {current_rarity}",
                value="• " + "\n• ".join(rarity_mobs),
                inline=False,
            )

        embed.set_footer(
            text=(
                f"Page {page}/{total_pages} ({total_mobs} total mobs) | Use {self.bot.command_prefix}mobs <page> to navigate\n"
                f"Use {self.bot.command_prefix}mobs <rarity> to filter by rarity\n"
                f"Use {self.bot.command_prefix}mob <mob_name> for more information about a specific mob"
            )
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
