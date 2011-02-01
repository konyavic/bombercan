#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node

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
