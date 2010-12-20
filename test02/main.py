#!/usr/bin/python

import gtk
import gtk.gdk as gdk
import math
import random
import gobject
import time
import cairo

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

def expose(widget, event):
    global area
    width = widget.allocation.width
    height = widget.allocation.height
    cx = width/2
    cy = height/2
    radius = min(cx, cy)

    cr = area.window.cairo_create()

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

    cr.arc( widget.allocation.width / 2, 
            widget.allocation.height / 2, 
            radius/2, 0, math.pi * 2)
    cr.set_source_rgba(0.5, 0.5, 0.7, 0.1)
    cr.fill_preserve()

    print_fps()
    return

def timeout():
    global area
    area.queue_draw()
    return True

def main():
    global window, area

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
