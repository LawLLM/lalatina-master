import discord
from discord.ext import commands
import logging
import traceback
import sys

import config

import src.controller.utils as utils

from src.lib.mongodb import PyMongoManager

pyMongoManager = PyMongoManager()

log = logging.getLogger(__name__)

intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.emojis = True
intents.guild_messages = True
intents.guild_reactions = True

initial_extensions = (
    'src.cogs.base_cog',
    'src.cogs.fun_cog',
    'src.cogs.owner_cog',
    'src.cogs.staff_cog',
    'src.cogs.calendar_cog',
    'src.cogs.tournament_cog',
    'src.cogs.economy_cog',
    'src.cogs.role_cog',
    'src.cogs.useful_cog',
    'src.cogs.help_cog',
    'src.cogs.adv_economy_cog',
    'src.cogs.games_cog',
)


class PanchesscoBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=config.prefix , help_command=None, max_messages=None, intents=intents)

        self.client_id = config.client_id

        self.prefixes = {}
        self.autogifs = {}
        self.embed_colors = {} # User Id -> hex_color

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
        profiles_list = pyMongoManager.get_all_profiles()

        for profile in profiles_list:
            if profile['embed_color']:
                self.embed_colors[profile['user_id']] = profile['embed_color']

    
    def set_embed_color(self, user_id, hex_color):
        self.embed_colors[user_id] = hex_color
    
    def get_embed_color(self, user_id):
        try:
            hex_color = self.embed_colors[user_id]
        except:
            hex_color = '#E3D9A4'       # Color del cabello de Darkness
        
        if hex_color == "#FFFFFF":
            hex_color = "#FFFFFE"
        r, g, b = utils.HEX_to_RGB(hex_color)
        return discord.Colour.from_rgb(r, g, b)
        
    def get_panchessco_staff_id_list(self):
        panchessco_guild = self.get_guild(config.panchessco_id)
        panchessco_role_admin = panchessco_guild.get_role(config.panchessco_role_staff_id)

        admins_id_list = [admin.id for admin in panchessco_role_admin.members]

        return admins_id_list

if __name__ == "__main__":
    bot = PanchesscoBot()
    bot.run(config.token, bot=True)


