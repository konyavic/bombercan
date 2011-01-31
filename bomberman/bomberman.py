#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import time

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node
from pnode import Game

from objects import Bomb
from objects import HardBlock
from menuscene import MenuScene

# z-index
layers = {
        'bg': 100,
        'map': 50,
        'object': 10
        }

class Player(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        self.speed = opt['speed']
        self.do_move = opt['move']
        self.do_bomb = opt['bomb']
        self.get_cell_size = opt['get_cell_size']
        self.on_update()

    def __draw_feet(self, cr, x, y, inverse=1):
        width, height = self.width, self.height
        cr.move_to(x, y)
        cr.rel_line_to(0, height * 0.13)
        cr.rel_line_to(-(inverse * width * 0.06), 0)
        cr.rel_line_to(0, height * 0.03)
        cr.rel_line_to(inverse * width * 0.2, 0)
        cr.rel_line_to(0, -(height * 0.03))
        cr.rel_line_to(-(inverse* width * 0.06), 0)
        cr.rel_line_to(0, -(height * 0.13))
        cr.close_path()

        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

    def __draw_cylinder(self, cr, x, y, cylinder_height, color):
        width, height = self.width, self.height
        cr.move_to(x, y)
        cr.rel_curve_to(
                width * 0.2, height * 0.07, 
                width * 0.4, height * 0.07, 
                width * 0.6, 0 
                )
        cr.rel_line_to(0, -cylinder_height)
        cr.rel_curve_to(
                -(width * 0.2), -(height * 0.07), 
                -(width * 0.4), -(height * 0.07), 
                -(width * 0.6), 0 
                )
        cr.close_path()

        cr.set_source_rgb(*color)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1.5)
        cr.stroke()

        cr.move_to(x, y - cylinder_height)
        cr.rel_curve_to(
                width * 0.2, height * 0.07, 
                width * 0.4, height * 0.07, 
                width * 0.6, 0 
                )

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

    def __draw_eyes(self, cr):
        width, height = self.width, self.height
        cr.save()
        cr.scale(1, 0.5)
        cr.arc(
                width * 0.38, height * 0.9,
                width * 0.1,
                0, 2 * math.pi)
        cr.restore()

        cr.set_source_rgb(1, 1, 0)
        cr.fill_preserve()

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

        cr.save()
        cr.scale(1, 0.5)
        cr.arc(
                width * (1 - 0.38), height * 0.9,
                width * 0.1,
                0, 2 * math.pi)
        cr.restore()

        cr.set_source_rgb(1, 1, 0)
        cr.fill_preserve()

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

    def on_update(self):
        width, height = self.width, self.height

        cr = cairo.Context(self.surface)
        self.clear_context(cr)
        cr.save()
        cr.set_line_join(cairo.LINE_JOIN_BEVEL)
        # draw feets
        self.__draw_feet(cr, width * 0.3, height * 0.8)
        self.__draw_feet(cr, width * (1 - 0.3), height * 0.8, -1)
        # draw body
        self.__draw_cylinder(cr, width * 0.2, height * 0.8, height * 0.3, (0, 0, 0.7))
        # draw head
        self.__draw_cylinder(cr, width * 0.2, height * 0.5, height * 0.2, (0.7, 0.7, 0.7))
        # draw eyes
        self.__draw_eyes(cr)
        cr.restore()

    def move(self, dir):
        def move_action(self, interval):
            delta = interval * self.speed * self.get_cell_size()
            if dir == 'up':
                self.do_move(self, 0, -delta)
            elif dir == 'down':
                self.do_move(self, 0, delta)
            elif dir == 'left':
                self.do_move(self, -delta, 0)
            elif dir == 'right':
                self.do_move(self, delta, 0)

        def move_animation(self, phase):
            width, height = self.width, self.height
            delta = height * 0.05 * math.cos(phase * math.pi * 2)

            cr = cairo.Context(self.surface)
            self.clear_context(cr)
            cr.save()
            cr.set_line_join(cairo.LINE_JOIN_BEVEL)
            # draw feets
            self.__draw_feet(cr, width * 0.3, height * 0.8 + delta)
            self.__draw_feet(cr, width * (1 - 0.3), height * 0.8 - delta, -1)
            # draw body
            self.__draw_cylinder(cr, width * 0.2, height * 0.8, height * 0.3, (0, 0, 0.7))
            # draw head
            self.__draw_cylinder(cr, width * 0.2, height * 0.5, height * 0.2, (0.7, 0.7, 0.7))
            # draw eyes
            self.__draw_eyes(cr)
            cr.restore()

        self.add_action(dir, move_action, loop=True, update=False)
        self.add_animation(dir, move_animation, loop=True, delay=0, period=0.2)

    def stop(self, dir=None):
        if dir:
            self.remove_action(dir)
            self.remove_animation(dir)
        else:
            for dir in ['up', 'down', 'left', 'right']:
                self.remove_action(dir)
                self.remove_animation(dir)

    def bomb(self):
        self.do_bomb(self, 5, 3)

