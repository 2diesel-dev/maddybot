import discord
from discord.ext import commands
from config import myid
from discord import app_commands

def isme():
    def predicate(ctx):
        return ctx.message.author.id == myid
    return commands.check(predicate)


def has_manage_messages_permission():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.guild_permissions.manage_messages
    return app_commands.check(predicate)