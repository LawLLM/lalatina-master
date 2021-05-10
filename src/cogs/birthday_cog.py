import discord
from discord.ext import commands
import copy

import aiohttp
import config

from src.services.StringService import StringService
import src.bean.CONSTANTS as CONSTANTS

import asyncio

from src.lib.mongodb import PyMongoManager

import datetime
from datetime import date


pyMongoManager = PyMongoManager()
#session_emoji = aiohttp.ClientSession()

PREFIX = config.prefix


class BirthdayCog(commands.Cog, name="Birthday"):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_auto_reaction_id = {
            'ale': 752648508850438275,
            'a': 757918565171986472,
            'sexo': 752658698723262517
        }
        self.bot.loop.create_task(self.check())
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id not in (691310556489056398, 512830421805826048):
            return
        
        content_lower = message.content.lower()
        if content_lower in self.emoji_auto_reaction_id.keys():
            emoji = self.bot.get_emoji(self.emoji_auto_reaction_id[content_lower])
            await message.add_reaction(emoji)
        

    @commands.command()
    async def setbirthday(self, ctx):
        args = ctx.message.content.split()[1:]

        # DIA - MES

        if len(args) == 0:
            await ctx.send(f'Uso correcto `{PREFIX}setbirthday día/mes`')
        else:
            string = ' '.join(args)
            stringService = StringService()
            numbers_list = stringService.findNumbers(string)

            if len(numbers_list) < 2:
                await ctx.send(f'Uso correcto `{PREFIX}setbirthday día/mes`')
            else:
                # MES
                if numbers_list[1] < 1 or numbers_list[1] > 12:
                    await ctx.send('El número de mes solo toma valores entre 1 y 12')
                elif numbers_list[0] < 1 or numbers_list[0] > CONSTANTS.MAX_DAYS_BY_MONTH[numbers_list[1]]:
                    await ctx.send(f"El número de día para el mes de **{CONSTANTS.MONTH_STRING[numbers_list[1]]}** solo toma valores entre 1 y {CONSTANTS.MAX_DAYS_BY_MONTH[numbers_list[1]]}")
                else:
                    profile = pyMongoManager.get_profile(ctx.author.id)

                    if profile['birthday_number_attemps'] < 2:
                        pyMongoManager.update_birthday(ctx.author.id, numbers_list[0], numbers_list[1])
                        remaining_attemps = 1 - profile['birthday_number_attemps']
                        if remaining_attemps == 0:
                            text_end = 'Ya no podrás cambiar tu fecha de cumpleaños.'
                        else:
                            text_end = 'Puedes cambiar tu fecha de cumpleaños una vez.'
                        await ctx.send(f"Día de cumpleaños guardado: **{numbers_list[0]} de {CONSTANTS.MONTH_STRING[numbers_list[1]]}**. {text_end}")
                    else:
                        await ctx.send('Ya no puedes cambiar tu fecha de cumpleaños :C')


    @commands.command()
    async def test2(self, ctx):
        args = ctx.message.content.split()[1:]

        # DIA - MES

        if len(args) == 0:
            await ctx.send(f'Uso correcto `{PREFIX}setbirthday día/mes`')
        else:
            string = ' '.join(args)
            stringService = StringService()
            numbers_list = stringService.findNumbers(string)

            await ctx.send(numbers_list)

            



    async def check(self):
        while not self.bot.is_closed():
            await asyncio.sleep(600)

            guild_panchessco = self.bot.get_guild(config.panchessco_id)
            role = guild_panchessco.get_role(config.role_birthday_id)
            birthday_members = guild_panchessco.get_role(config.role_birthday_id).members # Los que tienen el rol del cumpleaños
            result = list(pyMongoManager.collection_profiles.find({}))
            users = [x["user_id"] for x in result if
                     x["birthday_date_day"] == date.today().day and x["birthday_date_month"] == date.today().month]
            new_birthday_members = [guild_panchessco.get_member(y) for y in users] # Los que cumplen

            for busr in birthday_members:
                if busr not in new_birthday_members:
                    await busr.remove_roles(role)

            for usr in new_birthday_members:
                if role not in usr.roles:
                    await usr.add_roles(role)
                    
                    
    @commands.command()                
    async def test3(self):
        pyMongoManager.collection_profiles.insert_one({"Test": "Passed"})
        await ctx.send("Something")


def setup(bot):
    bot.add_cog(BirthdayCog(bot))
    print("Birthday Cog CARGADO")

