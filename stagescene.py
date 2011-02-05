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
from containers import *
from stagecontroller import *

# z-index table
layers = {
        'floor': -100,
        'object': -300
        }

class StageScene(Node):
    def __create_map(self):
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

    def __create_floor(self):
        cell_size = self.map.get_cell_size()

        for x in xrange(0, self.map_size[0]):
            for y in xrange(0, self.map_size[1]):
                def should_light(x, y):
                    return lambda node: (x, y) == self.map.get_cell(self.player)

                floor = Floor(
                        parent=self.map,
                        style={
                            'width': cell_size,
                            'height': cell_size,
                            'z-index': layers['floor'] },
                        opt={
                            '?should light': should_light(x, y) }
                        )
                self.map.add_node(floor, x, y)

    def create_player(self, x, y):
        cell_size = self.map.get_cell_size()
        obj = Can(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size * 2, 
                    'z-index': layers['object'] }
                )
        character(self, obj, 
                on_move=lambda dir: obj.move_animation(dir),
                on_stop=lambda dir: obj.remove_animation(dir))
        bombmaker(self, obj)
        self.map.add_node(obj, x, y, 0, -cell_size)
        return obj

    def create_enemy(self, x, y):
        cell_size = self.map.get_cell_size()
        obj = Bishi(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size, 
                    'z-index': layers['object'] }
                )
        character(self, obj, speed=1.0)
        simpleai(self, obj)
        self.map.add_node(obj, x, y, 0, 0)
        return obj

    def create_enemies(self, count):
        self.enemies = []

        while count > 0:
            x = int(random() * self.map_size[0])
            y = int(random() * self.map_size[1])
            if self.is_filled(x, y):
                continue

            enemy = self.create_enemy(x, y)
            self.enemies.append(enemy)
            count -= 1

    def __create_hard_blocks(self):
        cell_size = self.map.get_cell_size()

        for x in xrange(1, self.map_size[0], 2):
            for y in xrange(1, self.map_size[1], 2):
                block = blocking(HardBlock(
                    parent=self.map,
                    style={
                        'width': cell_size, 
                        'height': cell_size * 2, 
                        'z-index': layers['object'] }
                    ))
                self.map.add_node(block, x, y, 0, -cell_size)

    def __create_soft_blocks(self, count):
        cell_size = self.map.get_cell_size()

        while count > 0:
            x = int(random() * self.map_size[0])
            y = int(random() * self.map_size[1])
            if self.is_filled(x, y):
                continue

            block = blocking(SoftBlock(
                    parent=self.map,
                    style={
                        'width': cell_size, 
                        'height': cell_size * 2, 
                        'z-index': layers['object'] }
                    ))
            self.map.add_node(block, x, y, 0, -cell_size)
            count -= 1

    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        self.map_size = opt['$map size']
        self.margin = opt['$margin']
        self.bgimg = opt['$bgimg']
        self.key_up = opt['@key up']
        self.key_down = opt['@key down']
        self.game_reset = opt['@game reset']

        self.__create_map()
        self.__create_floor()
        self.player = self.create_player(0, 0)
        self.__create_hard_blocks()        
        self.create_enemies(10)
        self.__create_soft_blocks(25)        

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
            self.player.stop()
            self.player.move('left')
        elif self.key_up('Up'):
            self.player.stop()
            self.player.move('up')
        elif self.key_up('Right'):
            self.player.stop()
            self.player.move('right')
        elif self.key_up('Down'):
            self.player.stop()
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
            n.destroy()
            self.map.remove_node(n)

        self.__mark_destroy = set()

        # lose condition
        cell = self.map.get_cell(self.player)
        for e in self.enemies:
            if cell == self.map.get_cell(e):
                self.game_reset()

        # win condition
        if len(self.enemies) == 0:
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
                if is_blocking(n):
                    return True

            return False

        else:
            return False

    def move_object(self, node, dx, dy):
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
        bomb = blocking(Bomb(
                parent=self.map,
                style={
                    'width': cell_size,
                    'height': cell_size,
                    'z-index': layers['object'] },
                opt={
                    '$count': delay,
                    '$power': power,
                    '@explode': lambda node: self.explode(node, x, y, power) } 
                ))
        self.map.add_node(bomb, x, y)
        bomb.start_counting()

    def explode(self, node, x, y, power):
        self.__mark_destroy.add(node)
        cell_size = self.map.get_cell_size()

        def search_and_break(nodes):
            for n in nodes:
                if isinstance(n, Block) and n.is_breakable:
                    self.__mark_destroy.add(n)
                    return (True, 0)
                elif isinstance(n, Block) and not n.is_breakable:
                    return (True, -1)
                elif isinstance(n, Bomb) and not (n in self.__mark_destroy):
                    n.explode()
                elif isinstance(n, Enemy):
                    self.__mark_destroy.add(n)
                    if n in self.enemies:
                        self.enemies.remove(n)
                elif isinstance(n, Player):
                    # XXX: game over
                    self.game_reset()

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
                    '@destroy': lambda node: self.map.remove_node(node) }
                )
        self.map.add_node(explosion, x, y, -left * cell_size, -up * cell_size)
