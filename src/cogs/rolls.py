import discord
from discord.ext import commands
import random
from discord import Colour
from db.collection import Collection
from db.user import User
import time
from collections import defaultdict

RARITY_WEIGHTS = {"Common": 55, "Uncommon": 25, "Rare": 13, "Epic": 6, "Legendary": 1}
RARITY_COLORS = {
    "Common": Colour.light_grey(),
    "Uncommon": Colour.green(),
    "Rare": Colour.blue(),
    "Epic": Colour.purple(),
    "Legendary": Colour.orange(),
}
RARITY_EMERALD_REWARDS = {
    "Common": 1,
    "Uncommon": 2,
    "Rare": 4,
    "Epic": 8,
    "Legendary": 15,
}


class Rolls(commands.Cog):
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
    async def reroll(self, ctx):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        now = int(time.time())

        User.ensure_user(self.bot.db, guild_id, user_id)

        if User.has_claimed_today(self.bot.db, guild_id, user_id, now):
            await ctx.send("❌ You've already claimed today.")
            return

        if User.has_rerolled_today(self.bot.db, guild_id, user_id, now):
            await ctx.send("❌ You've already rerolled today.")
            return

        mob_id, mob = self.roll_random_mob()

        User.record_reroll(self.bot.db, guild_id, user_id, now)

        embed = discord.Embed(
            title=mob["name"],
            color=RARITY_COLORS.get(mob["rarity"], 0x2F3136),
        )
        embed.set_image(url=mob["image"])
        embed.set_footer(text=f"Rerolled by: {ctx.author.display_name}")

        await ctx.send(
            embed=embed,
            view=Claim(bot=self.bot, guild_id=guild_id, user_id=ctx.author.id, mob_id=mob_id, mob=mob),
        )

    @commands.command()
    async def roll(self, ctx):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        now = int(time.time())

        User.ensure_user(self.bot.db, guild_id, user_id)

        # if User.has_claimed_today(self.bot.db, guild_id, user_id, now):
        #     await ctx.send("❌ You've already claimed today.")
        #     return

        # cooldown = User.get_roll_cooldown(self.bot.db, guild_id, user_id, now)
        # if cooldown > 0:
        #     minutes = cooldown // 60
        #     if minutes == 0:
        #         msg = "⏳ You can roll again in less than a minute."
        #     else:
        #         msg = f"⏳ You can roll again in **{minutes} minutes**."
        #     await ctx.send(msg)
        #     return

        mob_id, mob = self.roll_random_mob()

        User.record_roll(self.bot.db, guild_id, user_id, now)

        embed = discord.Embed(
            title=mob["name"],
            color=RARITY_COLORS.get(mob["rarity"], 0x2F3136),
        )
        embed.set_image(url=mob["image"])
        embed.set_footer(text=f"Rolled by: {ctx.author.display_name}")

        await ctx.send(
            embed=embed,
            view=Claim(bot=self.bot, guild_id=guild_id, user_id=ctx.author.id, mob_id=mob_id, mob=mob),
        )

    def roll_random_mob(self):
        rarity = Rolls.roll_rarity()
        mob = random.choice(self.bot.mobs_by_rarity[rarity])
        return mob, self.bot.mobs[mob]

    @staticmethod
    def roll_rarity():
        rarities = list(RARITY_WEIGHTS.keys())
        weights = list(RARITY_WEIGHTS.values())
        return random.choices(rarities, weights=weights, k=1)[0]

    def build_collection_embed(self, ctx, rows):
        mobs_by_rarity = defaultdict(list)

        for row in rows:
            mob = self.bot.mobs[row["mob_id"]]
            mobs_by_rarity[mob["rarity"]].append(f"{mob['name']} x{row['quantity']}")

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


class Claim(discord.ui.View):
    def __init__(self, bot, guild_id: int, user_id: int, mob_id: str, mob: dict):
        super().__init__(timeout=3600)
        self.bot = bot
        self.guild_id = guild_id
        self.user_id = user_id
        self.mob_id = mob_id
        self.mob = mob

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Only the player who rolled this card can claim it.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Claim!", style=discord.ButtonStyle.secondary, emoji="🔥")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        now = int(time.time())
        reward = RARITY_EMERALD_REWARDS[self.mob["rarity"]]

        Collection.add_to_collection(self.bot.db, self.guild_id, self.user_id, self.mob_id)
        User.update_last_claim_at(self.bot.db, self.guild_id, self.user_id, now)
        User.add_emeralds(self.bot.db, self.guild_id, self.user_id, reward)

        button.disabled = True
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"🗸 Claimed by: {interaction.user.display_name}")
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(
            f"✅ {self.mob['rarity']} {self.mob['name']} claimed!\n💎 +{reward} emerald{'s' if reward != 1 else ''}!"
        )
        self.stop()


async def setup(bot):
    await bot.add_cog(Rolls(bot))
