import discord
from datetime import datetime
from tablefuncs import table
from discord.ext import commands
from discord.ext import tasks

admin_roles = {"Management Team","Support","Developers","Senior Support","Senior Developers"}

class DBCog(commands.Cog):
    """commands for the weather finder"""
    def __init__(self, bot,admin_roles=admin_roles):
        self.bot = bot
        self.table = table()
        self.admin_roles = admin_roles
        self.hour_count = 0

    """This command is used to close a ticket and increment the staff members ticket count"""
    @commands.command(
        name = "close",
        brief = "closes ticket",
    )
    @commands.has_any_role(*admin_roles)
    async def close(self,ctx):
      if "ticket" in ctx.channel.name:
        channel_id = ctx.channel.id
        self.hour_count = self.hour_count+1
        print(f"closed ticket: {ctx.channel.id}\nHour Count is: {self.hour_count}")
        await self.table.close_ticket(channel_id,ctx.author.id,ctx.author.name)

    """This command sends an embed with leaderboard"""
    @commands.command(
        name = "leaderboard",
        brief = "Gets ticket leaderboard",
    )
    @commands.has_any_role(*admin_roles)
    async def leaderboard(self,ctx):
      data = await self.table.gen_leaderboard()
      embed=discord.Embed(title="Staff Ticket Stats",color=0x0bbfff)
      weekly_str = ""
      total_str = ""
      started_str = ""
      weekly_start = ""
      for count,staff in enumerate(data['weekly'],1):
        weekly_str += f"**{count}** {staff[0]} with {staff[1]} tickets\n"
      embed.add_field(name='Weekly Closed Stats',value=weekly_str)
      for count,staff in enumerate(data['overall'],1):
        total_str += f"**{count}** {staff[0]} with {staff[1]} tickets\n"
      embed.add_field(name='Overall Closed Stats',value=total_str)
      embed.add_field(name=" \u200b ",value="__              _ _  _     __",inline=False)
      for count,staff in enumerate(data['weekly_started'],1):
        weekly_start += f"**{count}** {staff[0]} with {staff[1]} tickets\n"
      embed.add_field(name='Weekly Started Stats',value=weekly_start)
      for count,staff in enumerate(data['started'],1):
        started_str += f"**{count}** {staff[0]} with {staff[1]} tickets\n"
      embed.add_field(name='Overall Started Stats',value=started_str)
      await ctx.send(embed=embed)
        
 
    """This command gets the stats for a specific user"""
    @commands.command(
        name = "stats",
        brief = "Gets staff stats for ticket",
    )
    @commands.has_any_role(*admin_roles)
    async def stats(self,ctx,args=""):
        if not args:
          data = await self.table.get_staff(ctx.author.id)
          embed=discord.Embed(title=f"Ticket stats for {ctx.author.name}",color=0x0bbfff)
          embed.set_thumbnail(url = ctx.author.avatar_url)
          data = data[0]
        else:
          args = args[3:]
          args=args.replace(">","")
          user = self.bot.get_user(int(args))
          data = await self.table.get_staff(args)
          data = data[0]
          embed=discord.Embed(title=f"Ticket stats for {user.name}",color=0x0bbfff)
          embed.set_thumbnail(url = user.avatar_url)
        
        embed.add_field(name='Tickets This Week',value=data[0],inline=True)
        embed.add_field(name='Overall Tickets',value=data[1],inline=True)
        embed.add_field(name=" \u200b ",value="__              _ _  _     __",inline=False)
        embed.add_field(name='Started This Week',value=data[3],inline=True)
        embed.add_field(name='Started Overall',value=data[2],inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role(*admin_roles)
    async def ticketStats(self,ctx):
      data = await self.table.ticket_data()
      embed = discord.Embed(title="Ticket Stats",color=0x0bbfff)
      embed.add_field(name="Tickets From Last Hour",value=data['last_hour'],inline=False)
      embed.add_field(name="Difference From Previous Hour",value=data['hour_difference'],inline=False)
      embed.add_field(name="Difference From Yesterday",value=data['prev_difference'],inline=False)
      embed.add_field(name="Overall Average",value=data['overall_tph'],inline=False)
      embed.add_field(name="Todays Average",value=data['day_avg'],inline=False)
      await ctx.send(embed=embed)
      

    """The listener updates the DB update time"""
    @commands.Cog.listener()
    async def on_message(self, message):
      if message.guild:
        if "ticket" in message.channel.name:
          if 'close' not in message.content.lower():
            if bool(set(admin_roles) & set([y.name for y in message.author.roles])):
              await self.table.create_ticket(message.channel.id,message.author.id,message.author.name)
              print(message.author.id)

    @commands.Cog.listener()
    async def on_ready(self):
      print('starting task')
      self.weekly_reset.start()

    @tasks.loop(hours=1)
    async def weekly_reset(self):
      if datetime.utcnow().hour == 0 and datetime.utcnow().weekday() == 0:
        print('reset weekly stats')
        await self.table.reset_weekly_stats()
      else:
        print('passing reset')
      await self.table.set_hour_tickets(self.hour_count)
      self.hour_count = 0
      

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    """sets up the cog"""
    bot.add_cog(DBCog(bot))
