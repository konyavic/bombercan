#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module containes visual effects (also implemented as nodes)."""

from math import pi
from random import random

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node

class ExplosionEffect(Node):
    """This effect is showed when a bomb explode."""
    def __init__(self, parent, style, fire, get_cell_size, on_die):
        """Initialize this effect.
        
        @param fire: representing the length of four fire arms (top, right, down, left)
        @type fire: a list of four integers 
        @param get_cell_size: the callback function that always returns the cell size 
            (should be MapContainer.get_cell_size())
        @param on_die: the callback function called when the effect ends

        """
        super(ExplosionEffect, self).__init__(parent, style)
        self.fire = fire
        self.get_cell_size = get_cell_size
        self.on_die = on_die

        def animation(self, cr, phase):
            cell_size = self.get_cell_size()
            left = self.fire[3] * cell_size
            up = self.fire[0] * cell_size
            right = self.fire[1] * cell_size
            down = self.fire[2] * cell_size

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

        self.set_animation(animation, duration=1.5, cleanup=self.on_die)


class Particle(object):
    """The individual particle for particle system."""
    __slots__ = ('size', 'v_size', 'position', 
            'velocity', 'accel', 'color', 'v_color', 'lifetime')

class ParticleEffect(Node):
    """Display effects using particle system."""
    def __init__(self, parent, style, 
            size, color, v_color, center, 
            velocity, velocity_deviation, lifetime,
            v_size=0, size_deviation=0, accel=(0, 0),
            max_amount=0, initial_amount=0, spawn_interval=0.0):
        """Initilize this particle system.

        @param size: the size of one particle
        @param color: the rgba value of the initial color for each particle
        @param v_color: the vector for the change of color
        @param center: the position to spawn new particles 
            (in relative position, eg. (0.5, 0.5) represents the center of object)
        @param velocity: the velocity of each particle
        @param velocity_deviation: the deviation of initial velocity 
            of each paricle
        @param lifetime: the life of each particle (in second)
        @param v_size: the change of size
        @param size_deviation: the deviation of initial size of each particle
        @param accel: the acceleration
        @param max_amount: the max number of particles
        @param initial_amount: the initial number of particles
        @param spawn_interval: the period to spawn new particles

        """

        super(ParticleEffect, self).__init__(parent, style)
        # color
        self.color = color
        self.v_color = v_color
        # position (change upon resize)
        self.size = size
        self.size_deviation = size_deviation
        self.v_size = v_size
        self.center = center
        self.velocity = velocity
        self.velocity_deviation = velocity_deviation
        self.accel = accel
        self.orig_width = float(self.width)
        self.orig_height = float(self.height)
        # other
        self.lifetime = lifetime
        self.max_amount = max_amount
        self.spawn_interval = spawn_interval

        self.time_elapsed = 0.0
        self.particles = []
        for i in xrange(0, initial_amount):
            self.spawn()

    def spawn(self):
        def _deviated(e):
            return e[0] + e[1] * (random() - 0.5)

        p = Particle()
        p.size = _deviated((self.size, self.size_deviation))
        p.v_size = self.v_size
        p.lifetime = self.lifetime
        p.position = self.center
        p.velocity = map(_deviated, 
                zip(self.velocity, self.velocity_deviation))
        p.accel = self.accel
        p.color = self.color
        p.v_color = self.v_color
        self.particles.append(p)

    @staticmethod
    def update_action(self, interval, phase):
        def update_value(e):
            return e[0] + e[1] * e[2]

        def restrict(e):
            return 0.0 if e <= 0.0 else 1.0 if e >= 1.0 else e

        # Update particles
        particles = list(self.particles)
        interval2 = (interval, ) * 2
        interval4 = (interval, ) * 4
        for p in particles:
            p.position = map(update_value, 
                    zip(p.position, p.velocity, interval2))
            p.velocity = map(update_value, 
                    zip(p.velocity, p.accel, interval2))
            p.color = map(update_value, zip(p.color, p.v_color, interval4))
            p.color = map(restrict, p.color)
            p.size += p.v_size * interval
            p.lifetime -= interval
            if p.lifetime <= 0.0 or p.color[3] <= 0.0 or p.size <= 0:
                self.particles.remove(p)

        # Spawn a new particle
        self.time_elapsed += interval
        if (self.time_elapsed > self.spawn_interval
                and (self.max_amount == 0 
                    or len(self.particles) <= self.max_amount)):

            self.time_elapsed = 0.0
            self.spawn()

    def on_update(self, cr):
        w, h = self.width, self.height
        factor = w / self.orig_width
        for p in self.particles:
            x = p.position[0] * w
            y = p.position[1] * h
            # XXX: how to resize it?
            size = p.size * factor
            cr.set_source_rgba(*p.color)
            cr.arc(x, y, size, 0, 2 * pi)
            cr.fill()
