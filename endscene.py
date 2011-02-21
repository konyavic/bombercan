#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module contains the class EndScene only."""

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import *
from objects import *
from uicomponents import *
from effects import *
from motions import *

class EndScene(Node):
    def __init__(self, parent, style, key_down, key_up, on_game_reset):
        super(EndScene, self).__init__(parent, style)

        # Receive class audio, funtion key_up() and key_down() from class Game
        # to check player's input
        self.key_up = key_up
        self.key_down = key_down

        self.on_game_reset = on_game_reset

        list = Selections(
                parent=self,
                style={'height': '30%', 'top': '15%', 'left': '5%', 'right': '5%'},
                font='MS Gothic',
                labels=(
                    u'THANK YOU', 
                    u'FOR YOUR PLAYING!',
                    ),
                color=(1, 1, 1, 0.7),
                margin=(0, 0, 0, 0),
                cursor=None,
                )
        self.add_node(list)
        list = Selections(
                parent=self,
                style={'height': '30%', 'top': '60%', 'left': '10%', 'right': '10%'},
                font='MS Gothic',
                labels=(
                    u'<Press Space>',
                    u' ',
                    u'Program:',
                    u'李承益 (Victor Lee)',
                    u'Bombercan\'s Theme:',
                    u'沈威廷 (MWT)'
                    ),
                color=(1, 1, 1, 0.7),
                margin=(0, 0, 0, 0),
                cursor=None,
                center=False
                )
        self.add_node(list)

    def on_update(self, cr):
        cr.set_source_rgb(0, 0, 0)
        cr.paint()

    def on_tick(self, interval):
        # Back to main menu
        if self.key_up('space'):
            self.on_game_reset()
