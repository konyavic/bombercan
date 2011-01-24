#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
import gtk.gdk as gdk
import gobject
import cairo
import pango
import pangocairo

from pnode import Node

class Selections(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)

        # input attributes
        self.num = int(opt['num'])
        self.font = opt['font']
        self.label = [opt['label %d' % i] for i in range(0, self.num)]

        # private attributes
        self.__selected = None

        self.on_update()

    def on_update(self):
        cr = cairo.Context(self.surface)
        cr.set_source_rgb(0, 0, 1)
        cr.paint_with_alpha(0.5)
        cr.set_source_rgb(1, 1, 1)
        cr.move_to(10, 10)
        pcr = pangocairo.CairoContext(cr)
        layout = pcr.create_layout()
        layout.set_font_description(self.font)
        layout.set_text(u"スペースキーを押してくだし")
        pcr.show_layout(layout)

    def select(self, i):
        self.__selected = i


class MenuScene(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)

        # dependent functions
        self.start_game = opt['start game']
        self.activated = opt['activated']
        self.deactivated = opt['deactivated']

        # private attributes
        self.__font = pango.FontDescription("Meiryo, MS Gothic")

        # sub-nodes
        self.add_node(Selections(self.width * 0.25, self.height * 0.5, int(self.width * 0.5), int(self.height * 0.3),
            {
                'num': 1,
                'font': self.__font,
                'label 0': u"test"
                }))

        self.on_update()

    def on_update(self):
        cr = cairo.Context(self.surface)
        cr.set_source_rgb(0, 0, 0)
        cr.paint()
        cr.set_source_rgb(1, 1, 1)

        pcr = pangocairo.CairoContext(cr)
        layout = pcr.create_layout()

        layout.set_text(u"乾電池ボンバーマン")
        size = layout.get_pixel_size()
        self.__font.set_absolute_size(size[1] * float(self.width / size[0]) * pango.SCALE)
        layout.set_font_description(self.__font)
        size = layout.get_pixel_size()
        cr.move_to((self.width - size[0]) / 2, (self.height / 3) - (size[1] / 2))
        pcr.show_layout(layout)

    def on_tick(self, interval):
        if self.activated(32):
            self.start_game()

