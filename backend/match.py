from .errors import *
from .entities import BaseEntity

class Match:
    def __init__(self, player1: BaseEntity, player2: BaseEntity):
        player1.init_encounter(player2)
        player2.init_encounter(player1)
        self.player1 = player1
        self.player2 = player2
        self._whos_turn = 0

    @property
    def players(self):
        return [self.player1, self.player2]

    def next_turn(self):
        out = self.players[self._whos_turn]
        self._whos_turn = (self._whos_turn + 1) % 2
        return out

    def alive_count(self):
        return sum([i.alive for i in self.players])

    def finished(self):
        return self.alive_count() < 2

    def winner(self):
        count = self.alive_count()
        if not count % 2:
            return None
        return [i for i in self.players if i.alive][0]
