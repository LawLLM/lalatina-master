import discord
from discord.commands import Option, SlashCommandGroup, slash_command
from discord.ext import commands
import discord.utils as dutils

from src.aquaViews.RoleView import AutoAsignableRoleView, TestView
import src.controller.utils as utils
import src.lib.mongodb as mongodb


def getIdRolesSelfAssignable(guild_id, bot):
    guild_dict = bot.pyMongoManager.get_guild(guild_id)

    if guild_dict:
        try:
            return guild_dict["self_assignable_roles"]
        except:
            return []

    else:
        return []


class RoleCog(commands.Cog, name="Role"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def testmessage(self, ctx):
        if ctx.author.id != 402291352282464259:
            return

        await ctx.send(
            "https://cdn.discordapp.com/attachments/828140277579513897/948280621602598983/unknown.png",
            view=AutoAsignableRoleView(self.bot, (0, 24)),
        )
        await ctx.send(
            "https://cdn.discordapp.com/attachments/828140277579513897/948280655475773450/unknown.png",
            view=AutoAsignableRoleView(self.bot, (24, 48)),
        )
        await ctx.send(
            "https://cdn.discordapp.com/attachments/828140277579513897/948280698643574794/unknown.png",
            view=AutoAsignableRoleView(self.bot, (48, 72)),
        )
        await ctx.send(
            "https://cdn.discordapp.com/attachments/828140277579513897/948280732864905256/unknown.png",
            view=AutoAsignableRoleView(self.bot, (72, 96)),
        )
        await ctx.send(
            "https://cdn.discordapp.com/attachments/828140277579513897/948281030249414656/unknown.png",
            view=AutoAsignableRoleView(self.bot, (96, 120)),
        )

    @commands.command()
    async def iam(self, ctx):
        # TODO: GESTION DE ERRORES
        role_query = " ".join(ctx.message.content.split()[1:])

        if role_query:
            role = dutils.get(ctx.guild.roles, name=role_query)

            if role:
                roles_self_assignable = getIdRolesSelfAssignable(ctx.guild.id, self.bot)

                for role_aux in ctx.author.roles:
                    if (
                        role_aux.id in roles_self_assignable
                        and role_aux.name != role.name
                    ):
                        await ctx.author.remove_roles(role_aux)

                if role.id in roles_self_assignable:
                    if role in ctx.author.roles:
                        await ctx.send(
                            f"**{ctx.author.name}** you already have **{role_query}** role"
                        )
                    else:
                        await ctx.author.add_roles(role)

                        await ctx.send(
                            f"**{ctx.author.name}** you now have **{role_query}** role"
                        )

                        role_colour = role.colour
                        HEX_color = utils.RGB_to_HEX(
                            role_colour.r, role_colour.g, role_colour.b
                        )

                        self.bot.set_embed_color(ctx.author.id, HEX_color)
                        self.bot.pyMongoManager.set_embed_color(
                            ctx.author.id, HEX_color
                        )
                else:
                    await ctx.send(f"The role **{role_query}** is not self-assignable.")
            else:
                await ctx.send(f"There is no role named **{role_query}**")
        else:
            await ctx.send("Specify a role")


def setup(bot):
    bot.add_cog(RoleCog(bot))
    print("Role Cog CARGADO")
