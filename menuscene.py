#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module contains the class MenuScene only."""

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import *
from objects import *
from uicomponents import *
from effects import *
from motions import *

class MenuScene(Node):
    """The game scene that display the main menu from game start."""
    def __init__(self, parent, style, audio, key_down, key_up, on_game_start):
        """Create and put the components for the title, 
        the main menu, etc.
        
        """
        super(MenuScene, self).__init__(parent, style)

        # Receive class audio, funtion key_up() and key_down() from class Game
        # to check player's input
        self.audio = audio
        self.key_up = key_up
        self.key_down = key_down

        # Function on_game_start() is called if the player selected the menu
        self.on_game_start = on_game_start

        # The selection menu
        self.cursor = Bomb(parent=self, style={})
        self.sel = Selections(
                parent=self,
                style={
                    'left': '25%', 
                    'top': '50%', 
                    'width': '50%',
                    'height': '30%'
                    },
                font='MS Gothic',
                labels=(u'Story Mode', u'Free Game'),
                color=(1, 1, 1, 0.7),
                bgcolor=(0.3, 0.3, 0.7, 0.7),
                cursor=self.cursor
                )
        self.add_node(self.sel)
        self.cursor.count()

        # The title (a Label)
        title = Label(
                parent=self,
                style={
                    'top': '20%',
                    'left': '15%',
                    'right': '15%'
                    },
                text=u'ボンバー缶',
                font='MS Gothic bold',
                color=(1, 1, 0.3, 1),
                )
        self.add_node(title)

        # A smoke effect just for the demonstration of my particle system
        particle = ParticleEffect(self, 
                {
                    'width': '50%', 
                    'height': '50%', 
                    'align': 'center', 
                    'vertical-align': 'bottom'
                    },
                size=10, size_deviation=2, v_size=3,
                color=(0.8, 0.4, 0, 0.5), v_color=(-0.5, -0.5, 0, -0.25), 
                center=(0.5, 0.8),
                velocity=(0, -0.3), velocity_deviation=(0.2, 0.1),
                lifetime=2.0, initial_amount=100)
        self.add_node(particle)
        particle.add_action('action', particle.update_action, 
                duration=1, loop=True, update=True)

        # The background image
        self.texture = {}
        self.texture['bgimg'] = \
                cairo.ImageSurface.create_from_png('menu_bg.png')

    def on_update(self, cr):
        """Simply display the background image 
        (centered and touching the window from outside).
        
        Display of other GUI components are handled in each individual class.

        """
        scale_width = self.width / float(self.texture['bgimg'].get_width())
        scale_height = self.height / float(self.texture['bgimg'].get_height())
        if scale_width < scale_height:
            scale = scale_height
        else:
            scale = scale_width

        new_width = self.texture['bgimg'].get_width() * scale
        new_height = self.texture['bgimg'].get_height() * scale
        x = (self.width - new_width) / 2
        y = (self.height - new_height) / 2

        cr = cairo.Context(self.surface)
        cr.scale(scale, scale)
        cr.set_source_rgb(0, 0, 0)
        cr.paint()
        cr.set_source_surface(self.texture['bgimg'], x, y)
        cr.paint_with_alpha(0.7)

    def on_tick(self, interval):
        """In each tick, check player's input to move up / down in the menu 
        or select a menu item.
        
        """
        if self.key_up('Up'):
            self.sel.select_up()
            self.audio.play('select.wav')
        elif self.key_up('Down'):
            self.sel.select_down()
            self.audio.play('select.wav')

        # A menu item is selected
        if self.key_up('space'):
            if self.sel.selected == 0:
                self.on_game_start(0)
            elif self.sel.selected == 1:
                self.on_game_start(1)

