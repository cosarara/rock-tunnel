import sys
import curses
import math
import pickle
import random
from random import randint, sample
import sys
import os
import dungeon
import dirs
import menu
import visibility
import mons

walkable_tiles = '<>.#'

class Monster():
    def __init__(self, game, map, x=None, y=None, level=5):
        self.game = game
        if x is None or y is None:
            x, y = dungeon.get_floor_tile(map)
        self.map = map
        self.x = x
        self.y = y
        self.ch = 'z'
        self.name = 'Zubat'
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

        self.base_exp = 49
        self.level = level

        self.calc_stats()

        self.aggressive = random.random() < 0.3
        self.new_dest()

        self.setup_moves()

    def setup_moves(self):
        # Separated coz lambdas involved and pickle
        dmg = lambda p, at, de : ( ((((2 * self.level / 5 + 2) * at * p / de) /
                                     50) + 2) * randint(85, 100) / 100 )
        phy = lambda p : (lambda m : m.be_hit(dmg(p, self.attack, m.defense)))
        spe = lambda p : (lambda m : m.be_hit(dmg(p, self.spattack, m.spdefense)))
        def leech(p):
            def f(m):
                d = dmg(p, self.attack, m.defense)
                m.be_hit(d)
                self.get_hp(round(d * 0.5))
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
        sqrt = math.sqrt
        ev = 0xFF*(self.level-5)/95
        if ev < 0:
            ev = 0
        iv = 10
        return floor((iv + base + sqrt(ev)/8 + 50) * self.level / 50 + 10)

    def calc_stats(self):
        self.attack = self.calc_stat(self.base_attack)   
        self.defense = self.calc_stat(self.base_defense)   
        self.spattack = self.calc_stat(self.base_spattack)   
        self.spdefense = self.calc_stat(self.base_spdefense)   
        self.vel = self.calc_stat(self.base_vel)   
        old_max_hp = self.max_hp
        self.max_hp = self.calc_stat_hp(self.base_max_hp)   
        self.hp += self.max_hp - old_max_hp
    
    def new_dest(self):
        self.dx, self.dy = dungeon.get_floor_tile(self.map)

    def is_walkable(self, x, y):
        return self.map[y][x] in walkable_tiles and not self.game.entity_in_pos(x, y)

    def move(self, n=0):
        if self.aggressive:
            self.aggressive_dest()
        sx = self.x
        sy = self.y
        if ((randint(0, 100) < 4 and not self.aggressive) or 
          (sx == self.dx and sy == self.dy)):
            self.new_dest()
        distx = self.dx - sx
        disty = self.dy - sy
        dirx = distx // abs(distx) if distx != 0 else 0
        diry = disty // abs(disty) if disty != 0 else 0
        r = randint(0, 2)
        if self.try_attacking():
            pass
        elif abs(distx) > abs(disty) and self.is_walkable(sx+dirx, sy):
            sx += dirx
        elif self.is_walkable(sx, sy+diry):
            sy += diry
        else: 
            self.new_dest()
            if n < 30:
                self.move(n+1)
            return
        self.x = sx
        self.y = sy

    def try_attacking(self):
        if not self.aggressive:
            return False
        p = self.game.p
        distx = abs(p.x - self.x)
        disty = abs(p.y - self.y)
        if distx <= 1 and disty <= 1:
            self.battle()
            return True
        return False

    def aggressive_dest(self):
        def map_objects(map, coordlist):
            objects = []
            for x, y in coordlist:
                objects.append(map[y][x])
            return objects

        v = visibility
        sx, sy = self.x, self.y
        dx, dy = self.game.p.x, self.game.p.y
        if sx == dx and sy == dy:
            raise Exception("Player and monster are in the same spot!")
        if not v.opaque in map_objects(self.map, v.plot_path(sx, sy, dx, dy)):
            #self.game.msgwait("OMG!")
            self.dx, self.dy = dx, dy

    def clear_stats(self):
        h, w = self.game.stdscr.getmaxyx()
        c = self.game.COLS
        self.game.stdscr.addstr(10, c, " "*(w-c-1))

    def draw_stats(self):
        self.clear_stats()
        c = self.game.COLS
        self.game.stdscr.addstr(10, c, "M HP: {}".format(self.hp))

    def battle(self):
        self.game.draw()
        self.game.msgwait(
                "OMG! lvl {} {} wants to battle!".
                format(self.level, self.name))
        self.draw_stats()
        while self.hp > 0:
            self.game.msg("What will you do? (a)ttack, (p)okemon or (i)tem?")
            k = self.game.stdscr.getkey()
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
            self.game.p.give_exp(self)
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
    def __init__(self, game, map, x, y):
        self.game = game
        self.map = map
        self.x = x
        self.y = y
        self.ch = '@'
        self.name = "Pikachu"
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
        self.exp = 0

        self.calc_stats()

        self.setup_moves()

        self.inventory = []

    def setup_moves(self):
        dmg = lambda p, at, de : ( ((((2 * self.level / 5 + 2) * at * p / de) /
                                     50) + 2) * randint(85, 100) / 100 )
        phy = lambda p : (lambda m : m.be_hit(dmg(p, self.attack, m.defense)))
        spe = lambda p : (lambda m : m.be_hit(dmg(p, self.spattack, m.spdefense)))
        self.battle_moves = {
                'Quick attack': phy(40),
                'Shock Wave': spe(40),
                'Iron tail': phy(100),
                'Thunder': spe(120),
                }

        self.hp_bonus = 0

    def get_exp_needed(self):
        return self.level**3

    def give_exp(self, m):
        self.exp += round(m.base_exp*m.level/7)
        while self.exp > self.get_exp_needed():
            self.level += 1
            self.calc_stats()
            self.game.msgwait("Level up! You are now at lvl. {}!".
                                  format(self.level))

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
        e = self.get_exp_needed() - self.exp
        stats = (
                ("HP: {}", self.hp),
                ("Level: {}", self.level),
                ("Needed exp: {}", e),
                )
        for i, s in enumerate(stats):
            self.game.stdscr.addstr(i, self.game.COLS, s[0].format(s[1]))

    def rest(self):
        self.hp_bonus += 0.2
        if self.hp_bonus >= 1:
            self.hp += 1
            self.hp_bonus = 0
            self.fix_hp()

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
        self.levels = []
        self.level_i = 0

        self.game_loaded = 0

    def spawn_monsters(self):
        bl = round(5 + self.level_i)
        for i in range(randint(2, 8)):
            l = randint(bl-1, bl+1)
            m = random.choice((Monster, mons.Golbat) if l > 15 else (Monster,))
            self.monsters.append(m(self, self.map, level=l))

    def act_monsters(self):
        for m in self.monsters:
            m.move()

    def entity_in_pos(self, x, y):
        for m in self.monsters + [self.p]:
            if m.x == x and m.y == y:
                return m
        return False

    def draw(self):
        map, stdscr = visibility.darken(self.map, self.p.x, self.p.y), self.stdscr
        for y, row in enumerate(map):
            for x, ch in enumerate(row):
                if len(ch) > 1:
                    stdscr.addch(y, x, ch[0], curses.color_pair(int(ch[1])))
                else:
                    stdscr.addch(y, x, ch[0])
        self.draw_entities(map)
        self.p.draw_stats()

    def draw_entities(self, map):
        self.p.draw()
        for m in self.monsters:
            if map[m.y][m.x] in '.#':
                m.draw()

    def move(self, x, y):
        ''' Returns False if can't move, True if moved,
            e if monster battled '''
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
            return e
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
        class Item():
            def __init__(self):
                self.name = 'potatoe'
        if not self.p.inventory:
            self.msgwait("You have nothing.")
            return False
        x = 5
        y = 5
        self.stdscr.addstr(y-1, x, "Your things:")
        for item in self.p.inventory:
            self.stdscr.addstr(y, x, item.name)
            y += 1
        self.stdscr.getkey()
        self.draw()

    def die(self, msg):
        self.msgwait(msg)
        self.alive = False

    def level_up(self):
        if self.map[self.p.y][self.p.x] != '<':
            return False
        if self.level_i == 0:
            self.msgwait("You are next to the surface, "
                    "but the entrance is locked.")
            return True
        self.levels[self.level_i] = self.pack_level()
        self.level_i -= 1
        l = self.levels[self.level_i]
        self.unpack_level(l)
        self.draw()
        return True

    def level_down(self):
        if self.map[self.p.y][self.p.x] != '>':
            return False
        self.levels[self.level_i] = self.pack_level()
        self.level_i += 1
        if self.level_i < len(self.levels):
            l = self.levels[self.level_i]
            self.unpack_level(l)
            self.draw()
            return True
        self.p.x, self.p.y = self.new_level()
        self.levels.append(self.pack_level())
        self.draw()
        return True

    def pack_level(self):
        return {
            "map": self.map,
            "monsters": self.monsters,
            "pos": (self.p.x, self.p.y),
            }

    def unpack_level(self, l):
        self.map = l["map"]
        self.monsters = l["monsters"]
        # Fix monsters coz pickle fucks them
        for m in self.monsters:
            m.game = self
            m.setup_moves()
        self.p.x, self.p.y = l["pos"]

    def new_level(self):
        map = [[" " for x in range(self.COLS)] for y in range(self.ROWS)]
        x, y = dungeon.dig(map)
        self.map = map
        self.monsters = []
        self.spawn_monsters()
        return x, y

    def save_game(self):
        self.levels[self.level_i] = self.pack_level()
        save = {
                "levels": self.levels,
                "level_i": self.level_i,
                "p": self.p
            }
        fn = os.path.join(dirs.get_save_dir("cosarara", "pokerl"),
                          "save.pickle")
        import copyreg
        from types import FunctionType

        copyreg.pickle(FunctionType, lambda x : (str, ("STUB",)))
        copyreg.pickle(type(self.stdscr), lambda x : (str, ("STUB",)))
        with open(fn, "wb") as f:
            pickle.dump(save, f)

    def load_game(self):
        fn = os.path.join(dirs.get_save_dir("cosarara", "pokerl"),
                          "save.pickle")
        if not os.path.exists(fn):
            return None
        with open(fn, "rb") as f:
            save = pickle.load(f)
        self.p = save["p"]
        self.p.game = self
        self.p.setup_moves()
        self.levels = save["levels"]
        self.level_i = save["level_i"]
        self.unpack_level(self.levels[self.level_i])
        self.game_loaded = True

    def main(self, stdscr):
        stdscr.clear()
        curses.curs_set(False)
        curses.start_color()
        self.stdscr = stdscr
        menu_r = menu.display_menu(stdscr)
        if menu_r is None:
            return
        elif menu_r == "cont":
            self.load_game()

        for i in range(7):
            curses.init_pair(i+1, i, 7-i)

        stdscr.clear()

        if not self.game_loaded:
            x, y = self.new_level()
            self.p = Player(self, map, x, y)
            self.levels.append(self.pack_level())
            menu.show_big_msg(stdscr, menu.intro_txt)
        self.alive = True
        while self.alive:
            self.draw()
            stdscr.refresh()
            k = stdscr.getkey()
            if k == 'q':
                stdscr.addstr(0, 0, "Do you want to quit without saving? [y/n]")
                if stdscr.getkey() in 'yY':
                    break
            if k == 'S':
                return self.save_game()
            a = {'KEY_UP': self.move_up,
                 'KEY_DOWN': self.move_down,
                 'KEY_LEFT': self.move_left,
                 'KEY_RIGHT': self.move_right,
                 'h': self.move_left,
                 'j': self.move_down,
                 'k': self.move_up,
                 'l': self.move_right,
                 'y': self.move_ul,
                 'u': self.move_ur,
                 'b': self.move_dl,
                 'n': self.move_dr,
                 'i': self.open_inventory,
                 '<': self.level_up,
                 '>': self.level_down,
                 's': lambda : True,
                 }
            if k in a:
                if not a[k]():
                    continue
            else:
                if k.lower() in a:
                    r = a[k.lower()]()
                    while r is True:
                        self.act_monsters()
                        self.p.rest()
                        self.draw()
                        r = a[k.lower()]()
                    if r is False:
                        continue
                else:
                    continue
            if not self.alive:
                break
            self.act_monsters()
            self.p.rest()


if __name__ == "__main__":
    game = Game()
    if "--continue" in sys.argv:
        game.load_game()
    curses.wrapper(game.main)


