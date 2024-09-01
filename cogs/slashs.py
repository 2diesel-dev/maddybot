import discord
from discord.ext import commands
from discord import app_commands
from checks import has_manage_messages_permission

class Slashs(commands.Cog):
    def __init__(self, client):
        self.client = client
        

    @app_commands.command(name="hello", description="Sends a greeting")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello!", ephemeral=True)

    @app_commands.command(name='send_message', description='Sends a message to a channel by ID')
    @has_manage_messages_permission()
    async def send_message(self, interaction: discord.Interaction, channel: str, message: str):
        channel = self.client.get_channel(int(channel))
        if channel:
            await channel.send(message)
            await interaction.response.send_message(f"Message sent to {channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("Channel not found!", ephemeral=True)

    @app_commands.command(name='commands', description='Lists all commands')
    async def commands(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Commands", color=0xff0000)
        embed.add_field(name="hello", value="Sends a greeting", inline=False)
        embed.add_field(name="send_message", value="Sends a message to a channel by ID", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client):
    await client.add_cog(Slashs(client))
