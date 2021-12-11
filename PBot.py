import discord
import youtube_dl
from discord.ext import commands
import urllib.parse, urllib.request, re
from time import sleep
from datetime import datetime
from discord_together import DiscordTogether

bot = commands.Bot(command_prefix='.')
no_access = " You don't have access to this command :/"
owner = '<@!435088789048918017>'
thumbs_up = '\N{THUMBS UP SIGN}'
que = []
repeatMusic = False
url = ''


def read_token():
    with open('token.txt', 'r') as f:
        lines = f.readlines()
        return lines[0].strip()


token = read_token()


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for the . Prefix"))
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
        await ctx.author.voice.channel.connect()
    else:
        await ctx.send(':x: **You should be in a voice channel to use this command**')



# play music
@bot.command(aliases=['play', 'p', 'Play', 'PLAY'])
async def _playCommand(ctx, *, search: str):
    global que
    global url
    
    
    
    if ctx.author.voice:
        if !ctx.voice_client.channel:
            await ctx.author.voice.channel.connect()
        elif ctx.author.voice.channel != ctx.voice_client.channel:
            await ctx.send(':x: **I am being controlled by another voice channel **:confused:')
    else:
        await ctx.send(':x: **You should be in a voice channel to use this command**')
    
    
#     try:
#         await ctx.author.voice.channel.connect()
#     except:
#         if ctx.author.voice.channel == ctx.voice_client.channel:
#             print('already in voice channel')
#         else:
#             await ctx.send(':x: **I am being controlled by another voice channel **:confused:')
#             return
    if 'https://' in search:
        url = search
    else:
        await ctx.send(f'`searching for {search}`')
        query_string = urllib.parse.urlencode({'search_query': search})
        htm_content = urllib.request.urlopen(
            'http://www.youtube.com/results?' + query_string)
        search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
        url = 'http://www.youtube.com/watch?v=' + search_results[0]
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    ydl_opts = {'format': 'best'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(str(url), download=False)
        URL = info['formats'][0]['url']
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn', }
    player = discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)
    if len(que) == 0:
      voice.play(player, after=lambda x=None: play_next(voice))
      await ctx.send('**Song is being played**')
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

# clear message
@bot.command()
@has_permissions(manage_messages=True)
async def purge(ctx, ammount=1):
    await ctx.channel.purge(limit=ammount)


@bot.command()
async def calendar(ctx, user: discord.User = '', *, text=''):
    if user == '' and text == '':
        await ctx.send(f'`.calendar @user context;d/m/y;h:m`')
    else:
        loop = 'yes'
        context = text.split(';')[0]
        date = text.split(';')[1]
        time = text.split(';')[2]
        hour = time.split(':')[0]
        minutes = time.split(':')[1]
        await ctx.send(f'I will remind {user.mention} to: {context} at {date}')
        print(f'{date} / {time} / {hour} / {minutes}')
        print(datetime.now().strftime("%x"))
        print(datetime.now().strftime("%H"))
        print(datetime.now().strftime("%M"))
        while loop == 'yes':
            if date == datetime.now().strftime("%x").replace('0', '') and hour == datetime.now().strftime(
                    "%H") and minutes == datetime.now().strftime("%M"):
                await ctx.send(f'Hello, {user.mention}, i was told to remind you to: {context}')
                loop = 'no'


@bot.command()
async def remind(ctx, user: discord.User = '', *, text=''):
    if user == '' and text == '':
        await ctx.send(f'`.remind @user context;timer;unit(s / m / h)`')
    else:
        context = text.split(';')[0]
        time = int(text.split(';')[1])
        smh = text.split(';')[2]
        if smh == 's':
            time = time / 60
        elif smh == "m":
            time = time
        elif smh == 'h':
            time = time * 60
        await ctx.send(f'I will remind {user.mention} to: {context} after {time} minutes')
        sleep(time * 60)
        await ctx.send(f'Hello, {user.mention}, i was told to remind you to: {context}')
        
        
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


# kick members
@bot.command()
@has_permissions(manage_messages=True, manage_roles=True, manage_channels=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)


# ban members
@bot.command()
@has_permissions(manage_messages=True, manage_roles=True, manage_channels=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)


@bot.command()
async def inviteme(ctx):
    await ctx.send(
        'Here is the link to invite me to a server! : https://discord.com/api/oauth2/authorize?client_id=821806637496008745&permissions=8&scope=bot')


bot.run(token)
