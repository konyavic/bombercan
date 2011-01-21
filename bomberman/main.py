#!/usr/bin/python

import gtk
import gtk.gdk as gdk
import gobject
import time
import cairo
import math

class Node:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.surface = None

        self.children = []
        self.parent = None

        self.action_list = {}
        self.animation_list = {}
        self.animated = False

    '''
    Functions could be without restrictions
    '''

    def add_node(self, node):
        self.children.append(node)
        node.parent = self

    def remove_node(self, node):
        self.children.remove(node)
        node.parent = None

    def add_action(self, name, callback, loop, update):
        self.action_list[name] = {
            'callback': callback, 
            'loop': bool(loop), 
            'update': bool(update),
            'done': False
        }

    def remove_action(self, name):
        del self.action_list[name]

    def add_animation(self, name, callback, delay, period, loop):
        self.animation_list[name] = {
            'callback': callback,
            'delay':    float(delay),
            'period':   float(period),
            'loop':     bool(loop),
            'started':  False,
            'done':     False,
            'elapsed':  0.0
        }

    def remove_animation(self, name):
        del self.animation_list[name]

    '''
    Functions should be implemented in sub-class
    '''
    
    def on_update(self):
        pass

    def on_resize(self, width, height):
        self.width = width
        self.height = height
        self.on_update()

    def on_tick(self, interval):
        pass

    '''
    Functions should be called from the top
    '''

    def do_update_recursive(self, cr, x, y, interval):
        if self.animated and not self.animation_list:
            self.on_update()

        elif self.animation_list:
            self.animated = True
            tmp_animation_list = self.animation_list.copy()
            for name, anime in tmp_animation_list.iteritems():
                if anime['done']:
                    self.remove_animation(name)
                    continue

                if not anime['started']:
                    anime['delay'] -= interval
                    if anime['delay'] <= 0:
                        anime['started'] = True
                else:
                    anime['elapsed'] += interval

                if anime['elapsed'] > anime['period']:
                    if anime['loop']:
                        anime['elapsed'] -= anime['period']
                    else:
                        anime['elapsed'] = anime['period']
                        anime['done'] = True

                if anime['started']:
                    anime['callback'](self, anime['elapsed']/anime['period'])

        else:
            for action in self.action_list.itervalues():
                if action['update']:
                    self.on_update()
                    break

        x, y = x + self.x, y + self.y
        if self.surface:
            cr.set_source_surface(self.surface, x, y)
            cr.paint()

        for nodes in self.children:
            nodes.do_update_recursive(cr, x, y, interval)

    def do_tick_recursive(self, interval):
        self.on_tick(interval)

        ''' perform actions '''
        # to allow adding\removing actions during iteration
        tmp_action_list = self.action_list.copy()
        for name, action in tmp_action_list.iteritems():
            if action['done'] and not action['loop']:
                self.remove_action[name]
                continue

            action['callback'](self, interval)
            action['done'] = True

        for nodes in self.children:
            nodes.do_tick_recursive(interval)

class Player(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)
        self.pos = opt['pos']
        self.img = opt['img']
        self.speed = opt['speed']
        self.enabled_update = False
        self.texture = {}
        self.texture['img'] = cairo.ImageSurface.create_from_png(self.img)
        self.state = 'stopped'
        self.on_update()

    def on_update(self):
        scale = self.width / float(self.texture['img'].get_width())
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        cr = cairo.Context(self.surface)
        cr.scale(scale, scale)
        cr.set_source_surface(self.texture['img'])
        cr.paint()

    def on_resize(self, width, height):
        Node.on_resize(self, width, height)
        self.__update_pos()

    def on_action_tick(self, interval):
        pass

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

        self.add_action('move', move_action, loop=True, update=True)

    def stop(self):
        self.remove_action('move')

def draw_simple_pattern(surface, width, height, color):
    cr = cairo.Context(surface)
    cr.set_line_width(2)
    cr.rectangle(0, 0, width, height)
    cr.set_source_rgba(*color)
    cr.fill_preserve()
    cr.set_source_rgba(0.5, 0.5, 0.5, 0.7)
    cr.stroke()
    del cr

