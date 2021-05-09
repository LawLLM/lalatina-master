import discord
from discord.ext import commands
import logging
import traceback
import sys

import config

#from modules import mongodb

#pyMongoManager = mongodb.PyMongoManager()

log = logging.getLogger(__name__)

intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.emojis = True
intents.guild_messages = True
intents.guild_reactions = True

initial_extensions = (
    'src.cogs.base_cog',
    'src.cogs.emoji_cog',
    'src.cogs.owner_cog',
    'src.cogs.staff_cog',
    'src.cogs.birthday_cog',
    'src.cogs.tournament_cog',
)


class PanchesscoBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=config.prefix , help_command=None, max_messages=None, intents=intents)

        self.client_id = config.client_id

        self.prefixes = {}
        self.autogifs = {}
        self.welcome_channels_id = {
            691310556489056398: 691310556489056402,
            512830421805826048: 512830421805826050
        }

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

        #guilds_list = pyMongoManager.get_discord_guilds()

        """ for guild_dict in guilds_list:
            if 'prefix' in guild_dict.keys():
                self.prefixes[guild_dict['guild_id']] = guild_dict['prefix']
            if 'autogif' in guild_dict.keys():
                self.autogifs[guild_dict['guild_id']] = guild_dict['autogif'] """

    def set_autogif(self, guild_id, value):
        self.autogifs[guild_id] = value
        
    def get_autogif(self, guild_id):
        try:
            return self.autogifs[guild_id]
        except:
            return False

if __name__ == "__main__":
    bot = PanchesscoBot()
    bot.run(config.token, bot=True)


