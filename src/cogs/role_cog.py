import discord
from discord.ext import commands

import discord.utils as dutils

import src.lib.mongodb as mongodb

import matplotlib
import matplotlib.colors as mcolors

pyMongoManager = mongodb.PyMongoManager()


def getIdRolesSelfAssignable(guild_id):
    guild_dict = pyMongoManager.get_guild(guild_id)

    if guild_dict:
        try:
            return guild_dict['self_assignable_roles']
        except:
            return []

    else:
        return []


class RoleCog(commands.Cog, name="Role"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def iam(self, ctx):
        #TODO: GESTION DE ERRORES
        role_query = " ".join(ctx.message.content.split()[1:])
        
        if role_query:
            role = dutils.get(ctx.guild.roles, name=role_query)

            if role:
                roles_self_assignable = getIdRolesSelfAssignable(ctx.guild.id)

                for role_aux in ctx.author.roles:
                    if role_aux.id in roles_self_assignable and role_aux.name != role.name:
                        await ctx.author.remove_roles(role_aux)

                if role.id in roles_self_assignable:        
                    if role in ctx.author.roles:
                        await ctx.send(f"**{ctx.author.name}** you already have **{role_query}** role")
                    else:
                        await ctx.author.add_roles(role)
                        await ctx.send(f"**{ctx.author.name}** you now have **{role_query}** role")
                else:
                    await ctx.send(f"The role **{role_query}** is not self-assignable.")
            else:
                await ctx.send(f"There is no role named **{role_query}**")
        else:
            await ctx.send("Specify a role")


    @commands.command()
    async def iamnot(self, ctx):
        #TODO: GESTION DE ERRORES (PERMISO PARA MANEJAR ROLES)
        role_query = " ".join(ctx.message.content.split()[1:])
        
        if role_query:
            role = dutils.get(ctx.guild.roles, name=role_query)

            if role:
                if role.id in getIdRolesSelfAssignable(ctx.guild.id):
                    #member = ctx.guild.get_member(ctx.author.id)
                    
                    if role in ctx.author.roles:
                        await ctx.author.remove_roles(role)
                        await ctx.send(f"**{ctx.author.name}** you no longer have **{role_query}** role.")
                    else:
                        await ctx.send(f"**{ctx.author.name}** you don't have **{role_query}** role.")
                else:
                    await ctx.send(f"The role **{role_query}** is not self-assignable.")
            else:
                await ctx.send(f"There is no role named **{role_query}**")
        else:
            await ctx.send("Specify a role")

    """@commands.command()
    async def addassignablerole(self, ctx):
        #member = ctx.guild.get_member(ctx.author.id)
        
        if ctx.author.permissions_in(ctx.channel).administrator:
            role_query = " ".join(ctx.message.content.split()[1:])
            
            if role_query:
                role = dutils.get(ctx.guild.roles, name=role_query)

                if role:
                    if role.id in roleGroup.getIdRolesSelfAssignable(ctx.guild.id):
                        await ctx.send(f"**{role_query}** is already self-assignable role")
                    else:
                        pyMongoManager.update_discord_guild_push_sar(ctx.guild.id, role.id)
                        await ctx.send(f"**{role_query}** is now a self-assignable role.")
                else:
                    await ctx.send(f"There is no role named {role_query}**")
            else:
                await ctx.send("Specify a role")
        else:
            await ctx.send("Command only for administrators")

    @commands.command()
    async def removeassignablerole(self, ctx):
        member = ctx.guild.get_member(ctx.author.id)
        
        if member.permissions_in(ctx.channel).administrator:
            role_query = " ".join(ctx.message.content.split()[1:])
            
            if role_query:
                role = dutils.get(ctx.guild.roles, name=role_query)

                if role:
                    if role.id in roleGroup.getIdRolesSelfAssignable(ctx.guild.id):
                        pyMongoManager.update_discord_guild_pull_sar(ctx.guild.id, role.id)
                        await ctx.send(f"**{role_query}** is no longer a self-assignable role")
                    else:
                        await ctx.send(f"That role is not self-assignable.")
                else:
                    await ctx.send(f"There is no role named {role_query}**")
            else:
                await ctx.send("Specify a role")
        else:
            await ctx.send("Command only for administrators")
    """



def setup(bot):
    bot.add_cog(RoleCog(bot))
    print("Role Cog CARGADO")
