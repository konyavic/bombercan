#!/usr/bin/python

import cairo

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
