import discord
from discord.ext import commands
import copy

import aiohttp

from src.lib.mongodb import PyMongoManager

#import modules.CONSTANTS_IMAGES as CONSTANTS_IMAGES

#from modules.image_editor import ImageEditor

#import modules.CONSTANTS as CONSTANTS

i#mageEditor = ImageEditor()

pyMongoManager = PyMongoManager()
session_emoji = aiohttp.ClientSession()

# BASE PARA LA ECONOMIA DE PANCHESSCOBOT
class EconomyCog(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot
        
        self.all_products = {}
        self.all_products.update(CONSTANTS_IMAGES.BOARDS)
        self.all_products.update(CONSTANTS_IMAGES.PIECES)
        self.all_products.update(CONSTANTS_IMAGES.BORDERS)

        self.id_boards = CONSTANTS_IMAGES.BOARDS.keys()
        self.id_pieces = CONSTANTS_IMAGES.PIECES.keys()
        self.id_borders = CONSTANTS_IMAGES.BORDERS.keys()

        self.id_all = self.all_products.keys()


    @commands.command()
    async def shop(self, ctx):
        args = ctx.message.content.split()[1:]
        # No se podrá comprar los elementos por defecto (brown, cburnett, cyan-basic)
        if len(args) > 0:
            category_input = args[0].lower()
            correct_category = None
            if 'board' in category_input:
                correct_category = 'boards'
                shop_items = copy.deepcopy(CONSTANTS_IMAGES.BOARDS)
                del shop_items['brown']
            elif 'piece' in category_input:
                correct_category = 'pieces'
                shop_items = copy.deepcopy(CONSTANTS_IMAGES.PIECES)
                del shop_items['cburnett']
            elif 'border' in category_input:
                correct_category = 'borders'
                shop_items = copy.deepcopy(CONSTANTS_IMAGES.BORDERS)
                del shop_items['cyan']

            if correct_category:
                profile = pyMongoManager.get_chess_profile(ctx.author.id)
                own_items = profile[correct_category]
                emoji_aqua_coin = self.bot.get_emoji(795469711441002537)

                embed = discord.Embed()
                embed.colour = discord.Color.from_rgb(0, 255, 255)
                embed.title = correct_category.capitalize()
                text = 'Use `aq!buy <item_id>` for buy a item\n'
                text += 'Use `aq!preview <item_id>` to preview\n\n'
                text += '**PRICE | item_id**:\n----------------------\n'
                
                for item_id in shop_items.keys():
                    item_dict = shop_items[item_id]
                    item_price = item_dict['price']

                    if item_id in own_items:
                        text += f'~~{item_price}~~ {emoji_aqua_coin} | ~~{item_id}~~\n'
                    else:
                        text += f'{item_price} {emoji_aqua_coin} | {item_id}\n'
                
                embed.description = text

                await ctx.send(embed=embed)

            else:
                await ctx.send('Correct Use: **aq!shop <pieces/boards/borders>**')
        else:
            await ctx.send('Correct Use: **aq!shop <pieces/boards/borders>**')

        # aq!shop <category> |||| category: pieces, board, border, ¿profile_card?(en el futuro)

    @commands.command()
    async def buy(self, ctx):
        args = ctx.message.content.split()[1:]

        if len(args) > 0:
            item_id = args[0].lower()

            if item_id in self.id_all:
                player = pyMongoManager.get_chess_profile(ctx.author.id)
                player_items_id = player['boards'] + player['pieces'] + player['borders']   # Items comprados

                if item_id not in player_items_id:
                    product = self.all_products[item_id]

                    if player['eris'] >= product['price']:
                        final_balance = player['eris'] - product['price']
                        category = None
                        if item_id in self.id_boards:
                            category = 'boards'
                        elif item_id in self.id_pieces:
                            category = 'pieces'
                        elif item_id in self.id_borders:
                            category = 'borders'
                        
                        pyMongoManager.buy_item(ctx.author.id, category, item_id, final_balance)
                        emoji_aqua_coin = self.bot.get_emoji(795469711441002537)
                        embed = discord.Embed()
                        embed.colour = discord.Color.from_rgb(0, 255, 255)
                        text= f'Item purchased: **{product["name"]}**\n'
                        text += f'New Balance: {player["eris"]} - {product["price"]} = **{final_balance}** {emoji_aqua_coin}'
                        embed.description = text

                        await ctx.send(embed=embed)

                    # VERIFICAMOS EL SALDO, RETIRAMOS EL SALDO y AÑADIMOS EL ITEM AL INVENTARIO
                    else:
                        await ctx.send('Insufficient balance')
                else:
                    await ctx.send('You already own this product')
            else:
                await ctx.send('**Incorrect item_id**. Use `aq!shop` to see the list of products.')    

        else:
            await ctx.send('Correct Use: `aq!buy <item_id>`. Use `aq!shop` to see the list of products.')

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
                    member = await ctx.guild.fetch_member(int(args[0]))
                except:
                    try:
                        member = await self.bot.fetch_user(int(args[0]))
                    except:
                        emoji_nuu = self.bot.get_emoji(762174833752408106)
                        await ctx.send(f'{emoji_nuu} User not found')
                        return
            else:
                member = ctx.author
        
        if member.bot:
            await ctx.send("This command does not work on bots")
            return

        player = pyMongoManager.get_chess_profile(member.id)

        emoji_aqua_coin = self.bot.get_emoji(795469711441002537)

        embed = discord.Embed()
        embed.colour = discord.Color.from_rgb(0, 255, 255)
        embed.title = f"{member.name}'s Inventory"
        text = f'Cash: **{player["eris"]} {emoji_aqua_coin}**\n\n'
        text += '**Boards:**\n'
        text += ', '.join(player['boards'])
        text += '\n\n**Pieces:**\n'
        text += ', '.join(player['pieces'])
        text += '\n\n**Borders:**\n'
        text += ', '.join(player['borders'])

        embed.description = text

        await ctx.send(embed=embed)

    """
    @commands.command()
    async def info(self, ctx):
        pass
    """

    @commands.command(aliases=['equip'])
    async def use(self, ctx):
        args = ctx.message.content.split()[1:]

        if len(args) > 0:
            item_id = args[0].lower()

            if item_id in self.id_all:
                player = pyMongoManager.get_chess_profile(ctx.author.id)
                player_items_id = player['boards'] + player['pieces'] + player['borders']   # Items comprados

                if item_id in player_items_id:
                    product = self.all_products[item_id]

                    category_name = None
                    current_category = None
                    if item_id in self.id_boards:
                        current_category = 'current_board'
                        category_name = 'Board'
                    elif item_id in self.id_pieces:
                        current_category = 'current_pieces'
                        category_name = 'Pieces'
                    elif item_id in self.id_borders:
                        current_category = 'current_border'
                        category_name = 'Border'
                        
                    pyMongoManager.set_current_item(ctx.author.id, current_category, item_id)
                    text= f'Chosen {category_name}: **{product["name"]}**\n'

                    await ctx.send(text)
                else:
                    await ctx.send(f"You don't have that item, but you can buy it with the command `aq!buy {item_id}`")
            else:
                await ctx.send('**Incorrect item_id**. Use `aq!inventory` to see the list of purchased items.')    

        else:
            await ctx.send('Correct Use: `aq!use <item_id>`. Use `aq!inventory` to see the list of purchased items.')
    

    @commands.command()
    async def preview(self, ctx):
        args = ctx.message.content.split()[1:]

        async def help_preview():
            embed = discord.Embed()
            embed.colour = discord.Color.from_rgb(0, 255, 255)
            embed.description = 'Correct Use:\n\naq!preview <itemId>\naq!preview <itemId1> <itemId2> ...'
            await ctx.send(embed=embed)


        if len(args) == 0:
            await help_preview()
            return

        else:
            items_count = 0
            correct_pieces = None
            correct_board = None
            correct_border = None

            for arg in args:
                item_id = arg.lower()
                
                if item_id in self.id_all:
                    if item_id in self.id_boards:
                        correct_board = item_id
                    elif item_id in self.id_pieces:
                        correct_pieces = item_id
                    elif item_id in self.id_borders:
                        correct_border = item_id
                    items_count += 1
            
            player = pyMongoManager.get_chess_profile(ctx.author.id)
            
            if correct_pieces:
                player['current_pieces'] = correct_pieces
            if correct_board:
                player['current_board'] = correct_board
            if correct_border:
                player['current_border'] = correct_border

            if items_count:
                img_buffer = imageEditor.createChessBoard(player, CONSTANTS.BASE_FEN)
                await ctx.send(file=discord.File(fp=img_buffer, filename='game.png'))
            else:
                await help_preview()
                return
    
    @commands.cooldown(1, 10.0, commands.BucketType.user)
    @commands.command(aliases=['give-money', 'give', 'gm'])
    async def givemoney(self, ctx):
        args = ctx.message.content.split()[1:]  # User - Amount

        if len(args) >= 2:
            if args[1].isdigit():
                if len(ctx.message.mentions) > 0:
                    member = ctx.message.mentions[0]
                elif args[0].isdigit():
                    try:
                        member = await self.bot.fetch_user(int(args[0]))
                    except:
                        emoji_nuu = self.bot.get_emoji(762174833752408106)
                        await ctx.send(f'{emoji_nuu} User not found')
                        return
                if member.bot:
                    await ctx.send("This command does not work on bots")
                    return
                
                elif member.id == ctx.author.id:
                    await ctx.send("You can't give money to yourself")
                
                else:
                    emoji_aqua_coin = self.bot.get_emoji(795469711441002537)
                    player_author = pyMongoManager.get_chess_profile(ctx.author.id)
                    player_receiver = pyMongoManager.get_chess_profile(member.id)
                    amount = int(args[1])

                    if amount == 0:
                        await ctx.send(f"Please give more than **0¨** {emoji_aqua_coin}")
                    elif player_author['eris'] < amount:
                        await ctx.send(f"You don't have enough money. You currently have **{player_author['eris']}** {emoji_aqua_coin} ")
                    else:
                        new_balance_author = player_author['eris'] - amount
                        new_balance_receiver = player_receiver['eris'] + amount

                        pyMongoManager.update_money(ctx.author.id, new_balance_author)
                        pyMongoManager.update_money(member.id, new_balance_receiver)    

                        embed = discord.Embed()
                        embed.colour = discord.Color.from_rgb(0, 255, 255)

                        text = f"{ctx.author.name}'s Cash: **{new_balance_author}** {emoji_aqua_coin}"
                        text += f"\n{member.name}'s Cash: **{new_balance_receiver}** {emoji_aqua_coin}"
                        
                        embed.description = text

                        await ctx.send(embed=embed)
            else:
                await ctx.send('Incorrect <amount>. Correct Use: `aq!givemoney <user> <amount>`')
        else:
            await ctx.send('Correct Use: `aq!givemoney <user> <amount>`')


    @commands.command()
    async def addmoney(self, ctx):
        if ctx.author.id != 402291352282464259:
            return

        args = ctx.message.content.split()[1:]

        if len(args) == 2:
            if args[1].isdigit():
                if len(ctx.message.mentions) > 0:
                    member = ctx.message.mentions[0]
                elif args[0].isdigit():
                    try:
                        member = await self.bot.fetch_user(int(args[0]))
                    except:
                        emoji_nuu = self.bot.get_emoji(762174833752408106)
                        await ctx.send(f'{emoji_nuu} User not found')
                        return
                if member.bot:
                    await ctx.send("This command does not work on bots")
                    return
                
                player = pyMongoManager.get_chess_profile(member.id)
                new_balance = player['eris'] + int(args[1])

                emoji_aqua_coin = self.bot.get_emoji(795469711441002537)
                pyMongoManager.update_money(member.id, new_balance)
                await ctx.send(f"{member.name}'s Cash: **{new_balance}** {emoji_aqua_coin}")
            else:
                await ctx.send('Incorrect <amount>')
        else:
            await ctx.send('Correct Use: `aq!addmoney <user> <amoun>`')





    """ @commands.command()
    async def top(self, ctx):
        args = ctx.message.content.split()[1:]
        emoji_aqua_coin = self.bot.get_emoji(795469711441002537)

        # CALCULAMOS EN QUE PÁGINA ESTAMOS
        page = 1

        if len(args) == 0:
            num_page = 1
        else:
            if args[0].isdigit():
                page = int(args[0])
            else:
                page = 1

        #result = self.chess_players.find({'eris': {'$ne': 0}})
        result = pyMongoManager.collection_chess_players.find({'eris': {'$ne': 0}})
        list_result = list(result)
        list_result.sort(key=lambda result: result['eris'], reverse=True)
        
        num_users = len(list_result)        # TOTAL DE USUARIOS

        ITEMS_PER_PAGE = 10
        num_pages = int((num_users + (ITEMS_PER_PAGE-1)) / ITEMS_PER_PAGE)  # TOTAL DE PÁGINAS

        if page > num_pages:    # POR SI SE PASAN DE PÁGINA
            page = num_pages

        nmb_a = (page-1) * ITEMS_PER_PAGE     # EL RANGO DE VALORES QUE USAREMOS
        nmb_b = nmb_a + ITEMS_PER_PAGE

        embed = discord.Embed()
        embed.colour = discord.Color.from_rgb(0, 255, 255)
        embed.set_footer(text=f'Page {page} of {num_pages}')

        # MOSTRAMOS LOS RESULTADOS
        index = 1
        text = ""
        for item in list_result[nmb_a:nmb_b]:
            text += f"{index+nmb_a}. {item['user_id']} - {item['eris']} {emoji_aqua_coin}\n"
            index += 1
        
        embed.description = text

        await ctx.send(embed=embed) """

def setup(bot):
    bot.add_cog(EconomyCog(bot))
    print("Economy Cog CARGADO")

