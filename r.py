import sys
import curses
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
        self.hp = 20
        self.aggressive = False
        self.new_dest()
    
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

    def attack(self):
        while self.hp > 0:
            self.game.msgwait("OMG! {} wants to battle!".format(self.name))
            self.game.msg("What will you do? (a)ttack, (p)okemon, (i)tem or (r)un?")
            k = self.game.stdscr.getkey()
            if k == 'r':
                self.game.msg("You ran like a coward...")
                break
            a = {
                    'a': lambda : self.game.attack(self),
                    'p': lambda : True,
                    'i': self.game.open_inventory,
            }
            if k in a:
                a[k]()

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

    def spawn_monsters(self):
        for i in range(randint(0, 5)):
            self.monsters.append(Monster(self, self.map, 'd', 'Wild Zubat'))

    def act_monsters(self):
        for m in self.monsters:
            m.move()

    def entity_in_pos(self, x, y):
        for m in self.monsters:
            if m.x == x and m.y == y:
                return m
        if self.x == x and self.y == y:
            return True
        return False

    def draw(self):
        map, stdscr = self.map, self.stdscr
        for y, row in enumerate(map):
            for x, ch in enumerate(row):
                stdscr.addch(y, x, ch)
        self.draw_entities()

    def draw_entities(self):
        self.stdscr.addch(self.y, self.x, '@')
        for m in self.monsters:
            self.stdscr.addch(m.y, m.x, m.ch)

    def move(self, x, y):
        x += self.x
        y += self.y
        if not (0 <= x <= self.COLS-1 and 0 <= y <= self.ROWS-1):
            return False
        e = self.entity_in_pos(x, y)
        if self.map[y][x] in walkable_tiles and not e:
            self.x = x
            self.y = y
            return True
        if isinstance(e, Monster):
            e.attack()
            return True
        return False

    def clr_msg(self):
        h, w = self.stdscr.getmaxyx()
        self.stdscr.addstr(self.ROWS, 0, ' '*w)

    def msg(self, msg):
        self.clr_msg()
        self.stdscr.addstr(self.ROWS+1, 0, ' '*w)
        self.stdscr.addstr(self.ROWS, 0, msg)

    def msgwait(self, msg):
        self.stdscr.addstr(self.ROWS, 0, msg)
        self.stdscr.addstr(self.ROWS+1, 0, "--- Press any key to continue ---")
        self.stdscr.getkey()
        self.clr_msg()

    def open_inventory(self):
        pass

    def attack(self, m):
        self.msg("Attack: (1) Quick attack (2) Thunder\n(3) Iron tail (4) Shock Wave")
        k = self.stdscr.getkey()

    def main(self, stdscr):
        self.stdscr = stdscr
        stdscr.clear()
        map = [[" " for x in range(self.COLS)] for y in range(self.ROWS)]
        self.map = map
        self.x, self.y = dungeon.dig(map)
        self.spawn_monsters()
        curses.curs_set(False)
        while True:
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
            self.act_monsters()

if __name__ == "__main__":
    game = Game()
    curses.wrapper(game.main)


