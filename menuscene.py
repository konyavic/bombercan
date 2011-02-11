#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import pi

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node
from objects import *
from uicomponents import *
from effects import ParticleEffect

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

        particle = ParticleEffect(self, 
                {'width': '50%', 'height': '50%', 'align': 'center', 'vertical-align': 'bottom'},
                #size=10, size_deviation=1, v_size=3, v_size_deviation=2, 
                size=10, size_deviation=2, v_size=3, v_size_deviation=0, 
                #size=10, size_deviation=0, v_size=3, v_size_deviation=0, 
                #color=(0.8, 0.4, 0, 0.5), color_deviation=(0.2, 0.2, 0, 0.2), v_color=(-0.5, -0.5, 0, -0.25), 
                color=(0.8, 0.4, 0, 0.5), color_deviation=(0, 0, 0, 0), v_color=(-0.5, -0.5, 0, -0.25), 
                #center=(0.5, 0.8), center_deviation=(0.02, 0.02),
                center=(0.5, 0.8), center_deviation=(0, 0),
                velocity=(0, -0.3), velocity_deviation=(0.2, 0.1), 
                #velocity=(0, -0.1), velocity_deviation=(0.2, 0.3), 
                #velocity=(0, -0.5), velocity_deviation=(0.2, 0.2), 
                lifetime=2.0, initial_amount=100)
        self.add_node(particle)
        particle.set_alpha(0.8)
        particle.play(duration=1, loop=True)

        rect = DummyRect(self, {'width': '10%', 'height': '10%', 'top': '20%', 'left': '20%', 'aspect': 1.0})
        self.add_node(rect)
        def _rot(self, interval, phase):
            self.set_rotate(pi * 2 * phase, (0.8, 1,1))
        rect.add_action('rotation', _rot, duration=5.0, loop=True, update=True)

        self.texture = {}
        self.texture['bgimg'] = cairo.ImageSurface.create_from_png(self.bgimg)

    def on_update(self, cr):
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

