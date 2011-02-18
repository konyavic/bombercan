#!/usr/bin/python
# -*- coding: utf-8 -*-

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

# The z-index table
layers = {
        'floor': -100,
        'object': -300
        }

# Fire will exist for # seconds
FIRE_LASTING=1.5

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
                    'vertical-align': 'center' 
                    },
                map_size=self.map_size
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
        player(obj)
        make_character(self, obj, 
                on_move=lambda dir: obj.play_moving(duration=0.2, loop=True),
                on_stop=lambda dir: obj.reset_animations()) # XXX
        make_breakable(self, obj, 
                on_die=lambda: self.game_reset())
        make_bomber(self, obj)
        self.map.add_node(obj, x, y, 0, -cell_size)
        return obj

    def create_enemy_at(self, x, y):
        cell_size = self.map.get_cell_size()
        obj = Bishi(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size, 
                    'z-index': layers['object'] }
                )
        enemy(obj)
        make_character(self, obj, speed=3.0, 
                on_move=lambda dir: obj.rotate(duration=2, loop=True),
                on_stop=lambda dir: obj.reset_animations())
        make_breakable(self, obj,
                on_die=lambda: self.enemies.remove(obj))
        make_simpleai(self, obj)
        self.map.add_node(obj, x, y, 0, 0)
        return obj


    def create_enemies(self, count):
        self.enemies = []

        while count > 0:
            x = int(random() * self.map_size[0])
            y = int(random() * self.map_size[1])
            if self.is_filled(x, y):
                continue

            enemy = self.create_enemy_at(x, y)
            self.enemies.append(enemy)
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
        fireblocking(block(obj))
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
        block(obj)
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

    def __init__(self, parent, style, 
            map_size, margin, key_up, key_down, on_game_reset):

        super(StageScene, self).__init__(parent, style)
        self.map_size = map_size
        self.margin = margin
        self.key_up = key_up
        self.key_down = key_down
        self.game_reset = on_game_reset

        self.create_map()
        self.create_floor()
        self.player = self.create_player_at(0, 0)
        self.create_hard_blocks()        
        self.create_enemies(10)
        self.create_soft_blocks(25)        

        self._mark_destroy = set()

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
        self.texture['bgimg'] = cairo.ImageSurface.create_from_png('stage_bg.png')

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
        if self.key_up('Left'): self.player.move('left')
        if self.key_up('Up'): self.player.move('up')
        if self.key_up('Right'): self.player.move('right')
        if self.key_up('Down'): self.player.move('down')

        if self.key_down('Left'): self.player.stop('left')
        if self.key_down('Up'): self.player.stop('up')
        if self.key_down('Right'): self.player.stop('right')
        if self.key_down('Down'): self.player.stop('down')

        if self.key_up('space'): self.box.toggle()

        if self.key_up('z'): self.player.bomb()

        # Real destroy of marked nodes
        for n in self._mark_destroy:
            n.die()

        self._mark_destroy = set()

        # Check the losing condition
        cell = self.map.get_cell(self.player)
        for n in self.map.get_cell_nodes(*cell):
            if is_enemy(n):
                self.game_reset()
            elif is_fire(n):
                self.game_reset()

        # Check enemies
        for e in self.enemies:
            cell = self.map.get_cell(e)
            for n in self.map.get_cell_nodes(*cell):
                if is_fire(n):
                    e.die()
                    break

        # Check the winning condition
        if len(self.enemies) == 0:
            self.game_reset()

    def is_filled(self, x, y):
        if not (0 <= x and x < self.map_size[0]
                and 0 <= y and y < self.map_size[1]):
            return False

        # Is there something else than Floor?
        return (len(self.map.get_cell_nodes(x, y)) > 1)

    def is_blocked(self, node, x, y):
        """Check whether the target cell is blocked,
        according to the character who is moving.
        """
        # Out of the map
        if not (0 <= x and x < self.map_size[0]
                and 0 <= y and y < self.map_size[1]):
            return True

        # Check individual nodes in the cell
        for target in self.map.get_cell_nodes(x, y):
            if is_block(target):
                return True
            elif is_player(node) and is_player(target):
                return True
            elif is_enemy(node) and is_enemy(target):
                return True

        return False

    def move_object(self, node, dx, dy):
        """Check the target cell whether it is blocked or not,
        and move the object in the map.
        Some adjustion is applied to make the turning smoother.
        """
        if dx == 0 and dy == 0:
            return

        map = self.map
        cell = map.get_cell(node)
        pos = map.get_node_pos(node)
        current_cell_pos = map.get_cell_pos(*cell)
        cell_size = map.get_cell_size()
        is_blocked = self.is_blocked
        current_cell_delta_x = current_cell_pos[0] - pos[0]
        current_cell_delta_y = current_cell_pos[1] - pos[1]
        blocked_x = False
        blocked_y = False

        # Detect and handle collision
        if dx > 0 and is_blocked(node, cell[0] + 1, cell[1]):
            dx = min(current_cell_delta_x, dx)
            blocked_x = True
        elif dx < 0 and is_blocked(node, cell[0] - 1, cell[1]):
            dx = max(current_cell_delta_x, dx)
            blocked_x = True
        
        if dy > 0 and is_blocked(node, cell[0], cell[1] + 1):
            dy = min(current_cell_delta_y, dy)
            blocked_y = True
        elif dy < 0 and is_blocked(node, cell[0], cell[1] - 1):
            dy = max(current_cell_delta_y, dy)
            blocked_y = True

        # Smooth if needed
        if dx == 0 and not blocked_y:
            dx = current_cell_delta_x

        if dy == 0 and not blocked_x:
            dy = current_cell_delta_y

        map.move_pos(node, dx, dy)

    def put_bomb(self, x, y, delay, power):
        cell_size = self.map.get_cell_size()
        bomb = Bomb(
                parent=self.map,
                style={
                    'width': cell_size,
                    'height': cell_size,
                    'z-index': layers['object'] }
                )
        block(bomb)
        make_breakable(self, bomb, 
                on_die=lambda: self.explode(bomb, x, y, power))
        make_bomb(bomb, delay, power,
                on_explode=lambda: bomb.die())
        bomb.count()
        self.map.add_node(bomb, x, y)

    def explode(self, node, x, y, power):
        """Do all the works when a bomb explode.

        1) Calculate the path of fire
        2) Destroy things on the path
        3) Put 'fire object' to kill characters who entered the path later
        4) Show the effect

        """
        cell_size = self.map.get_cell_size()

        # Step 1-3

        def _search_and_break(nodes):
            def _shake(self, interval, phase):
                a = (pi / 8) * (1.0 - phase)
                self.set_rotate(a * sin(phase * 8 * 2 * pi))

            for n in nodes:
                n.add_action('shake', _shake, duration=2, update=True)
                if is_fireblocking(n):
                    return (True, -1)
                elif is_bomb(n):
                    # Method die() first removes the node from the map, 
                    # so it won't be an endless recursion.
                    # XXX: the original bomb enters twice?
                    n.die()
                elif is_character(n):
                    n.die()
                elif is_breakable(n):
                    self._mark_destroy.add(n)
                    return (True, 0)

            return (False, 0)

        def _put_fire(x, y):
            """Put an invisible fire object to target cell.
            This fire object may destroy characters coming in.
            """
            _fire = Node(self.map, {'width': 1, 'height': 1})
            fire(_fire)
            self.map.add_node(_fire, x, y)
            def _die_latter(node, interval, phase):
                pass

            _fire.add_action('die', _die_latter, delay=FIRE_LASTING, 
                    cleanup=lambda: self.map.remove_node(_fire))

        tmp_x, adjust = x, 0
        for tmp_x in xrange(x, max(x - power - 1, -1), -1):
            nodes = self.map.get_cell_nodes(tmp_x, y)
            stopped, adjust = _search_and_break(nodes)
            _put_fire(tmp_x, y)
            if stopped: 
                break

        fire_left = x - tmp_x + adjust

        tmp_x, adjust = x, 0
        for tmp_x in xrange(x, min(x + power + 1, self.map_size[0])):
            nodes = self.map.get_cell_nodes(tmp_x, y)
            stopped, adjust = _search_and_break(nodes)
            _put_fire(tmp_x, y)
            if stopped: 
                break

        fire_right = tmp_x - x + adjust

        tmp_y, adjust = y, 0
        for tmp_y in xrange(y, max(y - power - 1, -1), -1):
            nodes = self.map.get_cell_nodes(x, tmp_y)
            stopped, adjust = _search_and_break(nodes)
            _put_fire(x, tmp_y)
            if stopped: 
                break

        fire_up = y - tmp_y + adjust

        tmp_y, adjust = y, 0
        for tmp_y in xrange(y, min(y + power + 1, self.map_size[1])):
            nodes = self.map.get_cell_nodes(x, tmp_y)
            stopped, adjust = _search_and_break(nodes)
            _put_fire(x, tmp_y)
            if stopped: 
                break

        fire_down = tmp_y - y + adjust
                
        # Step 4

        width = (fire_left + fire_right + 1) * cell_size
        height = (fire_up + fire_down + 1) * cell_size
        explosion = ExplosionEffect(
                parent=self.map,
                style={
                    'width': width,
                    'height': height,
                    'z-index': layers['object'] },
                fire=(fire_up, fire_right, fire_down, fire_left),
                get_cell_size=self.map.get_cell_size,
                on_die=lambda: self.map.remove_node(explosion)
                )
        self.map.add_node(explosion, x, y, -fire_left * cell_size, -fire_up * cell_size)
        def _shake(self, interval, phase):
            a = (pi / 8) * (1.0 - phase)
            self.set_rotate(a * sin(phase * 8 * 2 * pi))
        explosion.add_action('shake', _shake, duration=2, update=True)
