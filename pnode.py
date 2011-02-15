#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import sqrt
from time import time
from functools import wraps

import gtk
import gtk.gdk as gdk
import gobject
import cairo

_style_key = ['width', 'height', 'left', 'top', 'right', 'bottom', 'aspect', 'align', 'vertical-align', 'z-index']
_style_key_prio = dict([(_style_key[i], i) for i in range(0, len(_style_key))])

def style_key_prio(key):
    if key in _style_key:
        return _style_key_prio[key]
    else:
        return len(_style_key)

def parse_value(value, rel):
    if value.__class__ is str:
        value = value.strip()
        if value[-1] is '%':
            return int(rel * float(value[0:-1]) / 100)
        else:
            return value
    else:
        return value

def evaluate_style(node, style):
    # defaults
    node.x = 0
    node.y = 0
    node.z_index = 0
    node.width = node.parent.width
    node.height = node.parent.height

    # parse style
    has_width = False
    has_height = False
    keys = style.keys()
    keys.sort(key=style_key_prio)
    for k in keys:
        value = style[k]
        if k == 'width':
            node.width = parse_value(value, node.parent.width)
            has_width = True
        elif k == 'height':
            node.height = parse_value(value, node.parent.height)
            has_height = True
        elif k == 'left':
            node.x = parse_value(value, node.parent.width)
        elif k == 'top':
            node.y = parse_value(value, node.parent.height)
        elif k == 'right':
            if has_width:
                node.x = node.parent.width - node.width - parse_value(value, node.parent.width)
            else:
                node.width = node.parent.width - node.x - parse_value(value, node.parent.width)
        elif k == 'bottom':
            if has_height:
                node.y = node.parent.height - node.height - parse_value(value, node.parent.height)
            else:
                node.height = node.parent.height - node.y - parse_value(value, node.parent.height)
        elif k == 'aspect':
            ratio = float(value)    # width / height
            if ratio == 1.0:
                minimum = min(node.height, node.width)
                node.height, node.width = minimum, minimum
            elif ratio > 1.0:
                node.height = node.width / ratio
            else:
                node.width = node.height * ratio
        elif k == 'align':
            if value == 'center':
                node.x = (node.parent.width - node.width) / 2.0
            elif value == 'left':
                node.x = 0
            elif value == 'right':
                node.x = node.parent.width - node.width
        elif k == 'vertical-align':
            if value == 'center':
                node.y = (node.parent.height - node.height) / 2.0
            elif value == 'top':
                node.y = 0
            elif value == 'bottom':
                node.y = node.parent.height - node.height
        elif k == 'z-index':
            node.z_index = int(value)

def animation(f):
    """Decorator for animation
    """
    @wraps(f)
    def _animation(self, duration, 
            delay=0.0, loop=False, cleanup=None, pend=False):
        self.set_animation(f, duration, delay, loop, cleanup, pend)

    return _animation

