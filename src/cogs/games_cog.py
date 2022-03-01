# create a cog for discord bot
from datetime import datetime
from random import randint
from time import sleep

import discord
from discord import embeds
from discord.ext import commands

import config
from src.bean.RouletteBean import RouletteBean


class Games(commands.Cog, name="Games"):
    def __init__(self, bot):
        self.bot = bot

        self.games_list_str = [
            "blackjack",
            "roulette",
            "cock-fight",
            "russian-roulette",
            "slot-machine",
        ]

        # TODO: los bets limits deben ser por cada servidor
        # guild_document = self.bot.pyMongoManager.get_guild(config.panchessco_id)

        # self.games_bet_limits = guild_document['bet_limits']

        self.games_bet_limits = {
            "blackjack": {"min": 100, "max": None},
            "roulette": {"min": 100, "max": None},
            "cock-fight": {"min": 100, "max": None},
            "russian-roulette": {"min": 100, "max": None},
            "slot-machine": {"min": 100, "max": None},
        }

    @commands.command(aliases=["set-bet-limit", "set-bet-limits"])
    async def set_bet_limit(self, ctx):
        """
        Set the minimum and maximum bet limits for the game.
        """

        async def error_message(reason, argument=None):
            embed = discord.Embed()
            embed.set_author(
                name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar.url
            )

            if reason == "pocos_argumentos":
                embed.description = f":x: Se han dado pocos argumentos\n\nUso:\n`{config.prefix}set-bet-limit <game> <min | max> <amount>`"
            elif reason == "invalid_argument":
                embed.description = f":x: El argumento `<{argument}>` no es válido\n\nUso:\n`{config.prefix}set-bet-limit <game> <min | max> <amount>`"
            elif reason == "less_than_min":
                embed.description = f":x: Este valor no puede ser menor que el mínimo permitido `{self.games_bet_limits[argument]['min']}`"
            elif reason == "more_than_max":
                embed.description = f":x: Este valor no puede ser mayor que el máximo permitido `{self.games_bet_limits[argument]['max']}`"

        args = ctx.message.content.split()[1:]

        if len(args) == 0:
            embed = discord.Embed()
            embed.title = "Bet Limits"
            description = (
                f"Usage: `{config.prefix}set-bet-limit <game> <min | max> <amount>`\n\n"
            )

            for game in self.games_list_str:
                embed.add_field(
                    name=game.capitalize(),
                    value=f'Min: {self.games_bet_limits[game]["min"]}\nMax: {self.games_bet_limits[game]["max"]}',
                    inline=False,
                )
                # description += f"**{game}**\nMin: {self.games_bet_limits[game]['min']}\nMax: {self.games_bet_limits[game]['max']}\n"

            embed.description = description
            embed.colour = discord.Colour.dark_red()
            await ctx.send(embed=embed)
            return
        elif len(args) < 3:
            await error_message("pocos_argumentos")
            return
        else:
            game = args[0]
            if game not in self.games_list_str:
                await error_message("invalid_argument", argument="game")
                return
            else:
                if args[1] in ["min", "max"]:
                    amount = args[2]
                    if amount.lower() == "none":
                        self.games_bet_limits[game][args[1]] = None
                    else:
                        try:
                            amount = int(args[2])
                        except ValueError:
                            await error_message("invalid_argument", argument="amount")
                            return
                        else:
                            if args[1] == "min":
                                if amount < 0:
                                    await error_message(
                                        "invalid_argument", argument="amount"
                                    )
                                    return
                                elif (
                                    self.games_bet_limits[game]["max"]
                                    and amount > self.games_bet_limits[game]["max"]
                                ):
                                    await error_message("more_than_max")
                                    return
                                self.games_bet_limits[game]["min"] = amount
                            elif args[1] == "max":
                                if amount < self.games_bet_limits[game]["min"]:
                                    await error_message("less_than_min")
                                    return
                                self.games_bet_limits[game]["max"] = amount

                    embed = discord.Embed()
                    embed.set_author(
                        name=f"{ctx.author.name}",
                        icon_url=ctx.author.display_avatar.url,
                    )

                    if args[1] == "min":
                        embed.description = f":white_check_mark: El límite mínimo para `{game}` ha sido establecido a `{amount}`"
                    elif args[1] == "max":
                        embed.description = f":white_check_mark: El límite máximo para `{game}` ha sido establecido a `{amount}`"

                    await ctx.send(embed=embed)

                    self.bot.pyMongoManager.collection_guilds.update_one(
                        {"guild_id": ctx.guild.id},
                        {"$set": {"bet_limits": self.games_bet_limits}},
                    )

                else:
                    await error_message("invalid_argument", argument="min | max")
                    return

    # roulete command from unbelieva bot
    @commands.command(name="roulette", aliases=["roulete", "roullete", "roullette"])
    async def roulette(self, ctx):
        args = ctx.message.content.split()[1:]

        async def error_message(reason, argument=None):
            embed = discord.Embed()
            embed.set_author(
                name=ctx.author.name, icon_url=ctx.author.display_avatar.url
            )

            if reason == "pocos_argumentos":
                embed.description = f":x: Se han dado pocos argumentos\n\nUso:\n`{config.prefix}roulette <bet> <space>`"
            elif reason == "invalid_argument":
                embed.description = f":x: El argumento `<{argument}>` no es válido\n\nUso:\n`{config.prefix}roulette <bet> <space>`"
            elif reason == "less_than_min":
                embed.description = f":x: La apuesta no debe ser menor a `{self.games_bet_limits['roulette']['min']}`"
            elif reason == "more_than_max":
                embed.description = f":x: La apuesta no debe ser mayor a `{self.games_bet_limits['roulette']['max']}`"

            embed.colour = discord.Colour.red()
            await ctx.send(embed=embed)

        if len(args) < 2:
            await error_message("pocos_argumentos")
            return
        else:
            bet = args[0]
            space = args[1].lower()

            if space == "1st":
                space = "1st12"
            elif space == "2nd":
                space = "2nd12"
            elif space == "3rd":
                space = "3rd12"

            if bet.isdigit():
                bet = int(bet)

                if bet < self.games_bet_limits["roulette"]["min"]:
                    await error_message("less_than_min")
                    return
                elif (
                    self.games_bet_limits["roulette"]["max"]
                    and bet > self.games_bet_limits["roulette"]["max"]
                ):
                    await error_message("more_than_max")
                    return
                else:
                    space_list = [
                        "red",
                        "black",
                        "even",
                        "odd",
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        "7",
                        "8",
                        "9",
                        "10",
                        "11",
                        "12",
                        "13",
                        "14",
                        "15",
                        "16",
                        "17",
                        "18",
                        "19",
                        "20",
                        "21",
                        "22",
                        "23",
                        "24",
                        "25",
                        "26",
                        "27",
                        "28",
                        "29",
                        "30",
                        "31",
                        "32",
                        "33",
                        "34",
                        "35",
                        "36",
                        "1-18",
                        "19-36",
                        "1st12",
                        "2nd12",
                        "3rd12",
                        "1-12",
                        "13-24",
                        "25-36",
                    ]

                    if space in space_list:
                        roulette = RouletteBean(bet, space)
                        win = roulette.play()

                        if win:
                            amount_win = roulette.calculate_win()

                            embed = discord.Embed()
                            embed.set_author(
                                name=ctx.author.name,
                                icon_url=ctx.author.display_avatar.url,
                            )
                            embed.description = (
                                f":white_check_mark: Has ganado `{amount_win}`"
                            )
                            embed.colour = discord.Colour.green()
                            await ctx.send(embed=embed)
                        else:
                            embed = discord.Embed()
                            embed.set_author(
                                name=ctx.author.name,
                                icon_url=ctx.author.display_avatar.url,
                            )
                            embed.description = f":x: Has perdido `{bet}`"
                            embed.colour = discord.Colour.red()
                            await ctx.send(embed=embed)
                    else:
                        await error_message("invalid_argument", argument="space")
            else:
                await error_message("invalid_argument", argument="bet")


def setup(bot):
    bot.add_cog(Games(bot))
