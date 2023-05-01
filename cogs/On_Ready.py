import discord
from discord.ext import commands
import random
import asyncio

class Ready(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.Cog.listener()
  async def on_ready(self):
    print('The Royal Bot is ready to server Her magesty!')

    statuses = [" '~' to use my commands", " around with Witchcraft!", " with The Goddess", " a chill game", " with THE PLAYERs", " video games!", " Toontown", " Wizard101", " The Gateway", " Toontown in VR", " with Tarot Cards", " Minecraft", " LEGO Star Wars", " Genshin Impact", " Club Penguin", " Club Penguin Island", " Halo", " LEGO Universe", " Star Wars games", " Among Us", " Pirates of the Caribbean Online", " Discord", " Toontown: Corporate Clash", " a LEGO game"]
    
    while not self.bot.is_closed():
        status = random.choice(statuses)
        
        await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Game(status))
        
        await asyncio.sleep(900)

  #game = discord.Game("around with Witchcraft!")
  #await bot.change_presence(status=discord.Status.dnd, activity=game)

def setup(bot):
  bot.add_cog(Ready(bot))