from discord import Intents
import discord
from discord.ext import commands
from discord.utils import get
import random
import os
from dadjokes import Dadjoke
import aiohttp
import json
import datetime
import asyncio
from better_profanity import profanity

bot = commands.Bot(command_prefix = '~', case_insensitive = True, description = "The Nebula Bot is THE PLAYER ZER0's Discord.py rewrite bot for The Nebula!", help_command=None)

# Message Managing

@bot.event
async def censor():
    profanity.load_censor_words_from_file('assets/blacklist/blacklist.txt')

@bot.event
async def censortwo(message):
	isBadWord = profanity.contains_profanity(message.content)
	if isBadWord:
		await message.delete()

@bot.event
async def on_message_delete(message):

    channel = bot.get_channel(732849621864546334)
    embed = discord.Embed(title=f"{message.author} message has deleted a message", description=f"{message.content}", color=0x9370DB)

    await channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.NotOwner):
        await ctx.send("Only administrator's have permission to use this command!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to use this command!")
    else:
      	await ctx.send("Sorry but you have tried a command that doesn't work or doesn't exist! Check the help command list for a list of commands! Or, ask Zachary (THE PLAYER ZER0) for help if you have any further questions!")
        
@bot.event
async def on_member_join(member):
    with open('assets/json/users.json', 'r') as f:
        users = json.load(f)
    await update_data(users, member)
    
    with open("assets/json/users.json", 'w') as f:
        json.dump(users, f, indent=4)
    print(f"{member} has joined the server!")
    channel = bot.get_channel(775528645447516188)
    embed = discord.Embed(title = "A new member has joined!", description = f"{member} has join our Discord server!", color=0x9370DB)
    embed.set_footer(text="Please welcome them to the server!")
    
    await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    print(f"{member} has left the server.")
    channel = bot.get_channel(775528645447516188)
    embed = discord.Embed(title = "A member has left!", description = f"{member} has left our Discord!", color=0x9370DB)
    embed.set_footer(text="Say farewell to them as they embark on their new journey!")
    await channel.send(embed=embed)

# Cogs

for filename in os.listdir("./cogs"):
  if filename.endswith(".py"):
    bot.load_extension(f"cogs.{filename[:-3]}")

# Moderation commands

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You need to specify an amount!")
    if isinstance(error, commands.BadArgument):
        await ctx.send("Give a number to clear!")
        
    raise error

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
  await member.kick(reason=reason)
  await ctx.send(f"Kicked {member.mention}")
  
@kick.error
async def kick_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send("Sorry but you missing something in your attempt to kick someone. Please check over your message and try again!")
          
  raise error

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
  await member.ban(reason=reason)
  
@ban.error
async def ban_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send("Sorry but you missing something in your attempt to ban a user. Please check over your message and try again!")
          
  raise error

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
  banned_users = await ctx.guild.bans()
  member_name, member_discriminator = member.split("#")

  for ban_entry in banned_users:
    user = ban_entry.user

    if (user.name, user.discriminator) == (member_name, member_discriminator):
      await ctx.guild.unban(user)
      await ctx.send(f"Unbanned {user.mention}")
      return

@bot.command(aliases=["whois", "user", "info"])
@commands.is_owner()
async def userinfo(ctx, member: discord.Member = None):
    member = ctx.author if not  member else member
    if not member:  # if member is no mentioned
        member = ctx.message.author  # set member as the author
    roles = [role for role in member.roles]
    embed = discord.Embed(color=0x9370DB, timestamp=ctx.message.created_at,
                          title=f"User Info - {member}")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}")

    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Display Name:", value=member.display_name)
    embed.add_field(name="Bot?", value=member.bot)

    embed.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p CDT"))
    embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p CDT"))

    embed.add_field(name="Roles:", value="".join([role.mention for role in roles[1:]]))
    roles.append('@everyone')  # set string @everyone instead of role
    embed.add_field(name="Highest Role:", value=member.top_role.mention)
    await ctx.send(embed=embed)

