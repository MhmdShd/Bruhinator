import discord
import youtube_dl
from discord.ext import commands
import urllib.parse, urllib.request, re
from time import sleep
from datetime import datetime
from discord_together import DiscordTogether
from discord.ext.commands import has_permissions

bot = commands.Bot(command_prefix='.')
no_access = " You don't have access to this command :/"
thumbs_up = '\N{THUMBS UP SIGN}'
que = []
url = ''
bot.remove_command('help')

def read_token():
    with open('token.txt', 'r') as f:
        lines = f.readlines()
        return lines[0].strip()


token = read_token()


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for .help"))
    bot.togetherControl = await DiscordTogether(token)
    print('-----_____ BOT ONLINE _____-----')
    print(f'{len(bot.guilds)}')

# stupid commands
@bot.event
async def on_message(messages):
    mention = f'<@!{bot.user.id}>'
    if messages.content == 'gay confirmed?':
        await messages.channel.send('Indeed!')
    if mention in messages.content.split():
        await messages.channel.send('Hey, i am just a bot :frowning: , try mentioning someone else!')
    await bot.process_commands(messages)



# get bot ping
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms ')



# MUSICCCCCCCCCCCC
# ---------------------
# ---------------------
# join voice
@bot.command(aliases=['connect', 'CONNECT', 'Connect', 'join', 'JOIN', 'Join'])
async def _joinCommand(ctx):
    if ctx.author.voice:
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        elif ctx.author.voice.channel != ctx.voice_client.channel:
            await ctx.send(':x: **I am being controlled by another voice channel **:confused:')
    else:
        await ctx.send(':x: **You should be in a voice channel to use this command**')

# play music
@bot.command(aliases=['play', 'p', 'Play', 'PLAY'])
async def _playCommand(ctx, *, search: str):
    global que
    global url

    if ctx.author.voice:
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        elif ctx.author.voice.channel != ctx.voice_client.channel:
            await ctx.send(':x: **I am being controlled by another voice channel **:confused:')
            
    else:
        await ctx.send(':x: **You should be in a voice channel to use this command**')
        
    if ctx.author.voice and ctx.voice_client.channel == ctx.author.voice.channel:
        if 'https://' in search:
            url = search
        else:
            query_string = urllib.parse.urlencode({'search_query': search})
            htm_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
            search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
            url = 'http://www.youtube.com/watch?v=' + search_results[0]
            await ctx.send(f'**searching for** `{search}`')
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        ydl_opts = {'format': 'best'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(str(url), download=False)
            URL = info['formats'][0]['url']
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn', }
        player = discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)
        if len(que) == 0:
            voice.play(player, after=lambda x=None: play_next(voice))
            await ctx.send('**Song is being played**\ntype `.link` to send video link!')
            que.append(player)
        else:
            await ctx.send(f'**Song queued** {thumbs_up}')
            que.append(player)
def play_next(voice):
    try:
        player = que.pop(0)
        voice.play(player, after=lambda x=None: play_next(voice))
    except:
        pass


@bot.command()
async def link(ctx):
    global url
    await ctx.send(f'song being played: {url}')



# disconnect from voice
@bot.command(aliases=['disconnect', 'DISCONNECT', 'Disconnect', 'leave', 'LEAVE', 'Leave', 'dc', 'DC', 'Dc'])
async def _leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not ctx.voice_client:
        await ctx.send(':x: **I am not in a voice channel **:confused:')
    else:
        if ctx.author.voice:
            if ctx.author.voice.channel == ctx.voice_client.channel:
                await voice.disconnect()
                await ctx.send('**Successfully disconnected** :thumbsup:')
            else:
                await ctx.send('**You should be in my voice channel to use this command**')
        else:
            await ctx.send("**You should be in my voice channel to use this command**")


@bot.command()
async def clearqueue(ctx):
    global que
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not ctx.voice_client:
        await ctx.send(':x: **I am not in a voice channel **:confused:')
    else:
        if ctx.author.voice:
            if ctx.author.voice.channel == ctx.voice_client.channel:
                await ctx.message.add_reaction(thumbs_up)
                que.clear()
            else:
                await ctx.send('**You should be in my voice channel to use this command**')
        else:
            await ctx.send("**You should be in my voice channel to use this command**")


# pause music
@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if ctx.voice_client:
        if ctx.author.voice:
            if ctx.author.voice.channel == ctx.voice_client.channel:
                voice.pause()
                await ctx.message.add_reaction(thumbs_up)
            else:
                await ctx.send(':x: **I am being controlled by another voice channel **:confused:')
        else:
            await ctx.send("**You should be in my voice channel to use this command**")
    else:
        await ctx.send(':x: **I am not connected to a voice channel.** Type `.join` to get me in')


# stop music
@bot.command(aliases=['skip', 'next', 's'])
async def _skipcommand(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if ctx.voice_client:
        if ctx.author.voice:
            if ctx.author.voice.channel == ctx.voice_client.channel:
                voice.stop()
                await ctx.message.add_reaction(thumbs_up)
            else:
                await ctx.send(':x: **I am being controlled by another voice channel **:confused:')
        else:
            await ctx.send("**You should be in my voice channel to use this command**")
    else:
        await ctx.send(':x: **I am not connected to a voice channel.** Type `.join` to get me in')

# resume music
@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if ctx.voice_client:
        if ctx.author.voice:
            if ctx.author.voice.channel == ctx.voice_client.channel:
                voice.resume()
                await ctx.message.add_reaction(thumbs_up)
            else:
                await ctx.send(':x: **I am being controlled by another voice channel **:confused:')
        else:
            await ctx.send("**You should be in my voice channel to use this command**")
    else:
        await ctx.send(':x: **I am not connected to a voice channel.** Type `.join` to get me in')


        
@bot.command()
async def activity(ctx,*,text=''):
    if (text == ''):
        embed = discord.Embed(
            title="Activites Available:\n",
            description=f"1. youtube\n2. poker\n3. chess\n4. betrayal\n5. fishing\n6. awkword\n7. spellcast \n8. doodle-crew\n9. word-snack\n10. letter-tile\n11. checkers",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)
    if (ctx.author.voice):
        print('true')
        link = await bot.togetherControl.create_link(ctx.author.voice.channel.id, text)
        text = text.replace('-',' ')
        embed = discord.Embed(
            title=f"Your Activity is ready!\n",
            description=f"[{text}]({link})",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send('Please connect to a voice channel first!')



@bot.command()
async def help(ctx):
    embed = discord.Embed(title = 'Help Center',description='**Music commands!**:\n\n1. `.join` **( i join your voice chat if i am free )**\n2. `.play [song name/link]` **( plays song! )**\n3. `.dc` / `.leave` /`.disconnect` **( i disconnect :( )**\n4. `.skip` / `.pause` / `.resume` / `.clearqueue` **( i think these are clear :D )**\n5. `.help` **( displays this message )** \n\n\n**Activities command!**\n\n1. `.activity [activity name]` **( sends a link with your desired activity! / without [activity name] i list all available activities )** \n\nadd Andr0x#8929 for support and suggestions',color= discord.Color.green()
    )
    await ctx.send(embed = embed)


bot.run(token)
