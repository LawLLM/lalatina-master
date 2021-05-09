import discord
from discord.ext import commands

import aiohttp
import requests
import json






class TournamentCog(commands.Cog, name='Tournament'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['torneos', 'torneo'])
    async def tournaments(self, ctx):
        args = ctx.message.content.split()[1:]
        tt = ""
        selected = False

        if len(args) == 0:
            pass

        else:
            if args[0].isdigit():
                tt = args[0]




        response = requests.get("https://lichess.org/api/team/panchessco/arena?max=5")
        torneo_lista = eval('[' + response.content.decode().replace('true', 'True').replace('false', 'False').replace('\n', ',').replace('null', 'None') + ']')
        torneo_dict_alpha = [eval(str(item)) for item in torneo_lista]
        torneo_dict = [x for x in torneo_dict_alpha if x['status'] in (10, 20)]



        if torneo_dict != []:
            t = torneo_dict[0]
            if tt.isdigit():
                if 0 < int(tt) <= len(torneo_dict):
                    selected = True
                    t = torneo_dict[int(tt) - 1]

                else:
                    selected = True


            text = ""
            if selected:
                embed = discord.Embed(title=t['fullName'], url=f"https://lichess.org/tournament/{t['id']}")
                embed.colour = discord.Color.from_rgb(0, 255, 255)


                icon = ""
                status = ""

                if t['status'] == 20:
                    icon = ":green_circle:"
                    status = "Playing"

                else:
                    icon = ":red_circle:"
                    status = "Waiting"
                    h = t['secondsToStart'] // 60 // 60
                    m = t['secondsToStart'] // 60 - h * 60
                    s = (t['secondsToStart'] - h * 60 * 60) - m * 60
                    text += f"Time remaining: **{h}h, {m}m, {s}s**\n"

                text += f"Type: {t['variant']['name']}\n"
                text += f"Duration: {t['minutes']}m\n"
                text += f"Actual Players: {t['nbPlayers']}\n"
                text += f"Rated: {str(t['rated']).replace('True', 'Yes').replace('False', 'No')}\n"
                text += f"Status: {status} {icon}"
                embed.description = text
                await ctx.send(embed=embed)


            else:

                embed = discord.Embed(title="Lichess Tournaments")
                embed.colour = discord.Color.from_rgb(0, 255, 255)
                for tmnt in torneo_dict:
                    if tmnt['status'] == 20:
                        icon = ":green_circle:"
                        status = "Playing"
                        text += f"**{tmnt['fullName']}**:\n"
                        text += f"Type: {tmnt['variant']['name']}\n"
                        text += f"Status: {status} {icon}\n"
                        text += f"[Link](https://lichess.org/tournament/{tmnt['id']})\n\n\n"
                    else:
                        icon = ":red_circle:"
                        status = "Waiting"
                        h = tmnt['secondsToStart'] // 60 // 60
                        m = tmnt['secondsToStart'] // 60 - h * 60
                        s = (tmnt['secondsToStart'] - h*60*60) - m * 60
                        text += f"**{tmnt['fullName']}**:\n"
                        text += f"Time remaining: **{h}h, {m}m, {s}s**\n"
                        text += f"Type: {tmnt['variant']['name']}\n"
                        text += f"Status: {status} {icon}\n"
                        text += f"[Link](https://lichess.org/tournament/{tmnt['id']})\n\n\n"

                embed.description = text
                await ctx.send(embed=embed)

        else:
            await ctx.send("There aren't any tournaments yet")


def setup(bot):
    bot.add_cog(TournamentCog(bot))
    print("Tournament Cog CARGADO")
