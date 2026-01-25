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
VALID_TOKEN_RARITIES = ["uncommon", "rare", "epic"]
RARITY_EMOJIS = {
    "Common": ":white_circle:",
    "Uncommon": ":green_circle:",
    "Rare": ":blue_circle:",
    "Epic": ":purple_circle:",
    "Legendary": ":orange_circle:",
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

        # TODO: Check that user has the Toolsmith villager

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
    async def roll(self, ctx, mode: str = None, value: str = None):
        mode = mode.lower() if mode else None
        value = value.lower() if value else None
        if mode is None:
            roll_type = "standard"
        elif mode == "focus":
            # TODO: Logic to check if user has unlocked the Librarian villager
            roll_type = mode
        elif mode == "token":
            if value is None:
                await ctx.send("❌ You must specify a token rarity (e.g. `uncommon`, `rare`, `epic`).")
                return
            if value not in VALID_TOKEN_RARITIES:
                await ctx.send(f"❌ Invalid token rarity. Valid options: {', '.join(VALID_TOKEN_RARITIES)}")
                return
            roll_type = mode
            token_id = f"token_{value}_roll"
        else:
            await ctx.send("❌ Invalid roll type. Try `$roll`, `$roll focus`, or `$roll token <rarity>`.")
            return

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

        if roll_type == "standard":
            mob_id, mob = self.roll_random_mob()
            User.record_roll(self.bot.db, guild_id, user_id, now)
        elif roll_type == "focus":
            if User.has_focus_rolled_today(self.bot.db, guild_id, user_id, now):
                await ctx.send("❌ You've already focus rolled today.")
                return
            mob_id, mob = self.roll_random_mob(exclude={"Common"})
            User.record_focus_roll(self.bot.db, guild_id, user_id, now)
        elif roll_type == "token":
            # TODO: Check if user has token and remove from inventory
            mob_id, mob = self.roll_random_mob(allowed={value.capitalize()})
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

    @commands.command()
    async def mobs(self, ctx, rarity: str = None):
        if rarity:
            await self._mobs_by_rarity(ctx, rarity)
            return

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

    def roll_random_mob(self, exclude=None, allowed=None):
        rarity = Rolls.roll_rarity(exclude, allowed)
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

        if "image" in villager:
            embed.set_thumbnail(url=villager["image"])

        embed.set_footer(text=f"Villager ID: {villager_id}")

        await ctx.send(embed=embed)


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

