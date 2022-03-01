import discord
import discord.utils as dutils

import config
import src.controller.utils as utils


class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Green",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:green",
    )
    async def green(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("This is green.", ephemeral=True)

    @discord.ui.button(
        label="Red", style=discord.ButtonStyle.red, custom_id="persistent_view:red"
    )
    async def red(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("This is red.", ephemeral=True)

    @discord.ui.button(
        label="Grey", style=discord.ButtonStyle.grey, custom_id="persistent_view:grey"
    )
    async def grey(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("This is grey.", ephemeral=True)


class RoleSelect(discord.ui.Select):
    def __init__(self, viewParent):
        self.viewParent = viewParent
        rango = self.viewParent.rango

        guild = self.viewParent.bot.get_guild(config.panchessco_id)
        guild_doc = self.viewParent.bot.pyMongoManager.get_guild(config.panchessco_id)
        role_id_list = guild_doc["self_assignable_roles"][rango[0] : rango[1]]

        role_name_id_dict = {}

        for role_id in role_id_list:
            try:
                role_aux = guild.get_role(role_id)
                role_name_id_dict[role_aux.name] = role_aux.id
            except:
                pass

        options = []
        for role_name in role_name_id_dict.keys():
            options.append(discord.SelectOption(label=role_name))

        super().__init__(
            placeholder="Select Role",
            options=options,
            min_values=1,
            max_values=1,
            custom_id=f"LALATINAGOD{rango[0]}-{rango[1]}",
        )

    async def callback(self, interaction):
        guild: discord.Guild = self.viewParent.bot.get_guild(config.panchessco_id)
        member: discord.Member = guild.get_member(interaction.user.id)

        role_query = self.values[0]

        role: discord.Role = dutils.get(guild.roles, name=role_query)

        guild_doc = self.viewParent.bot.pyMongoManager.get_guild(config.panchessco_id)

        roles_self_assignable = guild_doc["self_assignable_roles"]

        for role_aux in member.roles:
            if role_aux.id in roles_self_assignable and role_aux.name != role.name:
                await member.remove_roles(role_aux)

        if role in member.roles:
            await interaction.response.send_message(
                content=f"**{member.name}** you already have **{role_query}** role",
                ephemeral=True,
            )
        else:
            await member.add_roles(role)

            await interaction.response.send_message(
                f"**{member.name}** you now have **{role_query}** role", ephemeral=True
            )

            role_colour = role.colour
            HEX_color = utils.RGB_to_HEX(role_colour.r, role_colour.g, role_colour.b)

            self.viewParent.bot.set_embed_color(member.id, HEX_color)
            self.viewParent.bot.pyMongoManager.set_embed_color(member.id, HEX_color)


class AutoAsignableRoleView(discord.ui.View):
    def __init__(self, bot, rango):
        super().__init__(timeout=None)
        self.bot = bot
        self.rango = rango

        self.role_select = RoleSelect(self)

        self.add_item(self.role_select)
