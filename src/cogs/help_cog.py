import discord
from discord.ext import commands


import config
import unidecode


PREFIX = config.prefix

class HelpCog(commands.Cog, name='Help'):
	def __init__(self, bot):
		self.bot = bot
	
	
	@commands.command(aliases=['h', '-h', '-help'])
	async def help(self, ctx, arg=None):
		args = ctx.message.content.split(" ")[1:]
		arg = None if len(args) < 1 else args[0].lower()
		embed = discord.Embed()
		embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
		embed.colour = discord.Color.from_rgb(230, 126, 34)


		if not arg:
			embed.description=f"Usa **{PREFIX}h** <comando> para ver más información detallada sobre él"
			embed.add_field(name="**Cumpleaños**", value="- setbirthday\n - calendar", inline=True)
			embed.add_field(name="**Roles**", value="- iam\n - iamnot", inline=True)
			embed.add_field(name="**Economía**", value="- shop\n - buy\n - use\n - inventory / - inv\n - givemoney\n - top\n - work", inline=True)
			embed.add_field(name="**Apuestas**", value="- blackjack / - bj\n", inline=True)
			embed.add_field(name="**Torneos**", value="- tournaments / - torneos / - t\n", inline=True)
			embed.add_field(name="**Otros Comandos**", value="- ytsearch / - yt\n", inline=True)
			await ctx.send(embed=embed)
		
		elif arg == "setbirthday":
			embed.description=f"Usa **{PREFIX}setbirthday <fecha>** para registrar o actualizar tu fecha de cumpleaños\nPuedes cambiar tu fecha hasta un máximo de 3 veces"
			embed.set_image(url="https://cdn.discordapp.com/attachments/718133124680253614/869874282392616980/unknown.png")
			await ctx.send(embed=embed)
			
		elif arg == "calendar":
			embed.description=f"Puedes usar:\n **{PREFIX}calendar** (para ver la fecha actual)\n **{PREFIX}calendar <nº mes>** (para ver el mes seleccionado)\n\n Si has usado el comando birthday anteriormente, saldrá tu imagen de perfil en el dia que cumplas"
			embed.set_image(url="https://cdn.discordapp.com/attachments/718133124680253614/869875822352273428/unknown.png")
			await ctx.send(embed=embed)

		elif arg in ('iam', 'iamnot'):
			cnl = self.bot.get_channel('652653246795481121')
			embed.description=f"Los comandos `iam` y `iamnot` sirven para dar o quitar roles de colores ({cnl.mention})"
			await ctx.send(embed=embed)

		elif arg == 'shop':
			embed.description="En desarrollo"
			await ctx.send(embed=embed)
		
		elif arg == 'buy':
			embed.description="En desarrollo"
			await ctx.send(embed=embed)

		elif arg == 'use':
			embed.description="En desarrollo"
			await ctx.send(embed=embed)

		elif arg in ('inventory', 'inv'):
			embed.description="En desarrollo"
			await ctx.send(embed=embed)

		elif arg == 'givemoney':
			embed.description="En desarrollo"
			await ctx.send(embed=embed)

		elif arg == 'top':
			embed.description="En desarrollo"
			await ctx.send(embed=embed)

		elif arg == 'work':
			embed.description="En desarrollo"
			await ctx.send(embed=embed)
		
		elif arg in ('blackjack', 'bj'):
			embed.description="En desarrollo"
			await ctx.send(embed=embed)
		
		elif arg in ('tournaments', 'torneos', 't'):
			embed.description=f"Puedes usar:\n **{PREFIX}t** -> Muestra los torneos activos o en espera de panchessco en lichess\n **{PREFIX}t <nº torneo>** -> Muestra información sobre un torneo en específico"
			embed.set_image(url="https://cdn.discordapp.com/attachments/718133124680253614/869879684882644992/unknown.png")
			await ctx.send(embed=embed)
		
		elif arg in ('ytsearch', 'yt'):
			embed.description=f"Usa **{PREFIX}yt <nombre>** para que te muestre un video en específico\n*Lalatina te devolverá el primer resultado que salga con la petición solicitada*"
			embed.set_image(url="https://cdn.discordapp.com/attachments/718133124680253614/869880985687306270/unknown.png")
			await ctx.send(embed=embed)

		
		
		
		
		

def setup(bot):
	bot.add_cog(HelpCog(bot))
	print("Help Cog CARGADO")
