import copy
import time

import aiohttp
import discord
from discord.ext import commands

import config
import src.bean.CONSTANTS as CONSTANTS

session_emoji = aiohttp.ClientSession()


class RewardsCog(commands.Cog, name="Rewards"):
    def __init__(self, bot):
        self.bot = bot
        self.vote_reward = 50
        self.daily_reward = 25

    # Reescribir esto para que de monedas para los usuarios de Panchessco
    @commands.command()
    async def daily(self, ctx):
        player = self.bot.pyMongoManager.get_chess_profile(ctx.author.id)

        time_last_daily = player["time_last_daily"]

        gmtime_previus = time.gmtime(time_last_daily)
        gmtime_current = time.gmtime()
        time_current = time.time()

        multiplier = player["daily_multiplier"]

        MAX_MULTUPLIER = 5
        ERIS_BASE = 25

        can_claim = True

        if gmtime_previus.tm_year < gmtime_current.tm_year - 1:
            multiplier = 1
        elif gmtime_previus.tm_year == gmtime_current.tm_year - 1:
            if (
                gmtime_previus.tm_mon == 12
                and gmtime_previus.tm_mday == 31
                and gmtime_current.tm_yday == 1
            ):
                multiplier += 1
            else:
                multiplier = 1
        else:
            if gmtime_current.tm_yday - gmtime_previus.tm_yday == 0:
                can_claim = False
            elif gmtime_current.tm_yday - gmtime_previus.tm_yday == 1:
                multiplier += 1
                if multiplier > MAX_MULTUPLIER:
                    multiplier = MAX_MULTUPLIER
            else:
                multiplier = 1

        if not can_claim:
            time_advanced_seconds = (
                gmtime_current.tm_hour * 3600
                + gmtime_current.tm_min * 60
                + gmtime_current.tm_sec
            )
            time_remaing_seconds = 86400 - time_advanced_seconds

            warn_msg = None
            if time_remaing_seconds > 3600:
                num_hours = int(time_remaing_seconds / 3600)
                warn_msg = f"You can claim again in **{num_hours} hours**"
            elif time_remaing_seconds > 60:
                num_minutes = int(time_remaing_seconds / 60)
                warn_msg = f"You can claim again in **{num_minutes} minutes**"
            else:
                num_seconds = time_remaing_seconds + 1
                warn_msg = f"You can claim again in **{num_seconds} seconds**"

            await ctx.send(f"{warn_msg} (reset every 00:00 UTC)")
        else:
            multiplier_relative = MAX_MULTUPLIER if multiplier > 5 else multiplier
            new_eris = multiplier_relative * ERIS_BASE
            new_balance = player["eris"] + new_eris
            emoji_aqua_coin = self.bot.get_emoji(CONSTANTS.ID_EMOJI_AQUACOIN)

            msg_streak = None
            if multiplier == 1:
                msg_streak = "(1 day streak)"
            else:
                msg_streak = f"({multiplier} days streak)"

            await ctx.send(f"You earned **{new_eris}** {emoji_aqua_coin} {msg_streak}")

            self.bot.pyMongoManager.update_daily(
                ctx.author.id, new_balance, time_current, multiplier
            )


def setup(bot):
    bot.add_cog(RewardsCog(bot))
    print("Rewards Cog CARGADO")
