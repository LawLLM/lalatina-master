
from src.controller.StringController import StringController

class StringService:
    def findNumbers(self, string):
        stringController = StringController()
        return stringController.findNumbers(string)
