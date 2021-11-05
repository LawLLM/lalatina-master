import discord
from discord.ext import commands
import asyncio
import inspect

import pymongo

#import modules.CONSTANTS as CONSTANTS
import config
from src.lib.mongodb import PyMongoManager

pyMongoManager = PyMongoManager()
developers_id = pyMongoManager.panchessco['developers']

def inspeccionar(objeto):
    #result = inspect.getmembers(objeto, lambda a: not(inspect.isroutine(a)))
    result = inspect.getmembers(objeto)

    for item in result:
        print(item)

class OwnerCog(commands.Cog, name="Owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def evaluar(self, ctx):
        args = ctx.message.content.split()[1:]

        if ctx.author.id not in self.bot.get_panchessco_staff_id_list():
            return

        texto = " ".join(args)
        result = eval(texto)

        if result == None:
            await ctx.send('None')
        elif result == "":
            await ctx.send('Cadena vacía')
        else:
            await ctx.send(result)

    @commands.command()
    async def test(self, ctx):
        inspeccionar(ctx.channel.type)

    # Envia un msg a un determinado canal
    @commands.command()
    async def msg_channel(self, ctx, channel_id, *arg_msgs):
        if ctx.author.id not in developers_id:
            return

        msg = " ".join(arg_msgs)
        channel = self.bot.get_channel(int(channel_id))
        async with channel.typing():
            await asyncio.sleep(len(msg)/10.0)
            await channel.send(msg)

    @commands.command()
    async def msg_user(self, ctx, user_id, *arg_msgs):
        if ctx.author.id not in developers_id:
            return

        msg = " ".join(arg_msgs)
        user = await self.bot.fetch_user(int(user_id))

        await user.send(msg)
    
    @commands.command(aliases=['add-dev'])
    async def add_dev(self, ctx):
        if ctx.author.id not in developers_id:
            return
        args = ctx.message.content.split()[1:]
        pyMongoManager.collection_guilds.find_one_and_update({'guild_id':512830421805826048}, {'$push': {'developers': int(args[0])}})
        await ctx.send(f"`{args[0]}` ahora es desarrollador de lalatina")

    @commands.command(aliases=['delete-dev', 'remove-dev'])
    async def delete_dev(self, ctx):
        if ctx.author.id not in developers_id:
            return
        args = ctx.message.content.split()[1:]
        panchessco = pyMongoManager.collection_guilds.find_one({'guild_id':512830421805826048})
        panchessco['developers'].remove(int(args[0]))
        pyMongoManager.collection_guilds.replace_one({'guild_id':512830421805826048}, panchessco)
        await ctx.send(f"`{args[0]}` ya no es desarrollador de lalatina")

    @commands.command(aliases=['staff-list', 'dev-list'])
    async def staff_list(self, ctx):
        staff_list = self.bot.get_panchessco_staff_id_list()
        if ctx.author.id not in staff_list:
            return
        panchessco = pyMongoManager.collection_guilds.find_one({'guild_id':512830421805826048})

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


def setup(bot):
    bot.add_cog(OwnerCog(bot))
    print("Owner Cog CARGAdO")