@userinfo.error
async def info_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('I could not find that member...')

@bot.command()
@commands.is_owner()
async def reload(ctx, cog):
    try:
        bot.unload_extension(f"cogs.{cog}")
        bot.load_extension(f"cogs.{cog}")
        await ctx.send(f"{cog} got reloaded")
    except Exception as e:
        print(f"{cog} can not be reloaded:")
        raise e

# Custom commands

@bot.event
async def on_message(message):
    if message.author.bot == False:
        with open("assets/json/users.json", "r") as f:
            users = json.load(f)
            
        await update_data(users, message.author)
        await add_experience(users, message.author, 5)
        await level_up(users, message.author, message)
        
        with open("assets/json/users.json", "w") as f:
            json.dump(users, f, indent=4)
            
    await bot.process_commands(message)
    
async def update_data(users, user):
    if not f"{user.id}" in users:
        users[f"{user.id}"]["experience"] = 0
        users[f"{user.id}"]["level"] = 1
        
async def add_experience(users, user, exp):
    users[f"{user.id}"]["experience"] += exp
    
async def level_up(users, user, message):
    with open("assets/json/levels.json", "r") as g:
        levels = json.load(g)
    experience = users[f"{user.id}"]["experience"]
    lvl_start = users[f"{user.id}"]["level"]
    lvl_end = int(experience ** (1/4))
    if lvl_start < lvl_end:
        await message.channel.send(f"{user.mention} has leveled up to level {lvl_end}")
        users[f"{user.id}"]["level"] = lvl_end
        
@bot.command(aliases=["level"])
async def rank(ctx, member: discord.Member = None):
    if not member:
        id = ctx.message.author.id
        with open("assets/json/users.json", "r") as f:
            users = json.load(f)
        lvl = users[str(id)]["level"]
        await ctx.send(f"You are at level {lvl}!")
    else:
        id = member.id
        with open("assets/json/users.json", "r") as f:
            users = json.load(f)
        lvl = users[str(id)]["level"]
        await ctx.send(f"{member} is at level {lvl}!")

@bot.command(aliases=["her", "she"])
async def female(ctx):
    member = ctx.message.author
    role = get(member.guild.roles, name="she/her")
    await member.add_roles(role)
    await ctx.send("You will now be referred to by your name, she, and/or her!")
    
@bot.command(aliases=["him", "male"])
async def he(ctx):
    member = ctx.message.author
    role = get(member.guild.roles, name="he/him")
    await member.add_roles(role)
    await ctx.send("You will now be referred to by your name, he, and/or him!")
    
@bot.command(aliases=["them"])
async def they(ctx):
    member = ctx.message.author
    role = get(member.guild.roles, name="they/them")
    await member.add_roles(role)
    await ctx.send("You will now be referred to by your name, they, and/or them!")

@bot.command()
async def ping(ctx):
  await ctx.send(f"Pong! || {round(bot.latency * 1000)}ms")

@bot.command()
async def advice(ctx):
    await ctx.send("Be patient. This command is coming soon!")

@bot.command()
async def poetry(ctx):
    await ctx.send("Patience is a virtue. This command is coming soon!")

@bot.command(aliases=["py"])
async def python(ctx):
  await ctx.send("I am running on an unknown version of python!")

@bot.command(aliases=["hoster"])
async def host(ctx):
    await ctx.send("I am being hosted by Discloud!\n\nHere's the link to the hoster: https://discloudbot.com/")

@bot.command(aliases=["ms"])
async def monsterfight(ctx):
  await ctx.send("I think that Godzilla would win! After all, he *__is__* the King of the Monsters!")

