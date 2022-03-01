class StringController:
    def findNumbers(self, string):
        numbers_list = []

        pos = 0

        while pos < len(string):
            number = ""
            while pos < len(string) and string[pos].isdigit():
                number += string[pos]
                pos += 1

            if number:
                numbers_list.append(int(number))

            while pos < len(string) and not string[pos].isdigit():
                pos += 1

        return numbers_list
