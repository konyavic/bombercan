#!/usr/bin/python

import math
import time

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node
from pnode import Game

class Player(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)
        self.pos = opt['pos']
        self.img = opt['img']
        self.speed = opt['speed']
        self.texture = {}
        self.texture['img'] = cairo.ImageSurface.create_from_png(self.img)
        self.state = 'stopped'
        self.on_update()

    def on_update(self):
        scale = self.width / float(self.texture['img'].get_width())
        cr = cairo.Context(self.surface)
        cr.scale(scale, scale)
        cr.set_source_surface(self.texture['img'])
        cr.paint()

    def __update_pos(self):
        center_x = self.x + self.parent.cell_size*0.5 - self.parent.map[0][0].x
        center_y = self.y + self.parent.cell_size*1.5 - self.parent.map[0][0].y
        self.pos = [int(center_x/self.parent.cell_size), int(center_y/self.parent.cell_size)]

    def move(self, dir):
        def move_action(self, interval):
            if dir == 'up':
                self.y -= interval*self.speed*self.parent.cell_size
            elif dir == 'down':
                self.y += interval*self.speed*self.parent.cell_size
            elif dir == 'left':
                self.x -= interval*self.speed*self.parent.cell_size
            elif dir == 'right':
                self.x += interval*self.speed*self.parent.cell_size

            self.__update_pos()
            return

        #self.add_action(dir, move_action, loop=True, update=True)
        self.add_action(dir, move_action, loop=True, update=False)

    def stop(self, dir=None):
        if dir:
            self.remove_action(dir)
        else:
            for dir in ['up', 'down', 'left', 'right']:
                self.remove_action(dir)

class Cell(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)
        self.pos = opt['pos']
        self.lighted = False
        self.on_update()

    def __repr__(self):
        return '.'
    
    def __draw_simple_pattern(self, color):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        cr = cairo.Context(self.surface)
        
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

class Stage(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)
        self.map_size = opt['map_size']
        self.margin = opt['margin']
        self.bgimg = opt['bgimg']
        self.__update_metrics()

        self.map = [ [
            Cell(
                self.__get_cell_pos(x, y)[0],
                self.__get_cell_pos(x, y)[1],
                self.cell_size, 
                self.cell_size, 
                {'pos':[x, y]}
                )
            for y in xrange(0, self.map_size[1]) ] for x in xrange(0, self.map_size[0]) ]

        for row in self.map:
            for cell in row:
                self.add_node(cell)

        cell = self.map[0][0]
        self.player = Player(
                cell.x,
                cell.y - self.cell_size,
                self.cell_size, 
                self.cell_size*2, 
                {
                    'pos': [0, 0],
                    'img': 'player.png',
                    'speed': 5.0
                    }
                )
        self.add_node(self.player)
        self.characters = []
        self.characters.append(self.player)

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

    def on_resize(self, width, height):
        old_cell_size, old_top, old_left = self.cell_size, self.top, self.left

        Node.on_resize(self, width, height)
        self.__update_metrics()

        for x, row in enumerate(self.map):
            for y, cell in enumerate(row):
                cell.x, cell.y = self.__get_cell_pos(x, y)
                cell.on_resize(self.cell_size, self.cell_size)

        ratio = float(self.cell_size) / old_cell_size
        for c in self.characters:
            c.x = (c.x - old_left) * ratio + self.left
            c.y = (c.y - old_top) * ratio + self.top
            c.on_resize(int(c.width * ratio), int(c.height * ratio))

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
        stage = Stage(0, 0, 500, 500, {
            'map_size': [25, 25], 
            'margin': [20, 20, 20, 20],
            'bgimg': 'bg.png',
            })
        Game.__init__(self, 'Bomberman K', stage, 500, 500, 80)

    def on_tick(self, interval):
        if self.activated(100):
            print self.top_node
        elif self.activated(65361):
            self.top_node.player.stop()
            self.top_node.player.move('left')
        elif self.activated(65362):
            self.top_node.player.stop()
            self.top_node.player.move('up')
        elif self.activated(65363):
            self.top_node.player.stop()
            self.top_node.player.move('right')
        elif self.activated(65364):
            self.top_node.player.stop()
            self.top_node.player.move('down')
        elif self.deactivated(65361):
            self.top_node.player.stop('left')
        elif self.deactivated(65362):
            self.top_node.player.stop('up')
        elif self.deactivated(65363):
            self.top_node.player.stop('right')
        elif self.deactivated(65364):
            self.top_node.player.stop('down')
        
        print_fps()

if __name__ == '__main__':
    game = Bomberman()
    try:
        game.run()
    except KeyboardInterrupt:
        game.quit()
