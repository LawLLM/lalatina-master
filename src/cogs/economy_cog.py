import asyncio

import discord
from discord.ext import commands
import copy

import discord.utils as dutils
import requests
import aiohttp
import math
import time
from time import sleep
import pymongo
from src.lib.mongodb import PyMongoManager

import config
from src.bean.CONSTANTS import *

import random
import math

#import modules.CONSTANTS_IMAGES as CONSTANTS_IMAGES

#from modules.image_editor import ImageEditor

#import modules.CONSTANTS as CONSTANTS

#imageEditor = ImageEditor()

pyMongoManager = PyMongoManager()
session_emoji = aiohttp.ClientSession()

# BASE PARA LA ECONOMIA DE PANCHESSCOBOT
class EconomyCog(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def shop(self, ctx):
        args = ctx.message.content.split()[1:]

        items = pyMongoManager.get_items()
        num_pages = math.ceil(len(items)/10)
        page=1




        if len(args) > 0 and args[0].isdigit():
            page = int(args[0])
            if page > num_pages:
                page=num_pages
            elif page <= 0:
                page=1
        
        list_items = items[(page*10)-10:page*10]
        embed = discord.Embed()
        embed.set_author(name="Tienda de panchessco", icon_url=ctx.guild.icon_url)
        embed.colour = self.bot.get_embed_color(ctx.author.id)

        text = "\n"
        for item in list_items:
        	text += f"{item['name']} - {item['value']} :eggplant:\n*{item['description']}*\n\n\n"
        
        embed.description = text
        embed.set_footer(text=f"Página {page}/{num_pages}")
        await ctx.send(embed=embed)
        

        
        


    @commands.command()
    async def buy(self, ctx):
        args = ctx.message.content.split()[1:]

        user = pyMongoManager.get_profile(ctx.author.id)


        C_trencada = self.bot.get_emoji(555903896363466762)
        ded = self.bot.get_emoji(633063734721380403)

        if len(args) == 0:
            await ctx.send("Debes poner lo que quieras comprar")

        else:
            cons = ' '.join(args).lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó","o").replace("ú", "u").replace(" ", "").replace(".", "")
            
            obj = pyMongoManager.shop.find_one({"key": cons})
            
            if obj is not None:
                if obj['roleRequired'] is not None:
                    role = ctx.guild.get_role(obj['roleRequired'])
                    if role not in ctx.author.roles:
                        await ctx.send(f"Lo sentimos, pero no puedes comprar `{obj['name']}` si no tienes el rol `{role.name}`")
                        return
                if obj['stock'] == 0:
                    await ctx.send(f"No queda `{obj['name']}` en la tienda {C_trencada}")

                else:

                    if user['cash'] >=  obj['value']:
                        user['cash'] -= obj['value']

                        if obj['stock'] is not None:  
                            if obj['stock'] == 1:
                                pyMongoManager.shop.delete_one({'name': obj['name']})
                                await ctx.message.channel.send(f"Ya no quedan más `{obj['name']}`")
                            else:
                                pyMongoManager.shop.find_one_and_update({'name':obj['name']}, {"$inc": {"stock": -1}})
                                await ctx.message.channel.send(f"Número de `{obj['name']}` disponibles: `{obj['stock']-1}`")

                        if obj['name'] in user['inventory']:
                            user['inventory'][obj['name']] += 1

                        else:
                            user['inventory'][obj['name']] = 1



                        pyMongoManager.collection_profiles.replace_one({'user_id': ctx.author.id}, user)

                        await ctx.send(f"Has recibido `{obj['name']}`")

                    else:
                        await ctx.send("No tienes suficientes :eggplant:")

            else:
                await ctx.send("No se ha encontrado el objeto")





    @commands.command()
    async def use(self, ctx):
        args = ctx.message.content.split()[1:]

        if len(args) == 0:
            await ctx.send("Uso correcto -> la!use <nombre_objeto>")
            return

        cons = ' '.join(args).lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú","u").replace(" ", "").replace(".", "")
        obj = pyMongoManager.shop.find_one({"key": cons})
        user = pyMongoManager.get_profile(ctx.author.id)


        if obj is None:
            await ctx.send("No se ha encontrado el objeto")
            return

        if len(user['inventory']) == 0:
            await ctx.send(f"No tienes `{obj['name']}` en el inventario")
            return

        if obj['name'] not in user['inventory'].keys() or user['inventory'][obj['name']] == 0:
            await ctx.send(f"No tienes `{obj['name']}` en el inventario")
            return
        
        user['inventory'][obj['name']] -= 1
        if user['inventory'][obj['name']] == 0:
            del user['inventory'][obj['name']]


        if obj['message'] is not None:
            await ctx.send(obj['message'])
        
        if obj['roleAdded'] is not None:
            role = dutils.get(ctx.guild.roles, id=obj['roleAdded'])
            if role in ctx.author.roles:
                await ctx.send(f"Ya tienes el rol `{role.name}`")
                if obj['message'] is None:
                    return
            else:    
                await ctx.author.add_roles(role)
                await ctx.send(f"Has recibido el rol `{role.name}`")
        
        if obj['roleRemoved'] is not None:
            role = dutils.get(ctx.guild.roles, id=obj['roleRemoved'])
            if role not in ctx.author.roles:
                await ctx.send(f"No tienes el rol `{role.name}`")
                if obj['message'] is None:
                    return
            else:
                await ctx.author.remove_roles(role)
                await ctx.send(f"Se te ha eliminado el rol `{role.name}`")


        
        pyMongoManager.collection_profiles.replace_one({'user_id': ctx.author.id}, user)




    @commands.command(aliases=['inv', 'wallet', 'bal', 'balance'])
    async def inventory(self, ctx):
        args = ctx.message.content.split()[1:]
        
        if len(args) == 0:
            member = ctx.author
        else:
            if len(ctx.message.mentions) > 0:
                member = ctx.message.mentions[0]
            elif args[0].isdigit():
                try:
                    member = ctx.guild.get_member(int(args[0]))
                except:
                    try:
                        member = self.bot.get_user(int(args[0]))
                    except:
                        emoji_nuu = self.bot.get_emoji(762174833752408106)
                        await ctx.send(f'{emoji_nuu} Usuario no encontrado')
                        return
            else:
                member = ctx.author
        
        if member.bot:
            await ctx.send("Este comando no funciona en bots")
            return

        user = pyMongoManager.collection_profiles.find_one({"user_id":member.id})


        embed = discord.Embed()
        embed.colour = self.bot.get_embed_color(ctx.author.id)
        embed.title = f"Inventario de {member.name}"

        text = ""
        text += f"Cartera: {user['cash']} :eggplant:\nBanco: {user['bank']} :eggplant:\n\n"

        for name, quantity in user['inventory'].items():
            text += f"{name} (x{quantity})\n"

        embed.description = text
        await ctx.send(embed=embed)

    """
    @commands.command()
    async def info(self, ctx):
        pass
    """


    

    @commands.command()
    async def additem(self, ctx):

        obj = pyMongoManager.object_base
        stock = False
        roleAd = False
        roleRe = False
        roleReq = False
        img = False
        msgS = False

        await ctx.send("*Las preguntas opcionales se podrán saltar escribiendo `s`*\n*Pon `exit`  en cualquier momento para cancelar*")

        await ctx.send("Nombre:")
        try:
            name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
            if name.content == "exit":
                await ctx.send("Comando cancelado")
                return
            obj['name'] = name.content
            obj['key'] = name.content.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú","u").replace(" ", "").replace(".", "")
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send("Valor:")
        try:
            value = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
            if value.content == "exit":
                await ctx.send("Comando cancelado")
                return
            obj['value'] = int(value.content)
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send("Descripción:")
        try:
            description = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
            if description.content == "exit":
                await ctx.send("Comando cancelado")
                return
            obj['description'] = description.content
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return
        
        await ctx.send("Imagen: (opcional)")
        try:
            image = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
            if image.content == "exit":
                await ctx.send("Comando cancelado")
                return
            if image.content != "s":
                asdf = image.attachments[0].url
                obj['image'] = asdf
                img = True

            
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return      

        await ctx.send("Mensaje mandado al usarlo: (opcional)")
        try:
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
            if msg.content == "exit":
                await ctx.send("Comando cancelado")
                return
            if msg.content != "s":
                msgS = True
                obj['message'] = msg.content
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send(f"Cantidad de `{name.content}` en la tienda (opcional)")
        try:
            lot = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
            if lot.content == "exit":
                await ctx.send("Comando cancelado")
                return
            if lot.content != "s":
                if lot.content.isdigit():
                    stock = True
                    obj['stock'] = int(lot.content)
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send("Rol otorgado al usarlo: (opcional)")
        try:
            roleAdded = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
            if roleAdded.content == "exit":
                await ctx.send("Comando cancelado")
                return
            if roleAdded.content != "s":
                roleAd = True
                if roleAdded.content.isdigit():
                    obj['roleAdded'] = int(roleAdded.content)
                else:
                    obj['roleAdded'] = roleAdded.role_mentions[0].id
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

#        await ctx.send("¿Quieres que el objeto permita crear un rol personalizado?")
#        try:
#            newRoleAdded = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
#
#            if newRoleAdded.content.lower() in ("yes", "si", "see", "s"):
#                obj['newRoleAdded'] = True
#        except asyncio.TimeoutError:
#            await ctx.send("Tiempo agotado")
#            return

        await ctx.send(f"Rol removido al usarlo: (opcional)")
        try:
            roleRemoved = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
            if roleRemoved.content == "exit":
                await ctx.send("Comando cancelado")
                return
            if roleRemoved.content != "s":
                roleRe = True
                if roleRemoved.content.isdigit():
                    obj['roleRemoved'] = int(roleRemoved.content)
                obj['roleRemoved'] = roleRemoved.role_mentions[0].id
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return



        await ctx.send("Rol requerido para comprarlo: (opcional)")
        try:
            roleRequired = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)
            if roleRequired.content == "exit":
                await ctx.send("Comando cancelado")
                return
            if roleRequired.content != "s":
                roleReq = True
                if roleRequired.content.isdigit():
                    obj['roleRequired'] = int(roleRequired.content)
                obj['roleRequired'] = roleRequired.role_mentions[0].id
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return        

        
        pyMongoManager.shop.insert_one(obj)
        

        embed = discord.Embed(title="Nuevo objeto añadido a la tienda\n")
        embed.colour = self.bot.get_embed_color(ctx.author.id)
        if img:
            embed.set_thumbnail(url=obj['image'])

        embed.add_field(name="Nombre:", value=obj['name'])
        embed.add_field(name="Descripción:", value=obj['description'], inline=True)
        embed.add_field(name="Valor:", value=f"{obj['value']} :eggplant:")

        if stock:
            embed.add_field(name="Disponibles:", value=obj['stock'])
        else:
            embed.add_field(name="Disponibles:", value="Infinitos")

        if roleAd:
            role1 = ctx.guild.get_role(obj['roleAdded'])
            embed.add_field(name="Rol otorgable:", value=role1.mention)
        else:
            embed.add_field(name="Rol otorgable:", value="Ninguno")

        if roleRe:
            role2 = ctx.guild.get_role(obj['roleRemoved'])
            embed.add_field(name="Rol eliminable:", value=role2.mention)
        else:
            embed.add_field(name="Rol eliminable:", value="Ninguno")
        
        if roleReq:
            role3 = ctx.guild.get_role(obj['roleRequired'])
            embed.add_field(name="Rol requerido:", value=role3.mention)
        else:
            embed.add_field(name="Rol requerido:", value="Ninguno")
        
        if msgS:
            embed.add_field(name="Mensaje:", value=obj['message'])
        else:
            embed.add_field(name="Mensaje:", value="Ninguno")


        await ctx.send(embed=embed)



    @commands.command(aliases=['give-money', 'give', 'gm'])
    async def givemoney(self, ctx):
        args = ctx.message.content.split()[1:]  # User - Amount


        if len(args) >= 2:
            if args[1].isdigit():
                if len(ctx.message.mentions) > 0:
                    member = ctx.message.mentions[0]
                elif args[0].isdigit():
                    if len(args[0]) != 18:
                        await ctx.send('Uso correcto: `la!givemoney <user> <amount>`')
                        return
                    try:

                        member = ctx.guild.get_member(int(args[0]))
                    except:
                        try:
                            member = self.bot.get_user(int(args[0]))
                        except:
                            emoji_nuu = self.bot.get_emoji(762174833752408106)
                            await ctx.send(f'{emoji_nuu} Usuario no encontrado')
                            return
                if member.bot:
                    await ctx.send("Este comando no funciona en bots")
                    return
                
                elif member.id == ctx.author.id:
                    await ctx.send("No puedes darte dinero a ti mismo")
                
                else:
                    emoji_aqua_coin = self.bot.get_emoji(795469711441002537)
                    player_author = pyMongoManager.get_profile(ctx.author.id)
                    player_receiver = pyMongoManager.get_profile(member.id)
                    amount = int(args[1])

                    if amount == 0:
                        await ctx.send(f"Cantidad inválida de :eggplant:")
                    elif player_author['cash'] < amount:
                        await ctx.send(f"No tienes suficiente dinero. Ahora mismo tienes **{player_author['cash']}** :eggplant: ")
                    else:
                        new_balance_author = player_author['cash'] - amount
                        new_balance_receiver = player_receiver['cash'] + amount


                        pyMongoManager.update_money(ctx.author.id, new_balance_author)
                        pyMongoManager.update_money(member.id, new_balance_receiver)    

                        embed = discord.Embed()
                        embed.colour = discord.Color.from_rgb(230, 126, 34)

                        text = f"Dinero de {ctx.author.name}: **{new_balance_author}** (-{amount}) :eggplant:"
                        text += f"\n Dinero de {member.name}: **{new_balance_receiver}** (+{amount}) :eggplant:"
                        
                        embed.description = text

                        await ctx.send(embed=embed)
            else:
                await ctx.send('Cantidad no válida. Uso correcto: `la!givemoney <user> <amount>`')
        else:
            await ctx.send('Uso correcto: `la!givemoney <user> <amount>`')




    @commands.command()
    async def addmoney(self, ctx):
        if ctx.message.author.guild_permissions.administrator:

            args = ctx.message.content.split()[1:]

            if len(args) == 2:
                if args[1].isdigit():
                    if len(ctx.message.mentions) > 0:
                        member = ctx.message.mentions[0]
                    elif args[0].isdigit():
                        if len(args[0]) != 18:
                            await ctx.send('Uso correcto: `la!addmoney <user> <amount>`')
                            return
                        try:
                            member = self.bot.get_user(int(args[0]))
                        except:
                            emoji_nuu = self.bot.get_emoji(762174833752408106)
                            await ctx.send(f'{emoji_nuu} usuario no encontrado')
                            return
                    if member.bot:
                        await ctx.send("Este comando no funciona en bots")
                        return

                    player = pyMongoManager.get_profile(member.id)
                    new_balance = player['cash'] + int(args[1])

                    emoji_aqua_coin = self.bot.get_emoji(795469711441002537)
                    pyMongoManager.update_money(member.id, new_balance)
                    await ctx.send(f"Dinero de {member.name}: **{new_balance}** :eggplant:")
                else:
                    await ctx.send('Cantidad no válida')
            else:
                await ctx.send('Uso correcto: `la!addmoney <user> <amount>`')
        else:
            return


    @commands.command(aliases=['remove-money', 'remove-bal', 'removebal', 'rb'])
    async def removemoney(self, ctx):
        if ctx.message.author.guild_permissions.administrator:

            args = ctx.message.content.split()[1:]

            if len(args) == 2:
                if args[1].isdigit():
                    if len(ctx.message.mentions) > 0:
                        member = ctx.message.mentions[0]
                    elif args[0].isdigit():
                        if len(args[0]) != 18:
                            await ctx.send('Uso correcto: `la!removemoney <user> <amount>`')
                            return
                        try:
                            member = self.bot.get_user(int(args[0]))
                        except:
                            emoji_nuu = self.bot.get_emoji(762174833752408106)
                            await ctx.send(f'{emoji_nuu} usuario no encontrado')
                            return
                    if member.bot:
                        await ctx.send("Este comando no funciona en bots")
                        return

                    player = pyMongoManager.get_profile(member.id)
                    new_balance = player['cash'] - int(args[1])

                    emoji_aqua_coin = self.bot.get_emoji(795469711441002537)
                    pyMongoManager.update_money(member.id, new_balance)
                    await ctx.send(f"Dinero de {member.name}: **{new_balance}** :eggplant:")
                else:
                    await ctx.send('Cantidad no válida')
            else:
                await ctx.send('Uso correcto: `la!removemoney <user> <amount>`')
        else:
            return


    @commands.command()
    async def top(self, ctx):
        args = ctx.message.content.split()[1:]

        page = 1

        if len(args) == 0:
            num_page = 1
        else:
            if args[0].isdigit():
                page = int(args[0])
            else:
                page = 1


        result = pyMongoManager.collection_profiles.find({})
        list_result = list(result)
        list_result.sort(key=lambda result: result['cash']+result['bank'], reverse=True)
        
        num_users = len(list_result)

        ITEMS_PER_PAGE = 10
        num_pages = int((num_users + (ITEMS_PER_PAGE-1)) / ITEMS_PER_PAGE)

        if page > num_pages:
            page = num_pages

        nmb_a = (page-1) * ITEMS_PER_PAGE
        nmb_b = nmb_a + ITEMS_PER_PAGE

        embed = discord.Embed()
        embed.colour = discord.Color.from_rgb(230, 126, 34)
        embed.set_footer(text=f'Página {page} de {num_pages}')


        index = 1
        text = ""
        for item in list_result[nmb_a:nmb_b]:
            text += f"{index+nmb_a}. <@{item['user_id']}> - {item['cash']+item['bank']} :eggplant:\n"
            index += 1
        
        embed.description = text

        await ctx.send(embed=embed)



    @commands.cooldown(1, pyMongoManager.get_time_remaining(), commands.BucketType.user)
    @commands.command()
    async def work(self, ctx):
        user = pyMongoManager.get_profile(ctx.author.id)

        amount = random.randint(100, 700)

        user['cash'] += amount

        pyMongoManager.update_money(ctx.author.id, user['cash'])

        server = pyMongoManager.get_guild(512830421805826048)

        phrases = [x for x in server['work_phrases']]
        

        
        embed = discord.Embed()
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.colour = discord.Color.from_rgb(230, 126, 34)
        embed.description = random.choice(phrases).replace("{amount}", str(amount))
        await ctx.send(embed=embed)


    @commands.command(aliases=['addp', 'add_phrase', 'add-phrase'])
    async def addphrase(self, ctx):
        if ctx.message.author.guild_permissions.administrator:
            args = ctx.message.content.split()[1:]

            if len(args) == 0:
                await ctx.send("Debes poner la frase, sustituyendo las ganancias por `{{{}}}`".format('amount'))

            else:
                if "{{{}}}".format('amount') in args:
                    pyMongoManager.add_work_phrase(' '.join(args).replace("🍆", ":eggplant:"))
                    await ctx.send("Frase añadida!")

                else:
                    await ctx.send("Debes sustituir las ganancias por `{{{}}}`".format('amount'))

        else:
            emojiNo = self.bot.get_emoji(753432948371357696)
            await ctx.send(emojiNo)


    @commands.command(aliases=['showp', 'show_phrase', 'show-phrase'])
    async def showphrases(self, ctx):
        if ctx.message.author.guild_permissions.administrator:
            args = ctx.message.content.split()[1:]

            server = pyMongoManager.get_guild(512830421805826048)
            work_phrases = server['work_phrases']

            page = 1
            num_pages = math.ceil(len(work_phrases)/10)

            if len(args) > 0:
                if args[0].isdigit():
                    if num_pages >= page:
                        page = int(args[0])

                    else:
                        page = num_pages


            embed = discord.Embed(title='Frases del Comando Work')
            embed.colour = discord.Color.from_rgb(230, 126, 34)
            text = ""

            index = page*10-9
            for x in work_phrases[page*10-10:page*10]:
                text += f"{index}. {x}\n"
                index+= 1

            embed.description = text
            embed.set_footer(text=f"Página {page} de {num_pages}")
            await ctx.send(embed=embed)

        else:
            emojiNo = self.bot.get_emoji(753432948371357696)
            await ctx.send(emojiNo)            


            
            
    @commands.command(aliases=['delp', 'delete_phrase', 'delete-phrase'])
    async def deletephrase(self, ctx):
        if ctx.message.author.guild_permissions.administrator:
            args = ctx.message.content.split()[1:]
            
            if len(args) == 0:
                await ctx.send("Tienes que poner la frase o su posición")
    
            
            else:
                server = pyMongoManager.get_guild(512830421805826048)
                index = None
                if len(args) == 2 and args[0].isdigit() and args[1].isdigit():
                    index = [int(args[0]), int(args[1])]
                    try:
                        phrase = server['work_phrases'][index[0]-1:index[1]]
                        pyMongoManager.collection_guilds.update({'guild_id': 512830421805826048}, {'$pull': {'work_phrases': { '$in': phrase }}}, upsert=False, multi=True)
                        await ctx.send("Frase eliminada!")
                    except IndexError:
                        await ctx.send("Los índices son incorrectos")
    
    
                elif len(args) == 1 and args[0].isdigit():
                    index = int(args[0])
                    try:
                        phrase = server['work_phrases'][index-1]
                        pyMongoManager.collection_guilds.update({'guild_id': 512830421805826048}, {'$pull': {'work_phrases': phrase}})
                        await ctx.send("Frase eliminada!")
                    except IndexError:
                        await ctx.send(f"El índice es incorrecto (No existe elemento nº{index}")
    
    
    
                else:
                    phrase = ' '.join(args).replace("🍆", ":eggplant:")
                    if phrase not in server['work_phrases']:
                        await ctx.send(f"No se ha encontrado la frase `{phrase}`")
                    else:
                        pyMongoManager.collection_guilds.update({'guild_id': 512830421805826048}, {'$pull': {'work_phrases': phrase}})
                        await ctx.send("Frase eliminada!")

        else:
            emojiNo = self.bot.get_emoji(753432948371357696)
            await ctx.send(emojiNo)  
            
            
    @commands.command()
    async def withdraw(self, ctx):
        args = ctx.message.content.split()[1:]

        if len(args) == 0:
            await ctx.send("Uso correcto: la!withdraw <cantidad>")
            return

        amount = 0

        if args[0].isdigit():
            amount = int(args[0])
        else:
            if args[0].lower() == "all":
                amount = "all"
            else:
                await ctx.send("Por favor, ingrese una cantidad válida")
                return

        usr = pyMongoManager.collection_profiles.find_one({'user_id': ctx.author.id})
        if amount == "all":
            amount = usr['bank']
        if usr['bank'] < amount:
            await ctx.send("No tienes suficientes :eggplant:")
            return
        usr['cash'] += amount
        usr['bank'] -= amount
        pyMongoManager.collection_profiles.replace_one({'user_id': ctx.author.id}, usr)
        await ctx.send(f"Has sacado {amount} :eggplant: del banco")


    @commands.command()
    async def deposit(self, ctx):
        args = ctx.message.content.split()[1:]

        if len(args) == 0:
            await ctx.send("Uso correcto: la!deposit <cantidad>")
            return

        amount = 0
        if args[0].isdigit():
            amount = int(args[0])
        else:
            if args[0].lower() == "all":
                amount = "all"
            else:
                await ctx.send("Por favor, ingrese una cantidad válida")
                return


        usr = pyMongoManager.collection_profiles.find_one({'user_id': ctx.author.id})
        if amount == "all":
            amount = usr['cash']
        if usr['cash'] < amount:
            await ctx.send("No tienes suficientes :eggplant:")
            return
        usr['cash'] -= amount
        usr['bank'] += amount
        pyMongoManager.collection_profiles.replace_one({'user_id': ctx.author.id}, usr)
        await ctx.send(f"Has depositado {amount} :eggplant: en el banco")



def setup(bot):
    bot.add_cog(EconomyCog(bot))
    print("Economy Cog CARGADO")

