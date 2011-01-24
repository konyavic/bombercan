#!/usr/bin/python

import math

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node

class Bomb(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)

        # input attributes
        self.count = float(opt['count'])
        self.power = int(opt['power'])
        if opt.has_key('is endless'):
            self.is_endless = opt['is endless']
        else:
            self.is_endless = False

        # dependent functions
        self.do_explode = opt['explode']
        self.do_destroy = opt['destroy']

        # private attributes
        self.__scale = 1.0
        self.__is_counting = False

        self.on_update()

    def __draw(self, cr):
        s_width = self.width * self.__scale
        s_height = self.height * self.__scale
        self.clear_context(cr)
        cr.arc(
                s_width * 0.6, 
                s_height * 0.33, 
                s_width * 0.2, 
                0, math.pi * 2)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_line_width(1.5)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

        cr.arc(
                s_width * 0.45, 
                s_height * 0.55, 
                s_width * 0.35, 
                0, math.pi * 2)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_line_width(1.5)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

    def on_update(self):
        self.reset_surface()
        cr = cairo.Context(self.surface)
        self.__draw(cr)

    def on_tick(self, interval):
        if self.__is_counting and not self.is_endless:
            self.count -= interval
            if self.count < 0:
                self.__is_counting = False
                self.explode()

    def start_counting(self):
        def counting_animation(self, phase):
            self.__scale = 1.25 - 0.25 * math.cos(phase * math.pi * 2)
            self.create_surface_by_scale(self.__scale, rel_origin=(0.5, 1))
            cr = cairo.Context(self.surface)
            self.__draw(cr)

        self.__is_counting = True
        self.add_animation('count', counting_animation, loop=True, delay=0, period=1.5)

    def explode(self):
        self.do_explode(self)
        self.do_destroy(self)
