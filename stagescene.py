#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from random import random
from new import instancemethod

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node
from objects import Bomb
from objects import HardBlock
from objects import SoftBlock
from objects import Player
from objects import Enemy
from objects import Floor
from objects import MessageBox
from effects import ExplosionEffect
from containers import MapContainer

# z-index table
layers = {
        'floor': -100,
        'object': -300
        }

BLOCKING    = 1 << 0
FATAL       = 1 << 1
BREAKABLE   = 1 << 2
CHARACTER   = 1 << 3

def stageobj(flag, obj):
    try:
        obj.stageobj_flags |= flag
    except AttributeError:
        obj.stageobj_flags = flag

    return obj

def stageobj_has_flag(flag, obj):
    try:
        return obj.stageobj_flags
    except AttributeError:
        obj.stageobj_flags = 0
        return False

def blocking(obj):
    return stageobj(BLOCKING, obj)

def is_blocking(obj):
    return stageobj_has_flag(BLOCKING, obj)

def fatal(obj):
    return stageobj(FATAL, obj)

def is_fatal(obj):
    return stageobj_has_flag(FATAL, obj)

def breakable(obj):
    return stageobj(BREAKABLE, obj)

def is_breakable(obj):
    return stageobj_has_flag(BREAKABLE, obj)

def character(obj):
    return stageobj(CHARACTER, obj)

def is_character(obj):
    return stageobj_has_flag(CHARACTER, obj)

def make_player(stage, node, 
        speed=4.0, bomb_delay=5, bomb_power=2, bomb_count=1,
        on_move=None, on_stop=None, on_die=None, on_bomb=None):

    stageobj(BREAKABLE | BLOCKING | CHARACTER, node)
    node.speed = speed
    node.bomb_delay = bomb_delay
    node.bomb_power = bomb_power
    node.bomb_count = bomb_count

    def move(self, dir):
        def move_action(self, interval):
            delta = interval * self.speed * stage.map.get_cell_size()
            if dir == 'up':
                stage.move_object(self, 0, -delta)
            elif dir == 'down':
                stage.move_object(self, 0, delta)
            elif dir == 'left':
                stage.move_object(self, -delta, 0)
            elif dir == 'right':
                stage.move_object(self, delta, 0)

        self.add_action(dir, move_action, loop=True, update=False)
        if on_move: on_move(dir)
    
    def stop(self, dir=None):
        if dir:
            self.remove_action(dir)
            if on_stop: on_stop(dir)
        else:
            self.remove_action('up')
            self.remove_action('down')
            self.remove_action('right')
            self.remove_action('left')
            if on_stop: 
                on_stop('up')
                on_stop('down')
                on_stop('right')
                on_stop('left')


    def die(self):
        if on_die: on_die()

    def bomb(self):
        stage.place_bomb(*stage.map.get_cell(self), 
                delay=self.bomb_delay, power=self.bomb_power)

        if on_bomb: on_bomb()

    node.move = instancemethod(move, node)
    node.stop = instancemethod(stop, node)
    node.die = instancemethod(die, node)
    node.bomb = instancemethod(bomb, node)

def make_enemy():
    pass

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
                    'z-index': layers['object'] }
                )
        make_player(self, self.player, 
                on_move=lambda dir: self.player.move_animation(dir),
                on_stop=lambda dir: self.player.remove_animation(dir))
        self.map.add_node(self.player, 0, 0, 0, -cell_size)

    def __create_enemies(self, count):
        cell_size = self.map.get_cell_size()
        self.enemies = []

        while count > 0:
            x = int(random() * self.map_size[0])
            y = int(random() * self.map_size[1])
            if self.is_filled(x, y):
                continue

            enemy = Enemy(
                    parent=self.map,
                    style={
                        'width': cell_size, 
                        'height': cell_size, 
                        'z-index': layers['object'] },
                    opt={
                        '$speed': 2.0,
                        '@move': self.move_object,
                        '?cell size': lambda: self.map.get_cell_size() }
                    )
            self.map.add_node(enemy, x, y, 0, 0)
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
        self.__create_player()
        self.__create_hard_blocks()        
        self.__create_enemies(10)
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