class Floor(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        
        self.should_light = opt['should_light']

        self.lighted = False
        self.on_update()

    def __draw_simple_pattern(self, color):
        cr = cairo.Context(self.surface)
        self.clear_context(cr)
        
        cr.set_line_width(2)
        cr.set_source_rgba(*color)
        cr.paint()

        cr.set_source_rgba(0.5, 0.5, 0.5, 0.7)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

    def on_update(self):
        self.color = (0.5, 0.5, 1, 0.7)
        self.__draw_simple_pattern(self.color)

    def on_tick(self, interval):
        if self.should_light(self) and not self.lighted:
            self.light(True)
            self.lighted = True
        elif not self.should_light(self) and self.lighted:
            self.light(False)
            self.lighted = False 

    def light(self, b):
        def blink_animation(self, phase):
            c = math.cos(phase*math.pi*2)
            self.color = (
                    0.75-0.25*c, 
                    0.25+0.25*c, 
                    0.5+0.5*c,
                    0.7)
            self.__draw_simple_pattern(self.color)

        def fade_out_animation(self, phase):
            tmp_color = (
                    self.color[0]+(0.5-self.color[0])*phase,
                    self.color[1]+(0.5-self.color[1])*phase,
                    self.color[2]+(1-self.color[2])*phase,
                    0.7
                    )
            self.__draw_simple_pattern(tmp_color)

        if b:
            self.add_animation('blink', blink_animation, delay=0, period=1, loop=True)
        else:
            self.remove_animation('blink')
            self.add_animation('fade out', fade_out_animation, delay=0, period=1, loop=False)

class MessageBox(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        self.showing = False
        self.on_update()

    def __draw_box(self, box_width, box_height, alpha):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        cr = cairo.Context(self.surface)
        cr.set_source_rgba(0, 0, 0, alpha)
        cr.rectangle(0, 0, box_width, box_height)
        cr.fill()

    def on_update(self):
        if self.showing:
            self.__draw_box(self.width, self.height, 0.5)
        else:
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)

    def show(self, b):
        def show_animation(self, phase):
            self.__draw_box(
                    self.width * 2 * min(0.5, phase), 
                    self.height * 2 * max(0.05, phase - 0.5), 
                    0.5 * phase)

        def hide_animation(self, phase):
            self.__draw_box(self.width*(1-phase), self.height*(1-phase), 0.5*(1-phase))

        self.showing = b
        if b:
            self.remove_animation('hide')
            self.add_animation('show', show_animation, delay=0, period=0.5, loop=False)
        else:
            self.remove_animation('show')
            self.add_animation('hide', hide_animation, delay=0, period=0.1, loop=False)

    def toggle(self):
        if self.showing:
            self.show(False)
        else:
            self.show(True)

class ExplodeEffect(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)

        def explode_animation(self, phase):
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
            cr = cairo.Context(self.surface)
            cr.set_source_rgba(1, 1, 0, 0.5)
            cr.paint()

        def explode_cleanup(self):
            self.parent.remove_node(self)

        self.add_animation('explode', explode_animation, loop=False, delay=0, period=1, cleanup=explode_cleanup)

class MapEffectLayer(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)

    def explode(self, x, y, power):
        cell = self.parent.map[x][y]
        self.add_node( ExplodeEffect(
            parent=self,
            style={
                'left': cell.x - power * self.parent.cell_size,
                'top': cell.y - power * self.parent.cell_size,
                'width': (power * 2 + 1) * self.parent.cell_size,
                'height': (power * 2 + 1) * self.parent.cell_size,
                },
            opt=None
            ))

class MapContainer(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)

        # input attributes
        self.map_size = opt['map_size']

        # private attributes
        self.__map = [[ [] for y in xrange(0, self.map_size[1]) ] for x in xrange(0, self.map_size[0]) ]
        self.__delta = {}
        self.__cell = {}
        self.__orig_size = {}
        self.__orig_delta = {}

        self.__update_cell_size()
        self.__orig_cell_size = self.__cell_size
    
    def __update_cell_size(self):
        self.__cell_size = min(self.width / self.map_size[0], self.height / self.map_size[1])
        self.__padding = (
                (self.width - self.__cell_size * self.map_size[0]) / 2,
                (self.height - self.__cell_size * self.map_size[1]) / 2
                )

    def __update_pos(self, node, x, y, width, height):
        dx, dy = self.__delta[node]
        style = {
                'left': x + dx,
                'top': y + dy,
                'width': width,
                'height': height,
                # XXX: preserve z-index, bad approach
                'z-index': node.z_index
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

    def __sort_children(self):
        self.children.sort(key=lambda node: self.__cell[node][1])

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
                    self.__update_pos(node, pos[0], pos[1], new_width, new_height)
    
    def get_cell_size(self):
        return self.__cell_size

    def add_node(self, node, x, y, dx=0, dy=0):
        Node.add_node(self, node)
        self.__map[x][y].append(node)
        self.__delta[node] = (dx, dy)
        self.__orig_delta[node] = self.__delta[node]
        self.__cell[node] = (x, y)
        self.__orig_size[node] = (node.width, node.height)
        self.__sort_children()

        pos = self.get_cell_pos(x, y)
        self.__update_pos(node, pos[0], pos[1], node.width, node.height)

    def remove_node(self, node):
        Node.remove_node(self, node)
        cell = self.get_cell(node)
        self.__map[cell[0]][cell[1]].remove(node)
        del self.__delta[node]
        del self.__orig_delta[node]
        del self.__cell[node]
        del self.__orig_size[node]

    def get_cell(self, node):
        return self.__cell[node]

    def get_cell_nodes(self, x, y):
        return self.__map[x][y]

    def move_to(self, node, x, y):
        cell = self.get_cell(node)
        self.__map[cell[0]][cell[1]].remove(node)
        self.__map[x][y].append(node)
        self.__cell[node] = (x, y)
        self.__sort_children()

        pos = self.get_cell_pos(x, y)
        self.__update_pos(node, pos[0], pos[1], node.width, node.height)

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
        self.__sort_children()
        self.__update_pos(node, new_x, new_y, node.width, node.height)

    def get_cell_pos(self, x, y):
        return (
                self.__padding[0] + x * self.__cell_size, 
                self.__padding[1] + y * self.__cell_size
                )

    def get_node_pos(self, node):
        delta = self.__delta[node]
        return (node.x - delta[0], node.y - delta[1])

class Stage(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        self.map_size = opt['map_size']
        self.margin = opt['margin']
        self.bgimg = opt['bgimg']
        self.activated = opt['activated']
        self.deactivated = opt['deactivated']

        #
        # Floor Layer
        #

        self.floor_layer = MapContainer(
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
                opt={
                    'map_size': self.map_size
                    }
                )
        self.add_node(self.floor_layer)

        for x in xrange(0, self.map_size[0]):
            for y in xrange(0, self.map_size[1]):
                def should_light_func(x, y):
                    return lambda node: (x, y) == self.object_layer.get_cell(self.player)

                floor = Floor(
                        parent=self.floor_layer,
                        style={
                            'width': self.floor_layer.get_cell_size(),
                            'height': self.floor_layer.get_cell_size()
                            },
                        opt={
                            'should_light': should_light_func(x, y)
                            }
                        )
                self.floor_layer.add_node(floor, x, y)

        self.texture = {}
        self.texture['bgimg'] = cairo.ImageSurface.create_from_png(self.bgimg)
        self.on_update()

        #
        # Object Layer
        #
        
        self.object_layer = MapContainer(
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
                opt={
                    'map_size': self.map_size
                    }
                )
        layer = self.object_layer
        self.add_node(self.object_layer)

        def move_player(node, dx, dy):
            cell = layer.get_cell(node)
            pos = layer.get_node_pos(node)
            cell_size = layer.get_cell_size()

            if (dx > 0 
                    and cell[0] < (self.map_size[0] - 1) 
                    and layer.get_cell_nodes(cell[0] + 1, cell[1])):
                dx = min(layer.get_cell_pos(*cell)[0] - pos[0], dx)
            elif (dx < 0 
                    and cell[0] > 0 
                    and layer.get_cell_nodes(cell[0] - 1, cell[1])):
                dx = max(layer.get_cell_pos(*cell)[0] - pos[0], dx)
            elif dx == 0:
                dx = layer.get_cell_pos(*cell)[0] - pos[0]
            
            if (dy > 0 
                    and cell[1] < (self.map_size[1] - 1) 
                    and layer.get_cell_nodes(cell[0], cell[1] + 1)):
                dy = min(layer.get_cell_pos(*cell)[1] - pos[1], dy)
            elif (dy < 0 
                    and cell[1] > 0 
                    and layer.get_cell_nodes(cell[0], cell[1] - 1)):
                dy = max(layer.get_cell_pos(*cell)[1] - pos[1], dy)
            elif dy == 0:
                dy = layer.get_cell_pos(*cell)[1] - pos[1]

            layer.move_pos(node, dx, dy)

        self.player = Player(
                parent=layer,
                style={
                    'width': layer.get_cell_size(), 
                    'height': layer.get_cell_size() * 2, 
                    },
                opt={
                    'speed': 4.0,
                    'move': move_player,
                    'bomb': lambda node, count, power: 
                    self.place_bomb(*layer.get_cell(node), count=count, power=power),
                    'get_cell_size': lambda: layer.get_cell_size()
                    }
                )
        layer.add_node(self.player, 0, 0, 0, -layer.get_cell_size())

        for x in xrange(1, self.map_size[0], 2):
            for y in xrange(1, self.map_size[1], 2):
                block = HardBlock(
                    parent=layer,
                    style={
                        'width': layer.get_cell_size(), 
                        'height': layer.get_cell_size() * 2, 
                        },
                    )
                layer.add_node(block, x, y, 0, -layer.get_cell_size())

        self.box = MessageBox(
                parent=self, 
                style={
                    'width': '80%',
                    'height': '33%',
                    'align': 'center',
                    'vertical-align': 'center'
                    },
                opt=None)
        self.add_node(self.box)

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
        if self.activated(100):
            print self
        elif self.activated(65361):
            self.player.stop()
            self.player.move('left')
        elif self.activated(65362):
            self.player.stop()
            self.player.move('up')
        elif self.activated(65363):
            self.player.stop()
            self.player.move('right')
        elif self.activated(65364):
            self.player.stop()
            self.player.move('down')
        elif self.deactivated(65361):
            self.player.stop('left')
        elif self.deactivated(65362):
            self.player.stop('up')
        elif self.deactivated(65363):
            self.player.stop('right')
        elif self.deactivated(65364):
            self.player.stop('down')

        if self.activated(32):
            self.box.toggle()

        if self.activated(122):
            self.player.bomb()

    def place_bomb(self, x, y, count, power):
        bomb = Bomb(
                parent=self.object_layer,
                style={
                    'width': self.object_layer.get_cell_size(),
                    'height': self.object_layer.get_cell_size(),
                    },
                opt={
                    'count': count,
                    'power': power,
                    'destroy': lambda node: self.object_layer.remove_node(node),
                    'explode': lambda node: None
                    }
                )
        self.object_layer.add_node(bomb, x, y)
        bomb.start_counting()

fps_counters = [0 for i in range(0, 5)]
fps_cur_counter = 0
last_time = time.time()

def print_fps():
    global fps_counter, fps_cur_counter, last_time
    cur_time = time.time()
    elapsed_time = cur_time - last_time
    if elapsed_time > 1:
        last_time = cur_time
        fps_cur_counter = (fps_cur_counter + 1) % 5

        total_count = 0
        for count in fps_counters:
            total_count += count

        print 'fps =', float(total_count) / 5
        fps_counters[fps_cur_counter] = 1   # reset
    else:
        fps_counters[fps_cur_counter] += 1

class Bomberman(Game):
    def __init__(self):
        Game.__init__(self, 'Bomberman', 500, 500, 80)

        stage = Stage(
                parent=self,
                style={},
                opt={
                    'map_size': [15, 15], 
                    'margin': [20, 20, 20, 20],
                    'bgimg': 'stage_bg.png',
                    'activated': self.activated,
                    'deactivated': self.deactivated
                    }
                )

        def start_game():
            self.top_node=stage
            self.top_node.do_resize_recursive()

        menu = MenuScene(
                parent=self,
                style={},
                opt={
                    'bgimg': 'menu_bg.png',
                    'activated': self.activated,
                    'deactivated': self.deactivated,
                    'start game': start_game
                    }
                )
        self.top_node = menu

    def on_tick(self, interval):
        print_fps()

if __name__ == '__main__':
    game = Bomberman()
    try:
        game.run()
    except KeyboardInterrupt:
        game.quit()
