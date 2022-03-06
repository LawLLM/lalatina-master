
from src.bean.MenuBean import MenuBean


class AutoReplyMenuBean(MenuBean):
    def __init__(self, items_list, color, user_id, bot=None, items_per_page=10, current_page=1) -> None:
        super().__init__(items_list, color, user_id, bot=bot, items_per_page=items_per_page, current_page=current_page)

    def get_text_line(self, item, index_numeration=None):
        linea1 = f"**Tag**: {item['tag']}"
        linea2 = f"**Reply**: {item['message_reply']}"

        return f"{linea1}\n{linea2}"
