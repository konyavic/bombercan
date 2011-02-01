#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
import gtk.gdk as gdk
import gobject
import cairo
import pango
import pangocairo

from pnode import Node
from objects import Bomb

class Label(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        self.text = opt['$text']
        self.color = opt['$color']
        if opt.has_key('$font'):
            self.font = opt['$font']
            self.__font = pango.FontDescription(self.font)

        if opt.has_key('$bgcolor'):
            self.bgcolor = opt['$bgcolor']
        else:
            self.bgcolor = (0, 0, 0, 0)

        self.on_update()

    def set_text(self, text):
        self.text = text
        self.on_update()

    def get_size(self):
        cr = cairo.Context(self.surface)
        pcr = pangocairo.CairoContext(cr)
        layout = pcr.create_layout()
        layout.set_text(self.text)
        layout.set_font_description(self.__font)
        return layout.get_pixel_size()

    def on_update(self):
        size = self.get_size()
        self.style['width'], self.style['height'] = size
        self.set_style(self.style)
        self.reset_surface()

        cr = cairo.Context(self.surface)
        cr.set_source_rgba(*self.bgcolor)
        cr.paint()

        cr.set_source_rgba(*self.color)
        cr.move_to(0, 0)
        pcr = pangocairo.CairoContext(cr)
        layout = pcr.create_layout()
        layout.set_text(self.text)
        layout.set_font_description(self.__font)
        pcr.show_layout(layout)
    

class Selections(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)

        # input attributes
        self.labels = opt['$labels']
        if opt.has_key('$font'):
            self.font = opt['$font']

        if opt.has_key('$bgcolor'):
            self.bgcolor = opt['$bgcolor']
        else:
            self.bgcolor = (0, 0, 0, 0)

        # sub-nodes
        self.labels = [ Label(
            parent=self,
            style={
                'top': str((i + 1) * 100 / float(len(self.labels) + 2)) + '%',
                'align': 'center'
                },
            opt={
                '$text': self.labels[i],
                '$color': (1, 1, 1, 1),
                '$font': self.font
                }
            ) for i in range(0, len(self.labels)) ]

        for label in self.labels:
            self.add_node(label)

        self.curser = Bomb(
                parent=self,
                style={
                    'top': self.labels[0].y,
                    'left': self.labels[0].x - self.labels[0].height / 2,
                    'width': self.labels[0].height,
                    'height': self.labels[0].height,
                    },
                opt={
                    '$count': 0,
                    '$power': 0,
                    '$is endless': True,
                    '@explode': None,
                    '@destroy': None
                    }
                )
        self.add_node(self.curser)
        self.curser.start_counting()
        self.select(0)

        self.on_update()

    def on_update(self):
        cr = cairo.Context(self.surface)
        cr.set_source_rgba(*self.bgcolor)
        cr.paint()

    def on_resize(self):
        Node.on_resize(self)
        self.labels[self.selected].on_resize()
        self.select(self.selected)

    def select(self, i):
        self.selected = i
        self.curser.set_style({
            'top': self.labels[i].y,
            'left': self.labels[i].x - self.labels[i].height,
            'width': self.labels[i].height,
            'height': self.labels[i].height,
            })

    def select_up(self):
        i = self.selected - 1
        if i < 0:
            i = len(self.labels) - 1

        self.select(i)

    def select_down(self):
        i = self.selected + 1
        if i >= len(self.labels):
            i = 0

        self.select(i)

class MenuScene(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)

        self.bgimg = opt['$bgimg']
        self.start_game = opt['@start game']
        self.key_up = opt['@key up']
        self.key_down = opt['@key down']

        # sub-nodes
        self.sel = Selections(
                parent=self,
                style={
                    'left': '25%', 
                    'top': '50%', 
                    'width': '50%',
                    'height': '30%'
                    },
                opt={
                    '$font': 'Meiryo, MS Gothic 18',
                    #'$labels': [u'スタート', u'オプション', u'（゜д゜;;'],
                    '$labels': [u'Press Space'],
                    '$bgcolor': (0.3, 0.3, 0.7, 0.7)
                    }
                )
        self.add_node(self.sel)

        text = Label(
                parent=self,
                style={
                    'top': '30%',
                    'align': 'center'
                    },
                opt={
                    '$text': u'ボンバーマンのような何か',
                    '$font': 'Meiryo, MS Gothic bold 30',
                    '$color': (1, 1, 0.3, 1),
                    }
                )
        self.add_node(text)

        self.texture = {}
        self.texture['bgimg'] = cairo.ImageSurface.create_from_png(self.bgimg)
        self.on_update()

    def on_update(self):
        scale_width = self.width / float(self.texture['bgimg'].get_width())
        scale_height = self.height / float(self.texture['bgimg'].get_height())
        if scale_width < scale_height:
            scale = scale_height
        else:
            scale = scale_width

        new_width = self.texture['bgimg'].get_width()*scale
        new_height = self.texture['bgimg'].get_height()*scale
        x = (self.width - new_width)/2
        y = (self.height - new_height)/2

        cr = cairo.Context(self.surface)
        cr.scale(scale, scale)
        cr.set_source_rgb(0, 0, 0)
        cr.paint()
        cr.set_source_surface(self.texture['bgimg'], x, y)
        cr.paint_with_alpha(0.7)

    def on_tick(self, interval):
        if self.key_up('Up'):
            self.sel.select_up()
        elif self.key_up('Down'):
            self.sel.select_down()

        if self.key_up('space'):
            self.start_game()

