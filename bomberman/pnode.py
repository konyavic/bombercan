#!/usr/bin/python

import time

import gtk
import gtk.gdk as gdk
import gobject
import cairo

class Node:
    def __init__(self, x, y, width, height):
        # the following attributeds should be used as read-only variables in subclasses
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # the following attributes should never be directly accessed, 
        # except for surface
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.surface_x = 0
        self.surface_y = 0
        self.surface_width = width
        self.surface_height = height

        self.children = []
        self.parent = None

        self.action_list = {}
        self.action_remove_list = set()
        self.animation_list = {}
        self.animation_remove_list = set()
        self.animated = False

    def create_surface(self, x, y, width, height):
        del self.surface
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.surface_x = x
        self.surface_y = y
        self.surface_width = width
        self.surface_height = height

    def reset_surface(self):
        del self.surface
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        self.surface_x = 0
        self.surface_y = 0
        self.surface_width = self.width
        self.surface_height = self.height

    def create_surface_by_scale(self, scale, rel_origin=(0.5, 0.5)):
        rx, ry = rel_origin
        new_width = self.width * scale
        new_height = self.height * scale
        self.create_surface( 
                int(self.width * rx - new_width / 2 + 0.5),
                int(self.height * ry - new_height / 2 + 0.5), 
                int(new_width + 0.5),
                int(new_height + 0.5)
                )

    def clear_context(self, cr):
        cr.save()
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.restore()

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

    def add_animation(self, name, callback, delay, period, loop, cleanup=None):
        self.animation_list[name] = {
            'callback': callback,
            'delay':    float(delay),
            'period':   float(period),
            'loop':     bool(loop),
            'cleanup':  cleanup,
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

    # on_resize could be recursive because it is not a heavily-happening event
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
            if anime['cleanup']:
                anime['cleanup'](self)

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
        stack = [(self, x, y)]
        while stack:
            current, x, y = stack.pop(0)
            if current.animated and not current.animation_list:
                # update at the end of all animation queued
                current.animated = False
                current.on_update()
            elif current.animation_list:
                # perform animation
                current.animated = True
                for name, anime in current.animation_list.iteritems():
                    current.__update_animation(name, anime, interval)
                    
                # actual removal of done animation
                current.__remove_animations()
            else:
                # update for actions causing updates
                for action in current.action_list.itervalues():
                    if action['update']:
                        current.on_update()
                        break

            node_x = x + current.x
            node_y = y + current.y
            surface_x = node_x + current.surface_x
            surface_y = node_y + current.surface_y
            cr.set_source_surface(current.surface, surface_x, surface_y)
            cr.paint()

            stack = [(node, node_x, node_y) for node in current.children] + stack

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

            # actual removal of done actions
            current.__remove_actions()

            for nodes in current.children:
                queue.append(nodes)

class Game:
    def __init__(self, title, top_node, screen_x, screen_y, fps):
        self.title = title
        self.top_node = top_node
        self.screen_size = [int(screen_x), int(screen_y)]
        self.timer_interval = int(1000.0/fps)

        self.__quit = False
        self.__keymap = set()
        self.__next_keymap = set()

    def quit(self):
        self.__quit = True

    def activated(self, key):
        return not (key in self.__keymap) and (key in self.__next_keymap)

    def deactivated(self, key):
        return (key in self.__keymap) and not (key in self.__next_keymap)

    def on_tick(self, interval):
        """
        extend this method to handle input and time events
        """
        pass
        
    def do_expose(self, widget, event):
        try:
            cr = widget.window.cairo_create()
            self.top_node.do_update_recursive(cr, 0, 0, self.interval)
        except KeyboardInterrupt:
            self.quit()

    def do_timeout(self):
        try:
            if self.__quit:
                gtk.main_quit()

            # calculate elapsed time
            last_time = time.time()
            self.interval = last_time - self.cur_time
            self.cur_time = last_time
            # handle input and timer events
            self.on_tick(self.interval)
            # handle timer events of nodes
            self.top_node.do_tick_recursive(self.interval)
            # take a snapshot of the lastest state of keymap
            self.__keymap = self.__next_keymap.copy()
            # handle frame update
            self.area.queue_draw()
        except KeyboardInterrupt:
            self.quit()

        return True

    def do_key_press(self, widget, event):
        key = event.keyval
        self.__next_keymap.add(key)
        return True

    def do_key_release(self, widget, event):
        key = event.keyval
        if key in self.__next_keymap:
            self.__next_keymap.remove(key)

        return True

    def do_resize(self, widget, allocation):
        self.screen_size = [allocation.width, allocation.height]
        self.top_node.on_resize(*self.screen_size)

    def run(self):
        self.cur_time = time.time()
        self.interval = 0

        window = gtk.Window()
        window.connect('destroy', gtk.main_quit)
        window.connect('key-press-event', self.do_key_press)
        window.connect('key-release-event', self.do_key_release)
        window.set_default_size(*self.screen_size)
        window.set_title(self.title)

        area = gtk.DrawingArea()
        area.connect('expose-event', self.do_expose)
        area.connect('size-allocate', self.do_resize)
        self.area = area

        window.add(area)
        window.show_all()
        
        gobject.timeout_add(self.timer_interval, self.do_timeout)

        gtk.main()