@bot.command()
async def foo(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def snap(ctx):
  await ctx.send("Mr. Stark? I don't feel so good!")

@bot.command()
async def online(ctx):
  await ctx.send("I am online at the moment. If I am not online, you'll notice that my commands aren't working!")

@bot.command(aliases=["favoritesong", "fs"])
async def favsong(ctx):
  await ctx.send("Currently, Grace's favorite song is Geronimo by Sheppard! Here's a link to the song: https://www.youtube.com/watch?v=E-SeaCZE2TM")

@bot.command()
async def creation(ctx):
  await ctx.send("I was created on Wednesday, April 21st, 2021!")

@bot.command(aliases=["rd"])
async def releasedate(ctx):
  await ctx.send("There is no concrete release date for any of The LoveGlace Saga's content! Grace will announce one once he is certain he can make it!")

@bot.command()
async def mcjh(ctx):
  await ctx.send("Zachary Lovelight is a young Mage who was attacked by a mysterious masked personage. After narrowly escaping from Him through a portal, he finds himself stuck in the world of Minecraft.\n\nHowever, he swiftly finds out that he is not alone when someone by the initials T.G.D. reaches out to him, promising him a way to escape as long as he goes on a journey for Her.\n\nWhat will happen next? Watch Minecraft: the Journey Home - The Reawakening of the Wither to find out!\n\nPlaylist Link: https://www.youtube.com/playlist?list=PLqWmHBgL2jJHj4A689lAimA18U-mLl6gV")

@bot.command(aliases=["v"])
async def version(ctx):

  em = discord.Embed(title="Version 1.3.1 -- The Censor Update:", description="This version replaces the filter with a new filter that works better and has less words to it.")
  #em = discord.Embed(title="Version 1.3.0:", description = "This version catches the bot up with this bot's sister named The Royal Bot. It adds a censor to any/all sexual, racial, and really anything that could offend people! I also fixed the version number from the previous version which was concurrent with The Royal Bot but is now back to its original version track. I also moved hosting services")

  await ctx.send(embed = em)

@bot.command(aliases=["cancelledseries", "cancel"])
async def cancelled(ctx):
    embed = discord.Embed(title="THE PLAYER ZER0's Cancelled Series", description="This is a list of ALL of Zachary's cancelled game series.")
    
    embed.add_field(name="Toontown Frenchy", value="I might've mentioned this earlier but I cancelled the TTFr series after Bananabeth and some other team members working on Toontown: Market Crash causing the other two to lose interest in the series while I kept it going on for several more episodes before stopping the creation of more episodes because the charm had worn off.", inline=False)
    embed.add_field(name="Let's Play Toontown Rewritten with xEathan06x", value="I'm marking it as cancelled because Ethan and I (from what I understand) don't really want to make this series.", inline=False)
    embed.set_thumbnail(url="https://yt3.ggpht.com/ytc/AAUvwngLzBB2zSK78OHAWHCJ-f7yUgr368Jj7kjCxIoyiw=s176-c-k-c0x00ffffff-no-rj")

    await ctx.send(embed=embed)
    
@bot.command(aliases=["favChannel", "favChannels", "favoriteChannel", "favoriteChannels", "favoriteYouTubeChannel"])
async def favoriteYouTubeChannels(ctx):
    embed = discord.Embed(title="THE PLAYER ZER0's favorite channels", description="This is a list of THE PLAYER ZER0's favorite YouTube channels")
    
    embed.add_field(name="1. Zanny", value="Zanny is a great YouTuber that Zachary strives to be like while keeping the uniqueness of the channel.\n\nhttps://www.youtube.com/user/SirZandril")
    embed.add_field(name="2. SaveAFox", value="SaveAFox is a YouTube channel and a brand that save, among other animals, foxes, squirrels, and more! Their mission is one of the best and they treat their animals right. Check them out!\n\nhttps://www.youtube.com/channel/UCb3KY97ICfIkDJY_p6d7yig")
    embed.add_field(name="3. Nathan Boehm", value="I've known Nathan for about a year now; I actually met his brother back in fifth grade, and what and how he does his content is just to die for! Sure, I may be biased because I've known Nathan and his brother for year(s), but you should go check him out!\n\nhttps://www.youtube.com/channel/UCzyNaprXvVOKZgX85tq-RBg")

    await ctx.send(embed=embed)

@bot.command(aliases=["upcomingseries"])
async def upcoming(ctx):
    embed = discord.Embed(title="THE PLAYER ZER0's Upcoming Series", description="This is a list of ALL of Zachary's upcoming series on THE PLAYER ZER0!", color=0xAAFFAA, url="https://www.youtube.com/channel/UCG0OvtYX4qA6Ap1OxQpohOA/videos")
    
    embed.add_field(name="Minecraft: The Journey Home", value="Zachary Lovelight is a young Mage who was attacked by a mysterious masked personage. After narrowly escaping from Him through a portal, he finds himself stuck in the world of Minecraft.\n\nHowever, he swiftly finds out that he is not alone when someone by the initials T.G.D. reaches out to him, promising him a way to escape as long as he goes on a journey for Her.\n\nWhat will happen next? Watch Minecraft: the Journey Home - The Reawakening of the Wither to find out! / No release date yet.", inline=False)
    embed.add_field(name="Let's Play Minecraft", value="Just a regular-old Minecraft Modded Let's Play! / Releasing on November 12th, 2021.", inline=False)
    embed.add_field(name="Let's Play LEGO Harry Potter", value="This is my next flag ship series after I finish LEGO Star Wars: Season 1 but before I start season 2 of Let's Play LEGO Star Wars")
    embed.add_field(name="Let's Play Genshin Impact", value="This is going to be up there with Blessed on my most graphical series ever but it won't be as bad as previous seasons of Blessed were. This series has no concrete release date.")
    embed.add_field(name="Let's Play Star Wars: The Old Republic", value="This will be another Star Wars series but this time, I shouldn't have graphical issues with this series because of how old the game is!")
    embed.set_thumbnail(url="https://yt3.ggpht.com/ytc/AAUvwngLzBB2zSK78OHAWHCJ-f7yUgr368Jj7kjCxIoyiw=s176-c-k-c0x00ffffff-no-rj")

    await ctx.send(embed=embed)

@bot.command(aliases=["ongoingseries"])
async def ongoing(ctx):

    embed = discord.Embed(title="THE PLAYER ZER0's Ongoing Series", description="This is a list of ongoing series' on THE PLAYER ZER0", color=0xAAFFAA, url="https://www.youtube.com/playlist?list=PLqWmHBgL2jJEyixhIBxq3MTDg6KWEPtOw")

    embed.add_field(name="Let's Play LEGO Star Wars", value="1 Season, 61 Episodes / December 5th, 2020 - Present Day / Status: Alive", inline=False)
    embed.add_field(name="Club Penguin Island: Offline Mode", value="2 Seasons, 13 Episodes / July 11th, 2020 - Present Day / Status: Alive", inline=False)
    embed.add_field(name="Blessed", value="3 Seasons, 8 Episodes / October 4th, 2020 - Present Day / Status: Dormant", inline=False)
    embed.add_field(name="Let's Play Genshin Impact", value="1 Season, 1 Episode / April 10th, 2021 - Present Day / Status: Alive", inline=False)
    embed.add_field(name="YouTube Alerts", value="2 Seasons, 3 Episodes / August 10th, 2016 - Present Day / Status: Alive", inline=False)
    embed.add_field(name="Toontown's Funny Farm", value="1 Season, 4 Episodes / July 16th, 2020 - Present Day / Status: Dormant", inline=False)
    embed.add_field(name="Toontown Rewritten", value="1 Season, 6 Episodes / July 7th, 2020 / Status: Dormant", inline=False)
    embed.add_field(name="Clash 'n Task", value="1 Season, 3 Episodes / June 22nd, 2020 - Present Day / Status: Dormant", inline=False)
    #embed.add_field(name="Untitled Goose Game", value="1 Season, 4 Episodes / July 19th, 2020 - August 10th, 2020 / Status: Completed", inline=False)
    #embed.add_field(name="Toontown Frenchy", value="1 Season, 12 Episodes / July 26th, 2020 - December 17th, 2020 / Status: Cancelled", inline=False)
    embed.set_thumbnail(url="https://yt3.ggpht.com/ytc/AAUvwngLzBB2zSK78OHAWHCJ-f7yUgr368Jj7kjCxIoyiw=s176-c-k-c0x00ffffff-no-rj")

    await ctx.send(embed=embed)

@bot.command(aliases=["statistics", "youtube", "youtubestats", "THEPLAYERZER0", "THEPLAYERZERO", "subs", "subscribers", "views", "videos"])
async def stats(ctx):
  async with aiohttp.ClientSession() as session:
    async with session.get("https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UCG0OvtYX4qA6Ap1OxQpohOA&key=AIzaSyDqVdu61QOeF18-MS4MfN4ejejb4Bm0s8A") as response:
      subs = (await response.json())["items"][0]["statistics"]["subscriberCount"]
      views = (await response.json())["items"][0]["statistics"]["viewCount"]
      videos = (await response.json())["items"][0]["statistics"]["videoCount"]
      embed = discord.Embed(title="THE PLAYER ZER0", description="", color=0x9370DB, url="https://www.youtube.com/channel/UCG0OvtYX4qA6Ap1OxQpohOA")
      embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
      embed.set_thumbnail(url="https://yt3.ggpht.com/ytc/AAUvwngLzBB2zSK78OHAWHCJ-f7yUgr368Jj7kjCxIoyiw=s176-c-k-c0x00ffffff-no-rj")
      
      embed.add_field(name="Subscriber Count:", value=f"{subs}")
      embed.add_field(name="Viewer Count:", value=f"{views}")
      embed.add_field(name="Video Count:", value=f"{videos}")
    
      embed.set_footer(text=f"THE PLAYER ZER0 is currently at {subs} subscribers, {views} views, and has {videos} videos!")
      await ctx.send(embed=embed)
      await session.close()

@bot.command(aliases=["subscribergoal"])
async def subgoal(ctx):
  #await ctx.send("His subscriber goal is to surpass his previous main channel called Zachary StarBlade")
  await ctx.send("After achieving his initial goal to surpass Zachary Starblade on his subscriber count, his new goal is to surpass his first YouTube channel 320zachary which, at last count, had 100 subscribers.")
  #await ctx.send("THE PLAYER ZER0's third goal is to surpass Nathan Boehm's channel.")
  #await ctx.send("After achieving his third goal to surpass Nathan Boehm's subscriber count of 207, THE PLAYER ZER0's newest goal is to surpass his friend Stealth Bre's subscriber count of 241")

@bot.command()
async def goal(ctx):
  await ctx.send("THE PLAYER ZER0's goal, that isn't a subscriber-related is that he wants to be able to finish at least 1 complete let's play series which he very nearly completed until LEGO Star Wars: The Force Awakens came along, then it ended up being paused until a later date!")

@bot.command(aliases=["ff"])
async def funfact(ctx):
  await ctx.send("This feature is under construction. Try again later!")

@bot.command()
async def catfact(ctx):
  async with aiohttp.ClientSession() as session:
    async with session.get("https://catfact.ninja/fact") as response:
      fact = (await response.json())["fact"]
      length = (await response.json())["length"]
      embed = discord.Embed(title=f'Random Cat Fact Number: **{length}**', description=f'Cat Fact: {fact}', color=0x9370DB)
      embed.set_footer(text="")
      await ctx.send(embed=embed)
      await session.close()

@bot.command()
async def cat(ctx):
    await ctx.send("Here's a picture of Pancha and Ollie!", file=discord.File('assets/images/Cat.jpg'))

@bot.command()
async def dog(ctx):
    await ctx.send("Here's a picture of Pancha and Ollie!", file=discord.File('assets/images/Cat.jpg'))

@bot.command(aliases=["memes"])
async def meme(ctx):
  await ctx.send("Sorry but this feature is coming as soon as Zachary figures out how to import APIs to the bot!")

@bot.command(aliases=["dadjoke"])
async def dadjokes(ctx):
  dadjoke = Dadjoke()
  await ctx.send(dadjoke.joke)

# Do a Word of Wisdom generator
# Add a Poetry API
# Add a Fun Fact API and mix it with my fun facts
# Horoscope giver for specific horoscope

@bot.command()
async def links(ctx):
  await ctx.send("|\nMy Discords:\nPLAYER ZER0 STUDIOS: https://discord.com/invite/XJRNv3eNmY\nThe Nebula: https://discord.com/invite/wwkh4w9\n\nYouTube Channels:\n- THE PLAYER ZER0: https://www.youtube.com/channel/UCG0OvtYX4qA6Ap1OxQpohOA\n- PLAYER ZER0 STUDIOS: https://www.youtube.com/channel/UCP3Wq0hfaNJJif3ZKk2q8pA\n- PLAYER ZER0 ARCHIVES: https://www.youtube.com/channel/UCLO1uJK-2yu3CuXgIvwmaag\n- Arbitrium TV: https://www.youtube.com/channel/UCoYDqXueFCvlRAgqJwtmiiw\n\nWebsites:\n-THE PLAYER ZER0: https://www.theplayerzero.com\n-PLAYER ZER0 STUDIOS: https://www.playerzerostudios.com\n-Arbitrium TV: https://www.arbitriumtv.com\n|")

@bot.command(aliases=["invites"])
async def invite(ctx):
  await ctx.send("Here is the invite link to the PLAYER ZER0 STUDIOS Discord: https://discord.gg/9fgW8jAaf6\n\nAnd here's the link to the other Discord that I am in called The Nebula: https://discord.com/invite/wwkh4w9\n\nMore links can be found by using the `~links` command!")

@bot.command(aliases=["comingsoon"])
async def features(ctx):
  await ctx.send("Some features that Grace wants to add to me, ay? Well, video streaming between friends, Music Player, add webhooks to announce various things from YouTube video releases to Tweets, leveling system with cool perks, role-giving system, and more! But don't count on a release date for these features!")

# Custom Help Command

@bot.group(aliases=["pages"], invoke_without_command=True)
async def help(ctx):
    contents = ["Moderation Commands: `~clear`, `~kick`, `~ban`, `~unban`, `~whois`, `~reload`", "Technical Commands: `~version`, `~ping`, `~cog`, `~test`, `~python`, ", "Fun Commands: `~funfact` / `~ff` `~creation`, `~favsong / ~favoriteSong`, `~online`, `~snap`, `~monsterfight`, `~meme`, `~dadjokes`, `~tarot / ~pickacard / ~pick-a-card`, `~oracle / ~oraclecards / ~oraclecard / ~angelcards / ~angelcard`, `~wisdom / ~wordsofwisdom`, `~advice`, `~catfact`", "YouTube Commands: `~mcjh`, `~releasedate` / `~rd`, `statistics, youtube, youtubestats, THEPLAYERZER0, THEPLAYERZERO, subs, subscribers, views, videos`, `~subGoal`, `~Goal`, `~cancelled`, `~upcoming`, `~ongoing`", "Other Commands: `~links`, `~features`, `~she / ~her / ~female`, `~him / ~his / ~male`, `~they / ~them`"]
    pages = 5
    cur_page = 1
    
    message = await ctx.send(f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
    # getting the message object for editing and reacting

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", check=check)
            # waiting for a reaction to be added - times out after x seconds, 60 in this
            # example

            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except asyncio.TimeoutError:
            break
            # would end the loop if user doesn't react after x seconds but the timer is gone...

@help.error
async def help_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send("The command you have given me cannot be found! Please check the ~help command for all commands!")
    
# Moderation Commands for the Help Command:

@help.command()
async def clear(ctx):

  em = discord.Embed(title = "~Clear", description = "Clears messages for given number of messages!", color=0x2ECC71)

  await ctx.send(embed = em)

@help.command()
async def kick(ctx):

  em = discord.Embed(title = "~Kick", description = "Kicks the mentioned member from the Discord with out without reason!", color=0x2ECC71)

  await ctx.send(embed = em)

@help.command()
async def ban(ctx):

  em = discord.Embed(title = "~Ban", description = "Bans the mentioned member from the Discord with or without reason!", color=0x2ECC71)

  await ctx.send(embed = em)

@help.command()
async def unban(ctx):

  em = discord.Embed(title = "~Unban", description = "Unbans a member from the Discord!", color=0x2ECC71)

  await ctx.send(embed = em)

@help.command(aliases=["whois", "user", "info"])
async def userinfo(ctx):

  em = discord.Embed(title = "~WhoIs", description = "Tells the user who the mentioned user is.", color=0x2ECC71)

  await ctx.send(embed = em)

@help.command(aliases=["addbadword"])
async def addbannedword(ctx):

  em = discord.Embed(title = "~AddBannedWord", description = "Adds a banned word to the list of bad words!", color=0x2ECC71)

  await ctx.send(embed = em)

@help.command(aliases=["removebadword"])
async def removebannedword(ctx):

  em = discord.Embed(title = "~RemoveBannedWord", description = "Removes a banned word to the list of bad words!", color=0x2ECC71)

  await ctx.send(embed = em)

@help.command()
async def reload(ctx):

  em = discord.Embed(title = "~Reload", description = "Reloads the mentioned Cog!", color=0x2ECC71)

  await ctx.send(embed = em)

# Technical Commands for the Help Command:

@help.command()
async def version(ctx):

  em = discord.Embed(title = "~Version", description = "Tells the current version of the bot!", color=0xE67E22)

  await ctx.send(embed = em)

@help.command()
async def ping(ctx):

  em = discord.Embed(title = "~Ping", description = "Says 'Pong!' and gives the time it took to reply (in miliseconds)!", color=0xE67E22)

  await ctx.send(embed = em)

@help.command(aliases=["cogs"])
async def cog(ctx):

  em = discord.Embed(title = "~Cog / ~Cogs", description = "Tells you that the bot now uses Cogs!", color=0xE67E22)

  await ctx.send(embed = em)

@help.command(aliases=["Test"])
async def test(ctx):

  em = discord.Embed(title = "~Test", description = "Tells you that the Cogs are working.", color=0xE67E22)

  await ctx.send(embed = em)

@help.command(aliases=["py"])
async def python(ctx):

  em = discord.Embed(title = "~Python", description = "Tells you what version of Python I am running on!.", color=0xE67E22)

  await ctx.send(embed = em)

# Fun Commands for the Help Command:

@help.command(aliases=["ff"])
async def funfact(ctx):

  em = discord.Embed(title="~funfact / ~ff", description = "Gives a random fun fact from a number of given fun facts!", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command()
async def creation(ctx):

  em = discord.Embed(title = "~creation", description = "This command tells you my conception date and birth date!", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["favsong", "fs"])
async def favoritesong(ctx):

  em = discord.Embed(title = "~favoritesong / ~favsong", description = "Gives Zachary's current favorite song!", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command()
async def online(ctx):

  em = discord.Embed(title = "~online", description = "Tells you whether or not the bot is online or not.", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command()
async def snap(ctx):

  em = discord.Embed(title = "~snap", description = "It's a reference to Tom Holland's infamous improvised line in the climax of Avengers: Infinity War.", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["ms"])
async def monsterfight(ctx):

  em = discord.Embed(title = "~monsterFight / ~ms", description = "It's my prediction of which Monster will win in the Monster-verse's newest movie called Godzilla vs. Kong!", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command()
async def meme(ctx):

  em = discord.Embed(title = "~meme", description = "Sends a random meme from a API of memes", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command()
async def dadjokes(ctx):

  em = discord.Embed(title = "~dadJokes", description = "Once implemented, it will generate a Dad Joke from a database.", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command()
async def tarot(ctx):

  em = discord.Embed(title = "~Tarot:", description = "Gives a random tarot card plus a paragraph to determine what it means **__NOTE__**: This is meant for ENTERTAINMENT purposes ONLY.", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["cat"])
async def dog(ctx):

  em = discord.Embed(title = "~Dog / ~Cat:", description = "Sends a picture of Ollie and Pancha, THE PLAYER ZER0's dog and cat.", color=0xAAFFAA)

  await ctx.send(embed = em)
    
@help.command()
async def catfact(ctx):

  em = discord.Embed(title = "~CatFact:", description = "Gives a random cat fact.", color=0xAAFFAA)

  await ctx.send(embed = em)

# The LoveGlace Saga Commands for the Help Command:

@help.command()
async def mcjh(ctx):

  em = discord.Embed(title = "~mcjh:", description = "Upon usage, it provides a description for Minecraft: the Journey Home - The Reawakening of the Wither along with a link to the playlist.", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["rd"])
async def releasedate(ctx):

  em = discord.Embed(title = "~releasedate / ~rd:", description = "When used, it gives the release date for The Lovelight Saga's newest, upcoming series/movie!", color=0xAAFFAA)

  await ctx.send(embed = em)

# YouTube Commands for the Help Command:

@help.command(aliases=["cancelled", "cancelledseries"])
async def cancel(ctx):
    
  em = discord.Embed(title = "~Cancelled", desciption = "Gives the user a list of cancelled series's on THE PLAYER ZER0's YouTube channel", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["ongoingseries"])
async def ongoing(ctx):
    
  em = discord.Embed(title="~Ongoing", desciption = "Gives a list of ongoing series' on THE PLAYER ZER0", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["upcomingseries"])
async def upcoming(ctx):
    
  em = discord.Embed(title="~Upcoming", description = "Gives a list of upcoming series' on THE PLAYER ZER0", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["statistics", "youtube", "youtubestats", "THEPLAYERZER0", "THEPLAYERZERO", "subs", "subscribers", "views", "videos"])
async def stats(ctx):

  em = discord.Embed(title = "~Statistics:", description = "Gives the current number of Subscribers, view count, and video count for THE PLAYER ZER0!", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["subscribergoal"])
async def subgoal(ctx):

  em = discord.Embed(title = "~subGoal / ~subscriberGoal", description = "Gives Zachary's current Subscriber goal for his YouTube channel!", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command()
async def goal(ctx):

  em = discord.Embed(title = "~Goal", description = "Gives Zachary current goal for his YouTube channel that isn't related to subscribers!", color=0xAAFFAA)

  await ctx.send(embed = em)

# Other Commands for the Help Command:

@help.command()
async def links(ctx):

  em = discord.Embed(title = "~links", description = "Gives links that are listed in #links", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["comingsoon"])
async def features(ctx):

  em = discord.Embed(title = "~features / ~ComingSoon", description = "Gives a list of features that Zachary wants to add to me!", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["her"])
async def she(ctx):

  em = discord.Embed(title = "~she / ~her / ~female", description = "Gives the user the she/her role so that people know what to refer to the user by!", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["him"])
async def he(ctx):

  em = discord.Embed(title = "~he / ~him / ~male", description = "Gives the user the he/him role so that people know what to refer to the user by!", color=0xAAFFAA)

  await ctx.send(embed = em)

@help.command(aliases=["them"])
async def they(ctx):

  em = discord.Embed(title = "~they / ~them", description = "Gives the user the they/them role so that people know what to refer to the user by!", color=0xAAFFAA)

  await ctx.send(embed = em)

# Ending

bot.run("insert_your_token_here")