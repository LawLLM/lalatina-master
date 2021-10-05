import discord
from discord.ext import commands
import asyncio
import inspect

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
        if ctx.author.id not in config.owners_id:
            return

        msg = " ".join(arg_msgs)
        channel = self.bot.get_channel(int(channel_id))
        async with channel.typing():
            await asyncio.sleep(len(msg)/10.0)
            await channel.send(msg)

    @commands.command()
    async def msg_user(self, ctx, user_id, *arg_msgs):
        if ctx.author.id not in config.owners_id:
            return

        msg = " ".join(arg_msgs)
        user = await self.bot.fetch_user(int(user_id))

        await user.send(msg)

def setup(bot):
    bot.add_cog(OwnerCog(bot))
    print("Owner Cog CARGAdO")
