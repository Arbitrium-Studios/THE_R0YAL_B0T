import discord
from discord.ext import commands
import random

class Moderation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

# Moderation commands

  @commands.command()
  @commands.has_permissions(manage_messages=True)
  async def clear(self, ctx, amount=1):
    await ctx.channel.purge(limit=amount)

  @clear.error
  async def clear_error(self, ctx, error):
      if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You need to specify an amount!")
      if isinstance(error, commands.BadArgument):
        await ctx.send("Give a number to clear!")
        
      raise error

  @commands.command()
  @commands.has_permissions(kick_members=True)
  async def kick(self, ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"Kicked {member.mention}")
    
    @kick.error
    async def kick_error(self, ctx, error):
      if isinstance(error, commands.MissingRequiredArgument):
          await ctx.send("Sorry but you missing something in your attempt to kick someone. Please check over your message and try again!")
          
      raise error

  @commands.command()
  @commands.has_permissions(ban_members=True)
  async def ban(self, ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    
    @ban.error
    async def ban_error(self, ctx, error):
      if isinstance(error, commands.MissingRequiredArgument):
          await ctx.send("Sorry but you missing something in your attempt to ban a user. Please check over your message and try again!")

  @commands.command()
  @commands.has_permissions(ban_members=True)
  async def unban(self, ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
      user = ban_entry.user

    if (user.name, user.discriminator) == (member_name, member_discriminator):
        await ctx.guild.unban(user)
        await ctx.send(f"Unbanned {user.mention}")
    return

#@commands.command()
#@commands.has_permissions(administrator=True)
#async def warn(ctx, member: discord.Member=None, *, reason=None)
	#if member is None:
        #return await ctx.send("The provided member could not be found or you forgot to provide one.")
    
    #if reason is None:
        #return await ctx.send("Please provide a reason for warning this user.")
    
    #try:
        #first_warning = False
        #bot.warnings[ctx.guild.id][member.id][0] += 1
        #bot.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, reason))
        
    #except KeyError:
        #first_warning = True
        #bot.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, reason)]]
        
    #count = bot.warnings[ctx.guild.id][member.id][0]
    
    #async with aiofiles.open(f"{ctx.guild.id}.txt", mode="a") as file:
        #await file.write(f"{member.id} {ctx.author.id} {reason}\n")
    
    #await ctx.send(f"{member.mention} has {count} {'warning' if first_warning else 'warnings'}.")
    
#@bot.command()
#@commands.has_permissions(administrator=True)
#async def warnings(ctx, member: discord.Member=None):
    #if member is None:
        #return await ctx.send("The provided member could not be found or you forgot to provide one.")
    
	#embed = discord.Embed(title=f"Displaying warnings for {member.name}", description="", color=discord.Color.red())
    #try:
        #i = 1
        #for admin_id, reason in bot.warnings[ctx.guild.id][member.id][1]:
            #admin = ctx.guild.get_member(admin_id)
            #embed.description += f"**Warning {i}** given by: {admin.mention} for: *'{reason}'*.\n"
            #i += 1
            
        #await ctx.send(embed=embed)
    
    #except KeyError: # no warnings
        #await ctx.send("This user has no warnings.")

def setup(bot):
  bot.add_cog(Moderation(bot))