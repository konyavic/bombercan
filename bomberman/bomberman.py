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
        self.speed = opt['speed']
        self.state = 'stopped'
        self.on_update()

    def __draw_feet(self, cr, x, y, margin, inverse=1):
        cr.move_to(x, y)
        cr.rel_line_to(0, margin * 1.3)
        cr.rel_line_to(-inverse*margin * 0.3, 0)
        cr.rel_line_to(0, margin * 0.3)
        cr.rel_line_to(inverse*margin * 1, 0)
        cr.rel_line_to(0, -margin * 0.3)
        cr.rel_line_to(-inverse*margin * 0.3, 0)
        cr.rel_line_to(0, margin * -1.3)
        cr.close_path()

        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

    def __draw_cylinder(self, cr, x, y, margin, height, color):
        cr.move_to(x, y)
        cr.rel_curve_to(
                (self.width - margin * 2) / 2 - 0.5 * margin, margin * 0.7, 
                (self.width - margin * 2) / 2 + 0.5 * margin, margin * 0.7, 
                self.width - margin * 2, 0 
                )
        cr.rel_line_to(0, -height)
        cr.rel_curve_to(
                -(self.width - margin * 2) / 2 + 0.5 * margin, -margin * 0.7, 
                -(self.width - margin * 2) / 2 - 0.5 * margin, -margin * 0.7, 
                -(self.width - margin * 2), 0 
                )
        cr.close_path()

        cr.set_source_rgb(*color)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

        cr.move_to(x, y - height)
        cr.rel_curve_to(
                (self.width - margin * 2) / 2 - 0.5 * margin, margin * 0.7, 
                (self.width - margin * 2) / 2 + 0.5 * margin, margin * 0.7, 
                self.width - margin * 2, 0 
                )

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(0.8)
        cr.stroke()

    def __draw_eyes(self, cr, margin):
        cr.save()
        cr.scale(1, 0.5)
        cr.arc(
                margin * 1.9, self.height * 0.5 + margin * 4,
                margin * 0.5,
                0, 2*math.pi)
        cr.restore()

        cr.set_source_rgb(1, 1, 0)
        cr.fill_preserve()

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

        cr.save()
        cr.scale(1, 0.5)
        cr.arc(
                self.width - margin * 1.9, self.height * 0.5 + margin * 4,
                margin * 0.5,
                0, 2*math.pi)
        cr.restore()

        cr.set_source_rgb(1, 1, 0)
        cr.fill_preserve()

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

    def on_update(self):
        margin = int(self.width * 0.2)

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        cr = cairo.Context(self.surface)
        # draw feets
        self.__draw_feet(cr, margin * 1.7, self.height - margin * 2, margin)
        self.__draw_feet(cr, self.width - margin * 1.7, self.height - margin * 2, margin, -1)
        # draw body
        self.__draw_cylinder(cr, margin, self.height - margin * 2, margin, self.height * 0.3, (0, 0, 0.7))
        # draw head
        self.__draw_cylinder(cr, margin, self.height *0.7 - margin * 2, margin, self.height * 0.2, (0.7, 0.7, 0.7))
        # draw eyes
        self.__draw_eyes(cr, margin)


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

        def move_animation(self, phase):
            margin = int(self.width * 0.2)
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
            cr = cairo.Context(self.surface)
            # draw feets
            self.__draw_feet(cr, 
                    margin * 1.7, 
                    self.height - margin * 2 + margin * 0.5 * math.cos(phase*math.pi*2), 
                    margin)
            self.__draw_feet(cr, 
                    self.width - margin * 1.7, 
                    self.height - margin * 2 - margin * 0.5 * math.cos(phase*math.pi*2), 
                    margin, -1)
            # draw body
            self.__draw_cylinder(cr, margin, self.height - margin * 2, margin, self.height * 0.3, (0, 0, 0.7))
            # draw head
            self.__draw_cylinder(cr, margin, self.height *0.7 - margin * 2, margin, self.height * 0.2, (0.7, 0.7, 0.7))
            # draw eyes
            self.__draw_eyes(cr, margin)

            return

        self.add_action(dir, move_action, loop=True, update=False)
        self.add_animation(dir, move_animation, loop=True, delay=0, period=1)

    def stop(self, dir=None):
        if dir:
            self.remove_action(dir)
            self.remove_animation(dir)
        else:
            for dir in ['up', 'down', 'left', 'right']:
                self.remove_action(dir)
                self.remove_animation(dir)

    def bomb(self, count):
        self.parent.bomb(self.pos[0], self.pos[1], count)

class Bomb(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)
        self.count = float(opt['count'])
        self.on_update()

        def counting_animation(self, phase):
            self.scale = 1.25 - 0.25 * math.cos(phase*math.pi*2)

        self.add_animation('counting', counting_animation, loop=True, delay=0, period=1.5)


    def on_update(self):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        cr = cairo.Context(self.surface)
        cr.arc(self.width * 0.6, self.height * 0.33, self.width * 0.2, 0, math.pi * 2)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_line_width(1)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()
        cr.arc(self.width * 0.45, self.height * 0.55, self.width * 0.35, 0, math.pi * 2)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.fill_preserve()
        cr.set_line_width(1)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

    def on_tick(self, interval):
        self.count -= interval
        if self.count < 0:
            self.explode()

    def explode(self):
        self.parent.remove_node(self)

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

    def on_resize(self, width, height):
        Node.on_resize(self, width, height)
        for node in self.children:
            node.on_resize(width, height)

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
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)
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
                    'pos': cell.pos,
                    'img': 'player.png',
                    'speed': 2.0
                    }
                )
        self.add_node(self.player)
        self.characters = []
        self.characters.append(self.player)

        rect = self.__get_box()
        self.box = MessageBox(*rect, opt=None)
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

    def __get_box(self):
        height = max(150, (self.height - self.margin[0] - self.margin[2]) / 3)
        return (
                self.margin[3], 
                self.height - self.margin[2] - height, 
                self.width - self.margin[1] - self.margin[3],
                height
                )

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

        rect = self.__get_box()
        self.box.x = rect[0]
        self.box.y = rect[1]
        self.box.on_resize(rect[2], rect[3])

    def bomb(self, x, y, count):
        cell = self.map[x][y]
        bomb = Bomb(
                0, 0,
                self.cell_size, 
                self.cell_size, 
                {
                    'count': count
                    }
                )
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
        stage = Stage(0, 0, 500, 500, {
            'map_size': [16, 16], 
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

        if self.activated(32):
            self.top_node.box.toggle()

        if self.activated(122):
            self.top_node.player.bomb(10)
        
        print_fps()

if __name__ == '__main__':
    game = Bomberman()
    try:
        game.run()
    except KeyboardInterrupt:
        game.quit()
