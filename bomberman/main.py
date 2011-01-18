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

class Renderer:
    def do_expose(self, cr):
        pass

class StageRenderer(Renderer):
    def __init__(self, stage):
        self.stage = stage
        self.margin = (10, 10, 10, 10)

    def do_expose(self, cr):
        global game
        cell_width = (game.screen[0] - self.margin[1] - self.margin[3]) / game.map[0]
        cell_height = (game.screen[1] - self.margin[0] - self.margin[2]) / game.map[1]
        cell_size = min(cell_width, cell_height)

        start_x = lambda x: self.margin[3] + x * cell_size
        start_y = lambda y: self.margin[0] + y * cell_size

        for x in xrange(0, len(self.stage.map)):
            for y in xrange(0, len(self.stage.map[0])):
                cr.set_source_rgb(0.5, 0.5, 0.5)
                cr.rectangle(start_x(x), start_y(y), cell_size-1, cell_size-1)
                cr.fill()

        pass

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
    global area, renderers
    width = widget.allocation.width
    height = widget.allocation.height
    cr = area.window.cairo_create()    
    for r in renderers:
        r.do_expose(cr)

    return

def do_timeout():
    try:
        do_tick()
        area.queue_draw()
    except KeyboardInterrupt:
        global game
        game.quit = True

    return True

def do_key_press(widget, event):
    key = event.keyval
    print 'pressed', key
    if key == 100:
        print stage

    return True

def main():
    # game data
    global game
    game = Game()

    global stage
    stage = Stage(*game.map)

    # game redering
    global renderers
    stageRenderer = StageRenderer(stage)
    renderers = []
    renderers.append(stageRenderer)

    # gtk init
    global area

    window = gtk.Window()
    window.connect('destroy', gtk.main_quit)
    window.connect('key-press-event', do_key_press)

    area = gtk.DrawingArea()
    area.set_size_request(*game.screen)
    area.connect('expose-event', do_expose)

    window.add(area)
    window.show_all()
        
    gobject.timeout_add(1000/game.fps, do_timeout)

    gtk.main()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        global game
        game.quit = True
