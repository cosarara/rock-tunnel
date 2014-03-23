import sys
import curses
import random
import math
from random import randint, sample
import dungeon

walkable_tiles = '<>.#'

class Monster():
    def __init__(self, game, map, ch, name, x=None, y=None):
        self.game = game
        if x is None or y is None:
            x, y = dungeon.get_floor_tile(map)
        self.map = map
        self.x = x
        self.y = y
        self.ch = ch
        self.name = name
        self.hp = 0

        self.max_hp = 0
        self.attack = 0
        self.defense = 0
        self.spattack = 0
        self.spdefense = 0
        self.vel = 0

        self.base_max_hp = 40
        self.base_attack = 45
        self.base_defense = 35
        self.base_spattack = 30
        self.base_spdefense = 40
        self.base_vel = 55

        self.level = 5

        self.calc_stats()

        self.aggressive = False
        self.new_dest()

        self.hit_handicap = 0.2
        phy = lambda p : (lambda m : m.be_hit(p * self.hit_handicap))
        def leech(p):
            def f(m):
                m.be_hit(p * self.hit_handicap)
                self.get_hp(p * self.hit_handicap * 0.5)
            return f
        self.battle_moves = {
                'Leech Life': leech(40),
                #'Supersonic': ui(0),
                'Bite': phy(60),
                }

    def draw(self):
        self.game.stdscr.addch(self.y, self.x, self.ch)

    def calc_stat(self, base):
        floor = math.floor
        # Actual function is:
        # S = floor(floor((2 * B + I + E) * L / 100 + 5) * N)
        return floor((2 * base + 15 + self.level*2) * self.level / 100 + 5)

    def calc_stat_hp(self, base):
        floor = math.floor
        # Actual function is:
        # S = floor((2 * B + I + E) * L / 100 + L + 10)
        return floor((2 * base + 15 + self.level*2) * self.level / 100
                     + self.level + 10)

    def calc_stats(self):
        self.attack = self.calc_stat(self.base_attack)   
        self.defense = self.calc_stat(self.base_defense)   
        self.spattack = self.calc_stat(self.base_spattack)   
        self.spdefense = self.calc_stat(self.base_spdefense)   
        self.vel = self.calc_stat(self.base_vel)   
        self.max_hp = self.calc_stat_hp(self.base_max_hp)   
        self.hp = self.max_hp
    
    def move(self):
        if self.aggressive:
            return self.aggressive_move()
        return self.random_move()

    def new_dest(self):
        self.dx, self.dy = dungeon.get_floor_tile(self.map)

    def is_walkable(self, x, y):
        return self.map[y][x] in walkable_tiles and not game.entity_in_pos(x, y)

    def random_move(self, n=0):
        sx = self.x
        sy = self.y
        if randint(0, 100) < 4 or sx == self.dx and sy == self.dy:
            self.new_dest()
        distx = self.dx - sx
        disty = self.dy - sy
        dirx = distx // abs(distx) if distx != 0 else 0
        diry = disty // abs(disty) if disty != 0 else 0
        r = randint(0, 2)
        if abs(distx) > abs(disty) and self.is_walkable(sx+dirx, sy):
            sx += dirx
        elif self.is_walkable(sx, sy+diry):
            sy += diry
        else:
            self.new_dest()
            if n < 30:
                self.random_move(n+1)
            return
        self.x = sx
        self.y = sy

    def aggressive_move(self):
        pass

    def clear_stats(self):
        h, w = self.game.stdscr.getmaxyx()
        c = self.game.COLS
        self.game.stdscr.addstr(10, c, " "*(w-c-1))

    def draw_stats(self):
        self.clear_stats()
        c = self.game.COLS
        self.game.stdscr.addstr(10, c, "M HP: {}".format(self.hp))

    def battle(self):
        self.game.msgwait("OMG! {} wants to battle!".format(self.name))
        self.draw_stats()
        while self.hp > 0:
            self.game.msg("What will you do? (a)ttack, (p)okemon, (i)tem or (r)un?")
            k = self.game.stdscr.getkey()
            if k == 'r':
                self.game.msg("You ran like a coward...")
                break
            a = {
                    'a': lambda : self.game.p.do_attack(self),
                    'p': lambda : True,
                    'i': self.game.open_inventory,
            }
            if k in a:
                a[k]()
                self.draw_stats()
            else:
                continue
            if self.hp <= 0:
                break
            self.hit(self.game.p)
            if self.game.p.hp == 0:
                self.game.die("You've been killed by a {}".format(self.name))
                break
            self.game.p.draw_stats()
            self.draw_stats()

        if self.hp == 0:
            self.game.msgwait("{} dies...".format(self.name))
            self.clear_stats()
            del self.game.monsters[self.game.monsters.index(self)]

    def be_hit(self, v):
        ''' be hit '''
        self.hp -= v
        self.fix_hp()

    def get_hp(self, v):
        self.hp += v
        self.fix_hp()

    def fix_hp(self):
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        if self.hp < 0:
            self.hp = 0
        self.hp = math.floor(self.hp)

    def hit(self, m):
        a = random.choice(list(self.battle_moves.keys()))
        self.game.msgwait("Wild {} uses {}!".format(self.name, a))
        self.battle_moves[a](m)
        m.fix_hp()

