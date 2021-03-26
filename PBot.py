import discord
import nacl
import os
import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
import urllib.parse, urllib.request, re
from time import sleep
from datetime import datetime

bot = commands.Bot(command_prefix='.')
no_access = " You don't have access to this command :/"
owner = '<@!435088789048918017>'
thumbs_up = '\N{THUMBS UP SIGN}'
que = []
repeatMusic = False


def read_token():
    with open('token.txt', 'r') as f:
        lines = f.readlines()
        return lines[0].strip()


token = read_token()


@bot.event
async def on_ready():
    print('-----_____ BOT ONLINE _____-----')


# stupid commands
@bot.event
async def on_message(messages):
    mention = f'<@!{bot.user.id}>'
    if messages.content == 'gay confirmed?':
        await messages.channel.send('Indeed!')
    if mention in messages.content.split():
        await messages.channel.send('Hey, i am just a bot :frowning: , try mentioning someone else!')
    await bot.process_commands(messages)


# mention owner
@bot.command()
async def owner(ctx):
    await ctx.send('I was programmed by <@!435088789048918017>')


# get bot ping
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms ')


# create channels
@bot.command(aliases=['create', 'Create', 'CREATE'])
async def _create(ctx, category: discord.CategoryChannel = '', *, text=''):
    count = 0
    if category == '' and text == '':
        await ctx.send('`.create (valid category) (channels names separated by ;)`')
    else:
        if ctx.message.author.guild_permissions.manage_channels:
            channels = str(text).split(';')
            for channel in channels:
                await ctx.guild.create_text_channel(channel, category=category)
                count += 1
        else:
            await ctx.send(no_access)
            return
        await ctx.send(f'Created {count} Text channels!')


# delete channels
@bot.command(aliases=['DELETE', 'Delete', 'delete'])
async def _delete(ctx, *, channels_roles=""):
    count = 0
    if ctx.message.author.guild_permissions.manage_channels:
        if channels_roles == "":
            await ctx.send('`.delete (channel names separated by a ; )`')
            return
        x = channels_roles.split(';')
        for Channel in x:
            channel = discord.utils.get(ctx.guild.text_channels, name=Channel)
            await channel.delete()
            count += 1
    else:
        await ctx.send(no_access)
    await ctx.send(f'deleted {count} channels!')


# create categories
@bot.command(aliases=['CreateCategory', 'createCategory', 'createcategory'])
async def _CreateCategory(ctx, *, text=''):
    if ctx.message.author.guild_permissions.manage_channels:
        count = 0
        if text == '':
            await ctx.send('`.createcategory (Category names separated with ;)`')
            return
        categories = text.split(';')
        for category in categories:
            await ctx.guild.create_category(category)
            count += 1
    else:
        await ctx.send(no_access)
    await ctx.send(f'Created {count} Categories!')


# delete categories
@bot.command(aliases=['deleteCategory', 'DeleteCategory', 'deletecategory'])
async def _deletecAtegory(ctx, *, categories=""):
    count = 0
    if ctx.message.author.guild_permissions.manage_channels:
        if categories == "":
            await ctx.send('`.deletecategory (valid Category names separated ; )`')
            return
        x = categories.split(';')
        for Category in x:
            category = discord.utils.get(ctx.guild.categories, name=Category)
            for channel in category.text_channels:
                await channel.delete()
            await category.delete()
            count += 1
    else:
        await ctx.send(no_access)
        return
    await ctx.send(f'Deleted {count} Categories!')


# MUSICCCCCCCCCCCC
# ---------------------
# ---------------------
# join voice
@bot.command(aliases=['connect', 'CONNECT', 'Connect', 'join', 'JOIN', 'Join'])
async def _join(ctx):
    try:
        await ctx.author.voice.channel.connect()
    except:
        await ctx.send(':x: **I am already connected to another channel.**')


# play music
@bot.command(aliases=['play', 'p', 'Play', 'PLAY'])
async def _playcommand(ctx, *, search: str):
    global que
    try:
        await ctx.author.voice.channel.connect()
    except:
        if ctx.author.voice.channel == ctx.voice_client.channel:
            print('already in voice channel')
        else:
            await ctx.send(':x: **I am being controlled by another voice channel **:confused:')
            return
    if 'https://' in search:
        url = search
    else:
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
        que.append(player)
    else:
        que.append(player)


def play_next(voice):
    try:
        player = que.pop(0)
        voice.play(player, after=lambda x=None: play_next(voice))
    except:
        pass

#
# @bot.command()
# async def repeat(ctx):
#     global repeatMusic
#     if repeatMusic:
#         repeatMusic = False
#         await ctx.send("**Song will not be repeated** :thumbsup:")
#     else:
#         repeatMusic = True
#         await ctx.send("**Song will be repeated** :thumbsup:")


# disconnect from voice
@bot.command(aliases=['disconnect', 'DISCONNECT', 'Disconnect', 'leave', 'LEAVE', 'Leave', 'dc', 'DC', 'Dc'])
async def _leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    await voice.disconnect()
    await ctx.send('**Successfully disconnected** :thumbsup:')


@bot.command()
async def clearqueue(ctx):
    global que
    await ctx.message.add_reaction(thumbs_up)
    que.clear()


# pause music
@bot.command()
async def pause(ctx):
    if ctx.author.voice.channel == ctx.voice_client.channel:
        try:
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            voice.pause()
        except:
            await ctx.send(':x: **I am not connected to a voice channel.** Type `.join` to get me in one')
            return
        await ctx.message.add_reaction(thumbs_up)
    else:
        await ctx.send(':x: **I am being controlled by another voice channel **:confused:')


# stop music
@bot.command(aliases=['skip', 'next', 's'])
async def _skipcommand(ctx):
    if ctx.author.voice.channel == ctx.voice_client.channel:
        try:
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            voice.stop()
        except:
            await ctx.send(':x: **I am not connected to a voice channel.** Type `.join` to get me in one')
            return
        await ctx.message.add_reaction(thumbs_up)
    else:
        await ctx.send(':x: **I am being controlled by another voice channel **:confused:')


# resume music
@bot.command()
async def resume(ctx):
    if ctx.author.voice.channel == ctx.voice_client.channel:
        try:
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            voice.resume()
        except:
            await ctx.send(':x: **I am not connected to a voice channel.** Type `.join` to get me in one')
            return
        await ctx.message.add_reaction(thumbs_up)
    else:
        await ctx.send(':x: **I am being controlled by another voice channel **:confused:')
    await play_next(voice)


# clear message
@bot.command()
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


# kick members
@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)


# ban members
@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)


@bot.command()
async def inviteme(ctx):
    await ctx.send(
        'Here is the link to invite me to a server! : https://discord.com/api/oauth2/authorize?client_id=821806637496008745&permissions=8&scope=bot')


bot.run(token)
