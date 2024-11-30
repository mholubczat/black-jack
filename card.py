import random


class Card:
    def __init__(self, suit, rank, points):
        self.suit = suit
        self.rank = rank
        self.points = points

    def __eq__(self, other):
        return self.rank == other.rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"


suits = ['diamonds', 'clubs', 'hearts', 'spades']
ranks = {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 'jack': 10, 'queen': 10, 'king': 10,
         'ace': 11}


class Deck:
    def __init__(self, count):
        self.count = count
        self.cards = []
        self.add_new_cards()

    def __str__(self):
        return f'{len(self.cards)} cards left'

    def dealCard(self):
        if len(self.cards) == 0:
            print("The deck is empty! Creating a new deck")
            self.add_new_cards()

        return self.cards.pop()

    def add_new_cards(self):
        for i in range(self.count):
            for suit in suits:
                for rank in ranks:
                    self.cards.append(Card(suit, rank, ranks[rank]))
        random.shuffle(self.cards)
