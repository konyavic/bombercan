#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from random import random

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node
from objects import *
from effects import *
from uicomponents import *
from stagecontroller import *

# z-index table
layers = {
        'floor': -100,
        'object': -300
        }

class StageScene(Node):
    def create_map(self):
        self.map = MapContainer(
                parent=self,
                style={
                    'top': self.margin[0],
                    'right': self.margin[1],
                    'bottom': self.margin[2],
                    'left': self.margin[3],
                    'aspect': 1.0,
                    'align': 'center',
                    'vertical-align': 'center' },
                opt={
                    '$map size': self.map_size }
                )
        self.add_node(self.map)

    def create_floor(self):
        def _on_enter(obj):
            return lambda: obj.play_blink(duration=1, loop=True)
        def _on_leave(obj):
            return lambda: obj.play_fadeout(duration=1)

        cell_size = self.map.get_cell_size()
        for x in xrange(0, self.map_size[0]):
            for y in xrange(0, self.map_size[1]):
                obj = Floor(
                        parent=self.map,
                        style={
                            'width': cell_size,
                            'height': cell_size,
                            'z-index': layers['floor'] }
                        )
                make_trackingfloor(self, obj, x, y, 
                        on_enter=_on_enter(obj),
                        on_leave=_on_leave(obj)
                        )
                self.map.add_node(obj, x, y)

    def create_player_at(self, x, y):
        cell_size = self.map.get_cell_size()
        obj = Can(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size * 2, 
                    'z-index': layers['object'] }
                )
        # player(blocking(obj))
        make_character(self, obj, 
                on_move=lambda dir: obj.play_moving(duration=0.2, loop=True),
                on_stop=lambda dir: obj.reset_animations()) # XXX
        make_breakable(self, obj, 
                on_die=lambda: self.game_reset())
        make_bomber(self, obj)
        self.map.add_node(obj, x, y, 0, -cell_size)
        return obj

    def create_enemy_at(self, x, y):
        def _dec_enemy_count():
            self.enemy_count -= 1

        cell_size = self.map.get_cell_size()
        obj = Bishi(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size, 
                    'z-index': layers['object'] }
                )
        # enemy(fatal(blocking(obj)))
        fatal(blocking(obj))
        make_character(self, obj, speed=3.0)
        make_breakable(self, obj,
                on_die=_dec_enemy_count)
        make_simpleai(self, obj)
        self.map.add_node(obj, x, y, 0, 0)
        return obj


    def create_enemies(self, count):
        self.enemy_count = count

        while count > 0:
            x = int(random() * self.map_size[0])
            y = int(random() * self.map_size[1])
            if self.is_filled(x, y):
                continue

            self.create_enemy_at(x, y)
            count -= 1

    def create_hard_block_at(self, x, y):
        cell_size = self.map.get_cell_size()
        obj = HardBlock(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size * 2, 
                    'z-index': layers['object'] }
                )
        fireblocking(blocking(obj))
        self.map.add_node(obj, x, y, 0, -cell_size)

    def create_hard_blocks(self):
        for x in xrange(1, self.map_size[0], 2):
            for y in xrange(1, self.map_size[1], 2):
                self.create_hard_block_at(x, y)

    def create_soft_block_at(self, x, y):
        cell_size = self.map.get_cell_size()
        obj = SoftBlock(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size * 2, 
                    'z-index': layers['object'] }
                )
        blocking(obj)
        make_breakable(self, obj)
        self.map.add_node(obj, x, y, 0, -cell_size)

    def create_soft_blocks(self, count):
        while count > 0:
            x = int(random() * self.map_size[0])
            y = int(random() * self.map_size[1])
            if self.is_filled(x, y):
                continue

            self.create_soft_block_at(x, y)
            count -= 1

    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        self.map_size = opt['$map size']
        self.margin = opt['$margin']
        self.bgimg = opt['$bgimg']
        self.key_up = opt['@key up']
        self.key_down = opt['@key down']
        self.game_reset = opt['@game reset']

        self.create_map()
        self.create_floor()
        self.player = self.create_player_at(0, 0)
        self.create_hard_blocks()        
        self.create_enemies(10)
        self.create_soft_blocks(25)        

        self.__mark_destroy = set()

        self.box = MessageBox(
                parent=self, 
                style={
                    'width': '80%',
                    'height': '33%',
                    'align': 'center',
                    'vertical-align': 'center',
                    'z-index': -500 },
                opt=None)
        self.add_node(self.box)

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
        if self.key_up('Left'):
            self.player.move('left')
        elif self.key_up('Up'):
            self.player.move('up')
        elif self.key_up('Right'):
            self.player.move('right')
        elif self.key_up('Down'):
            self.player.move('down')
        elif self.key_down('Left'):
            self.player.stop('left')
        elif self.key_down('Up'):
            self.player.stop('up')
        elif self.key_down('Right'):
            self.player.stop('right')
        elif self.key_down('Down'):
            self.player.stop('down')

        if self.key_up('space'):
            self.box.toggle()

        if self.key_up('z'):
            self.player.bomb()

        # actual destroy of marked nodes
        for n in self.__mark_destroy:
            n.die()

        self.__mark_destroy = set()

        # lose condition
        cell = self.map.get_cell(self.player)
        for n in self.map.get_cell_nodes(*cell):
            if is_fatal(n):
                self.game_reset()

        # win condition
        if self.enemy_count == 0:
                self.game_reset()

    def is_filled(self, x, y):
        if (0 <= x and x < self.map_size[0]
                and 0 <= y and y < self.map_size[1]):
            return (len(self.map.get_cell_nodes(x, y)) > 1)
        else:
            return False

    def is_blocked(self, node, x, y):
        if (0 <= x and x < self.map_size[0]
                and 0 <= y and y < self.map_size[1]):
            for n in self.map.get_cell_nodes(x, y):
                if is_player(node) and is_fatal(n):
                    return False
                elif is_blocking(n):
                    return True

            return False

        else:
            return False

    def move_object(self, node, dx, dy):
        # XXX: refactor
        map = self.map
        cell = map.get_cell(node)
        pos = map.get_node_pos(node)
        cell_size = map.get_cell_size()
        is_blocked = self.is_blocked

        if dx > 0 and is_blocked(node, cell[0] + 1, cell[1]):
            dx = min(map.get_cell_pos(*cell)[0] - pos[0], dx)
        elif dx < 0 and is_blocked(node, cell[0] - 1, cell[1]):
            dx = max(map.get_cell_pos(*cell)[0] - pos[0], dx)
        elif dx == 0:
            dx = map.get_cell_pos(*cell)[0] - pos[0]
        
        if dy > 0 and is_blocked(node, cell[0], cell[1] + 1):
            dy = min(map.get_cell_pos(*cell)[1] - pos[1], dy)
        elif dy < 0 and is_blocked(node, cell[0], cell[1] - 1):
            dy = max(map.get_cell_pos(*cell)[1] - pos[1], dy)
        elif dy == 0:
            dy = map.get_cell_pos(*cell)[1] - pos[1]

        map.move_pos(node, dx, dy)

    def place_bomb(self, x, y, delay, power):
        cell_size = self.map.get_cell_size()
        bomb = Bomb(
                parent=self.map,
                style={
                    'width': cell_size,
                    'height': cell_size,
                    'z-index': layers['object'] }
                )
        make_breakable(self, bomb, 
                on_die=lambda: self.explode(bomb, x, y, power))
        make_bomb(bomb, delay, power,
                on_explode=lambda: self.explode(bomb, x, y, power))
        blocking(bomb)
        bomb.play_counting(duration=1.5, loop=True)
        self.map.add_node(bomb, x, y)

    def explode(self, node, x, y, power):
        # XXX: refactor
        cell_size = self.map.get_cell_size()

        def search_and_break(nodes):
            for n in nodes:
                if is_fireblocking(n):
                    return (True, -1)
                elif is_bomb(n):
                    n.die()
                elif is_character(n):
                    n.die()
                elif is_breakable(n):
                    self.__mark_destroy.add(n)
                    return (True, 0)

            return (False, 0)

        tmp_x, end = x, (False, 0)
        for tmp_x in xrange(x, max(x - power - 1, -1), -1):
            nodes = self.map.get_cell_nodes(tmp_x, y)
            end = search_and_break(nodes)
            if end[0]: break

        left = x - tmp_x + end[1]

        tmp_x, end = x, (False, 0)
        for tmp_x in xrange(x, min(x + power + 1, self.map_size[0])):
            nodes = self.map.get_cell_nodes(tmp_x, y)
            end = search_and_break(nodes)
            if end[0]: break

        right = tmp_x - x + end[1]

        tmp_y, end = y, (False, 0)
        for tmp_y in xrange(y, max(y - power - 1, -1), -1):
            nodes = self.map.get_cell_nodes(x, tmp_y)
            end = search_and_break(nodes)
            if end[0]: break

        up = y - tmp_y + end[1]

        tmp_y, end = y, (False, 0)
        for tmp_y in xrange(y, min(y + power + 1, self.map_size[1])):
            nodes = self.map.get_cell_nodes(x, tmp_y)
            end = search_and_break(nodes)
            if end[0]: break

        down = tmp_y - y + end[1]
                
        # show effect
        width = (left + right + 1) * cell_size
        height = (up + down + 1) * cell_size
        explosion = ExplosionEffect(
                parent=self.map,
                style={
                    'width': width,
                    'height': height,
                    'z-index': layers['object'] },
                opt={
                    '$arms': (up, right, down, left),
                    '?cell size': lambda: self.map.get_cell_size(),
                    '@destroy': lambda: self.map.remove_node(explosion) }
                )
        self.map.add_node(explosion, x, y, -left * cell_size, -up * cell_size)

        particle = ParticleEffect(self, 
                {'width': cell_size, 'height': cell_size * up, 'z-index': layers['object']},
                size=(cell_size * 0.5), size_deviation=(0.1 * cell_size), 
                v_size=(-0.2 * cell_size), v_size_deviation=(0.05 * cell_size),
                color=(1.0, 0.8, 0.0, 0.2), color_deviation=(0.5, 0.5, 0.0, -0.05), v_color=(0, -0.2, 0, 0),
                center=(0.5, 0.8), center_deviation=(0.2, 0.1),
                velocity=(0, -1.0), velocity_deviation=(0.0, 0.2), lifetime=1.0)
        self.map.add_node(particle, x, y, 0, -up * cell_size)
        particle.play(duration=3, cleanup=lambda: self.map.remove_node(particle))
