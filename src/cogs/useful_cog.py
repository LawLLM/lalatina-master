import discord
from discord.ext import commands

import urllib
from urllib import parse, request
import re



class UsefulCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command(aliases=['yt'])
	async def ytsearch(self, ctx, *, search):
		query_string = parse.urlencode({'search_query': search})
		html_content = request.urlopen('http://www.youtube.com/results?' + query_string)
		search_results = re.findall(r'/watch\?v=(.{11})', html_content.read().decode())
		await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])
		
		
def setup(bot):
    bot.add_cog(UsefulCog(bot))
    print("Useful Cog CARGADO")