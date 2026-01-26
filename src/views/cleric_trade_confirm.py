import discord
from database.collection import Collection
from database.user import User
from database.inventory import Inventory


class ClericTradeConfirm(discord.ui.View):
    def __init__(self, bot, guild_id, user_id, mob_id, mob_amount, token_id, token, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.guild_id = guild_id
        self.user_id = user_id
        self.mob_id = mob_id
        self.mob_amount = mob_amount
        self.token_id = token_id
        self.token = token

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This trade isn't for you.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success, emoji="✅")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        Collection.remove_mob(self.bot.db, self.guild_id, self.user_id, self.mob_id, self.mob_amount)
        Inventory.add_to_inventory(self.bot.db, self.guild_id, self.user_id, self.token_id, self.mob_amount // 2)

        button.disabled = True

        embed = discord.Embed(
            title="✅ Trade Completed",
            description=f"You traded **{self.mob_amount}** mobs for **{self.mob_amount // 2} {self.token['name']}** tokens.",
            colour=discord.Colour.green(),
        )

        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
