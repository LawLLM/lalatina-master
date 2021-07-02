import discord
from discord.ext import commands
import copy

import unidecode

import aiohttp
import config

#from modules.mongodb import PyMongoManager

#pyMongoManager = PyMongoManager()
#session_emoji = aiohttp.ClientSession()

PREFIX = config.prefix

class EmojiCog(commands.Cog, name="Emoji"):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_auto_reaction_id = {
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
        }
        self.message_auto_reply = {
            'lalatina': 'https://media.tenor.com/images/37465eb4d7edea808a511abc18be5484/tenor.gif',
            'lala': 'Es lalatina :c'
        }
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id not in (691310556489056398, 512830421805826048):
            return
        
        content_lower = unidecode.unidecode(message.content.lower().replace(".", ""))
        if content_lower in self.emoji_auto_reaction_id.keys():
            emoji = self.bot.get_emoji(self.emoji_auto_reaction_id[content_lower])
            await message.add_reaction(emoji)
        elif content_lower in self.message_auto_reply.keys():
            text = self.message_auto_reply[content_lower]
            await message.channel.send(text)
        

    @commands.command()
    async def asdf(self, ctx):
        args = ctx.message.content.split()[1:]

        # DIA - MES

        if len(args) == 0:
            await ctx.send(f'Uso correcto: ``')
        

def setup(bot):
    bot.add_cog(EmojiCog(bot))
    print("Emoji Cog CARGADO")

