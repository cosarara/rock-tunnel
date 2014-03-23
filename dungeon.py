
import sys
from random import randint, sample

def dig_shape(map, x, y, shape):
    for yi, row in enumerate(shape):
        for xi, ch in enumerate(row):
            map[y+yi][x+xi] = ch

def shape_fits(map, x, y, shape):
    for yi, row in enumerate(shape):
        for xi, ch in enumerate(row):
            if map[y+yi][x+xi] != ' ':
                return False
    return True

def make_room(h, w):
    w, h = w+2, h+2
    r = [["." for x in range(w)] for y in range(h)]
    for row in r:
        row[0] = "|"
        row[w-1] = "|"
    r[0] = ['-']*w
    r[h-1] = list(r[0])
    return r

def enlarge_room(room, n):
    room = [r+[' ' for i in range(n)] for r in room]
    room += [room[0]]*n
    return room

def get_room_center(x, y, h, w):
    return round(x + w/2), round(y + h/2)

def place_room(map, room):
    big_room = enlarge_room(room, 2)
    roomh = len(big_room)
    roomw = len(big_room[0])
    for t in range(40): # Give up at nth attempt
        x = randint(0, len(map[0])-roomw-1)
        y = randint(0, len(map)-roomh-1)
        if shape_fits(map, x, y, big_room):
            dig_shape(map, x+1, y+1, room)
            return get_room_center(x+1, y+1, roomh, roomw)
    return False

def dig_path(map, sx, sy, dx, dy):
    ''' Dig interesting paths '''
    def dig(x, y): 
        if map[y][x] in [' ', '-', '|']:
            map[y][x] = '#'
    if sx == dx and sy == dy:
        return
    distx = dx - sx
    disty = dy - sy
    dirx = distx // abs(distx) if distx != 0 else 0
    diry = disty // abs(disty) if disty != 0 else 0
    r = randint(0, 2)
    if abs(distx) > abs(disty) and r or r == 1:
        sx += dirx
    else:
        sy += diry
    dig(sx, sy)
    dig_path(map, sx, sy, dx, dy)

def get_floor_tile(map):
    w = len(map[0])
    h = len(map)
    while True:
        x, y = randint(0, w-1), randint(0, h-1)
        if map[y][x] == '.':
            return x, y

def put(map, t, x, y):
    map[y][x] = t

def dig(map):
    ''' Digs a dungeon level '''
    main_room = make_room(6, 6)
    main_room_center = place_room(map, main_room)
    sizes = [(16, 16), (3, 4), (8, 20), (15, 8), (4, 8),
             (3, 3), (2, 3), (2, 4), (4, 4), (10, 12)]
    centers = []
    for pick in sample(sizes, randint(3, len(sizes))):
        c = place_room(map, make_room(*pick))
        if c:
            centers += [c]
    last_center = main_room_center
    for c in centers:
        dig_path(map, *(last_center + c))
        last_center = c

    exit = get_floor_tile(map)
    entrance = get_floor_tile(map)
    put(map, '>', *exit)
    put(map, '<', *entrance)
    return entrance


