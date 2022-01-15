import configparser
from start import CONFIG

class Player:
    def __init__(self, team):
        """team can be 'red' or 'blue'"""
        self.team = team

    def __hash__(self):
        return hash(self.team)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def getRussianName(self):
        return 'Игрок'


class Bot(Player):
    """Must be clever"""
    def __init__(self, *args):
        super().__init__(*args)
        self.extraEnitities = 0
        self.target = None

    def spawn_entity(self, group, ent, tower):
        """if returns True -> need to spawn ent else False"""
        print(str(type(tower.lastAttacker))[:17])
        if tower.lastAttacker != self.target and\
                str(type(tower.lastAttacker))[:17] == "<class 'Entities.":
            self.extraEnitities = 1
            self.target = tower.lastAttacker

        bot_count = 0
        player_count = 0
        for el in group:
            if type(el.player) == type(self):
                bot_count += 1
            else:
                player_count += 1

        if tower.money >= ent((0, 0), None, None, False).cost:
            if self.extraEnitities > 0:
                self.extraEnitities -= 1
                return ent, (self.target, 'playerTower')
            elif player_count > bot_count:
                return ent, ('playerTower',)
        return False

    def getRussian(self):
        return 'Бот'
