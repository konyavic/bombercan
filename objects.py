#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import pi
from math import sin
from math import cos

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import *

class Bomb(Node):
    def __init__(self, parent, style):
        Node.__init__(self, parent, style)

    def __draw(self, cr):
        s_width = self.width
        s_height = self.height
        cr.arc(
                s_width * 0.6, 
                s_height * 0.33, 
                s_width * 0.2, 
                0, pi * 2)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_line_width(3)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

        cr.arc(
                s_width * 0.45, 
                s_height * 0.55, 
                s_width * 0.35, 
                0, pi * 2)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_line_width(3)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

    def on_update(self, cr):
        self.__draw(cr)

    # XXX: move to controller
    def count(self):
        def _count(self, interval, phase):
            s = 1.25 - 0.25 * cos(phase * pi * 2)
            self.set_scale(s, s, (0.5, 0.8))

        self.add_action('count', _count, duration=1.5, loop=True, update=True)

class HardBlock(Node):
    def on_update(self, cr):
        cr.move_to(self.width * 0.15, self.height * 0.85)
        cr.curve_to(
                self.width * 0.3, 0,
                self.width * 0.7, 0,
                self.width * 0.85, self.height * 0.85 
                )
        cr.curve_to(
                self.width * 0.7, self.height * 0.9,
                self.width * 0.3, self.height * 0.9,
                self.width * 0.15, self.height * 0.85 
                )
        cr.close_path()
        cr.set_source_rgb(0, 0.3, 0.3)
        cr.fill_preserve()
        cr.set_line_width(3)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

class SoftBlock(Node):
    def on_update(self, cr):
        width, height = self.width, self.height
        cr.move_to(width * 0.2, height * 0.85)
        cr.rel_curve_to(
                width * 0.2, height * 0.07, 
                width * 0.4, height * 0.07, 
                width * 0.6, 0 
                )
        cr.rel_line_to(0, -height * 0.4)
        cr.rel_curve_to(
                -(width * 0.2), -(height * 0.07), 
                -(width * 0.4), -(height * 0.07), 
                -(width * 0.6), 0 
                )
        cr.close_path()

        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1.5)
        cr.stroke()

        cr.move_to(width * 0.2, height * 0.45)
        cr.rel_curve_to(
                width * 0.2, height * 0.07, 
                width * 0.4, height * 0.07, 
                width * 0.6, 0 
                )

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

