import asyncio

import discord
from discord.ext import commands
import copy

import aiohttp
import math

import pymongo
from src.lib.mongodb import PyMongoManager

import config
from src.bean.CONSTANTS import *

import random


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
        list_objects = list(pyMongoManager.shop.find())
        list_objects.sort(key=lambda x: x['value'])

        num_pages = math.ceil((len(list_objects)/10))



        for x in range(1, num_pages+1):
            embed = discord.Embed()
            embed.colour = discord.Color.from_rgb(230, 126, 34)
            text = ""
            for i in list_objects[x*10-10:x*10]:
                text += f"**{i['name'].capitalize()}** - {i['value']} :eggplant:\n"
                text += f"{i['description']}\n\n"

            embed.description = text
            embed.set_footer(text=f"Página {x} de {num_pages}")
            await ctx.send(embed=embed)

        await ctx.message.delete()



    @commands.command()
    async def buy(self, ctx):
        args = ctx.message.content.split()[1:]

        user = pyMongoManager.get_profile(ctx.author.id)


        channel_logs = self.bot.get_channel(config.channel_logs_id)

        C_trencada = self.bot.get_emoji(555903896363466762)
        ded = self.bot.get_emoji(633063734721380403)

        if len(args) == 0:
            await ctx.send("Debes poner lo que quieras comprar")

        else:
            cons = ' '.join(args).lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó","o").replace("ú", "u").replace(" ", "").replace(".", "")
            obj = pyMongoManager.shop.find_one({"key": cons})

            if obj:
                if obj['lot'] == 0:
                    await ctx.send(f"No queda `{obj['name']}` en la tienda {C_trencada}")

                else:

                    if user['panchessco_money'] >=  obj['value']:
                        user['panchessco_money'] -= obj['value']

                        if obj['lot'] is not None:
                            quantity = obj['lot']-1
                            pyMongoManager.collection_profiles.update_one({'name': obj['name']}, {"$set":{"lot":quantity}})

                        if obj['name'] in user['inventory']:
                            user['inventory'][obj['name']] += 1

                        else:
                            user['inventory'][obj['name']] = 1

                        if obj['log'] is True:
                            await channel_logs.send(f"El usuario **{ctx.author.name}** ha comprado el objeto `{obj['name']}`")

                        pyMongoManager.collection_profiles.replace_one({'user_id': ctx.author.id}, user)

                        await ctx.send(f"Has recibido `{obj['name']}`")

                    else:
                        await ctx.send("No tienes suficientes :eggplant:")

            else:
                await ctx.send("No se han encontrado el objeto")





    @commands.command()
    async def use(self, ctx):
        args = ctx.message.content.split()[1:]

        cons = ' '.join(args).lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú","u").replace(" ", "").replace(".", "")
        obj = pyMongoManager.shop.find_one({"key": cons})
        user = pyMongoManager.get_profile(ctx.author.id)

        channel_logs = self.bot.get_channel(config.channel_logs_id)

        if obj['name'] in user['inventory']:


            if user['inventory'][obj['name']] > 0:


                if obj['oldRoleAdded'] != 0:
                    role = ctx.guild.get_role(obj['oldRoleAdded'])
                    if role not in ctx.author.roles:
                        await ctx.author.add_roles(role)

                        if obj['log'] is True:
                            await channel_logs.send(f"El usuario **{ctx.author.name}** ha recibido el rol {role.name}")

                    else:
                        await ctx.send("Ya posees ese rol")

                if obj['newRoleAdded'] != 0:
                    await ctx.send("¿Qué nombre quieres ponerle al rol?")
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=3600)
                    await ctx.guild.create_role(name=msg)
                    roleCreated = ctx.guild.get_role(name=msg)
                    if roleCreated in ctx.author.roles:
                        await ctx.send("Ya posees ese rol")
                    else:
                        if obj['log'] is True:
                            await channel_logs.send(f"El usuario **{ctx.author.name}** ha creado y recibido el rol {roleCreated.name} por la compra de `{obj['name']}`")
                        await ctx.author.add_roles(roleCreated)
                        await ctx.send("Rol añadido")

                if obj['roleRemoved'] != 0:
                    roleRemoved = ctx.guild.get_role(obj['roleRemoved'])
                    if roleRemoved in ctx.author.roles:
                        await ctx.author.remove_roles(roleRemoved)
                        if obj['log'] is True:
                            await channel_logs.send(f"El rol {roleRemoved.name} ha sido removido del usuario **{ctx.author.name}** por la compra de `{obj['name']}`")
                    else:
                        await ctx.send("No se ha encontrado el rol a eliminar")

                if obj['channel_id'] != 0:
                    channelToSend = ctx.guild.get_channel(obj['channel_id'])
                    await channelToSend.send(obj['message'])
                    if obj['log'] is True:
                        await channel_logs.send(f"El usuario **{ctx.author.name}** ha comprado el objeto `{obj['name']}`")

                user['inventory'][cons] -= 1
                pyMongoManager.collection_profiles.replace_one({"user_id": ctx.author.id}, user)

            else:
                await ctx.send(f"No tienes `{obj['name']}`")

        else:
            await ctx.send("No tienes o no se ha encontrado el objeto seleccionado")




    @commands.command(aliases=['inv', 'wallet'])
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
        embed.colour = discord.Color.from_rgb(230, 126, 34)
        embed.title = f"Inventario de {member.name}"

        text = ""
        text += f"Dinero: {user['panchessco_money']} :eggplant:\n\n"

        for name, quantity in user['inventory'].items():
            text += f"{name} (x{quantity})\n"

        embed.description = text
        await ctx.send(embed=embed)

    """
    @commands.command()
    async def info(self, ctx):
        pass
    """


    

    @commands.command(aliases=['add_item', 'add_object', 'co'])
    async def createobject(self, ctx):

        obj = pyMongoManager.object_base

        await ctx.send("¿Qué nombre quieres ponerle?")
        try:
            name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)

            obj['name'] = name.content
            obj['key'] = name.content.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú","u").replace(" ", "").replace(".", "")
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send("¿Qué valor tendrá?")
        try:
            value = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)

            obj['value'] = int(value.content)
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send("Escribe la descripción:")
        try:
            description = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)

            obj['description'] = description.content
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send(f"¿Cuántos {name.content} habrá en la tienda? Si no quieres que haya límite, pon `s`")
        try:
            lot = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)

            if lot.content != "s":
                if lot.content.isdigit():
                    obj['lot'] = int(lot.content)
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send("¿Qué rol otorgará el objeto? Si no quieres que de ninguno, pon `s`")
        try:
            oldRoleAdded = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and len(message.role_mentions) > 0 or message.content == "s", timeout=600)

            if oldRoleAdded.content != "s":
                obj['oldRoleAdded'] = oldRoleAdded.role_mentions[0].id
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send("¿Quieres que el objeto permita crear un rol personalizado?")
        try:
            newRoleAdded = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)

            if newRoleAdded.content.lower() in ("yes", "si", "see", "s"):
                obj['newRoleAdded'] = True
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send(f"¿Qué rol quieres que `{obj['name']}` elimine un rol de un usuario? Si no quieres que quite ningún rol, pon `s`")
        try:
            roleRemoved = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and len(message.role_mentions) > 0 or message.content == "s", timeout=600)

            if roleRemoved.content != "s":
                obj['roleRemoved'] = roleRemoved.role_mentions[0].id
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send("¿En qué canal quieres que envíe un mensaje? Si no quieres, pon `s`")
        try:
            channel_id = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)

            if channel_id.content.lower() != "s":
                obj['channel_id'] = int(channel_id.content)

                await ctx.send("Introduce el mensaje a enviar")
                message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)

                obj['message'] = message.content
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return

        await ctx.send("¿Quieres que se notifique en el canal <#835391694215053352> cuando alguien adquiera el objeto o cuando se le de un rol por su uso?")
        try:
            log = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=600)

            if log.content.lower() in ("yes", "si", "see", "s"):
                obj['log'] = True

            pyMongoManager.shop.insert_one(obj)
            await ctx.send(f"{obj['name']} creado!")
        except asyncio.TimeoutError:
            await ctx.send("Tiempo agotado")
            return





    @commands.command(aliases=['give-money', 'give', 'gm'])
    async def givemoney(self, ctx):
        args = ctx.message.content.split()[1:]  # User - Amount
        print(args)

        if len(args) >= 2:
            if args[1].isdigit():
                if len(ctx.message.mentions) > 0:
                    member = ctx.message.mentions[0]
                elif args[0].isdigit():
                    try:
                        print("a")
                        print(int(args[0]))
                        member = ctx.guild.get_member(int(args[0]))
                    except:
                        try:
                            print("b")
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
                        await ctx.send(f"Por favor da más de **0** :eggplant:")
                    elif player_author['panchessco_money'] < amount:
                        await ctx.send(f"No tienes suficiente dinero. Ahora mismo tienes **{player_author['panchessco_money']}** :eggplant: ")
                    else:
                        new_balance_author = player_author['panchessco_money'] - amount
                        new_balance_receiver = player_receiver['panchessco_money'] + amount


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
                    new_balance = player['panchessco_money'] + int(args[1])

                    emoji_aqua_coin = self.bot.get_emoji(795469711441002537)
                    pyMongoManager.update_money(member.id, new_balance)
                    await ctx.send(f"Dinero de {member.name}: **{new_balance}** :eggplant:")
                else:
                    await ctx.send('Cantidad no válida')
            else:
                await ctx.send('Uso correcto: `la!addmoney <user> <amount>`')
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


        result = pyMongoManager.collection_profiles.find({'panchessco_money': {'$ne': 0}})
        list_result = list(result)
        list_result.sort(key=lambda result: result['panchessco_money'], reverse=True)
        
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
            text += f"{index+nmb_a}. <@{item['user_id']}> - {item['panchessco_money']} :eggplant:\n"
            index += 1
        
        embed.description = text

        await ctx.send(embed=embed)



    @commands.cooldown(1, pyMongoManager.get_time_remaining(), commands.BucketType.user)
    @commands.command()
    async def work(self, ctx):
        user = pyMongoManager.get_profile(ctx.author.id)

        amount = random.randint(100, 700)

        user['panchessco_money'] += amount

        pyMongoManager.update_money(ctx.author.id, user['panchessco_money'])

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
                    if phrase not in work_phrases:
                        await ctx.send(f"No se ha encontrado la frase `{phrase}`")
                    else:
                        pyMongoManager.collection_guilds.update({'guild_id': 512830421805826048}, {'$pull': {'work_phrases': phrase}})
                        await ctx.send("Frase eliminada!")

        else:
            emojiNo = self.bot.get_emoji(753432948371357696)
            await ctx.send(emojiNo)  
            
            
            

    @commands.command(aliases=['bj'])
    async def blackjack(self, ctx):
        args = ctx.message.content.split()[1:]

        player_cards = []
        bot_cards = []

        

        player_value = 0
        bot_value = 0

        endgame = False

        player_wins = False
        blackjack = False

        emoji_server1 = self.bot.get_guild(728003338880286753)
        emoji_server2 = self.bot.get_guild(855864156765945897)


        game_cards = [11, 11, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6,
        7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]*3

        game_cards_string = {
    
            1: ['<:AsTreboles:855862941164109824>', '<:AsCorazones:855862941219946536>'],
            2: ['<:2corazones:855862940980346893>', '<:2diamantes:855862941034348585>', '<:2picas:855862941168304198>', '<:2treboles:855862941265952788>'],
            3: ['<:3picas:855862940796452936>', '<:3treboles:855862940904849409>', '<:3diamantes:855862941413146624>', '<:3corazones:855862941563617310>'],
            4: ['<:4treboles:855862940871688253>', '<:4picas:855862941047455765>', '<:4diamantes:855862941152575546>', '<:4corazones:855862941228597289>'],
            5: ['<:5treboles:855862940984279082>', '<:5picas:855862941186654249>', '<:5diamantes:855862941295181824>', '<:5corazones:855862941337124914>'],
            6: ['<:6corazones:855862940912582667>', '<:6diamantes:855862941113647105>', '<:6treboles:855862941201989672>', '<:6picas:855862941311303731>'],
            7: ['<:7treboles:855862940980740167>', '<:7picas:855862941201858580>', '<:7corazones:855862941202645042>', '<:7diamantes:855862941231218718>'],
            8: ['<:8treboles:855862940899737621>', '<:8corazones:855862941268836383>', '<:8diamantes:855862941303832625>', '<:8picas:855862941424156722>'],
            9: ['<:9picas:855862940792389633>', '<:9treboles:855862940993060884>', '<:9diamantes:855862941236330526>', '<:9corazones:855862941337124904>'],
            10:['<:KDiamantes:855862940883746816>', '<:KTreboles:855862940943384627>', '<:JPicas:855862941035528232>', '<:JTreboles:855862941080616980>',
            '<:JDiamantes:855862941114433556>', '<:JCorazones:855862941189931028>', '<:KCorazones:855862941261758534>', '<:QDiamantes:855862941390602281>',
            '<:KPicas:855862941404758066>', '<:QCorazones:855862941454696488>', '<:QPicas:855864206392950825>', '<:QTreboles:855864206527430657>', 
            '<:10treboles:855862941287317544>', '<:10diamantes:855862941366747156>', '<:10picas:855862941282467870>', '<:10corazones:855862941499785246>'],
            11:['<:AsPicas:855862941240655892>', '<:AsDiamantes:855862941262151751>']
        
        
        
        }




        if len(args) == 0:
            await ctx.send("Debes poner tu apuesta")

        else:
            
            if args[0].isdigit():

                player = pyMongoManager.get_profile(ctx.author.id)

                if player['panchessco_money'] >= (amount := int(args[0])):


                    async def hit(gambler):

                        card_value = random.choice(game_cards)
                        card_emoji = random.choice([x for x in game_cards_string[card_value]])
                        game_cards.remove(card_value)
                        
                        if gambler == "player":

                            player_cards.append(card_emoji)
                            player_value += card_value

                        else:
                            bot_cards.append(card_emoji)
                            bot_value += card_value


                    async def double(gambler):

                        card_value = random.choice(game_cards)
                        card_emoji = random.choice([x for x in game_cards_string[card_value]])
                        game_cards.remove(card_value)

                        if gambler == "player":

                            player_cards.append(card_emoji)
                            player_value += card_value
                            amount*=2

                        else:
                            bot_cards.append(card_emoji)
                            bot_value += card_value

                        endgame = True


                    async def stand():

                        if bot_value < 17:
                            await hit("bot")
                        endgame = True


                    async def check():

                        if player_value > 21 and bot_value <= 21:
                            endgame = True 

                        elif player_value == 21 and bot_value != 21:
                            blackjack = True 
                            endgame = True
                            player_wins = True

                        elif player_value < 21 and bot_value > 21:
                            engame = True
                            player_wins = True

                        else:
                            pass




                    embed = discord.Embed()
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                    embed.add_field(name=f"{ctx.author.name}'s cards:\n", value=f"{' '.join(player_cards)}\n Value: {player_value}", inline=True)
                    embed.add_field(name=f"Lalatina's cards:\n", value=f"{' '.join(bot_cards)}\n Value: {bot_value}", inline=True)
                    btn_red = Button(label='Red Button!', style=ButtonStyle.Red, custom_id='red_btn')
                    await hit("player")
                    await hit("player")
                    await hit("bot")
                    await hit("bot")

                    await ctx.send(embed=embed)





def setup(bot):
    bot.add_cog(EconomyCog(bot))
    print("Economy Cog CARGADO")

