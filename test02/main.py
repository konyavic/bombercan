#!/usr/bin/python

import gtk
import gtk.gdk as gdk
import math
import random
import gobject
import time
import cairo

class Sprite:
    def expose(self):
        return
    def do_tick(self):
        return
    def do_update(self, time):
        return

def circular(val, v, low, high):
    val += v
    if val < low:
        val = low
        v = -v
    elif val > high:
        val = high
        v = -v
    return (val, v)

class Sprite01(Sprite):
    def __init__(self):
        self.stops = [
                [0, 0, 0],
                [0.3, 0.7, 0.7],
                [0.7, 0.7, 0.9],
                [0.7, 0.3, 0.3],
                [0.8, 0.8, 0.3],
                ]
        self.stops_v = [
                [0.05, 0.05, 0.05],
                [0.05, 0.05, 0.05],
                [0.05, 0.05, 0.05],
                [0.05, 0.05, 0.05],
                [0.05, 0.05, 0.05],
                ]
        self.pos = [0, 0]
        self.pos_v = [1, 3]
        self.border_width = 1
        self.border_width_v = 0.2
        return

    def expose(self, cr, width, height):
        cx = width/2
        cy = height/2
        radius = min(cx, cy)

        linepat = cairo.LinearGradient(0, 0, width, height)
        for i in range(0, 5):
            linepat.add_color_stop_rgb(i*0.25, *self.stops[i])

        radpat = cairo.RadialGradient(cx, cy, radius/2, cx, cy, radius)
        radpat.add_color_stop_rgba(0, 0, 0, 0, 1)
        radpat.add_color_stop_rgba(1, 0, 0, 0, 0)

        cr.set_source(linepat)
        cr.mask(radpat)

        cr.arc(width/2+self.pos[0], height/2+self.pos[1], radius/2, 0, math.pi*2)
        cr.set_source_rgba(0.5, 0.5, 0.7, 0.3)
        cr.fill_preserve()

        cr.set_source_rgba(1, 1, 1, 0.1)
        cr.set_line_width(self.border_width)
        cr.stroke()
        return

    def do_tick(self):
        for i in range(0, 5):
            for color in range(0, 3):
                (self.stops[i][color], self.stops_v[i][color]) = circular(
                        self.stops[i][color], self.stops_v[i][color], 0, 1)
        for i in range(0, 2):
            (self.pos[i], self.pos_v[i]) = circular(
                    self.pos[i], self.pos_v[i], -50, 50)
        (self.border_width, self.border_width_v) = circular(
                self.border_width, self.border_width_v, 0.5, 10)
        return

fps_counter = 0
last_time = time.time()

def print_fps():
    global fps_counter, last_time
    fps_counter += 1
    cur_time = time.time()
    elapsed_time = cur_time - last_time
    if elapsed_time > 2:
        print 'fps =', fps_counter, '/', elapsed_time, '=', float(fps_counter) / elapsed_time
        last_time = cur_time
        fps_counter = 0

def do_tick():
    print_fps()
    for s in sprites:
        s.do_tick()
    return

def expose(widget, event):
    global area, sprites
    width = widget.allocation.width
    height = widget.allocation.height

    cr = area.window.cairo_create()    
    for s in sprites:
        s.expose(cr, width, height)
    return

def timeout():
    global area
    do_tick()
    area.queue_draw()
    return True

def main():
    global window, area, sprites
    
    """ sprite init """
    s1 = Sprite01()
    sprites = []
    sprites.append(s1)


    """ gtk init """
    window = gtk.Window()
    window.connect("destroy", gtk.main_quit)

    area = gtk.DrawingArea()
    area.set_size_request(800, 600)
    area.connect("expose-event", expose)

    window.add(area)
    window.show_all()
        
    gobject.timeout_add(1000/200, timeout)  # fps = 100 (ideally)
    gtk.main()

if __name__ == '__main__':
    main()
