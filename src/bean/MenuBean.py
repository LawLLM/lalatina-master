
import discord


class MenuBean:
    def __init__(self, items_list, color, user_id, bot=None, items_per_page=10, current_page=1) -> None:
        self.bot = bot

        self.items_list = items_list
        self.ITEMS_PER_PAGE = items_per_page
        self.num_pages = int((len(items_list)+self.ITEMS_PER_PAGE-1) / self.ITEMS_PER_PAGE)
        self.num_items = len(items_list)

        self.user_id = user_id

        if current_page < 1:
            self.current_page = 1
        elif current_page > self.num_pages:
            self.current_page = self.num_pages
        else:
            self.current_page = current_page

        self.color = color
        self.embed_title = None
        self.embed_text = None
        self.embed_void = "Nothing"


    async def next_page(self):
        if self.current_page == self.num_pages:
            pass
        else:
            self.current_page += 1
            await self.update_message()

    async def previus_page(self):
        if self.current_page == 1:
            pass
        else:
            self.current_page -= 1
            await self.update_message()
    
    def is_valid_num(self, num):
        return num <= self.num_items

    async def delete_menu_message(self):
        await self.message.delete()

    async def send_initial_message(self, ctx):
        self.message = await ctx.send(embed=self.create_embed_page())
        self.message_id = self.message.id
        self.channel_id = self.message.channel.id
        #self.user_id = self.message.author.id

        if self.num_pages > 1:
            await self.message.add_reaction('\N{BLACK LEFT-POINTING TRIANGLE}')
            await self.message.add_reaction('\N{BLACK RIGHT-POINTING TRIANGLE}')

    async def update_message(self):
        await self.message.edit(embed=self.create_embed_page())


    def create_embed_page(self):
        embed = discord.Embed()

        if self.embed_title:
            embed.title = self.embed_title
        
        embed.colour = self.color

        relative_page = self.current_page - 1
        index_0 = relative_page * self.ITEMS_PER_PAGE
        index_f = index_0 + self.ITEMS_PER_PAGE

        relative_item_list = self.items_list[index_0: index_f]

        if self.embed_text:
            text = self.embed_text + '\n\n'
        else:
            text = ""
        
        index_numeration = relative_page * self.ITEMS_PER_PAGE + 1

        
        if len(relative_item_list) > 0:
            for item in relative_item_list:                
                text += self.get_text_line(item, index_numeration=index_numeration) + '\n\n'
                index_numeration += 1
        else:
            text += self.embed_void

        embed.description = text

        if self.num_pages > 1:
            embed.set_footer(text=self.get_text_footer())

        return embed


    def get_text_line(self, item, index_numeration=None):
        pass

    def get_text_footer(self):
        return f'Page {self.current_page} of {self.num_pages}.'




