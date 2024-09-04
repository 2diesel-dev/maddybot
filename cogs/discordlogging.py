import discord
from discord.ext import commands
from datetime import timezone, datetime
import os
import asqlite
import checks
from config import prefix

class Logging(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def log_to_log(self, guild_id: int, channel_id: int, channel_name: str, member_id: int, member_name: str, message_id: int, message_content: str):
        '''Saves the message to a log file'''
        now = datetime.now(timezone.utc).strftime("%H:%M:%S %d-%m-%Y")
        os.makedirs(f".logs/{guild_id}", exist_ok=True)
        log_entry = f'{now}: {member_name} ({member_id}) said: \"{message_content}\" in: {channel_name} ({channel_id}) message_id: {message_id}\n'

        try:
            with open(f".logs/{guild_id}/{member_id}.log", "a") as f:
                f.write(log_entry)
            with open(f".logs/{guild_id}/master.log", "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log: {e}")

    async def create_db(self, name: str):
        async with asqlite.connect(f"{name}.db") as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    guild_id INTEGER, channel_id INTEGER, channel_name TEXT,
                    member_id INTEGER, member_name TEXT, message_id INTEGER,
                    message_content TEXT, time TEXT)
            """)
            await conn.commit()

    async def log_to_db(self, guild_id: int, channel_id: int, channel_name: str, member_id: int, member_name: str, message_id: int, message_content: str):
        '''Saves the message to a database'''
        db_name = f"{guild_id}_logs"
        await self.create_db(db_name)
        now = datetime.now(timezone.utc).strftime("%H:%M:%S %d-%m-%Y")
        async with asqlite.connect(f"{db_name}.db") as conn:
            await conn.execute("""
                INSERT INTO logs 
                (guild_id, channel_id, channel_name, member_id, member_name, message_id, message_content, time) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (guild_id, channel_id, channel_name, member_id, member_name, message_id, message_content, now))
            await conn.commit()

    async def create_master_db(self):
        async with asqlite.connect("master_logs.db") as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS master_logs (
                    guild_id INTEGER, channel_id INTEGER, channel_name TEXT,
                    member_id INTEGER, member_name TEXT, message_id INTEGER,
                    message_content TEXT, time TEXT)
            """)
            await conn.commit()

    async def log_to_master_db(self, guild_id: int, channel_id: int, channel_name: str, member_id: int, member_name: str, message_id: int, message_content: str):
        '''Saves the message to a master database'''
        now = datetime.now(timezone.utc).strftime("%H:%M:%S %d-%m-%Y")
        async with asqlite.connect("master_logs.db") as conn:
            await conn.execute("""
                INSERT INTO master_logs 
                (guild_id, channel_id, channel_name, member_id, member_name, message_id, message_content, time) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (guild_id, channel_id, channel_name, member_id, member_name, message_id, message_content, now))
            await conn.commit()

    async def quick_txt(self, logtype: str, guild_id: int, amount: int, member_id: int = None):
        '''Opens the database, saves the last x entries to a text file'''
        log_file = '.logs/temp.log'
        try:
            if logtype == 'member':
                async with asqlite.connect("logs.db") as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute("""
                            SELECT * FROM logs WHERE guild_id = ? AND member_id = ?
                        """, (guild_id, member_id))
                        rows = await cursor.fetchall()
                        # Select the last `amount` rows (newest entries)
                        rows = rows[-amount:]
                        rows.reverse()
                        with open(log_file, 'w') as f:
                            # Write rows in reverse order to show newest first
                            for row in reversed(rows):
                                f.write(f'{row[7]}: {row[4]} ({row[3]}) said: \"{row[6]}\" in: {row[2]} ({row[1]}) message_id: {row[5]}\n')
            elif logtype == 'master':
                async with asqlite.connect("master_logs.db") as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute("""
                            SELECT * FROM master_logs WHERE guild_id = ?
                        """, (guild_id))
                        rows = await cursor.fetchall()
                        # Select the last `amount` rows (newest entries)
                        rows = rows[-amount:]
                        rows.reverse()
                        with open(log_file, 'w') as f:
                            # Write rows in reverse order to show newest first
                            for row in reversed(rows):
                                f.write(f'{row[7]}: {row[4]} ({row[3]}) said: \"{row[6]}\" in: {row[2]} ({row[1]}) message_id: {row[5]}\n')
            return log_file
        except Exception as e:
            print(f"Error during quick_txt: {e}")
            return None

    @commands.command(hidden=False)
    @checks.isme()
    async def get_member_logs(self, ctx, member: discord.Member, amount: int):
        '''Gets the last x logs of a member'''
        log_file = await self.quick_txt('member', ctx.guild.id, amount, member.id)
        if log_file:
            await ctx.send(file=discord.File(log_file))
            os.remove(log_file)

    @commands.command(hidden=False)
    @checks.isme()
    async def get_master_logs(self, ctx, amount: int):
        '''Gets the last x logs of the server'''
        log_file = await self.quick_txt('master', ctx.guild.id, amount)
        if log_file:
            await ctx.send(file=discord.File(log_file))
            os.remove(log_file)
            
    @commands.command(hidden=False, aliases=['show'])
    @checks.isme()
    async def send_all_master_logs(self, ctx):
        '''Sends all master.log files'''
        for dirpath, _, filenames in os.walk('.logs'):
            for filename in filenames:
                if filename == 'master.log':
                    await ctx.send(file=discord.File(os.path.join(dirpath, filename)))

    @commands.command(hidden=False)
    @checks.isme()
    async def get_member_logs_id(self, ctx, member_id: int, amount: int):
        '''Gets the last x logs of a member by ID'''
        log_file = await self.quick_txt('member', ctx.guild.id, amount, member_id)
        if log_file:
            await ctx.send(file=discord.File(log_file))
            os.remove(log_file)


    @commands.command(hidden=False)
    @checks.isme()
    async def send(self, ctx, id: int = None):
        '''Sends the log file of a member by ID'''
        if id:
            log_file = f'.logs/{ctx.guild.id}/{id}.log'
            if os.path.exists(log_file):
                await ctx.send(file=discord.File(log_file))
            else:
                await ctx.send(f'No log file found for {id}')
        if not id:
            log_file = f'.logs/{ctx.guild.id}/master.log'
            if os.path.exists(log_file):
                await ctx.send(file=discord.File(log_file))
            else:
                await ctx.send('No master log file found')
        

    @commands.Cog.listener()
    async def on_message(self, message):

        list_to_ignore = [12345, 6789] # Add user IDs to ignore here

        if message.author == self.client.user or message.guild is None or not message.content or message.attachments or message.author.bot or message.content.startswith(prefix) or message.author.id in list_to_ignore:
            return

        print(f'{message.author.name} ({message.author.id}) said: \"{message.content}\" in: {message.channel.name} ({message.channel.id}) message_id: {message.id}')
        await self.log_to_log(message.guild.id, message.channel.id, message.channel.name, message.author.id, message.author.name, message.id, message.content)
        await self.log_to_db(message.guild.id, message.channel.id, message.channel.name, message.author.id, message.author.name, message.id, message.content)
        await self.log_to_master_db(message.guild.id, message.channel.id, message.channel.name, message.author.id, message.author.name, message.id, message.content)

    @commands.command(hidden=False)
    @checks.isme()
    async def send_member_log(self, ctx, member: discord.Member):
        '''Sends the log file of a member'''
        log_file = f'.logs/{ctx.guild.id}/{member.id}.log'
        if os.path.exists(log_file):
            await ctx.send(file=discord.File(log_file))
        else:
            await ctx.send(f'No log file found for {member.name}')


    @commands.command(hidden=False)
    @checks.isme()
    async def send_master_log(self, ctx):
        '''Sends the master log file'''
        log_file = f'.logs/{ctx.guild.id}/master.log'
        if os.path.exists(log_file):
            await ctx.send(file=discord.File(log_file))
        else:
            await ctx.send('No master log file found')

    @commands.Cog.listener()
    async def on_ready(self):
        await self.create_master_db()

async def setup(client):
    await client.add_cog(Logging(client))
