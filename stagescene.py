#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from random import random

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node
from objects import Bomb
from objects import Block
from objects import HardBlock
from objects import SoftBlock
from objects import Player
from objects import Floor
from objects import MessageBox
from effects import ExplosionEffect

# z-index table
layers = {
        'floor': -100,
        'object': -300
        }

class MapContainer(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)

        # input attributes
        self.map_size = opt['$map size']

        # private attributes
        self.__map = [[ [] for y in xrange(0, self.map_size[1]) ] for x in xrange(0, self.map_size[0]) ]
        self.__delta = {}
        self.__cell = {}
        self.__orig_size = {}
        self.__orig_delta = {}
        self.__orig_z_index = {}

        self.__update_cell_size()
        self.__orig_cell_size = self.__cell_size
    
    def __update_cell_size(self):
        self.__cell_size = min(self.width / self.map_size[0], self.height / self.map_size[1])
        self.__padding = (
                (self.width - self.__cell_size * self.map_size[0]) / 2,
                (self.height - self.__cell_size * self.map_size[1]) / 2
                )

    def __update_pos(self, node, x, y, width, height, z_index):
        dx, dy = self.__delta[node]
        style = {
                'left': x + dx,
                'top': y + dy,
                'width': width,
                'height': height,
                'z-index': z_index
                }
        node.set_style(style)

    def __restrict_pos(self, x, y):
        if x < 0:
            x = 0
        elif x >= self.map_size[0]:
            x = self.map_size[0] - 1

        if y < 0:
            y = 0
        elif y >= self.map_size[1]:
            y = self.map_size[1] - 1

        return (x, y)

    def __get_z_index_delta(self, y):
        return -y

    def on_resize(self):
        Node.on_resize(self)
        self.__update_cell_size()
        ratio = float(self.__cell_size) / self.__orig_cell_size

        for x, col in enumerate(self.__map):
            for y, cell in enumerate(col):
                pos = self.get_cell_pos(x, y)
                for node in cell:
                    # XXX: node.x node.y is not handled properly
                    width, height = self.__orig_size[node]
                    new_width = width * ratio
                    new_height = height * ratio
                    dx, dy = self.__orig_delta[node]
                    dx = dx * ratio
                    dy = dy * ratio
                    self.__delta[node] = (dx, dy)
                    self.__update_pos(node, pos[0], pos[1], new_width, new_height, node.z_index)
    
    def get_cell_size(self):
        return self.__cell_size

    def add_node(self, node, x, y, dx=0, dy=0):
        Node.add_node(self, node)
        self.__map[x][y].append(node)
        self.__delta[node] = (dx, dy)
        self.__orig_delta[node] = self.__delta[node]
        self.__cell[node] = (x, y)
        self.__orig_size[node] = (node.width, node.height)
        self.__orig_z_index[node] = node.z_index

        pos = self.get_cell_pos(x, y)
        self.__update_pos(node, pos[0], pos[1], node.width, node.height, node.z_index + self.__get_z_index_delta(y))

    def remove_node(self, node):
        Node.remove_node(self, node)
        cell = self.get_cell(node)
        self.__map[cell[0]][cell[1]].remove(node)
        del self.__delta[node]
        del self.__orig_delta[node]
        del self.__cell[node]
        del self.__orig_size[node]
        del self.__orig_z_index[node]

    def get_cell(self, node):
        return self.__cell[node]

    def get_cell_nodes(self, x, y):
        return self.__map[x][y]

    def move_to(self, node, x, y):
        cell = self.get_cell(node)
        self.__map[cell[0]][cell[1]].remove(node)
        self.__map[x][y].append(node)
        self.__cell[node] = (x, y)

        pos = self.get_cell_pos(x, y)
        self.__update_pos(node, pos[0], pos[1], node.width, node.height, self.__orig_z_index[node] + self.__get_z_index_delta(y))

    def move_pos(self, node, delta_x, delta_y):
        dx, dy = self.__delta[node]
        new_x = node.x + delta_x - dx
        new_y = node.y + delta_y - dy

        top_left = self.get_cell_pos(0, 0)
        bottom_right = self.get_cell_pos(self.map_size[0] - 1, self.map_size[1] - 1)
        if new_x < top_left[0]:
            new_x = top_left[0]
        elif new_x > bottom_right[0]:
            new_x = bottom_right[0]
        elif new_y < top_left[1]:
            new_y = top_left[1]
        elif new_y > bottom_right[1]:
            new_y = bottom_right[1]

        half_cell = self.__cell_size / 2
        new_cell = (
                int((new_x - self.__padding[0] + half_cell) / self.__cell_size),
                int((new_y - self.__padding[1] + half_cell) / self.__cell_size)
                )
        new_cell = self.__restrict_pos(*new_cell)
        old_cell = self.get_cell(node)

        self.__map[old_cell[0]][old_cell[1]].remove(node)
        self.__map[new_cell[0]][new_cell[1]].append(node)
        self.__cell[node] = new_cell
        self.__update_pos(node, new_x, new_y, node.width, node.height, 
                self.__orig_z_index[node] + self.__get_z_index_delta(new_cell[1]))

    def get_cell_pos(self, x, y):
        return (
                self.__padding[0] + x * self.__cell_size, 
                self.__padding[1] + y * self.__cell_size
                )

    def get_node_pos(self, node):
        delta = self.__delta[node]
        return (node.x - delta[0], node.y - delta[1])

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

    def __create_player(self):
        cell_size = self.map.get_cell_size()

        self.player = Player(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size * 2, 
                    'z-index': layers['object'] },
                opt={
                    '$speed': 4.0,
                    '@move': self.move_object,
                    '@bomb': (lambda node, count, power:
                        self.place_bomb(*self.map.get_cell(node), count=count, power=power)),
                    '?cell size': lambda: self.map.get_cell_size() }
                )
        self.map.add_node(self.player, 0, 0, 0, -cell_size)

    def __create_hard_blocks(self):
        cell_size = self.map.get_cell_size()

        for x in xrange(1, self.map_size[0], 2):
            for y in xrange(1, self.map_size[1], 2):
                block = HardBlock(
                    parent=self.map,
                    style={
                        'width': cell_size, 
                        'height': cell_size * 2, 
                        'z-index': layers['object'] },
                    opt={
                        '$breakable': False }
                    )
                self.map.add_node(block, x, y, 0, -cell_size)

    def __create_soft_blocks(self, count):
        cell_size = self.map.get_cell_size()

        while count > 0:
            x = int(random() * self.map_size[0])
            y = int(random() * self.map_size[1])
            if self.is_blocked(x, y):
                continue

            block = SoftBlock(
                    parent=self.map,
                    style={
                        'width': cell_size, 
                        'height': cell_size * 2, 
                        'z-index': layers['object'] },
                    opt={
                        '$breakable': True,
                        '@destroy': lambda node: self.map.remove_node(node) }
                    )
            self.map.add_node(block, x, y, 0, -cell_size)
            count -= 1

    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        self.map_size = opt['$map size']
        self.margin = opt['$margin']
        self.bgimg = opt['$bgimg']
        self.key_up = opt['@key up']
        self.key_down = opt['@key down']

        self.__create_map()
        self.__create_floor()
        self.__create_player()
        self.__create_hard_blocks()        
        self.__create_soft_blocks(25)        

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

    def is_blocked(self, x, y):
        if (0 <= x and x < self.map_size[0]
                and 0 <= y and y < self.map_size[1]):
            return (len(self.map.get_cell_nodes(x, y)) > 1)
        else:
            return False

    def move_object(self, node, dx, dy):
        map = self.map
        cell = map.get_cell(node)
        pos = map.get_node_pos(node)
        cell_size = map.get_cell_size()

        if dx > 0 and self.is_blocked(cell[0] + 1, cell[1]):
            dx = min(map.get_cell_pos(*cell)[0] - pos[0], dx)
        elif dx < 0 and self.is_blocked(cell[0] - 1, cell[1]):
            dx = max(map.get_cell_pos(*cell)[0] - pos[0], dx)
        elif dx == 0:
            dx = map.get_cell_pos(*cell)[0] - pos[0]
        
        if dy > 0 and self.is_blocked(cell[0], cell[1] + 1):
            dy = min(map.get_cell_pos(*cell)[1] - pos[1], dy)
        elif dy < 0 and self.is_blocked(cell[0], cell[1] - 1):
            dy = max(map.get_cell_pos(*cell)[1] - pos[1], dy)
        elif dy == 0:
            dy = map.get_cell_pos(*cell)[1] - pos[1]

        map.move_pos(node, dx, dy)

    def place_bomb(self, x, y, count, power):
        cell_size = self.map.get_cell_size()
        bomb = Bomb(
                parent=self.map,
                style={
                    'width': cell_size,
                    'height': cell_size,
                    'z-index': layers['object'] },
                opt={
                    '$count': count,
                    '$power': power,
                    '@destroy': lambda node: self.map.remove_node(node),
                    '@explode': lambda node: self.explode(x, y, power) } 
                )
        self.map.add_node(bomb, x, y)
        bomb.start_counting()

    def explode(self, x, y, power):
        cell_size = self.map.get_cell_size()

        # XXX
        def search_and_break(nodes):
            for n in nodes:
                if isinstance(n, Block) and n.is_breakable:
                    n.destroy()
                    return (True, 0)
                elif isinstance(n, Block) and not n.is_breakable:
                    return (True, -1)

            return (False, 0)

        tmp_x, end = x, (False, 0)
        for tmp_x in xrange(x, max(x - power - 1, 0), -1):
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
        for tmp_y in xrange(y, max(y - power - 1, 0), -1):
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
