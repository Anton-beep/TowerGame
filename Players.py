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


class Bot(Player):
    """Must be clever"""
    def spawn_entity(self, group, ent, money) -> bool:
        """if returns True -> need to spawn ent else False"""
        bot_count = 0
        player_count = 0
        for el in group:
            if type(el.player) == type(self):
                bot_count += 1
            else:
                player_count += 1

        if player_count > bot_count and money >= ent((0, 0), None, None, False).cost:
            pass
            # return ent
        return False
