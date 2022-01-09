from random import randint

# Roulette Game complet by Unbelievable
class RouletteBean:
    def __init__(self, bet, space):
        self.bet = bet
        self.space = space
        self.space_list = ['red', 'black', 'even', 'odd', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '1-18', '19-36', '1st12', '2nd12', '3rd12', '1-12', '13-24', '25-36']

        self.red = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        self.black = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        self.even = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
        self.odd = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]
        self.first12 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.second12 = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        self.third12 = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        self.first_space = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        self.second_space = [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36]

        self.spaces = {
            'red': self.red,
            'black': self.black,
            'even': self.even,
            'odd': self.odd,
            '1-18': self.first_space,
            '19-36': self.second_space,
            '1st12': self.first12,
            '2nd12': self.second12,
            '3rd12': self.third12,
            '1-12': self.first12,
            '13-24': self.second12,
            '25-36': self.third12
        }

    def play(self):
        roulette_number = randint(0, 36)
        
        if self.space == 'red':
            if roulette_number in self.red:
                return True
            else:
                return False
        elif self.space == 'black':
            if roulette_number in self.black:
                return True
            else:
                return False
        elif self.space == 'even':
            if roulette_number in self.even:
                return True
            else:
                return False
        elif self.space == 'odd':
            if roulette_number in self.odd:
                return True
            else:
                return False
        elif self.space == '1-18':
            if roulette_number in self.first_space:
                return True
            else:
                return False
        elif self.space == '19-36':
            if roulette_number in self.second_space:
                return True
            else:
                return False
        elif self.space == '1st12':
            if roulette_number in self.first12:
                return True
            else:
                return False
        elif self.space == '2nd12':
            if roulette_number in self.second12:
                return True
            else:
                return False
        elif self.space == '3rd12':
            if roulette_number in self.third12:
                return True
            else:
                return False
        elif self.space == '1-12':
            if roulette_number in self.first12:
                return True
            else:
                return False
        elif self.space == '13-24':
            if roulette_number in self.second12:
                return True
            else:
                return False
        elif self.space == '25-36':
            if roulette_number in self.third12:
                return True
            else:
                return False
        else:
            if roulette_number == self.space:
                return True
            else:
                return False
    
    def calculate_win(self):
        if self.space in ['red', 'black', 'even', 'odd', '1-18', '19-36']:
            return self.bet * 2
        elif self.space in ['1st12', '2nd12', '3rd12', '1-12', '13-24', '25-36']:
            return self.bet * 3
        else:
            return self.bet * 36
