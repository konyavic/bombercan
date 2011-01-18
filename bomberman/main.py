#!/usr/bin/python

import gtk
import gtk.gdk as gdk
import math
import random
import gobject
import time
import cairo

class Game:
    def __init__(self):
        self.quit = False
        self.fps = 120
        self.screen = (600, 600)
        self.map = (25, 25)

class Cell:
    def __init__(self, pos):
        self.pos = pos

    def __repr__(self):
        return '.'

class Stage:
    def __init__(self, width, height):
        self.map = [[Cell([x, y]) for y in xrange(0, height)] for x in xrange(0, width)]

    def __repr__(self):
        str = ''
        for x in xrange(0, len(self.map)):
            if (x % 5 == 0): 
                str += '%2d' % x
            else: 
                str += '  '
            for cell in self.map[x]:
                str += repr(cell)

            str += '\n'

        return str

class StageRenderer:
    def __init__(self, stage):
        self.stage = stage

fps_counters = [0 for i in range(0, 5)]
fps_cur_counter = 0
last_time = time.time()

def print_fps():
    global fps_counter, fps_cur_counter, last_time
    cur_time = time.time()
    elapsed_time = cur_time - last_time
    if elapsed_time > 1:
        last_time = cur_time
        fps_cur_counter = (fps_cur_counter + 1) % 5

        total_count = 0
        for count in fps_counters:
            total_count += count

        print 'fps =', float(total_count) / 5
        fps_counters[fps_cur_counter] = 1   # reset

    else:
        fps_counters[fps_cur_counter] += 1

def do_tick():
    global game
    if game.quit:
        gtk.main_quit()

    print_fps()
    return

def do_expose(widget, event):
    global area
    width = widget.allocation.width
    height = widget.allocation.height
    cr = area.window.cairo_create()    

    return

def do_timeout():
    do_tick()
    area.queue_draw()

    return True

def do_key_press(widget, event):
    key = event.keyval
    print 'pressed', key
    if key == 100:
        print stage

    return True

def main():
    ''' game data '''
    global game
    game = Game()

    global stage
    stage = Stage(*game.map)

    ''' game redering '''
    global area

    # gtk init
    window = gtk.Window()
    window.connect('destroy', gtk.main_quit)
    window.connect('key-press-event', do_key_press)

    area = gtk.DrawingArea()
    area.set_size_request(*game.screen)
    area.connect('expose-event', do_expose)

    window.add(area)
    window.show_all()
        
    # setting fps
    gobject.timeout_add(1000/game.fps, do_timeout)

    gtk.main()

if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        global game
        game.quit = True
