import discord
from discord.ext import commands
import copy

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
            'sexo': 752658698723262517
        }
        self.message_auto_reply = {
            #'lalatina': 'https://media.tenor.com/images/37465eb4d7edea808a511abc18be5484/tenor.gif',
        }
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id not in (691310556489056398, 512830421805826048):
            return
        
        content_lower = message.content.lower()
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

