#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module contains objects that deal with graphics only 
(including animations).

"""

from math import pi
from math import sin
from math import cos

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import *
from motions import *

class Bomb(Node):
    def __init__(self, parent, style):
        super(Bomb, self).__init__(parent, style)
        use_basic_motions(self)

    def _draw(self, cr):
        width = self.width
        height = self.height

        # Draw the small circle
        cr.arc(
                width * 0.6, 
                height * 0.33, 
                width * 0.2, 
                0, pi * 2)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_line_width(3)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

        # Draw the big circle
        cr.arc(
                width * 0.45, 
                height * 0.55, 
                width * 0.35, 
                0, pi * 2)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_line_width(3)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

    def on_update(self, cr):
        self._draw(cr)

    def count(self):
        """Play the animtion when it is counting down."""
        self.scale(end_scale=(1.5, 1.5), duration=1.5, 
                rel_origin=(0.5, 0.8), harmonic=True, loop=True)

class HardBlock(Node):
    def on_update(self, cr):
        # Draw a mountain-like shape
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

        # Draw a drum-like shape
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
    def _draw_feet(self, cr, x, y, inverse=1):
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

    def _draw_cylinder(self, cr, x, y, cylinder_height, color):
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

    def _draw_eyes(self, cr):
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
        # Draw feets
        self._draw_feet(cr, width * 0.3, height * 0.8)
        self._draw_feet(cr, width * (1 - 0.3), height * 0.8, -1)
        # Draw body
        self._draw_cylinder(cr, width * 0.2, height * 0.8, height * 0.3, (0, 0, 0.7))
        # Draw head
        self._draw_cylinder(cr, width * 0.2, height * 0.5, height * 0.2, (0.7, 0.7, 0.7))
        # Draw eyes
        self._draw_eyes(cr)
        cr.restore()

    @animation
    def play_moving(self, cr, phase):
        """This animation is displayed when it is moving.
        
        It's feets will step.

        """
        width, height = self.width, self.height
        delta = height * 0.05 * cos(phase * pi * 2)

        cr.save()
        cr.set_line_join(cairo.LINE_JOIN_BEVEL)
        # Draw feets
        self._draw_feet(cr, width * 0.3, height * 0.8 + delta)
        self._draw_feet(cr, width * (1 - 0.3), height * 0.8 - delta, -1)
        # Draw body
        self._draw_cylinder(cr, width * 0.2, height * 0.8, height * 0.3, (0, 0, 0.7))
        # Draw head
        self._draw_cylinder(cr, width * 0.2, height * 0.5, height * 0.2, (0.7, 0.7, 0.7))
        # Draw eyes
        self._draw_eyes(cr)
        cr.restore()

class BadCan(Can):
    def __init__(self, parent, style):
        super(BadCan, self).__init__(parent, style)
        use_basic_motions(self)

    def on_update(self, cr):
        width, height = self.width, self.height
        cr.save()
        cr.set_line_join(cairo.LINE_JOIN_BEVEL)
        # Draw feets
        self._draw_feet(cr, width * 0.3, height * 0.8)
        self._draw_feet(cr, width * (1 - 0.3), height * 0.8, -1)
        # Draw body
        self._draw_cylinder(cr, width * 0.2, height * 0.8, height * 0.3, (0.2, 0.2, 0.2))
        # Draw head
        self._draw_cylinder(cr, width * 0.2, height * 0.5, height * 0.2, (0.3, 0.3, 0.3))
        # Draw eyes
        self._draw_eyes(cr)
        cr.restore()

    @animation
    def play_moving(self, cr, phase):
        """Same with play_moving() in class Can."""
        width, height = self.width, self.height
        delta = height * 0.05 * cos(phase * pi * 2)

        cr.save()
        cr.set_line_join(cairo.LINE_JOIN_BEVEL)
        # Draw feets
        self._draw_feet(cr, width * 0.3, height * 0.8 + delta)
        self._draw_feet(cr, width * (1 - 0.3), height * 0.8 - delta, -1)
        # Draw body
        self._draw_cylinder(cr, width * 0.2, height * 0.8, height * 0.3, (0.2, 0.2, 0.2))
        # Draw head
        self._draw_cylinder(cr, width * 0.2, height * 0.5, height * 0.2, (0.3, 0.3, 0.3))
        # Draw eyes
        self._draw_eyes(cr)
        cr.restore()

class Enemy(Node):
    class Eyes(Node):
        def on_update(self, cr):
            # Draw the eyes
            width, height = self.width, self.height
            cr.save()
            cr.scale(1, 0.5)
            cr.arc(
                    width * 0.33, height,
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
                    width * (1 - 0.33), height,
                    width * 0.1,
                    0, 2 * pi)
            cr.restore()

            cr.set_source_rgb(1, 1, 0)
            cr.fill_preserve()

            cr.set_source_rgb(0, 0, 0)
            cr.set_line_width(1)
            cr.stroke()

    def __init__(self, parent, style):
        super(Enemy, self).__init__(parent, style)
        eyes = Enemy.Eyes(parent=self, style={})
        self.add_node(eyes)
        use_basic_motions(self)

class Bishi(Enemy):
    def on_update(self, cr):
        # Draw the purpple diamond-like body
        cr.move_to(self.width / 2, 0)
        cr.line_to(self.width, self.height / 2)
        cr.line_to(self.width / 2, self.height)
        cr.line_to(0, self.height / 2)
        cr.close_path()
        cr.set_source_rgb(0.5, 0, 0.5)
        cr.fill_preserve()
        cr.set_line_width(1.5)
        cr.stroke()

class Drop(Enemy):
    def _draw(self, cr, phase):
        width, height = self.width, self.height
        phase = sin(phase * 2 * pi)
        # Draw the drop-like shape
        cr.move_to(width * (0.3 + 0.4 * phase), height * 0.05)
        cr.curve_to(
                width * 0.9 * phase, height * 0.5 * phase,
                width * -0.05, height * 0.8,
                width * 0.5, height * 0.95
                )
        cr.curve_to(
                width * 0.95, height * 0.95,
                width * 1.0 * phase, height * 0.3,
                width * (0.3 + 0.4 * phase), height * 0.05
                )
        cr.close_path()
        cr.set_source_rgb(0, 0, 1)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1.5)
        cr.stroke()

    def on_update(self, cr):
        self._draw(cr, 1)
        
    @animation
    def play_moving(self, cr, phase):
        self._draw(cr, phase)

class Ameba(Enemy):
    def _draw(self, cr, phase):
        width, height = self.width, self.height
        phase = sin(phase * 2 * pi)

        # Draw the shape
        cr.move_to(width * 0.5, height * 0.05)
        cr.curve_to(
                width * (1.0 + 0.3 * phase), height * 0.05,
                width * 0.5, height * 0.25,
                width * 0.6, height * 0.4
                )
        cr.curve_to(
                width * 0.75, height * 0.5,
                width * 0.95, height * (0.0 - 0.3 * phase),
                width * 0.95, height * 0.5
                )
        cr.curve_to(
                width * 0.95, height * (1.0 + 0.3 * phase),
                width * 0.75, height * 0.5,
                width * 0.6, height * 0.6
                )
        cr.curve_to(
                width * 0.5, height * 0.75,
                width * (1.0 + 0.3 * phase), height * 0.95,
                width * 0.5, height * 0.95
                )
        cr.curve_to(
                width * (0.0 - 0.3 * phase), height * 0.95,
                width * 0.5, height * 0.75,
                width * 0.4, height * 0.6
                )
        cr.curve_to(
                width * 0.25, height * 0.5,
                width * 0.05, height * (1.0 + 0.3 * phase),
                width * 0.05, height * 0.5
                )
        cr.curve_to(
                width * 0.05, height * (0.0 - 0.3 * phase),
                width * 0.25, height * 0.5,
                width * 0.4, height * 0.4
                )
        cr.curve_to(
                width * 0.5, height * 0.25,
                width * (0.0 - 0.3 * phase), height * 0.05,
                width * 0.5, height * 0.05
                )
        cr.close_path()
        cr.set_source_rgb(0, 1, 0)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1.5)
        cr.stroke()

    def on_update(self, cr):
        self._draw(cr, 1.0)

    @animation
    def play_moving(self, cr, phase):
        self._draw(cr, phase)

class Floor(Node):
    def __init__(self, parent, style):
        super(Floor, self).__init__(parent, style)
        self.color = (0.5, 0.5, 1, 0.7)

    def _draw_simple_pattern(self, cr, color):
        cr.set_line_width(2)
        cr.set_source_rgba(*color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgba(0.5, 0.5, 0.5, 0.7)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

    def on_update(self, cr):
        self.color = (0.5, 0.5, 1, 0.7)
        self._draw_simple_pattern(cr, self.color)

    @animation
    def play_blink(self, cr, phase):
        c = cos(phase * pi * 2)
        self.color = (
                0.75 - 0.25 * c, 
                0.25 + 0.25 * c, 
                0.5 + 0.5 * c,
                0.7)
        self._draw_simple_pattern(cr, self.color)

    @animation
    def play_fadeout(self, cr, phase):
        tmp_color = (
                self.color[0] + (0.5 - self.color[0]) * phase,
                self.color[1] + (0.5 - self.color[1]) * phase,
                self.color[2] + (1 - self.color[2]) * phase,
                0.7
                )
        self._draw_simple_pattern(cr, tmp_color)

class FireItem(Node):
    def on_update(self, cr):
        width = self.width
        height = self.height
        # Draw the background
        cr.rectangle(0, 0, width, height)
        cr.set_source_rgba(1, 1, 1, 0.5)
        cr.fill()

        # Draw the fire-like shape
        cr.move_to(width * 0.2, height * 0.2)
        cr.curve_to(
                width * 0.5, height * 0.5,
                width * -0.05, height * 0.9,
                width * 0.5, height * 0.95)
        cr.curve_to(
                width * 1.05, height * 0.9,
                width * 0.55, height * 0.5,
                width * 0.95, height * 0.2
                )
        cr.curve_to(
                width * 0.8, height * 0.2,
                width * 0.7, height * 0.2,
                width * 0.6, height * 0.4
                )
        cr.curve_to(
                width * 0.55, height * 0.2,
                width * 0.55, height * 0.2,
                width * 0.6, height * 0.05
                )
        cr.curve_to(
                width * 0.45, height * 0.1,
                width * 0.45, height * 0.15,
                width * 0.4, height * 0.4
                )
        cr.curve_to(
                width * 0.4, height * 0.35,
                width * 0.35, height * 0.3,
                width * 0.2, height * 0.2
                )
        cr.close_path()
        cr.set_source_rgb(1.0, 0.7, 0)
        cr.fill_preserve()
        cr.set_line_width(1.5)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

        cr.arc(width * 0.5, height * 0.7, width * 0.15, 0, pi * 2)
        cr.set_source_rgb(1.0, 1.0, 0)
        cr.fill()

class BombItem(Node):
    def on_update(self, cr):
        width = self.width
        height = self.height

        # Draw the background
        cr.rectangle(0, 0, width, height)
        cr.set_source_rgba(1, 1, 1, 0.5)
        cr.fill()

        # Draw the bomb
        cr.arc(
                width * 0.6, 
                height * 0.33, 
                width * 0.2, 
                0, pi * 2)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_line_width(3)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

        cr.arc(
                width * 0.45, 
                height * 0.55, 
                width * 0.35, 
                0, pi * 2)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_line_width(3)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()


class DummyRect(Node):
    def on_update(self, cr):
        # Show the surface
        cr.set_source_rgba(0, 0, 1, 0.5)
        cr.paint()
        
        # Show the drawing space
        cr.rectangle(0, 0, self.width, self.height)
        cr.set_source_rgb(1, 1, 0)
        cr.set_line_width(2.5)
        cr.stroke()
        
        # Show the center of drawing space
        center = self.width * 0.5, self.height * 0.5
        cr.move_to(center[0] - 5, center[1] - 5)
        cr.rel_line_to(10, 0)
        cr.rel_line_to(0, 10)
        cr.rel_line_to(-10, 0)
        cr.close_path()
        cr.set_source_rgb(1, 0, 0)
        cr.set_line_width(2.5)
        cr.stroke()
