#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import pi
from random import random

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import *

class ExplosionEffect(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        self.arms = opt['$arms']
        self.get_cell_size = opt['?cell size']
        self.do_destroy = opt['@destroy']

        def animation(self, phase):
            cell_size = self.get_cell_size()
            left = self.arms[3] * cell_size
            up = self.arms[0] * cell_size
            right = self.arms[1] * cell_size
            down = self.arms[2] * cell_size

            cr = cairo.Context(self.surface)
            self.clear_context(cr)
            cr.move_to(left, up)
            cr.rel_line_to(0, -up)
            cr.rel_line_to(cell_size, 0)
            cr.rel_line_to(0, up)
            cr.rel_line_to(right, 0)
            cr.rel_line_to(0, cell_size)
            cr.rel_line_to(-right, 0)
            cr.rel_line_to(0, down)
            cr.rel_line_to(-cell_size, 0)
            cr.rel_line_to(0, -down)
            cr.rel_line_to(-left, 0)
            cr.rel_line_to(0, -cell_size)
            cr.close_path()
            cr.set_source_rgba(1, 1, 0, 0.5)
            cr.fill()

        self.add_animation('explosion', animation, delay=0, period=1, loop=False, cleanup=self.do_destroy)


class Particle():
    __slots__ = ('size', 'position', 'velocity', 'color', 'v_color', 'lifetime')

def restrict(e):
    if e <= 0.0: 
        return 0.0
    elif e >= 1.0: 
        return 1.0
    else: 
        return e

class ParticleEffect(Node):
    def __init__(self, parent, style, 
            size, color, v_color, center, velocity, velocity_deviation, lifetime,
            size_deviation=0, center_deviation=(0, 0), 
            color_deviation=(0, 0, 0, 0), v_color_deviation=(0, 0, 0, 0),
            lifetime_deviation=0, max_amount=0, initial_amount=0, spawn_interval=0.0):

        Node.__init__(self, parent, style)
        # color
        self.color = color
        self.v_color = v_color
        self.color_deviation = color_deviation
        self.v_color_deviation = v_color_deviation
        # position (change upon resize)
        self.size = size
        self.size_deviation = size_deviation
        self.center = center
        self.center_deviation = center_deviation
        self.velocity = velocity
        self.velocity_deviation = velocity_deviation
        self.orig_width = float(self.width)
        self.orig_height = float(self.height)
        # lifetime
        self.lifetime = lifetime
        self.lifetime_deviation = lifetime_deviation
        # other
        self.max_amount = max_amount
        self.spawn_interval = spawn_interval
        self.time_elapsed = 0.0
        self.particles = []
        for i in xrange(0, initial_amount):
            self.spawn()

    def spawn(self):
        def deviated(e):
            return e[0] + e[1] * (random() - 0.5)

        p = Particle()
        p.size = deviated((self.size, self.size_deviation))
        p.lifetime = deviated((self.lifetime, self.lifetime_deviation))
        p.position = map(deviated, zip(self.center, self.center_deviation))
        p.velocity = map(deviated, zip(self.velocity, self.velocity_deviation))
        p.color = map(lambda e: restrict(deviated(e)), zip(self.color, self.color_deviation))
        p.v_color = map(deviated, zip(self.v_color, self.v_color_deviation))
        self.particles.append(p)

    def on_tick(self, interval):
        def update_value(e):
            return e[0] + e[1] * e[2]

        particles = list(self.particles)
        interval2 = (interval, ) * 2
        interval4 = (interval, ) * 4
        for p in particles:
            p.position = map(update_value, zip(p.position, p.velocity, interval2))
            p.color = map(update_value, zip(p.color, p.v_color, interval4))
            p.color = map(restrict, p.color)
            p.lifetime -= interval
            if p.lifetime <= 0.0 or p.color[3] <= 0.0:
                self.particles.remove(p)

        # spawn new particle
        self.time_elapsed += interval
        if (self.time_elapsed > self.spawn_interval 
                and (self.max_amount == 0 or len(self.particles) <= self.max_amount)):

            self.time_elapsed = 0.0
            self.spawn()

    @animation
    def play(self, phase):
        rect = (self.width, self.height)
        cr = cairo.Context(self.surface)
        self.clear_context(cr)
        for p in self.particles:
            x = p.position[0] * rect[0]
            y = p.position[1] * rect[1]
            size = p.size * (rect[0] + rect[1]) / 2
            cr.set_source_rgba(*p.color)
            cr.arc(x, y, size, 0, 2 * pi)
            cr.fill()