class Can(Node):
    def __draw_feet(self, cr, x, y, inverse=1):
        width, height = self.width, self.height
        cr.move_to(x, y)
        cr.rel_line_to(0, height * 0.13)
        cr.rel_line_to(-(inverse * width * 0.06), 0)
        cr.rel_line_to(0, height * 0.03)
        cr.rel_line_to(inverse * width * 0.2, 0)
        cr.rel_line_to(0, -(height * 0.03))
        cr.rel_line_to(-(inverse* width * 0.06), 0)
        cr.rel_line_to(0, -(height * 0.13))
        cr.close_path()

        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

    def __draw_cylinder(self, cr, x, y, cylinder_height, color):
        width, height = self.width, self.height
        cr.move_to(x, y)
        cr.rel_curve_to(
                width * 0.2, height * 0.07, 
                width * 0.4, height * 0.07, 
                width * 0.6, 0 
                )
        cr.rel_line_to(0, -cylinder_height)
        cr.rel_curve_to(
                -(width * 0.2), -(height * 0.07), 
                -(width * 0.4), -(height * 0.07), 
                -(width * 0.6), 0 
                )
        cr.close_path()

        cr.set_source_rgb(*color)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1.5)
        cr.stroke()

        cr.move_to(x, y - cylinder_height)
        cr.rel_curve_to(
                width * 0.2, height * 0.07, 
                width * 0.4, height * 0.07, 
                width * 0.6, 0 
                )

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

    def __draw_eyes(self, cr):
        width, height = self.width, self.height
        cr.save()
        cr.scale(1, 0.5)
        cr.arc(
                width * 0.38, height * 0.9,
                width * 0.1,
                0, 2 * pi)
        cr.restore()

        cr.set_source_rgb(1, 1, 0)
        cr.fill_preserve()

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

        cr.save()
        cr.scale(1, 0.5)
        cr.arc(
                width * (1 - 0.38), height * 0.9,
                width * 0.1,
                0, 2 * pi)
        cr.restore()

        cr.set_source_rgb(1, 1, 0)
        cr.fill_preserve()

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

    def on_update(self, cr):
        width, height = self.width, self.height
        cr.save()
        cr.set_line_join(cairo.LINE_JOIN_BEVEL)
        # draw feets
        self.__draw_feet(cr, width * 0.3, height * 0.8)
        self.__draw_feet(cr, width * (1 - 0.3), height * 0.8, -1)
        # draw body
        self.__draw_cylinder(cr, width * 0.2, height * 0.8, height * 0.3, (0, 0, 0.7))
        # draw head
        self.__draw_cylinder(cr, width * 0.2, height * 0.5, height * 0.2, (0.7, 0.7, 0.7))
        # draw eyes
        self.__draw_eyes(cr)
        cr.restore()

    @animation
    def play_moving(self, cr, phase):
        width, height = self.width, self.height
        delta = height * 0.05 * cos(phase * pi * 2)

        cr.save()
        cr.set_line_join(cairo.LINE_JOIN_BEVEL)
        # draw feets
        self.__draw_feet(cr, width * 0.3, height * 0.8 + delta)
        self.__draw_feet(cr, width * (1 - 0.3), height * 0.8 - delta, -1)
        # draw body
        self.__draw_cylinder(cr, width * 0.2, height * 0.8, height * 0.3, (0, 0, 0.7))
        # draw head
        self.__draw_cylinder(cr, width * 0.2, height * 0.5, height * 0.2, (0.7, 0.7, 0.7))
        # draw eyes
        self.__draw_eyes(cr)
        cr.restore()

class Bishi(Node):
    def on_update(self, cr):
        cr.move_to(self.width / 2, 0)
        cr.line_to(self.width, self.height / 2)
        cr.line_to(self.width / 2, self.height)
        cr.line_to(0, self.height / 2)
        cr.close_path()
        cr.set_source_rgb(0.5, 0, 0.5)
        cr.fill_preserve()
        cr.set_line_width(1.5)
        cr.stroke()

class Floor(Node):
    def __init__(self, parent, style):
        Node.__init__(self, parent, style)
        self.color = (0.5, 0.5, 1, 0.7)

    def __draw_simple_pattern(self, cr, color):
        cr.set_line_width(2)
        cr.set_source_rgba(*color)
        cr.paint()

        cr.set_source_rgba(0.5, 0.5, 0.5, 0.7)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

    def on_update(self, cr):
        self.color = (0.5, 0.5, 1, 0.7)
        self.__draw_simple_pattern(cr, self.color)

    @animation
    def play_blink(self, cr, phase):
        c = cos(phase * pi * 2)
        self.color = (
                0.75 - 0.25 * c, 
                0.25 + 0.25 * c, 
                0.5 + 0.5 * c,
                0.7)
        self.__draw_simple_pattern(cr, self.color)

    @animation
    def play_fadeout(self, cr, phase):
        tmp_color = (
                self.color[0] + (0.5 - self.color[0]) * phase,
                self.color[1] + (0.5 - self.color[1]) * phase,
                self.color[2] + (1 - self.color[2]) * phase,
                0.7
                )
        self.__draw_simple_pattern(cr, tmp_color)

class DummyRect(Node):
    def on_update(self, cr):
        cr.set_source_rgb(0, 0, 1)
        cr.paint()
        cr.rectangle(0, 0, self.width, self.height)
        cr.set_source_rgb(1, 1, 0)
        cr.set_line_width(2.5)
        cr.stroke()
