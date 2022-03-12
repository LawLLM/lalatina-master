import asyncio
import copy
from datetime import date
import time

import aiohttp
import discord
from discord.ext import commands

import config
import src.bean.CONSTANTS as CONSTANTS
from src.bean.calendar_generator import CalendarGenerator
from src.services.StringService import StringService

PREFIX = config.prefix


class BirthdayCog(commands.Cog, name="Birthday"):
    def __init__(self, bot):
        self.bot = bot

        self.bot.loop.create_task(self.check_birthday())

    @commands.command()
    async def setbirthday(self, ctx):
        args = ctx.message.content.split()[1:]

        # DIA - MES

        if len(args) == 0:
            await ctx.send(f"Uso correcto `{PREFIX}setbirthday día/mes`")
        else:
            string = " ".join(args)
            stringService = StringService()
            numbers_list = stringService.findNumbers(string)

            if len(numbers_list) < 2:
                await ctx.send(f"Uso correcto `{PREFIX}setbirthday día/mes`")
            else:
                # MES
                if numbers_list[1] < 1 or numbers_list[1] > 12:
                    await ctx.send("El número de mes solo toma valores entre 1 y 12")
                elif (
                    numbers_list[0] < 1
                    or numbers_list[0] > CONSTANTS.MAX_DAYS_BY_MONTH[numbers_list[1]]
                ):
                    await ctx.send(
                        f"El número de día para el mes de **{CONSTANTS.MONTH_STRING[numbers_list[1]]}** solo toma valores entre 1 y {CONSTANTS.MAX_DAYS_BY_MONTH[numbers_list[1]]}"
                    )
                else:
                    profile = self.bot.pyMongoManager.get_profile(ctx.author.id)

                    if profile["birthday_number_attemps"] < 2:
                        self.bot.pyMongoManager.update_birthday(
                            ctx.author.id, numbers_list[0], numbers_list[1]
                        )
                        remaining_attemps = 1 - profile["birthday_number_attemps"]
                        if remaining_attemps == 0:
                            text_end = "Ya no podrás cambiar tu fecha de cumpleaños."
                        else:
                            text_end = "Puedes cambiar tu fecha de cumpleaños una vez."
                        await ctx.send(
                            f"Día de cumpleaños guardado: **{numbers_list[0]} de {CONSTANTS.MONTH_STRING[numbers_list[1]]}**. {text_end}"
                        )
                    else:
                        await ctx.send("Ya no puedes cambiar tu fecha de cumpleaños :C")

    @commands.command()
    async def calendar(self, ctx):
        args = ctx.message.content.split()[1:]

        month_num = None

        if len(args) > 0:
            if args[0].isdigit():
                arg_int = int(args[0])

                if arg_int > 0 and arg_int < 13:
                    month_num = arg_int

        if not month_num:
            month_num = time.gmtime().tm_mon

        users_birthday = self.bot.pyMongoManager.get_users_birthday(month_num)

        bytes_dict = {}

        for profile in users_birthday:
            member = ctx.guild.get_member(profile["user_id"])

            if member:
                asset = member.avatar_url_as(format="png", size=128)
                avatar_bytes = await asset.read()

                bytes_dict[profile["birthday_date_day"]] = avatar_bytes

        cg = CalendarGenerator()
        # img_buffer = cg.new_calendar_img(month_num, users_birthday)
        img_buffer = cg.new_calendar_img(month_num, bytes_dict)

        await ctx.send(file=discord.File(fp=img_buffer, filename="hb.png"))

    @commands.command()
    async def test_avatar(self, ctx):
        avatar_asset = ctx.author.avatar_url_as(format="png", size=128)
        avatar_bytes = await avatar_asset.read()

        cg = CalendarGenerator()
        img_buffer = cg.avatar_test(avatar_bytes)

        await ctx.send(file=discord.File(fp=img_buffer, filename="hb.png"))

    @commands.command()
    async def test2(self, ctx):
        args = ctx.message.content.split()[1:]

        # DIA - MES

        if len(args) == 0:
            await ctx.send(f"Uso correcto `{PREFIX}setbirthday día/mes`")
        else:
            string = " ".join(args)
            stringService = StringService()
            numbers_list = stringService.findNumbers(string)

            await ctx.send(numbers_list)

    async def check_birthday(self):
        while not self.bot.is_closed():
            await asyncio.sleep(600)

            guild_panchessco = self.bot.get_guild(config.panchessco_id)
            role = guild_panchessco.get_role(config.role_birthday_id)
            birthday_members = guild_panchessco.get_role(
                config.role_birthday_id
            ).members  # Los que tienen el rol del cumpleaños
            result = list(self.bot.pyMongoManager.collection_profiles.find({}))
            users = [
                x["user_id"]
                for x in result
                if x["birthday_date_day"] == date.today().day
                and x["birthday_date_month"] == date.today().month
            ]
            new_birthday_members = [
                guild_panchessco.get_member(y) for y in users
            ]  # Los que cumplen

            for busr in birthday_members:
                if busr not in new_birthday_members:
                    await busr.remove_roles(role)

            for usr in new_birthday_members:
                if role not in usr.roles:
                    await usr.add_roles(role)


def setup(bot):
    bot.add_cog(BirthdayCog(bot))
    print("Calendar Cog CARGADO")
