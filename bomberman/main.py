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

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)

        self.children = []
        self.parent = None

        self.action_list = {}
        self.action_remove_list = set()
        self.animation_list = {}
        self.animation_remove_list = set()
        self.animated = False

    '''
    Functions could be called without restrictions
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
        if name in self.action_list:
            self.action_remove_list.add(name)

    def __remove_actions(self):
        for name in self.action_remove_list:
            del self.action_list[name]

        self.action_remove_list = set()

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
        if name in self.animation_list:
            self.animation_remove_list.add(name)

    def __remove_animations(self):
        for name in self.animation_remove_list:
            del self.animation_list[name]

        self.animation_remove_list = set()

    '''
    Functions should be implemented in sub-classes
    '''
    
    def on_update(self):
        pass

    def on_resize(self, width, height):
        self.width = width
        self.height = height
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        self.on_update()

    def on_tick(self, interval):
        pass

    '''
    Functions should be called from the top
    '''

    def __update_animation(self, name, anime, interval):
        # remove the anime if it is done
        if anime['done']:
            self.remove_animation(name)
            return

        # calculate delay and elapsed time
        if not anime['started']:
            anime['delay'] -= interval
            if anime['delay'] <= 0:
                anime['started'] = True
        else:
            anime['elapsed'] += interval
        
        # wrap elapsed time
        if anime['elapsed'] > anime['period']:
            if anime['loop']:
                anime['elapsed'] -= anime['period']
            else:
                anime['elapsed'] = anime['period']
                anime['done'] = True

        # perform this anime
        if anime['started']:
            anime['callback'](self, anime['elapsed']/anime['period'])

    def do_update_recursive(self, cr, x, y, interval):
        queue = [(self, x, y)]
        while queue:
            current, x, y = queue.pop(0)
            if current.animated and not current.animation_list:
                # update at the end of all animation queued
                current.on_update()
            elif current.animation_list:
                # perform animation
                current.animated = True
                for name, anime in current.animation_list.iteritems():
                    current.__update_animation(name, anime, interval)
                    
                # actual remove of done animation
                current.__remove_animations()
            else:
                # update for actions causing updates
                for action in current.action_list.itervalues():
                    if action['update']:
                        current.on_update()
                        break

            x, y = x + current.x, y + current.y
            cr.set_source_surface(current.surface, x, y)
            cr.paint()

            for nodes in current.children:
                queue.append((nodes, x, y))

    def do_tick_recursive(self, interval):
        queue = [self]
        while queue:
            current = queue.pop(0)
            current.on_tick(interval)

            # perform actions
            for name, action in current.action_list.iteritems():
                if action['done'] and not action['loop']:
                    current.remove_action[name]
                else:
                    action['callback'](current, interval)
                    action['done'] = True

            # actual remove of done actions
            current.__remove_actions()

            for nodes in current.children:
                queue.append(nodes)

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
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)

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

        self.fps = 80
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
