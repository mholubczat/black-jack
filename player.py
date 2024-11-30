class Player:
    def __init__(self, name):
        self.name = name
        self.hands = [{"cards": [], "bid": 0, "lastAction": ""}]
        self.credits = 100

    def __str__(self):
        return f'Player {self.name}'

    def print_value(self):
        return f'Player {self.name} has {self.value} credits'
