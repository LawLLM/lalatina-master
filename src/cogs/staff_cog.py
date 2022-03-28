import asyncio
import time

import discord
from discord.ext import commands

import config

# import modules.CONSTANTS as CONSTANTS


PREFIX = config.prefix


class StaffCog(commands.Cog, name="Staff"):
    def __init__(self, bot):
        self.bot = bot

        self.bot.loop.create_task(self.legend_cleaner())

    @commands.command()
    async def addleyenda(self, ctx):
        args = ctx.message.content.split()[1:]
        if (
            ctx.author.id not in self.bot.get_panchessco_staff_id_list()
            and ctx.author.id
            not in self.bot.get_panchessco_tournament_manager_id_list()
            and not ctx.author.permissions_in(ctx.channel).administrator
        ):
            await ctx.send(
                "Necesitas ser parte del staff o ser admin para usar este comando"
            )
            return
        if len(args) == 0:
            await ctx.send(f"Correcto uso: `{PREFIX}addleyenda <mention/user_id>`")
            return
        else:
            if len(ctx.message.mentions) > 0:
                member = ctx.message.mentions[0]
            elif args[0].isdigit():
                member = ctx.guild.get_member(int(args[0]))
            else:
                await ctx.send(f"Correcto uso: `{PREFIX}addleyenda <mention/user_id>`")
                return

        if not member:
            await ctx.send("Usuario no encontrado")
        elif member.bot:
            await ctx.send("Este comando no funciona en bots")
        else:
            rolLeyenda = ctx.guild.get_role(config.role_legend_id)

            await member.add_roles(rolLeyenda)

            profile = self.bot.pyMongoManager.update_legend(member.id)

            text = f"**{member.name}** gano el rol {rolLeyenda.mention} durante una semana.\n"

            if profile["legend_times"] == 1:
                text += f"**{member.name}** gano el rol por **primera vez!**"
            else:
                text += f"**{member.name}** gano el rol un total de **{profile['legend_times']} veces!**"

            embed = discord.Embed()
            embed.colour = discord.Color.from_rgb(230, 126, 34)
            embed.description = text
            await ctx.send(embed=embed)

            await ctx.message.delete()

    async def legend_cleaner(self):
        while not self.bot.is_closed():
            await asyncio.sleep(3600)  # Cada hora
            guild_panchessco = self.bot.get_guild(config.panchessco_id)
            legend_members = guild_panchessco.get_role(config.role_legend_id).members
            legend_members_id = list(map(lambda member: member.id, legend_members))
            profiles = self.bot.pyMongoManager.get_profiles(legend_members_id)

            for profile in profiles:
                if time.time() - profile["legend_start_time"] > 3600 * 24 * 7:  # 7 days
                    try:
                        member = guild_panchessco.get_member(profile["user_id"])
                        role_legend = guild_panchessco.get_role(config.role_legend_id)
                        await member.remove_roles(role_legend)
                        print(f"Role removido a {member.name}")
                    except:
                        print("Hummm")


def setup(bot):
    bot.add_cog(StaffCog(bot))
    print("Staff Cog CARGADO")
