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
from menuscene import MenuScene

class Player(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        self.pos = opt['pos']
        self.speed = opt['speed']
        self.get_cell_size = opt['get_cell_size']
        #get_pos
        #get_cell
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

    def __update_pos(self):
        center_x = self.x + self.get_cell_size() * 0.5 - self.parent.map[0][0].x
        center_y = self.y + self.get_cell_size() * 1.5 - self.parent.map[0][0].y
        self.pos = [int(center_x/self.get_cell_size()), int(center_y/self.get_cell_size())]

    def move(self, dir):
        def move_action(self, interval):
            delta = interval * self.speed * self.get_cell_size()
            if dir == 'up':
                self.y -= delta
            elif dir == 'down':
                self.y += delta
            elif dir == 'left':
                self.x -= delta
            elif dir == 'right':
                self.x += delta

            self.__update_pos()
            return

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

            return

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
        self.parent.bomb(self.pos[0], self.pos[1], 5, 3)

class Cell(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        self.pos = opt['pos']
        self.lighted = False
        self.on_update()

    def __repr__(self):
        return '.'
    
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
        if self.parent.player.pos == self.pos and self.lighted == False:
            self.light(True)
            self.lighted = True
        elif self.parent.player.pos != self.pos and self.lighted == True:
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

class Stage(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)
        self.map_size = opt['map_size']
        self.margin = opt['margin']
        self.bgimg = opt['bgimg']
        self.activated = opt['activated']
        self.deactivated = opt['deactivated']
        self.__update_metrics()

        self.map = [ [
            Cell(
                parent=self,
                style={
                    'left': self.__get_cell_pos(x, y)[0],
                    'top': self.__get_cell_pos(x, y)[1],
                    'width': self.cell_size, 
                    'height': self.cell_size, 
                    },
                opt={'pos':[x, y]}
                )
            for y in xrange(0, self.map_size[1]) ] for x in xrange(0, self.map_size[0]) ]

        for row in self.map:
            for cell in row:
                self.add_node(cell)

        cell = self.map[0][0]
        self.player = Player(
                parent=self,
                style={
                    'left': cell.x,
                    'top': cell.y - self.cell_size,
                    'width': self.cell_size, 
                    'height': self.cell_size*2, 
                    },
                opt={
                    'pos': cell.pos,
                    'img': 'player.png',
                    'speed': 2.0,
                    'get_cell_size': lambda: self.cell_size
                    }
                )
        self.add_node(self.player)
        self.characters = []
        self.characters.append(self.player)

        cell = self.map[0][0]
        self.effect = MapEffectLayer(parent=self, style={}, opt=None)
        self.add_node(self.effect)

        self.box = MessageBox(
                parent=self, 
                style={
                    'width': 0.8,
                    'height': 0.3,
                    'align': 'center',
                    'vertical-align': 'center'
                    },
                opt=None)
        self.add_node(self.box)

        self.texture = {}
        self.texture['bgimg'] = cairo.ImageSurface.create_from_png(self.bgimg)
        self.on_update()

    def __repr__(self):
        str = ''
        for x in xrange(0, len(self.map)):
            if (x % 5 == 0): 
                str += '%2d' % x
            else: 
                str += '  '
            for cell in self.map[x]:
                str += repr(cell)

            str += '\n'

        return str
    
    def __update_metrics(self):
        self.cell_size = min(
                (self.width - self.margin[1] - self.margin[3])/self.map_size[0], 
                (self.height - self.margin[0] - self.margin[2])/self.map_size[1]
                )
        self.top = (self.height - self.cell_size * self.map_size[1]) / 2
        self.left = (self.width - self.cell_size * self.map_size[0]) / 2

    def __get_cell_pos(self, x, y):
        return (self.left + self.cell_size*x, self.top + self.cell_size*y)

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
        cr.paint_with_alpha(0.5)

    def on_resize(self):
        old_cell_size, old_top, old_left = self.cell_size, self.top, self.left

        Node.on_resize(self)
        self.__update_metrics()

        for x, row in enumerate(self.map):
            for y, cell in enumerate(row):
                cell.set_style({
                    'left': self.__get_cell_pos(x, y)[0],
                    'top': self.__get_cell_pos(x, y)[1],
                    'width': self.cell_size, 
                    'height': self.cell_size
                    })

        ratio = float(self.cell_size) / old_cell_size
        for c in self.characters:
            c.set_style({
                'left': int((c.x - old_left) * ratio + self.left),
                'top': int((c.y - old_top) * ratio + self.top),
                'width': int(c.width * ratio),
                'height': int(c.height * ratio)
                })

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

    def bomb(self, x, y, count, power):
        cell = self.map[x][y]
        bomb = Bomb(
                parent=cell,
                style={},
                opt={
                    'count': count,
                    'power': power,
                    'destroy': lambda node: cell.remove_node(node),
                    'explode': lambda node: self.effect.explode(cell.pos[0], cell.pos[1], node.power)
                    }
                )
        bomb.start_counting()
        cell.add_node(bomb)

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
        Game.__init__(self, 'Bomberman K', 500, 500, 80)

        stage = Stage(
                parent=self,
                style={},
                opt={
                    'map_size': [15, 15], 
                    'margin': [20, 20, 20, 20],
                    'bgimg': 'bg.png',
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
