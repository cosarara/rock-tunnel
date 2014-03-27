
import random
import r
import dungeon

class Golbat(r.Monster):
    def __init__(self, game, map, x=None, y=None, level=5):
        self.game = game
        if x is None or y is None:
            x, y = dungeon.get_floor_tile(map)
        self.map = map
        self.x = x
        self.y = y
        self.ch = 'g'
        self.name = 'Golbat'
        self.hp = 0

        self.max_hp = 0
        self.attack = 0
        self.defense = 0
        self.spattack = 0
        self.spdefense = 0
        self.vel = 0

        self.base_max_hp = 75
        self.base_attack = 80
        self.base_defense = 70
        self.base_spattack = 65
        self.base_spdefense = 75
        self.base_vel = 90

        self.base_exp = 171
        self.level = level

        self.calc_stats()

        self.aggressive = random.random() < 0.2
        self.new_dest()

        self.setup_moves()



