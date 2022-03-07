from src.bean.MenuBean import MenuBean


class AutoReactionMenuBean(MenuBean):
    def __init__(
        self, items_list, color, user_id, bot=None, items_per_page=10, current_page=1
    ) -> None:
        super().__init__(
            items_list,
            color,
            user_id,
            bot=bot,
            items_per_page=items_per_page,
            current_page=current_page,
        )

    def get_text_line(self, item, index_numeration=None):
        emoji = self.bot.get_emoji(item["emoji_id"])

        linea1 = f"**Mensaje:** {item['message_base']}"
        linea2 = f"**Reaccion:** {emoji}"

        linea3 = f"{emoji} {item['message_base']}"

        # return f"{linea1}\n{linea2}"
        return linea3