class Cell(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)
        self.pos = opt['pos']
        self.lighted = False
        self.on_update()

    def __repr__(self):
        return '.'

    def on_update(self):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        self.color = (0.5, 0.5, 1, 0.7)
        draw_simple_pattern(self.surface, self.width, self.height, self.color)

    def on_tick(self, interval):
        if self.parent.player.pos == self.pos and self.lighted == False:
            self.light(True)
            self.lighted = True
        elif self.parent.player.pos != self.pos and self.lighted == True:
            self.light(False)
            self.lighted = False

    def light(self, b):
        def blink_animation(self, phase):
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
            c = math.cos(phase*math.pi*2)
            self.color = (
                    0.75-0.25*c, 
                    0.25+0.25*c, 
                    0.5+0.5*c,
                    0.7)
            draw_simple_pattern(self.surface, self.width, self.height, self.color)

        def fade_out_animation(self, phase):
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
            tmp_color = (
                    self.color[0]+(0.5-self.color[0])*phase,
                    self.color[1]+(0.5-self.color[1])*phase,
                    self.color[2]+(1-self.color[2])*phase,
                    0.7
                    )
            draw_simple_pattern(self.surface, self.width, self.height, tmp_color)

        if b:
            self.add_animation('blink', blink_animation, delay=0, period=1.5, loop=True)
        else:
            self.remove_animation('blink')
            self.add_animation('fade out', fade_out_animation, delay=0, period=1, loop=False)

class Stage(Node):
    def __init__(self, x, y, width, height, opt):
        Node.__init__(self, x, y, width, height)
        self.map_size = opt['map_size']
        self.margin = opt['margin']
        self.bgimg = opt['bgimg']
        self.enabled_update = False

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

        self.texture = {}
        self.texture['bgimg'] = cairo.ImageSurface.create_from_png(self.bgimg)
        self.on_update()

        self.state = 'stopped'

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

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        cr = cairo.Context(self.surface)
        cr.scale(scale, scale)
        cr.set_source_rgb(0, 0, 0)
        cr.paint()
        cr.set_source_surface(self.texture['bgimg'], x, y)
        cr.paint_with_alpha(0.5)

    def on_resize(self, width, height):
        Node.on_resize(self, width, height)
        self.__update_metrics()
        for x, row in enumerate(self.map):
            for y, cell in enumerate(row):
                cell.x, cell.y = self.__get_cell_pos(x, y)
                cell.on_resize(self.cell_size, self.cell_size)

        cell = self.map[self.player.pos[0]][self.player.pos[1]]
        self.player.x , self.player.y = cell.x, cell.y - self.cell_size
        self.player.on_resize(self.cell_size, self.cell_size*2)

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

class Game:
    def __init__(self):
        self.__quit__ = False

        self.fps = 120
        self.screen_size = [500, 500]
        self.top_node = Stage(
                0, 0, 500, 500, 
                {
                    'map_size': [25, 25], 
                    'margin': [20, 20, 20, 20],
                    'bgimg': 'bg.png',
                    }
                )
        self.keymap = {
                65361: False,
                65362: False,
                65363: False,
                65364: False,
                }

    def quit(self):
        self.__quit__ = True

    def do_tick(self):
        if self.__quit__:
            gtk.main_quit()
        print_fps()

        self.top_node.do_tick_recursive(self.interval)

    def do_expose(self, widget, event):
        try:
            cr = widget.window.cairo_create()
            width = widget.allocation.width
            height = widget.allocation.height
            node = self.top_node
            node.do_update_recursive(cr, 0, 0, self.interval)
        except KeyboardInterrupt:
            self.quit()

    def do_timeout(self):
        try:
            last_time = time.time()
            self.interval = last_time - self.cur_time
            self.cur_time = last_time

            self.do_tick()
            self.area.queue_draw()
        except KeyboardInterrupt:
            self.quit()

        return True

    def do_key_press(self, widget, event):
        key = event.keyval
        self.keymap[key] = True

        if key == 100:
            print self.top_node
        elif key == 65361:
            self.top_node.player.move('left')
        elif key == 65362:
            self.top_node.player.move('up')
        elif key == 65363:
            self.top_node.player.move('right')
        elif key == 65364:
            self.top_node.player.move('down')

        return True

    def do_key_release(self, widget, event):
        key = event.keyval
        self.keymap[key] = False

        if (self.keymap[65361] 
                == self.keymap[65362] 
                == self.keymap[65363] 
                == self.keymap[65364]
                == False):
            self.top_node.player.stop()

        return True

    def do_resize(self, widget, allocation):
        self.screen_size = (allocation.width, allocation.height)
        self.top_node.on_resize(allocation.width, allocation.height)

    def run(self):
        self.cur_time = time.time()
        self.interval = 0

        window = gtk.Window()
        window.connect('destroy', gtk.main_quit)
        window.connect('key-press-event', self.do_key_press)
        window.connect('key-release-event', self.do_key_release)
        window.set_default_size(*self.screen_size)

        area = gtk.DrawingArea()
        area.connect('expose-event', self.do_expose)
        area.connect('size-allocate', self.do_resize)
        self.area = area

        window.add(area)
        window.show_all()
        
        gobject.timeout_add(1000/self.fps, self.do_timeout)

        gtk.main()

if __name__ == '__main__':
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        game.quit()
