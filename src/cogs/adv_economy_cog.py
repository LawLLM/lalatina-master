import discord
from discord.ext import commands
from src.lib.mongodb import PyMongoManager
import config
import asyncio


pyMongoManager = PyMongoManager()



class AdvEconomyCog(commands.Cog, name="AdvEconomyCog"):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command(aliases=['set-start-balance'])
    async def set_start_balance(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            return
        args = ctx.message.content.split()[1:]

        if len(args) == 0:
            await ctx.send("`Uso correcto: la!set-start-balance <balance>`")
        
        else:
            if args[0].isdigit():
                balance = int(args[0])
                pyMongoManager.collection_guilds.update_one({'guild_id':512830421805826048}, {'$set': {'start_balance': balance}})
                await ctx.send(f"`set-start-balance` cambiado a {balance}")
            else:
                await ctx.send("`Uso correcto: la!set-start-balance <balance>`")
    
    @commands.command(aliases=['add-money-role'])
    async def add_money_role(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            return
        args = ctx.message.content.split()[1:]

        if len(args) < 2:
            await ctx.send(args)
            await ctx.send("Uso correcto: `la!add-money-role <role> <amount>`")
            return
        
        if args[0].isdigit():
            if len(str(args[0])) == 18:
                role_id = int(args[0])
            else:
                await ctx.send("Uso correcto: `la!add-money-role <role> <amount>`")
                return
        else:
            if len(ctx.message.role_mentions) == 0:
                await ctx.send("Uso correcto: `la!add-money-role <role> <amount>`")
                return
            else:
                role_id = ctx.message.role_mentions[0].id
        
        if args[1].isdigit():
            amount = int(args[1])
        else:
            await ctx.send("Por favor, introduzca una cantidad válida")
            return
        
        role = ctx.guild.get_role(role_id)
        list_users = [user.id for user in ctx.guild.members if role in user.roles and user.bot == False]
        if len(list_users) == 1:
            pyMongoManager.collection_profiles.find_one_and_update({'user_id': list_users[0]}, {'$inc': {'cash': amount}})
        elif len(list_users) == 0:
            await ctx.send("No hay usuarios con ese rol")
            return
        else:
            pyMongoManager.collection_profiles.update_many({'$or': {'user_id': list_users}}, {'$inc': {'cash': amount}})
        await ctx.send(f"Se ha agregado {amount} :eggplant: a los usuarios con el rol `{role.name}`")
            


    @commands.command(aliases=['remove-money-role'])
    async def remove_money_role(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            return
        args = ctx.message.content.split()[1:]

        if len(args) < 2:
            await ctx.send("Uso correcto: `la!remove-money-role <role> <\"all\"/amount>`")
            return
        
        if args[0].isdigit():
            if len(str(args[0])) == 18:
                role_id = int(args[0])
            else:
                await ctx.send("Uso correcto: `la!remove-money-role <role> <\"all\"/amount>`")
                return
        else:
            if len(ctx.message.role_mentions) == 0:
                await ctx.send("Uso correcto: `la!remove-money-role <role> <\"all\"/amount>`")
                return
            else:
                role_id = ctx.message.role_mentions[0].id
        allm = False
        if args[1].isdigit():
            amount = int(args[1])
        else:
            if args[1].lower() == "all":
                allm = True
            else:
                await ctx.send("Por favor, introduzca una cantidad válida")
                return


        role = ctx.guild.get_role(role_id)
        list_users = [user.id for user in ctx.guild.members if role in user.roles and user.bot == False]
        if allm:
            if len(list_users) == 0:
                await ctx.send("No hay usuarios con ese rol")
                return
            elif len(list_users) == 1:
                pyMongoManager.collection_profiles.find_one_and_update({'user_id': list_users[0]}, {'$set': {'cash': 0, 'bank': 0}})
            else:
                pyMongoManager.collection_profiles.update_many({'$or': {'user_id': list_users}}, {'$set': {'cash': 0, 'bank': 0}})
            await ctx.send(f"Se les ha quitado todo el dinero a los usuarios con el rol {role.name}")
        else:
            users_l = pyMongoManager.get_profiles(list_users) 
            for user in users_l:
                if amount > user['cash']:
                    user['bank'] -= amount - user['cash']
                    user['cash'] = 0
                    
                else:
                    user['cash'] -= amount
                pyMongoManager.collection_profiles.find_one_and_replace({'user_id': user['user_id']}, user)
                await ctx.send(f"Se les ha quitado {amount} :eggplant: a los usuarios con el rol {role.name}")




    @commands.command(aliases=['reset-money'])
    async def reset_money(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            return
        args = ctx.message.content.split()[1:]

        user_id = 0

        if len(args) == 0:
            user_id = ctx.author.id
        else:
            if len(ctx.message.mentions) == 0:
                if args[0].isdigit():
                    if len(args[0]) == 18:
                        user_id = int(args[0])
                    else:
                        await ctx.send("Uso correcto: `la!reset-money <user>`")
                        return
                else:
                    await ctx.send("Uso correcto: `la!reset-money <user>`")
                    return
            else:
                user_id = ctx.message.mentions[0].id
        
        pyMongoManager.collection_profiles.find_one_and_update({'user_id': user_id}, {'$set': {'cash': 0, 'bank': 0}})
        await ctx.send("Dinero del usuario eliminado con éxito")


    @commands.command(aliases=['reset-economy'])
    async def reset_economy(self, ctx):
        if ctx.author.id not in pyMongoManager.get_dev_list():
            return
        
        await ctx.send("¿Seguro que quieres eliminar el dinero de todos los usuarios? [Y/n]")
        try:
            confirmation = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
            if confirmation.content.lower() in ('y', 'n'):
                if confirmation.content.lower() == 'y':
                    pyMongoManager.collection_profiles.update_many({}, {'$set': {'cash': 0, 'bank': 0}})
                else:
                    await ctx.send("Cancelado")
        except asyncio.TimeoutError:
            await ctx.send("Cancelado")  




def setup(bot):
    bot.add_cog(AdvEconomyCog(bot))
    print("AdvEconomyCog CARGADO")