import discord 
from discord.ext import commands
import os
import asyncio
from config import token, prefix
import checks
import traceback


# Create a bot instance
client = commands.Bot(command_prefix=prefix, intents=discord.Intents.all(), case_insensitive=True)


# Sync command for slash commands
@client.command(name="sync")
@checks.isme()
async def sync(ctx):
    await client.tree.sync()
    embed = discord.Embed(title="🔄 Slash Commands Synced", color=0xff0000)
    await ctx.send(embed=embed)



@client.command(hidden=True)
@checks.isme()
async def uall(ctx):
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != 'checks.py' and filename != 'config.py':
            try:
                await client.unload_extension(f'cogs.{filename[:-3]}')
            except Exception as e:
                print(f"Failed to unload {filename}: {e}")

@client.command(hidden=True)
@checks.isme()
async def lall(ctx):
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != 'checks.py' and filename != 'config.py':
            try:
                await client.load_extension(f'cogs.{filename[:-3]}')
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

@client.command(hidden=True)
@checks.isme()
async def rall(ctx):
    try:
        await ctx.invoke(client.get_command('uall'))
        await ctx.invoke(client.get_command('lall'))
        embed = discord.Embed(title="🔄 ALL COGS RELOADED", color=0xff0000)
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="❌ ERROR RELOADING COGS", color=0xff0000)
        await ctx.send(embed=embed)
        print(f"Error reloading cogs: {e}")
        traceback.print_exc()

# Function to load all cogs at startup asynchronously
async def load_all_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != 'checks.py' and filename != 'config.py':
            try:
                await client.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")


# Entry point to run the bot
async def main():
    '''Printed messages are so you can see them in the console when the bot starts, if it was all in one line you might ignore it in the code.'''

    print("Messages will be logged, make sure you have consent from everyone in the guild before logging messages.")
    print("Do not use this bot in a guild without consent.")
    print("This bot is not responsible for any abuse.")
    print("This bot is not responsible for any misuse.")
    print("This bot is not responsible for any illegal actions.")
    print("This bot is not responsible for any illegal activities.")
    print("This bot is not responsible for any illegal usage.")
    print("Cogs loading...")
    await load_all_cogs()
    await client.start(token)

# Start the bot
if __name__ == "__main__":
    asyncio.run(main())
