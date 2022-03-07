import discord
from discord.ext import commands
import copy
from discord.ext.commands.core import command

import pymongo

import unidecode

import aiohttp
import config


from src.bean.AutoReactionMenuBean import AutoReactionMenuBean
from src.bean.AutoReplyMenuBean import AutoReplyMenuBean

from src.bean.MenuStackBean import MenuStackBean


PREFIX = config.prefix

autoReactionMenuStackBean = MenuStackBean()
autoReplyMenuStackBean = MenuStackBean()

class EmojiCog(commands.Cog, name="Emoji"):
    def __init__(self, bot):
        self.bot = bot

        self.reaction_count_min = 5

        self.star_board_dict = {}       # original_message_id: { startbaord_channel_message_id, emoji_id}
        self.auto_reaction_dict = {}    # emoji -> reaction
        self.auto_reply_dict = {}       # tag -> reply

        star_board_list = self.bot.pyMongoManager.get_all_starboard()
        auto_reaction_list = self.bot.pyMongoManager.get_all_auto_reaction()
        auto_reply_list = self.bot.pyMongoManager.get_all_auto_reply()

        for item in star_board_list:
            self.star_board_dict[item['original_message_id']] = {
                'starboard_channel_message_id': item['starboard_channel_message_id'],
                'emoji_id': item['emoji_id']
            }

        for item in auto_reaction_list:
            self.auto_reaction_dict[item['message_base']] = item['emoji_id']

        for item in auto_reply_list:
            self.auto_reply_dict[item['tag']] = item['message_reply']

        # Esto se deberá agregar con otro comando
        """self.auto_reaction_dict = {
            'ale': 752648508850438275,
            'a': 757918565171986472,
            'sexo': 752658698723262517,
            'gane': 750007424278200380,
            'a?': 757918565171986472,
            'chesscom': 856739513794297886,
            'chess24': 856739557349130250,
            'lichess': 856739640727175169,
            'f': 855227960234344468,
            'perdi': 852663438358347806,
            'ah': 757918565171986472,
            'no': 752651912951627786,
            'nel': 752651912951627786,
            'nope': 752651912951627786,
            'nop': 752651912951627786,
            'es menor': 859501615110291466
        }"""
        
        """# Movido a base_cog.py
        self.message_auto_reply = {
            'lalatina': 'https://media.tenor.com/images/37465eb4d7edea808a511abc18be5484/tenor.gif',
            'lala': 'Es lalatina :c'
        }"""
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        if payload.message_id in autoReactionMenuStackBean.getMessageIdList():
            await autoReactionMenuStackBean.updateMenuBean(payload.message_id, payload.user_id, payload.emoji)
        elif payload.message_id in autoReplyMenuStackBean.getMessageIdList():
            await autoReplyMenuStackBean.updateMenuBean(payload.message_id, payload.user_id, payload.emoji)
        
        else:
            channel_message = self.bot.get_channel(payload.channel_id)
            category_channel = channel_message.category

            if category_channel.id in config.star_board_category_channels_id:
                if payload.message_id in self.star_board_dict.keys():
                    star_board = self.star_board_dict[payload.message_id]

                    if payload.emoji.id and payload.emoji.id == star_board['emoji_id']:
                        channel_star_board = self.bot.get_channel(config.channel_star_board_id)
                        msg_channel_star_board = await channel_star_board.fetch_message(star_board['starboard_channel_message_id'])
                        
                        count = int(msg_channel_star_board.content.split('**')[1])

                        new_content = msg_channel_star_board.content.replace(f'**{count}**', f'**{count+1}**')
                        
                        await msg_channel_star_board.edit(content=new_content)
                    pass
                else:
                    # ver si agregar el mensaje
                    original_message = await channel_message.fetch_message(payload.message_id)

                    content_lower = unidecode.unidecode(original_message.content.lower().replace(".", ""))
                    if content_lower in self.auto_reaction_dict.keys():
                        return

                    if payload.emoji.id and self.bot.get_emoji(payload.emoji.id) and not original_message.author.bot:
                        emoji_count = 0

                        for reaction in original_message.reactions:
                            if type(reaction.emoji) != str and reaction.emoji.id == payload.emoji.id:
                                emoji_count = reaction.count
                                break
                        
                        if emoji_count >= self.reaction_count_min:
                            embed_star_board = discord.Embed()
                            embed_star_board.colour = discord.Colour.from_rgb(255, 215, 0)
                            author = original_message.author
                            embed_star_board.set_author(name=author.name, icon_url=author.avatar_url)
                            
                            if original_message.content:
                                embed_star_board.description = original_message.content
                            
                            if len(original_message.attachments) > 0:
                                if 'image' in original_message.attachments[0].content_type:
                                    embed_star_board.set_image(url=original_message.attachments[0].url)
                            
                            embed_star_board.add_field(name='Fuente', value=f'[Jump!]({original_message.jump_url})')

                            self.star_board_dict[original_message.id] = {
                                'emoji_id': payload.emoji.id
                            }

                            channel_star_board = self.bot.get_channel(config.channel_star_board_id)

                            star_board_message_content = f"{payload.emoji} **{emoji_count}** {channel_message.mention}"

                            msg_channel_star_board = await channel_star_board.send(content=star_board_message_content, embed=embed_star_board)
                            await msg_channel_star_board.add_reaction(payload.emoji)
                            
                            self.star_board_dict[original_message.id]['starboard_channel_message_id'] = msg_channel_star_board.id

                            self.bot.pyMongoManager.add_star_board(original_message.id, msg_channel_star_board.id, payload.emoji.id)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        
        if payload.message_id in autoReactionMenuStackBean.getMessageIdList():
            await autoReactionMenuStackBean.updateMenuBean(payload.message_id, payload.user_id, payload.emoji)
        elif payload.message_id in autoReplyMenuStackBean.getMessageIdList():
            await autoReplyMenuStackBean.updateMenuBean(payload.message_id, payload.user_id, payload.emoji)
        else:
            channel_message = self.bot.get_channel(payload.channel_id)
            category_channel = channel_message.category

            if category_channel.id in config.star_board_category_channels_id:
                if payload.message_id in self.star_board_dict.keys():
                    star_board = self.star_board_dict[payload.message_id]

                    if payload.emoji.id and payload.emoji.id == star_board['emoji_id']:
                        channel_star_board = self.bot.get_channel(config.channel_star_board_id)
                        msg_channel_star_board = await channel_star_board.fetch_message(star_board['starboard_channel_message_id'])
                        
                        count = int(msg_channel_star_board.content.split('**')[1])

                        new_content = msg_channel_star_board.content.replace(f'**{count}**', f'**{count-1}**')
                        
                        await msg_channel_star_board.edit(content=new_content)

                    

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id not in (691310556489056398, 512830421805826048):
            return
        
        content_lower = unidecode.unidecode(message.content.lower().replace(".", ""))
        if content_lower in self.auto_reaction_dict.keys():
            emoji = self.bot.get_emoji(self.auto_reaction_dict[content_lower])
            await message.add_reaction(emoji)
        if content_lower in self.auto_reply_dict.keys():
            await message.channel.send(self.auto_reply_dict[content_lower])
        

    @commands.command()        
    async def addautoreaction(self, ctx):
        args = ctx.message.content.split()[1:]

        if len(args) < 2:
            await ctx.send("`la!addautoreaction <emoji> <frase>`")
        else:
            if ctx.author.id in self.bot.get_panchessco_staff_id_list():
                try:
                    emoji_id = int(args[0].split(':')[2][:-1])
                    frase = ' '.join(args[1:])
                    frase = frase.lower()

                    self.auto_reaction_dict[frase] = emoji_id

                    await ctx.send('Se agrego una nueva auto reacción')
                    self.bot.pyMongoManager.add_auto_reaction(frase, emoji_id)
                except:
                    await ctx.send("`la!addautoreaction <emoji> <frase>`")
            else:
                await ctx.send('Solo administradores de panchessco pueden usar el comando')
        
    @commands.command()
    async def deleteautoreaction(self, ctx):
        args = ctx.message.content.split()[1:]

        if len(args) < 1:
            await ctx.send("`la!deleteautoreaction <frase>`")
        else:
            if ctx.author.id in self.bot.get_panchessco_staff_id_list():
                frase = ' '.join(args)
                frase = frase.lower()

                auto_reaction = self.bot.pyMongoManager.get_auto_reaction(frase)

                if auto_reaction:
                    await ctx.send('Auto reacción eliminada')
                    self.bot.pyMongoManager.delete_auto_reaction(frase)

                    try:
                        del self.auto_reaction_dict[frase]
                    except:
                        pass
                else:
                    await ctx.send('No existe esa frase en la base de datos.')
            else:
                await ctx.send('Solo administradores de panchessco pueden usar el comando')

    @commands.command()
    async def autoreactionlist(self, ctx):
        args = ctx.message.content.split()[1:]

        if len(args) > 0:
            if args[0].isdigit():
                page = int(args[0])
            else:
                page = 1
        else:
            page = 1

        autoReactionList = self.bot.pyMongoManager.get_all_auto_reaction()

        autoReactionMenuBean = AutoReactionMenuBean(autoReactionList, self.bot.get_embed_color(ctx.author.id), ctx.author.id, self.bot, 10, page)
        
        await autoReactionMenuBean.send_initial_message(ctx)

        autoReactionMenuStackBean.addMenu(autoReactionMenuBean)
    

    @commands.command()        
    async def addautoreply(self, ctx):
        args = ctx.message.content.split()[1:]

        if len(args) < 2:
            await ctx.send("`la!addautoreply <tag> <reply>`")
        else:
            if ctx.author.id in self.bot.get_panchessco_staff_id_list():
                try:
                    tag = args[0].lower()
                    frase = ' '.join(args[1:])

                    self.auto_reply_dict[tag] = frase

                    await ctx.send('Se agrego una nuevo auto reply')
                    self.bot.pyMongoManager.add_auto_reply(tag, frase)
                except:
                    await ctx.send("`la!addautoreply <tag> <reply>`")
            else:
                await ctx.send('Solo administradores de panchessco pueden usar el comando')
        
    @commands.command()
    async def deleteautoreply(self, ctx):
        args = ctx.message.content.split()[1:]

        if len(args) < 1:
            await ctx.send("`la!deleteautoreply <tag>`")
        else:
            if ctx.author.id in self.bot.get_panchessco_staff_id_list():
                tag = args[0].lower()

                auto_reply = self.bot.pyMongoManager.get_auto_reply(tag)

                if auto_reply:
                    await ctx.send('Auto reply eliminado')
                    self.bot.pyMongoManager.delete_auto_reply(tag)

                    try:
                        del self.auto_reply_dict[tag]
                    except:
                        pass
                else:
                    await ctx.send('No existe ese tag en la base de datos.')
            else:
                await ctx.send('Solo administradores de panchessco pueden usar el comando')

    @commands.command()
    async def autoreplylist(self, ctx):
        args = ctx.message.content.split()[1:]

        if len(args) > 0:
            if args[0].isdigit():
                page = int(args[0])
            else:
                page = 1
        else:
            page = 1

        autoReplyList = self.bot.pyMongoManager.get_all_auto_reply()

        autoReplyMenuBean = AutoReplyMenuBean(autoReplyList, self.bot.get_embed_color(ctx.author.id), ctx.author.id, self.bot, 8, page)
        
        await autoReplyMenuBean.send_initial_message(ctx)

        autoReplyMenuStackBean.addMenu(autoReplyMenuBean)
    


        

def setup(bot):
    bot.add_cog(EmojiCog(bot))
    print("Emoji Cog CARGADO")