class Player(Monster):
    def __init__(self, game, map, ch, name, x, y):
        self.game = game
        self.map = map
        self.x = x
        self.y = y
        self.ch = ch
        self.name = name
        self.hp = 0

        self.max_hp = 0
        self.attack = 0
        self.defense = 0
        self.spattack = 0
        self.spdefense = 0
        self.vel = 0

        self.base_max_hp = 35
        self.base_attack = 55
        self.base_defense = 30
        self.base_spattack = 50
        self.base_spdefense = 40
        self.base_vel = 90

        self.level = 5

        self.calc_stats()

        self.hit_handicap = 0.25
        phy = lambda p : (lambda m : m.be_hit(p * self.hit_handicap))
        self.battle_moves = {
                'Quick attack': phy(40),
                'Shock Wave': phy(40),
                'Iron tail': phy(100),
                'Thunder': phy(120),
                }

    def do_attack(self, m):
        while True:
            moves = sorted(self.battle_moves)
            self.game.msg("Attack:\t(1) {} (2) {}\n\t(3) {} (4) {}"\
                        .format(*(a for a in moves)))
            k = self.game.stdscr.getkey()
            try:
                move = moves[int(k)-1]
                self.game.msgwait("You use {}!".format(move))
                self.battle_moves[move](m)
            except ValueError:
                continue
            break

    def be_hit(self, v):
        self.hp -= v

    def clear_stats(self):
        h, w = self.game.stdscr.getmaxyx()
        c = self.game.COLS
        self.game.stdscr.addstr(0, c, " "*(w-c-1))

    def draw_stats(self):
        self.clear_stats()
        self.game.stdscr.addstr(0, self.game.COLS, "HP: {}".format(self.hp))

class Game():
    COLS = 80
    ROWS = 30

    def __init__(self):
        self.move_up = lambda : self.move(0, -1)
        self.move_down = lambda : self.move(0, 1)
        self.move_left = lambda : self.move(-1, 0)
        self.move_right = lambda : self.move(1, 0)
        self.move_ul = lambda : self.move(-1, -1)
        self.move_dl = lambda : self.move(-1, 1)
        self.move_ur = lambda : self.move(1, -1)
        self.move_dr = lambda : self.move(1, 1)

        self.monsters = []

        #self.hp = 20
        #self.hit_handicap = 0.2
        #phy = lambda p : (lambda m : m.be_hit(p * self.hit_handicap))
        #self.battle_moves = {
        #        'Quick attack': phy(40),
        #        'Shock Wave': phy(40),
        #        'Iron tail': phy(100),
        #        'Thunder': phy(120),
        #        }

    def spawn_monsters(self):
        for i in range(randint(0, 5)):
            self.monsters.append(Monster(self, self.map, 'd', 'Wild Zubat'))

    def act_monsters(self):
        for m in self.monsters:
            m.move()

    def entity_in_pos(self, x, y):
        for m in self.monsters + [self.p]:
            if m.x == x and m.y == y:
                return m
        return False

    def draw(self):
        map, stdscr = self.map, self.stdscr
        for y, row in enumerate(map):
            for x, ch in enumerate(row):
                stdscr.addch(y, x, ch)
        self.draw_entities()
        self.p.draw_stats()

    def draw_entities(self):
        self.p.draw()
        for m in self.monsters:
            m.draw()

    def move(self, x, y):
        x += self.p.x
        y += self.p.y
        if not (0 <= x <= self.COLS-1 and 0 <= y <= self.ROWS-1):
            return False
        e = self.entity_in_pos(x, y)
        if self.map[y][x] in walkable_tiles and not e:
            self.p.x = x
            self.p.y = y
            return True
        if isinstance(e, Monster):
            e.battle()
            return True
        return False

    def clr_msg(self):
        h, w = self.stdscr.getmaxyx()
        for i in range(h-self.ROWS-1):
            self.stdscr.addstr(self.ROWS+i, 0, ' '*w)

    def msg(self, msg):
        self.clr_msg()
        self.stdscr.addstr(self.ROWS, 0, msg)

    def msgwait(self, msg):
        self.clr_msg()
        self.stdscr.addstr(self.ROWS, 0, msg)
        self.stdscr.addstr(self.ROWS+1, 0, "--- Press any key to continue ---")
        self.stdscr.getkey()
        self.clr_msg()

    def open_inventory(self):
        pass

    def die(self, msg):
        self.msgwait(msg)
        self.alive = False

    def main(self, stdscr):
        self.stdscr = stdscr
        stdscr.clear()
        map = [[" " for x in range(self.COLS)] for y in range(self.ROWS)]
        self.map = map
        x, y = dungeon.dig(map)
        self.p = Player(self, map, "@", "Pikachu", x, y)
        self.alive = True
        self.spawn_monsters()
        curses.curs_set(False)
        while self.alive:
            self.draw()
            stdscr.refresh()
            k = stdscr.getkey()
            if k == 'q':
                #stdscr.addstr(0, 0, "Do you want to quit? [y/n]")
                #if stdscr.getkey() in 'yY':
                break
            a = {'KEY_UP': self.move_up,
                 'k': self.move_up,
                 'KEY_DOWN': self.move_down,
                 'j': self.move_down,
                 'KEY_LEFT': self.move_left,
                 'h': self.move_left,
                 'KEY_RIGHT': self.move_right,
                 'l': self.move_right,
                 'y': self.move_ul,
                 'u': self.move_ur,
                 'b': self.move_dl,
                 'n': self.move_dr,
                 's': lambda : True,
                 }
            if not (k in a and a[k]()):
                continue
            if not self.alive:
                break
            self.act_monsters()

if __name__ == "__main__":
    game = Game()
    curses.wrapper(game.main)


