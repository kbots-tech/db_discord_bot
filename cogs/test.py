import discord
from discord.ext import commands


class testCommands(commands.Cog, name='Developer Commands'):
  '''These are the developer commands'''

  def __init__(self, bot):
	  self.bot = bot

  @commands.command(name='all_commands', aliases=('all', 'all_cmds', 'cmds'), brief="List every command osf the bot")
  @commands.cooldown(2, 60, commands.BucketType.user)
  async def all_commands(self, ctx):
        """ Provide a list of every command available command for the user,
        split by extensions and organized in alphabetical order.
        Will not show the event-only extensions """

        _embed = discord.Embed(
            title='All commands', description='\n'.join(
                (f'Use `{ctx.prefix}help *cog*` to find out more about a cog !',
                 f'> `{len(self.bot.commands)}` commands available')
            )
        )

        for cog_name, cog in self.bot.cogs.items():
            if  len(cog.get_commands()):
                _embed.add_field(
                    name=cog_name.capitalize(), inline=False,
                    value=' - '.join(sorted(f'`{c.name}`' for c in cog.get_commands()))
                )

        _embed.set_footer(**self.bot.set_footer(ctx))
        await ctx.send(embed=_embed)


def setup(bot):
	bot.add_cog(testCommands(bot))