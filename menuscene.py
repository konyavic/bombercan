#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node
from uicomponents import *

class MenuScene(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)

        self.bgimg = opt['$bgimg']
        self.key_up = opt['@key up']
        self.key_down = opt['@key down']
        self.game_start = opt['@game start']

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
                    '$text': u'ボンバー缶',
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
            self.game_start()

