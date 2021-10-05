


class MenuStackBean:
    def __init__(self) -> None:
        self.menuDict = {}      # MessageID - Menu


    def addMenu(self, menu):
        self.menuDict[menu.message_id] = menu

    def removeMenuListener(self, message_id):
        try:
            del self.menuDict[message_id]
        except:
            pass

    async def removeMenuView(self, channel_id, user_id):
        currentMenu = None
        currentKey = None

        for key in self.menuDict.keys():
            if self.menuDict[key].channel_id == channel_id and self.menuDict[key].user_id == user_id:
                currentMenu = self.menuDict[key]
                currentKey = key
        
        if currentMenu:
            try:
                await currentMenu.delete_menu_message()
                del self.menuDict[currentKey]
            except:
                pass

    def getMessageIdList(self):
        return list(self.menuDict.keys())

    def getChannelIdList(self):
        channelIdList = []

        for key in self.menuDict.keys():
            channelIdList.append(self.menuDict[key].channel_id)
        
        return channelIdList
    
    def getUserIdList(self):
        userIdList = []

        for key in self.menuDict.keys():
            userIdList.append(self.menuDict[key].user_id)
        
        return userIdList

    async def updateMenuBean(self, message_id, user_id, emoji):
        if message_id in self.menuDict.keys():
            if self.menuDict[message_id].user_id == user_id:
                if emoji.name == "◀":
                    await self.menuDict[message_id].previus_page()
                elif emoji.name == "▶":
                    await self.menuDict[message_id].next_page()

    def isValidNum(self, channel_id, user_id, num):
        currentMenu = None

        for key in self.menuDict.keys():
            if self.menuDict[key].channel_id == channel_id and self.menuDict[key].user_id == user_id:
                currentMenu = self.menuDict[key]
        
        if currentMenu:
            if currentMenu.is_valid_num(num):
                return currentMenu
            else:
                return False
        else:
            return False


