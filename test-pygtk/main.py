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

# The number of circles and the window size.
#num = 128
num = 256
size = 512
r = range(num)

# Initialize circle coordinates and velocities.
x = []
y = []
xv = []
yv = []
for i in r:
    x.append(random.randint(0, size))
    y.append(random.randint(0, size))
    xv.append(random.randint(-4, 4))
    yv.append(random.randint(-4, 4))

def create_basic_image():
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 24, 24)
    c = cairo.Context(img)
    c.set_line_width(4)
    c.arc(12, 12, 8, 0, 2 * math.pi)
    c.set_source_rgb(1, 0, 0)
    c.stroke_preserve()
    c.set_source_rgb(1, 1, 1)
    c.fill()
    return img

# Draw the circles and update their positions.
def expose(*args):
    global fps_counter
    global last_time
    global img
    cr = darea.window.cairo_create()
    cr.set_line_width(4)
    for i in r:
        cr.set_source_surface(img, x[i], y[i])        
        cr.paint()        
        x[i] += xv[i]
        y[i] += yv[i]
        if x[i] > size or x[i] < 0:
            xv[i] = -xv[i]
        if y[i] > size or y[i] < 0:
            yv[i] = -yv[i]
    fps_counter += 1
    cur_time = time.time()
    elapsed_time = cur_time - last_time
    if elapsed_time > 2:
        print "fps=", float(fps_counter) / elapsed_time
        last_time = cur_time
        fps_counter = 0

# Self-evident?
def timeout():
    darea.queue_draw()
    return True

def main():
    global window, darea, img
    # Initialize the window.
    window = gtk.Window()
    window.resize(size, size)
    window.connect("destroy", gtk.main_quit)
    darea = gtk.DrawingArea()
    darea.connect("expose-event", expose)
    window.add(darea)
    window.show_all()
        
    img = create_basic_image()

    # Self-evident?
    gobject.timeout_add(1000/100, timeout)
    #gobject.idle_add(timeout)
    gtk.main()

if __name__ == '__main__':
    main()
