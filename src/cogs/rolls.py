import discord
from discord.ext import commands
import random
from database.user import User
import time
from views.claim import Claim
from constants import RARITY_WEIGHTS, RARITY_COLORS, VALID_TOKEN_RARITIES
from datetime import datetime, timezone


class Rolls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reroll(self, ctx):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        now = int(time.time())

        User.ensure_user(self.bot.db, guild_id, user_id)
        user = User.get_user(self.bot.db, guild_id, user_id)

        user_trading_hall_level = user["trading_hall_level"] if user else 0
        if user_trading_hall_level < self.bot.villagers["toolsmith"]["level"]:
            await ctx.send(
                "❌ Your village doesn't have a Toolsmith yet! Upgrade your Trading Hall to get one reroll per day."
            )
            return

        last_claim_at = user["last_claim_at"] if user else 0
        if same_utc_day(last_claim_at, now):
            await ctx.send("❌ You've already claimed today.")
            return

        last_reroll_at = user["last_reroll_at"] if user else 0
        if same_utc_day(last_reroll_at, now):
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

        guild_id = ctx.guild.id
        user_id = ctx.author.id
        now = int(time.time())

        User.ensure_user(self.bot.db, guild_id, user_id)
        user = User.get_user(self.bot.db, guild_id, user_id)

        if mode is None:
            roll_type = "standard"
        elif mode == "focus":
            user_trading_hall_level = user["trading_hall_level"] if user else 0
            if user_trading_hall_level < self.bot.villagers["librarian"]["level"]:
                await ctx.send(
                    "❌ Your village doesn't have a Librarian yet! Upgrade your Trading Hall to get one focus roll per day."
                )
                return
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

        last_claim_at = user["last_claim_at"] if user else 0
        if same_utc_day(last_claim_at, now):
            await ctx.send("❌ You've already claimed today.")
            return

        last_roll_at = user["last_roll_at"] if user else None
        cooldown = get_cooldown_remaining(last_roll_at, now, 3600)
        if cooldown > 0:
            minutes = cooldown // 60
            if minutes == 0:
                msg = "⏳ You can roll again in less than a minute."
            else:
                msg = f"⏳ You can roll again in **{minutes} minutes**."
            await ctx.send(msg)
            return

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


async def setup(bot):
    await bot.add_cog(Rolls(bot))


def same_utc_day(ts1: int, ts2: int) -> bool:
    d1 = datetime.fromtimestamp(ts1, tz=timezone.utc).date()
    d2 = datetime.fromtimestamp(ts2, tz=timezone.utc).date()
    return d1 == d2


def get_cooldown_remaining(last_action_ts: int | None, now_ts: int, cooldown_seconds: int) -> int:
    if last_action_ts is None:
        return 0

    elapsed = now_ts - last_action_ts
    return max(0, cooldown_seconds - elapsed)