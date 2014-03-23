
import random
import math
import sys

opaque = '-| '

def see_path(map, darkmap, sx, sy, dx, dy):
    color = random.randint(0, 6) + 1
    w = len(map[0])
    h = len(map)
    distx = dx - sx
    disty = dy - sy

    def plot(x, y):
        c = map[y][x]
        darkmap[y][x] = c#+str(color)
        return c in opaque

    try: 
        m = (disty/distx)
    except ZeroDivisionError:
        if sy < dy:
            for y in range(disty):
                if plot(sx, sy+y):
                    return
        else:
            for y in range(abs(disty)):
                if plot(sx, sy-y):
                    return
        return
    if m > 1 or m < -1:
        for y in reversed(range(dy, sy)) if sy > dy else range(sy, dy):
            x = round(sx + 1/m * (y - sy))
            if x > w-1:
                x = w-1
            if plot(x, y):
                return
    else:
        for x in reversed(range(dx, sx)) if sx > dx else range(sx, dx):
            y = round(sy + m * (x - sx))
            if y > h-1:
                y = h-1
            if plot(x, y):
                return

def darken(map, x, y):
    """ Hides everything except what's visible from (x,y) """ 
    darkmap = [[' ' for c in row] for row in map]
    w = len(map[0])
    h = len(map)
    for i in range(w):
        see_path(map, darkmap, x, y, i, 0)
        see_path(map, darkmap, x, y, i, h-1)

    for i in range(h):
        see_path(map, darkmap, x, y, 0, i)
        see_path(map, darkmap, x, y, w-1, i)

    return darkmap