class Node(object):
    def __init__(self, parent, style):
        self.children = []
        # XXX: repack after tree setup
        self.parent = parent
        self.set_style(style)
        #self.reset_surface()

        self.reset_transforms()

        self.reset_actions()
        self.reset_animations()

        self.repaint()

    def set_style(self, style):
        self.style = style
        evaluate_style(self, style)

    #
    # Functions for manipulating surface
    #
   
    def create_surface(self, x, y, width, height):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
        self.surface_x = x
        self.surface_y = y
        self.surface_width = width
        self.surface_height = height

    def reset_surface(self):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(self.width), int(self.height))
        self.surface_x = 0
        self.surface_y = 0
        self.surface_width = self.width
        self.surface_height = self.height

    def create_surface_by_scale(self, sx, sy, rel_origin=(0.5, 0.5)):
        rx = rel_origin[0] * self.width
        ry = rel_origin[1] * self.height
        new_width = self.width * sx
        new_height = self.height * sy
        delta_x = rel_origin[0] * new_width
        delta_y = rel_origin[1] * new_height
        self.create_surface( 
                rx - delta_x,
                ry - delta_y, 
                new_width,
                new_height
                )

    def create_surface_by_rotate(self, ang, rel_origin=(0.5, 0.5)):
        rx = rel_origin[0] * self.width
        ry = rel_origin[1] * self.height
        # the corner with max length from the origin
        mx = rel_origin[0] if rel_origin[0] > 0.5 else 1.0 - rel_origin[0]
        my = rel_origin[1] if rel_origin[1] > 0.5 else 1.0 - rel_origin[1]
        mlen = sqrt((self.width * mx) ** 2 + (self.height * my) ** 2)
        new_width = mlen * 2
        new_height = mlen * 2
        delta_x = 0.5 * new_width
        delta_y = 0.5 * new_height
        self.create_surface( 
                rx - delta_x,
                ry - delta_y, 
                new_width,
                new_height
                )

    def create_surface_by_scale_rotate(self, sx, sy, ang, 
            scale_origin=(0.5, 0.5), ang_origin=(0.5, 0.5)):
        # XXX: to be implemented
        pass

    def clear_context(self, cr):
        cr.save()
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.restore()

    #
    # Functions for manipulating sub-nodes
    #

    def add_node(self, node):
        self.children.append(node)
        node.parent = self

    def remove_node(self, node):
        self.children.remove(node)
        node.parent = None

    #
    # Functions for actions
    #

    def add_action(self, name, func, 
            duration=0.0, delay=0.0, update=False, loop=False, cleanup=None):

        self.action_list[name] = {
            'func': func,
            'duration': float(duration),
            'delay': float(delay),
            'update': bool(update),
            'loop': bool(loop),
            'cleanup': cleanup,
            'elapsed': 0.0,
            'started': False
        }

    def remove_action(self, name):
        if name in self.action_list:
            del self.action_list[name]

    def reset_actions(self):
        self.action_list = {}
        self.action_need_update = False

    def repaint(self):
        self.action_need_update = True

    #
    # Functions for animations
    #

    def set_animation(self, func, 
            duration=0.0, delay=0.0, loop=False, cleanup=None, pend=False):

        anime = {
                'func': func,
                'duration': float(duration),
                'delay': float(delay),
                'loop': bool(loop),
                'cleanup': cleanup,
                'elapsed': 0.0,
                'started': False
                } 

        if pend:
            self.animation_list.append(anime)
        else:
            self.animation_list = [ anime ]

    def reset_animations(self):
        self.animation_list = []

    #
    # Functions for transforms
    #
    
    SURFACE_CREATED = 0
    SURFACE_CHANGED = 1 << 0
    SURFACE_SCALE   = 1 << 1
    SURFACE_ROTATE  = 1 << 2

    def reset_transforms(self):
        self.set_alpha()
        self.set_translation()
        self.surface_changed = Node.SURFACE_CHANGED
    
    def set_scale(self, sx=1.0, sy=1.0, rel_origin=(0.5, 0.5)):
        self.sx = sx
        self.sy = sy
        self.scale_origin=rel_origin
        self.surface_changed |= Node.SURFACE_SCALE | Node.SURFACE_CHANGED

    def set_rotate(self, ang=0.0, rel_origin=(0.5, 0.5)):
        self.ang=ang
        self.rotate_origin=rel_origin
        self.surface_changed |= Node.SURFACE_ROTATE | Node.SURFACE_CHANGED

    def set_alpha(self, alpha=1.0):
        self.alpha=alpha

    def set_translation(self, dx=0.0, dy=0.0):
        self.dx = dx
        self.dy = dy

    #
    # Functions to be overwritten in sub-classes
    #
    
    def on_update(self, cr):
        pass

    def on_resize(self):
        evaluate_style(self, self.style)
        self.reset_surface()
        self.repaint()

    def on_tick(self, interval):
        pass

    #
    # Core functions
    #

    def _do_update(self, interval):
        anime = self.animation_list[0]
        if not anime['started']:
            anime['delay'] -= interval
            if anime['delay'] <= 0.0:
                anime['started'] = True

        else:
            # check it's life
            anime['elapsed'] += interval
            if anime['elapsed'] > anime['duration']:
                if anime['loop']:
                    # XXX: if duration is too small?
                    anime['elapsed'] -= anime['duration']
                else:
                    if anime['cleanup']: anime['cleanup']()
                    self.animation_list.pop(0)
                    return

            # perform this animation
            phase = anime['elapsed'] / anime['duration']
            cr = self._get_context()
            anime['func'](self, cr, phase)
            self._updated = True

    def _get_context(self):
        """Get the cairo context of this node.

        1) re-create the surface as needed
        2) push the transformation matrix to the context
        3) return this context

        """
        state = self.surface_changed
        if state & Node.SURFACE_CHANGED:
            if state == Node.SURFACE_CHANGED:
                self.reset_surface()
                cr = cairo.Context(self.surface)
            elif state & Node.SURFACE_SCALE and state & Node.SURFACE_ROTATE:
                # XXX: to be implemented
                self.create_surface_by_scale_rotate()
            elif state & Node.SURFACE_SCALE:
                self.create_surface_by_scale(self.sx, self.sy, self.scale_origin)
                cr = cairo.Context(self.surface)
                cr.scale(self.sx, self.sy)
                self.clear_context(cr)
            elif state & Node.SURFACE_ROTATE:
                self.create_surface_by_rotate(self.ang, self.rotate_origin)
                cr = cairo.Context(self.surface)
                delta = self.surface_width * 0.5
                cr.translate(delta, delta)
                cr.rotate(self.ang)
                cr.translate(-delta, -delta)
                cr.translate(-self.surface_x, -self.surface_y)
                self.clear_context(cr)
        else:
            cr = cairo.Context(self.surface)
            self.clear_context(cr)

        return cr
        
    def do_update(self, interval):
        self._updated = False
        if len(self.animation_list) > 0:
            self._do_update(interval)

        if self.action_need_update and not self._updated:
            cr = self._get_context()
            self.on_update(cr)
            self.action_need_update = False

    def do_update_recursive(self, cr, x, y, interval):
        stack = [(self, x, y)]
        queue = []

        while stack:
            current, x, y = stack.pop(0)
            node_x = x + current.x
            node_y = y + current.y
            queue.append((current, node_x, node_y))
            stack = [(node, node_x, node_y) for node in current.children] + stack

        queue.sort(key=lambda tup: -tup[0].z_index)

        while queue:
            current, x, y = queue.pop(0)
            current.do_update(interval)
            abs_x = x + current.surface_x + current.dx
            abs_y = y + current.surface_y + current.dy
            cr.set_source_surface(current.surface, abs_x, abs_y)
            cr.paint_with_alpha(current.alpha)

    def do_tick(self, interval):
        self.on_tick(interval)
        # loop over all actions
        tmp_list = self.action_list.copy()
        for name, action in tmp_list.iteritems():
            if not action['started']:
                action['delay'] -= interval
                if action['delay'] <= 0.0:
                    action['started'] = True

            else:
                # check it's life
                action['elapsed'] += interval
                if action['elapsed'] > action['duration']:
                    if action['loop']:
                        # XXX: if duration is too small?
                        action['elapsed'] -= action['duration']
                    else:
                        if action['cleanup']: action['cleanup']()
                        self.action_list.remove_action(name)
                        continue

                # perform the action
                phase = 0.0 if action['duration'] <= 0.0 \
                            else action['elapsed'] / action['duration']
                action['func'](self, interval, phase)
                if action['update']:
                    # cleaned in do_update_recursive
                    self.action_need_update = True

    def do_tick_recursive(self, interval):
        queue = [self]
        while queue:
            current = queue.pop(0)
            current.do_tick(interval)
            for node in current.children:
                queue.append(node)

    def do_resize_recursive(self):
        queue = [self]
        while queue:
            current = queue.pop(0)
            current.on_resize()
            for node in current.children:
                queue.append(node)

class Game(object):
    def __init__(self, title, width, height, fps):
        self.title = title
        self.screen_size = [width, height]
        self.timer_interval = int(1000.0/fps)

        self.top_node = None

        self.__quit = False
        self.__keymap = set()
        self.__next_keymap = set()

        self.width = width
        self.height = height

    def quit(self):
        self.__quit = True

    def key_up(self, keyname):
        key = gdk.keyval_from_name(keyname)
        return not (key in self.__keymap) and (key in self.__next_keymap)

    def key_down(self, keyname):
        key = gdk.keyval_from_name(keyname)
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
            last_time = time()
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
        self.width = allocation.width
        self.height = allocation.height
        self.top_node.do_resize_recursive()

    def run(self):
        self.cur_time = time()
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
