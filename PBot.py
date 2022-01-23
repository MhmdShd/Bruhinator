import discord
import yt_dlp
from discord.ext import commands
import urllib.parse, urllib.request, re
from discord_together import DiscordTogether
import asyncio

bot = commands.Bot(command_prefix='.')
no_access = " You don't have access to this command :/"
thumbs_up = '\N{THUMBS UP SIGN}'
cross = '❌'
que = []
url = ''
bot.remove_command('help')

def read_token():
    with open('token.txt', 'r') as f:
        lines = f.readlines()
        return lines[0].strip()


token = read_token()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title=f"Error!!!", description=f"Command not found.\n\n`.help` for the list of commands", color=discord.Color.red())
        try:
            await ctx.send(embed = embed)
        except:
            try:
                await ctx.send('no Perms to send **Embedded content** :( !')
            except:
                # await ctx.message.author.send("I have no access to that channel.")
                pass



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
        await messages.channel.send('Hey, i am just a bot :frowning: , try typing `.help`!')
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
    print(f"[.join], from [{ctx.message.guild.name}]")
    if ctx.author.voice:
        VoiceChannel = ctx.author.voice.channel
        if not ctx.voice_client:
            if VoiceChannel.permissions_for(ctx.guild.me).connect:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("**I don't have access to your channel **:(")
        elif ctx.author.voice.channel != ctx.voice_client.channel:
            await ctx.send(':x: **I am being controlled by another voice channel **:confused:')
    else:
        await ctx.send(':x: **You should be in a voice channel to use this command**')

# play music
@bot.command(aliases=['play', 'p', 'Play', 'PLAY'])
async def _playCommand(ctx, *, search: str):
    print(f"[.play], from [{ctx.message.guild.name}]")
    global que
    global url

    if ctx.author.voice:
        VoiceChannel = ctx.author.voice.channel
        if not ctx.voice_client:
            if VoiceChannel.permissions_for(ctx.guild.me).connect:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("**I don't have access to your channel **:(")
        elif ctx.author.voice.channel != ctx.voice_client.channel:
            await ctx.send(':x: **I am being controlled by another voice channel **:confused:')

    else:
        await ctx.send(':x: **You should be in a voice channel to use this command**')

    if ctx.author.voice and ctx.voice_client.channel == ctx.author.voice.channel:
        if 'https://' in search or 'http://' in search:
            url = search
        else:
            query_string = urllib.parse.urlencode({'search_query': search})
            htm_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
            search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
            url = 'http://www.youtube.com/watch?v=' + search_results[0]
            await ctx.send(f':mag: **searching for** `{search}`')
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        ydl_opts = {'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(str(url), download=False)
            duration = info['duration']/60
            duration = str(duration).replace('.',':')[0:5]
            title = info['title']
            channel = info['channel']
            channel_url = info['channel_url']
            URL = info['formats'][3]['url']

        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn', }
        player = discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)
        if len(que) == 0:
            voice.play(player, after=lambda x=None: play_next(voice))
            embed = discord.Embed(title="Song played:", description=f"**Channel :** [{channel}]({channel_url})\n\n[{title}]({url})\n\n\nduration:  {duration}",color=discord.Color.blue())
            await ctx.send(embed=embed)
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
    print(f"[.link], from [{ctx.message.guild.name}]")
    global url
    await ctx.send(f'song being played: {url}')


# disconnect from voice
@bot.command(aliases=['disconnect', 'DISCONNECT', 'Disconnect', 'leave', 'LEAVE', 'Leave', 'dc', 'DC', 'Dc'])
async def _leave(ctx):
    print(f"[.dc], from [{ctx.message.guild.name}]")
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
    print(f"[.clearqueue], from [{ctx.message.guild.name}]")
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
    print(f"[.pause], from [{ctx.message.guild.name}]")
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
    print(f"[.skip], from [{ctx.message.guild.name}]")
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
    print(f"[.resume], from [{ctx.message.guild.name}]")
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
    print(f"[.activity], from [{ctx.message.guild.name}]")
    if (text == ''):
        embed = discord.Embed(
            title="Activites Available (by name):\n",
            description=f"1. youtube\n2. poker\n3. chess\n4. betrayal\n5. fishing\n6. awkword\n7. spellcast \n8. doodle-crew\n9. word-snack\n10. letter-tile\n11. checkers\n\nuse .activity `activity name`",
            color=discord.Color.purple()
        )
        try:
            await ctx.send(embed = embed)
        except:
            try:
                await ctx.send('no Perms to send **Embedded content** :( !')
            except:
                await ctx.message.author.send("I have no access to that channel.")
    elif text != '':
        if (ctx.author.voice):
            if text == 'youtube' or text == 'chess' or text == 'poker' or text == 'betrayal' or text == 'fishing' or text == 'awkword' or text == 'spellcast' or text == 'doodle-crew' or text == 'word-snack' or text == 'letter-tile' or text == 'checkers':
                try:
                    link = await bot.togetherControl.create_link(ctx.author.voice.channel.id, text)
                except:
                    await ctx.send("I need Permission to **create invite** to your voice channel!")
            else:
                await ctx.send(f"**{text}** is not a valid activity! (`.activity` for the available list)")
            text = text.replace('-',' ')
            embed = discord.Embed(
                title=f"Your Activity is ready!\n",
                description=f"[{text}]({link})",
                color=discord.Color.green()
            )
            try:
                await ctx.send(embed = embed)
            except:
                try:
                    await ctx.send('no Perms to send **Embedded content** :( !')
                except:
                    await ctx.message.author.send("I have no access to that channel.")
        else:
            try:
                await ctx.send('Please connect to a voice channel first!')
            except:
                await ctx.message.author.send("I have no access to that channel.")


