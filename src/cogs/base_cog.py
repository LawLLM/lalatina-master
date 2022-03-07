import asyncio
import traceback

import aiohttp
import discord
from discord.ext import commands
import unidecode

import config
import src.bean.CONSTANTS as CONSTANTS

PREFIX = config.prefix
en_es = config.en_es
es_en = config.es_en

session_dbg = aiohttp.ClientSession()
session_dbl = aiohttp.ClientSession()


class BaseCog(commands.Cog, name="Base"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("El bot se ha iniciado correctamente.")
        print(self.bot.user)

        game = discord.Game(f"Panchessco ♟️")
        await self.bot.change_presence(status=discord.Status.online, activity=game)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel.type.name != "text":
            return

        if (
            message.content == f"<@{self.bot.user.id}>"
            or message.content == f"<@!{self.bot.user.id}>"
        ):
            await message.channel.send(f"Hola! mi prefijo es `{config.prefix}`")
        elif message.content.startswith(en_es) or message.content.startswith(es_en):
            if message.content.startswith(en_es):
                args = message.content.replace(en_es, "").split(" ")[0:]
                data = {
                    "auth_key": config.deepl_pass,
                    "text": " ".join(args),
                    "target_lang": "ES",
                }

            else:
                args = message.content.replace(es_en, "").split(" ")[0:]
                data = {
                    "auth_key": config.deepl_pass,
                    "text": " ".join(args),
                    "target_lang": "EN",
                    "source_lang": "ES",
                }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://api-free.deepl.com/v2/translate", data=data
                ) as resp:
                    if resp.status == 200:
                        data_json = await resp.json()
                        text_translation = data_json["translations"][0]["text"]

                        await message.channel.send(text_translation)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        name = unidecode.unidecode(member.name)
        await member.edit(nick=name)

        if guild_id in self.bot.welcome_channels_id.keys():
            channel = self.bot.get_channel(self.bot.welcome_channels_id[guild_id])

            emoji_fantasmita = self.bot.get_emoji(CONSTANTS.ID_EMOJI_FANTASMITA)

            await channel.send(
                f"Bienvenido al servidor **{member.name}**. Esperamos que la pases bien {emoji_fantasmita}"
            )
            # guild_panchessco = self.bot.get_guild(config.panchessco_id)
            # member_lolced = guild_panchessco.get_member(335197648342745088)
            # F lolced, esperemos que vuelva
            # await member_lolced.send(f'**{member.name}** entro al server weon!!!')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        ignored = (commands.CommandNotFound,)
        # await ctx.send(f'ERROR 1: {type(error)}')

        error = getattr(error, "original", error)

        # await ctx.send(f'ERROR 2: {type(error)}')

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.CommandOnCooldown):
            time_left = int(ctx.command.get_cooldown_retry_after(ctx) + 1)

            if time_left > 3600:
                num_hours = int(time_left / 3600)
                warn_msg = (
                    f"Command on **cooldown**. Try again in **{num_hours} hours**."
                )
            elif time_left > 60:
                num_minutes = int(time_left / 60)
                warn_msg = (
                    f"Command on **cooldown**. Try again in **{num_minutes} minutes**."
                )
            else:
                num_seconds = time_left + 1
                warn_msg = (
                    f"Command on **cooldown**. Try again in **{num_seconds} seconds**."
                )

            await ctx.send(warn_msg)
            return

        # await ctx.send(f'TIPE COMMAND DEL ERROR: {commands.errors.CommandInvokeError}')
        if isinstance(error, discord.errors.Forbidden):
            aqua_member = ctx.guild.get_member(config.client_id)

            if not aqua_member.permissions_in(ctx.channel).send_messages:
                return

            else:
                if ctx.command.name in (
                    "puzzle",
                    "displayfen",
                    "accept",
                    "move",
                    "board",
                ):
                    await ctx.send(
                        "This command requieres: **Embed Links** and **Attach Files** permissions in this channel"
                    )
                    return
                else:
                    await ctx.send(
                        "This command requieres: **Embed Links** permission in this channel"
                    )
                    return

        """if isinstance(error, discord.errors.MissingPermissions):
            await ctx.send("No tengo suficientes permisos")"""

        text_0 = f"Author: {ctx.author} ({ctx.author.id})"

        channel_fails = self.bot.get_channel(config.channel_fails_id)
        text_1 = ctx.message.content
        # text_2 = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))

        lines_list = traceback.format_exception(
            etype=type(error), value=error, tb=error.__traceback__
        )

        parrafos_list = []

        i = 0
        while i < len(lines_list):
            parrafo = ""

            while i < len(lines_list) and len(parrafo + lines_list[i]) < 1900:
                parrafo = parrafo + "\n" + lines_list[i]
                i += 1

            parrafos_list.append(parrafo)

        await channel_fails.send(f"{text_0}\n```{text_1}```")

        for parrafo in parrafos_list:
            await channel_fails.send(f"```py\n{parrafo}```")


def setup(bot):
    bot.add_cog(BaseCog(bot))
    print("Base Cog CARGADO")
