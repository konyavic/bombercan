#!/usr/bin/python

import gtk
import gtk.gdk as gdk
import math
import random
import gobject
import time
import cairo

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
    def __init__(self):
        self.nodes = {}

    def do_expose(self, cr):
        pass

    def do_expose_nodes(self, cr):
        for k, v in self.node.items():
            self.node[v].do_expose(self, cr)

class StageRenderer(Renderer):
    def __init__(self, stage, env):
        self.stage = stage
        self.env = env

        # create surface
        self.texture = {}
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 24, 24)
        self.texture['cell'] = img

    def do_expose(self, cr):
        env = self.env
        screen_size = env['screen size']
        map_size = env['map size']
        margin = env['margin']

        cell_width = (screen_size[0] - margin[1] - margin[3]) / map_size[0]
        cell_height = (screen_size[1] - margin[0] - margin[2]) / map_size[1]
        cell_size = min(cell_width, cell_height)

        margin_left = (screen_size[0] - map_size[0]*cell_size) / 2
        margin_top = (screen_size[1] - map_size[1]*cell_size) / 2
        start_x = lambda x: margin_left + x * cell_size
        start_y = lambda y: margin_top + y * cell_size

        for x in xrange(0, map_size[0]):
            for y in xrange(0, map_size[1]):
                cr.set_source_rgb(0.5, 0.5, 0.5)
                cr.rectangle(start_x(x), start_y(y), cell_size-1, cell_size-1)
                cr.fill()

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

class Game:
    def __init__(self):
        self.__quit__ = False

        self.env = {}
        self.env['fps'] = 120
        self.env['screen size'] = (500, 500)
        self.env['map size'] = (25, 25)
        self.env['margin'] = (10, 10, 10, 10)

        self.stage = Stage(*self.env['map size'])
        self.top_renderer = StageRenderer(self.stage, self.env)

    def quit(self):
        self.__quit__ = True

    def do_tick(self):
        if self.__quit__:
            gtk.main_quit()
        print_fps()

    def do_expose(self, widget, event):
        width = widget.allocation.width
        height = widget.allocation.height
        cr = widget.window.cairo_create()    
        self.top_renderer.do_expose(cr)

    def do_timeout(self):
        try:
            self.do_tick()
            self.area.queue_draw()
        except KeyboardInterrupt:
            self.quit()

        return True

    def do_key_press(self, widget, event):
        key = event.keyval
        print 'pressed', key
        if key == 100:
            print self.stage

        return True

    def do_resize(self, widget, allocation):
        self.env['screen size'] = (allocation.width, allocation.height)

    def run(self):
        window = gtk.Window()
        window.connect('destroy', gtk.main_quit)
        window.connect('key-press-event', self.do_key_press)
        window.set_default_size(*self.env['screen size'])

        area = gtk.DrawingArea()
        area.connect('expose-event', self.do_expose)
        area.connect('size-allocate', self.do_resize)
        self.area = area

        window.add(area)
        window.show_all()
        
        gobject.timeout_add(1000/self.env['fps'], self.do_timeout)

        gtk.main()

if __name__ == '__main__':
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        game.quit()
