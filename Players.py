import configparser

from start import CONFIG


class Player:
    def __init__(self, team):
        """team can be 'red' or 'blue'"""
        self.team = team
        self.money = CONFIG.getint('player', 'MoneyStart')
        self.money_max = CONFIG.getint('player', 'MoneyMax')

    def __hash__(self):
        return hash(self.team)

    def __eq__(self, other):
        return hash(self) == hash(other)


class Bot(Player):
    """Must be clever"""
    pass
