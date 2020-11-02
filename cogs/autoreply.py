import discord
from datetime import datetime
from discord.ext import commands

class AutoReply(commands.Cog):

  def __init__(self, bot):
        self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.guild:
      #Carb Auto Reply
      if "ticket" in message.channel.name:
        if 'carb256' in message.content.lower():
          await message.channel.send(embed=discord.Embed(title = 'Claiming Carb256',description="To speed up the process of claiming your server please make sure you have ran the '!signup' command, once you've done that please let us know your panel username, the programming language and version you'd like for your server, this makes things easier for you and for us",color=0x0bbfff))

      #Power Issue Auto Reply
      if "support" in message.channel.category.name or "ticket" in message.channel.name:
        if 'power action' in message.content.lower():
          await message.channel.send(embed=discord.Embed(title = 'Event [e71c4b61-a71d-486b-97f2-2931b282b140]: another power action is currently being processed for this server, please try again later',description="This error is caused when trying to start or stop the server when it was already either turning on or off the best fix for this is to wait a few minutes for it to settle into a stable status then try again.",color=0x0bbfff))


      #Power Issue Auto Reply
      if "support" in message.channel.category.name or "ticket" in message.channel.name:
        if 'unexpected error' in message.content.lower():
          await message.channel.send(embed=discord.Embed(title = 'Error Event [9afdd970-8746-488f-abce-a8a719babbbd]: an unexpected error was encountered while handling this request',description="This error is caused due to panel limits, trying to start the server again should fix this issue..",color=0x0bbfff))

      if 'errors' in message.channel.name:
        print('new error message')
        user = self.bot.get_user(int(message.content.split("(",1)[1].split(")",1)[0]))
        print(user)
        await user.dm_channel.send(embed=discord.Embed(title=f" Errors for {user.name}",description=message.content.split(":",1)[1].replace("```",""),color=0x0bbfff))



def setup(bot):
    """sets up the cog"""
    bot.add_cog(AutoReply(bot))

def agecheck(user):
  return ((datetime.utcnow() - user.created_at).days) > 14

