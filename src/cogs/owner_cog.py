from re import S
import discord
from discord.ext import commands
import asyncio
import inspect
from contextlib import redirect_stdout
import traceback
import io
import textwrap
import pymongo
import json
import aiohttp
import time
#import modules.CONSTANTS as CONSTANTS
import config


def inspeccionar(objeto):
	#result = inspect.getmembers(objeto, lambda a: not(inspect.isroutine(a)))
	result = inspect.getmembers(objeto)

	for item in result:
		print(item)

class OwnerCog(commands.Cog, name="Owner"):
	def __init__(self, bot):
		self.bot = bot
		self._last_result = None

	def cleanup_code(self, content):
		"""Automatically removes code blocks from the code."""
		if content.startswith("```") and content.endswith("```"):
			return "\n".join(content.split("\n")[1:-1])

		return content.strip("` \n")
	
	@commands.command()
	async def e(self, ctx: commands.Context, *, body: str = None):
		if ctx.channel.id == config.panchessco_id:
			if not ctx.channel.permissions_for(ctx.author).administrator:
				return
		else:
			if ctx.author.id not in config.owners_id:
				return

		if not body:
			return

		"""Evaluates a code"""

		env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

		env.update(globals())

		body = self.cleanup_code(body)
		stdout = io.StringIO()

		to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

		try:
			exec(to_compile, env)
		except Exception as e:
			return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

		func = env['func']
		try:
			with redirect_stdout(stdout):
				ret = await func()
		except Exception as e:
			value = stdout.getvalue()
			await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
		else:
			value = stdout.getvalue()

			if ret is None:
				if value:
					await ctx.send(f'```py\n{value}\n```')
			else:
				self._last_result = ret
				await ctx.send(f'```py\n{value}{ret}\n```')

	@commands.command()
	async def test(self, ctx):
		inspeccionar(ctx.channel.type)

	# Envia un msg a un determinado canal
	@commands.command()
	async def msg_channel(self, ctx, channel_id, *arg_msgs):
		if ctx.author.id not in self.bot.pyMongoManager.get_dev_list():
			return

		msg = " ".join(arg_msgs)
		channel = self.bot.get_channel(int(channel_id))
		async with channel.typing():
			await asyncio.sleep(len(msg)/10.0)
			await channel.send(msg)

	@commands.command()
	async def msg_user(self, ctx, user_id, *arg_msgs):
		if ctx.author.id not in self.bot.pyMongoManager.get_dev_list():
			return

		msg = " ".join(arg_msgs)
		user = await self.bot.fetch_user(int(user_id))

		await user.send(msg)
	
	@commands.command(aliases=['add-dev'])
	async def add_dev(self, ctx):
		if ctx.author.id not in self.bot.pyMongoManager.get_dev_list():
			return
		args = ctx.message.content.split()[1:]
		self.bot.pyMongoManager.collection_guilds.find_one_and_update({'guild_id':512830421805826048}, {'$push': {'developers': int(args[0])}})
		await ctx.send(f"`{args[0]}` ahora es desarrollador de lalatina")

	@commands.command(aliases=['delete-dev', 'remove-dev'])
	async def delete_dev(self, ctx):
		if ctx.author.id not in self.bot.pyMongoManager.get_dev_list():
			return
		args = ctx.message.content.split()[1:]
		panchessco = self.bot.pyMongoManager.collection_guilds.find_one({'guild_id':512830421805826048})
		panchessco['developers'].remove(int(args[0]))
		self.bot.pyMongoManager.collection_guilds.replace_one({'guild_id':512830421805826048}, panchessco)
		await ctx.send(f"`{args[0]}` ya no es desarrollador de lalatina")

	@commands.command(aliases=['staff-list', 'dev-list'])
	async def staff_list(self, ctx):
		staff_list = self.bot.get_panchessco_staff_id_list()
		if ctx.author.id not in staff_list:
			return
		panchessco = self.bot.pyMongoManager.collection_guilds.find_one({'guild_id':512830421805826048})

		embed = discord.Embed(title="Staff de Panchessco")
		embed.colour = self.bot.get_embed_color(ctx.author.id)
		embed.set_author(name=ctx.author.name, icon_url=ctx.guild.icon_url)

		index1 = 1
		index2 = 1

		text = "*Staff*\n"
		for staff_id in staff_list:
			staff = self.bot.get_user(staff_id)
			text += f"{index2}. `{staff.name}`\n"
			index2 += 1
		
		text += "\n"
		
		text += "*Desarrollo de lalatina*\n"
		for user_id in panchessco['developers']:
			user = self.bot.get_user(user_id)
			text += f"{index1}. `{user.name}`\n"
			index1 += 1


		embed.description = text
		await ctx.send(embed=embed)
		
		
		
	
	@commands.command()
	async def unbelievaboat(self, ctx): 
		staff_list = self.bot.get_panchessco_staff_id_list()
		if ctx.author.id not in staff_list:
			return
		await ctx.send("¿Estás seguro? (Este proceso es irreversible y modificará el dinero de todos los usuarios) [Y/n]")
		try:
			confirm = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
			if confirm.content.lower() != "y":
				await ctx.send("Comando cancelado")
				return
		except asyncio.TimeoutError:
			await ctx.send("Tiempo agotado")
			return
		await ctx.send("`Proceso iniciado`")
		start = time.time()
		async with aiohttp.ClientSession() as session:
			async with session.get(f'https://unbelievaboat.com/api/v1/guilds/512830421805826048/leaderboard?limit=25&page=1') as resp:
				if resp.status == 200:
					data_json = await resp.json()
					pages = data_json['total_pages']
					page_1_data = data_json['balances']
					for y in page_1_data:
						self.bot.pyMongoManager.update_money(y['user_id'], y['total'])
		tiempo_aprox = int(round((pages*25)/17.7204968944, 0))
		await ctx.send(f"`Tiempo de espera aproximado: {tiempo_aprox} segundos`")
		for x in range(pages):
			async with aiohttp.ClientSession() as session:
				async with session.get(f'https://unbelievaboat.com/api/v1/guilds/512830421805826048/leaderboard?limit=25&page={x+2}') as resp:
					if resp.status == 200:
						data_json = await resp.json()
						balances = data_json['balances']
						for y in balances:
							self.bot.pyMongoManager.update_money(y['user_id'], y['total'])
					else:
						await ctx.send(f"`Error: index {x+1}`\nhttps://unbelievaboat.com/api/v1/guilds/512830421805826048/leaderboard?limit=25&page={x+1}")
		end=time.time()
		spend_time = end-start
		if spend_time/60 >= 1:
			s = spend_time%60
			m = spend_time/60
		else:
			s= spend_time
			m=0
		await ctx.send(f"Tarea completada, tiempo empleado aproximado: `{int(round(m, 0))}m y {int(round(s, 0))}`s")



	



def setup(bot):
	bot.add_cog(OwnerCog(bot))
	print("Owner Cog CARGAdO")