@bot.command()
async def start(ctx,*, text=''):
    if text == '':
        await ctx.send(f'`.start #channel;timer;unit(s/m/h/d);first_message;second_message`')
    else:
        Channel = text.split(';')[0].replace(' ','')
        delay = text.split(';')[1]
        smh = text.split(';')[2].lower()
        first = text.split(';')[3]
        second = text.split(';')[4]
        time = int(delay)
        if smh == 's':
            unit = 'Second(s)'
            time = time / 60
        elif smh == "m":
            unit = "Minute(s)"
            time = time
        elif smh == 'h':
            unit = "Hour(s)"
            time = time * 60
        elif smh == 'd':
            unit = "day(s)"
            time = time * 60 * 24
        time = time * 60
        for channel in ctx.guild.channels:
            if str(Channel) == "<#" + str(channel.id) + ">":
                message = await ctx.send(f'<@{ctx.message.author.id}>, Timer started in <#{channel.id}> for {delay} {unit}.')
                if first != ' ':
                    await channel.send(first)
                while float(time) > 0:
                    hours = int(time / 3600)
                    minutes = int(((time % 3600) / 3600) * 60)
                    seconds = int((((time % 3600) % 60) / 60) * 60)
                    time -= 5
                    await message.edit(content=f'<@{ctx.message.author.id}>, message will be sent in {hours}:{minutes}:{seconds}.')
                    await asyncio.sleep(5)
                await channel.send(second)
                await message.edit(content=f'<@{ctx.message.author.id}>, message sent in <#{channel.id}>.')


@bot.command()
async def remind(ctx, *, text=''):
    if text == '':
        await ctx.send(f'`.remind Context;Duration;unit(s / m / h)`')
    else:
        user = ctx.message.author
        unit = 'null'
        context = text.split(';')[0]
        time = float(text.split(';')[1])
        smh = text.split(';')[2]
        duration = time
        if smh == 's':
            unit = 'Second(s)'
            time = time / 60
        elif smh == "m":
            unit = "Minute(s)"
            time = time
        elif smh == 'h':
            unit = "Hour(s)"
            time = time * 60
        await ctx.send(f'I will remind {user.mention} about: **{context}** after {duration} {unit}')
        time *= 60
        while float(time) >= 0:
            await asyncio.sleep(2)
            print(time)
            time -= 2
        await ctx.send(f'Hello, {user.mention}, i was told to remind you about: {context}')




@bot.command()
async def servers(ctx):
    print(f"[.server], from [{ctx.message.guild.name}]")
    await ctx.send(f'{len(bot.guilds)}')
    

@bot.command()
async def serversinv(ctx):
    print(f"[.serverinv], from [{ctx.message.guild.name}]")
    for guild in bot.guilds:
        for c in guild.text_channels:
            if c.permissions_for(guild.me).create_instant_invite:
                invite = await c.create_invite()
                await ctx.send(invite)
                break
    

@bot.command()
async def help(ctx):
    print(f"[.help], from [{ctx.message.guild.name}]")
    embed = discord.Embed(title = 'Help Center ( Prefix: `.`)',description=f'**Music commands!**:\n\n'
                                                            '1. `.join` **( i join your voice chat if i am free )**\n'
                                                            '2. `.play [song name/link]` **( plays song! )**\n'
                                                            '3. `.dc` / `.leave` /`.disconnect` **( i disconnect D: )**''\n'
                                                            '4. `.skip` / `.pause` / `.resume` / `.clearqueue` **( i think these are clear :D )**''\n'
                                                            '\n\n'
                                                            '**Activities command!:**'
                                                            '\n\n'
                                                            '1. `.activity [activity name]` **( sends a link with your desired activity! / without [activity name] i list all available activities )** \n\n\n'
                                                            '**Others!:**\n'
                                                            '\n1. `.remind` **(i remind you about anything at any time you want)**'
                                                            '\n2. `.start` **(i send a schedualed message in any channel that I have access to)**'
                                                            '\n3. `.help` **( displays this message )** '
                                                            '\n\n'
                                                            '**The Nexus**\n'
                                                            f'[invite me](https://discord.com/oauth2/authorize?client_id=821806637496008745&permissions=36816960&scope=bot)\n\n'
                                                            'Created by: Andr0x#8929 feel free to add for support / suggestions'
                                                            '\n', color=discord.Color.green()
    )
    try:
        await ctx.send(embed = embed)
    except:
        try:
            await ctx.send('no Perms to send **Embedded content** :( !')
        except:
            await ctx.message.author.send("I have no access to that channel.")
bot.run(token)
