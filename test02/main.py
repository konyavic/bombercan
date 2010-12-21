#!/usr/bin/python

import gtk
import gtk.gdk as gdk
import math
import random
import gobject
import time
import cairo

class Sprite:
    def __init__(self, do_tick=None, expose=None):
        self.do_tick = do_tick
        self.expose = expose
        return

def sprite1_expose(cr, width, height):
    cx = width/2
    cy = height/2
    radius = min(cx, cy)

    linepat = cairo.LinearGradient(0, 0, width, height)
    linepat.add_color_stop_rgb(0, 0, 0, 0)
    linepat.add_color_stop_rgb(0.25, 0.3, 0.7, 0.7)
    linepat.add_color_stop_rgb(0.5, 0.7, 0.7, 0.9)
    linepat.add_color_stop_rgb(0.75, 0.7, 0.3, 0.3)
    linepat.add_color_stop_rgb(1, 0.8, 0.8, 0.3)

    radpat = cairo.RadialGradient(cx, cy, radius/2, cx, cy, radius)
    radpat.add_color_stop_rgba(0, 0, 0, 0, 1)
    radpat.add_color_stop_rgba(1, 0, 0, 0, 0)

    cr.set_source(linepat)
    cr.mask(radpat)

    cr.arc(width/2, height/2, radius/2, 0, math.pi*2)
    cr.set_source_rgba(0.5, 0.5, 0.7, 0.1)
    cr.fill_preserve()
    return

def sprite1_do_tick():
    # do nothing
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
    s1 = Sprite(sprite1_do_tick, sprite1_expose)
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
