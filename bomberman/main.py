#!/usr/bin/python

import gtk
import gtk.gdk as gdk
import gobject
import time
import cairo

class Node:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.enabled_update = True
        self.enabled_tick = True
        self.surface = None
        self.children = []

    def add_node(self, node):
        self.children.append(node)
        node.parent = self

    def remove_node(self, node):
        self.children.remove(node)
        node.parent = None

    def on_update(self):
        pass

    def on_resize(self, width, height):
        self.width = width
        self.height = height
        self.on_update()

    def on_tick(self, phase):
        pass

    def do_update_recursive(self, cr, x, y):
        x, y = x + self.x, y + self.y
        if self.enabled_update:
            self.on_update()

        if self.surface:
            cr.set_source_surface(self.surface, x, y)
            cr.rectangle(x, y, self.width, self.height)
            cr.fill()

        for nodes in self.children:
            nodes.do_update_recursive(cr, x, y)

    def do_tick_recursive(self, phase):
        if self.enabled_tick:
            self.on_tick(phase)

        for nodes in self.children:
            nodes.do_tick_recursive(phase)

def draw_simple_pattern(surface, width, height):
    cr = cairo.Context(surface)
    cr.set_line_width(2)
    cr.rectangle(0, 0, width, height)
    cr.set_source_rgb(0.5, 0.5, 1)
    cr.fill_preserve()
    cr.set_source_rgb(0.5, 0.5, 0.5)
    cr.stroke()
    del cr

class Cell(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)
        self.pos = opt['pos']
        self.enabled_tick = False
        self.enabled_update = False
        self.on_update()

    def __repr__(self):
        return '.'

    def on_update(self):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        draw_simple_pattern(self.surface, self.width, self.height)

class Stage(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)
        self.map_size = opt['map_size']
        self.margin = opt['margin']
        self.enabled_tick = False
        self.enabled_update = False

        self.update_metrics()
        self.map = [ [
            Cell(
                self.get_cell_pos(x, y)[0],
                self.get_cell_pos(x, y)[1],
                self.cell_size, 
                self.cell_size, 
                {'pos':[x, y]}
                )
            for y in xrange(0, self.map_size[1]) ] for x in xrange(0, self.map_size[0]) ]

        for row in self.map:
            for cell in row:
                self.add_node(cell)

        self.on_update()

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

    def update_metrics(self):
        self.cell_size = min(
                (self.width - self.margin[1] - self.margin[3])/self.map_size[0], 
                (self.height - self.margin[0] - self.margin[2])/self.map_size[1]
                )
        self.top = (self.height - self.cell_size * self.map_size[1]) / 2
        self.left = (self.width - self.cell_size * self.map_size[0]) / 2

    def get_cell_pos(self, x, y):
        return (self.left + self.cell_size*x, self.top + self.cell_size*y)

    def on_update(self):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        cr = cairo.Context(self.surface)
        cr.rectangle(0, 0, self.width, self.height)
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.fill()

    def on_resize(self, width, height):
        Node.on_resize(self, width, height)
        self.update_metrics()
        for x in xrange(0, self.map_size[0]):
            for y in xrange(0, self.map_size[1]):
                cell = self.map[x][y]
                cell.x, cell.y = self.get_cell_pos(x, y)
                cell.on_resize(self.cell_size, self.cell_size)
        

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

        self.fps = 120
        self.screen_size = [500, 500]
        self.top_node = Stage(0, 0, 500, 500, 
                {
                    'map_size': [25, 25], 
                    'margin': [10, 10, 10, 10]
                    }
                )

    def quit(self):
        self.__quit__ = True

    def do_tick(self):
        if self.__quit__:
            gtk.main_quit()
        print_fps()
        self.top_node.do_tick_recursive(12345)

    def do_expose(self, widget, event):
        try:
            cr = widget.window.cairo_create()
            width = widget.allocation.width
            height = widget.allocation.height
            node = self.top_node
            node.do_update_recursive(cr, 0, 0)
        except KeyboardInterrupt:
            self.quit()

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
        self.screen_size = (allocation.width, allocation.height)
        self.top_node.on_resize(allocation.width, allocation.height)

    def run(self):
        window = gtk.Window()
        window.connect('destroy', gtk.main_quit)
        window.connect('key-press-event', self.do_key_press)
        window.set_default_size(*self.screen_size)

        area = gtk.DrawingArea()
        area.connect('expose-event', self.do_expose)
        area.connect('size-allocate', self.do_resize)
        self.area = area

        window.add(area)
        window.show_all()
        
        gobject.timeout_add(1000/self.fps, self.do_timeout)

        gtk.main()

if __name__ == '__main__':
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        game.quit()
