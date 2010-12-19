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
        print "fps =", float(fps_counter) / elapsed_time
        last_time = cur_time
        fps_counter = 0

def expose(widget, event):
    global area
    
    radius = min(widget.allocation.width / 2, widget.allocation.height / 2)

    cr = area.window.cairo_create()
    cr.arc( widget.allocation.width / 2, 
            widget.allocation.height / 2, 
            radius * 0.7, 0, math.pi * 2)
    cr.set_source_rgba(0.5, 0.5, 0.7, 0.3)
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
    window.resize(800, 600)
    window.connect("destroy", gtk.main_quit)

    area = gtk.DrawingArea()
    area.connect("expose-event", expose)

    window.add(area)
    window.show_all()
        
    gobject.timeout_add(1000/100, timeout)  # fps = 100 (ideally)
    gtk.main()

if __name__ == '__main__':
    main()
