#!/usr/bin/python
# -*- coding: utf-8 -*-

"""The pnode framework.

There are only two core classes in this framework: Node and Game.

"""

from math import sqrt
from time import time
from functools import wraps

import gtk
import gtk.gdk as gdk
import gobject
import cairo

# The keywords for style, the order stands for the priority of evaluation
_style_key = ['width', 'height', 'left', 'top', 'right', 
    'bottom', 'aspect', 'align', 'vertical-align', 'z-index']
_style_key_prio = dict([(_style_key[i], i) for i in range(0, len(_style_key))])

def style_key_prio(key):
    """Get the priority of this keyword."""
    if key in _style_key:
        return _style_key_prio[key]
    else:
        return len(_style_key)

def parse_value(value, rel):
    """Parse the value of keyword.
    
    Three types are allowed:
        - integer
        - a string representing percentage, eg. '20%'
        - a plain string, eg. 'center'

    """
    if value.__class__ is str:
        value = value.strip()
        if value[-1] is '%':
            return int(rel * float(value[0:-1]) / 100)
        else:
            return value
    else:
        return value

def evaluate_style(node, style):
    """Evaluate the style."""
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
    """A decorator for animation."""
    @wraps(f)
    def _animation(self, duration, 
            delay=0.0, loop=False, cleanup=None, pend=False):
        self.set_animation(f, duration, delay, loop, cleanup, pend)

    return _animation

class Node(object):
    """The basic element in the pnode framework."""
    def __init__(self, parent, style):
        """Initialized the node.
        
        @param parent: the new node need a parent immediately 
            to evaluate the style. It is safe to add this node 
            under another parent after initialization, 
            but you may have to call do_resize_recursive() 
            to ensure the style of it being evaluated according 
            to the latest parent.
        @type parent: pnode.Node
        @param style: the dictionary listing the style

        """
        self.children = []
        self.parent = parent
        self.set_style(style)
        #self.reset_surface()

        self.reset_transforms()

        self.reset_actions()
        self.reset_animations()

        self.repaint()

    def set_style(self, style):
        """Set to a new style.
        
        The new style will be evaluated immediatley.

        @param style: the dictionary listing the style

        """
        self.style = style
        evaluate_style(self, style)

    #
    # Functions for manipulating surface
    #
   
    def create_surface(self, x, y, width, height):
        """Create the surface with specified position and size.
        
        @param x: the delta on x 
            between the logical position and the real position
        @param y: the delta on y
            between the logical position and the real position
        @param width: the real width
        @param height: the real height

        """
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
        self.surface_x = x
        self.surface_y = y
        self.surface_width = width
        self.surface_height = height

    def reset_surface(self):
        """Re-create the surface using current real position and size."""
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(self.width), int(self.height))
        self.surface_x = 0
        self.surface_y = 0
        self.surface_width = self.width
        self.surface_height = self.height

    def create_surface_by_scale(self, sx, sy, rel_origin=(0.5, 0.5)):
        """Re-create the surface for scaling.
        
        @param sx: the scale factor on x
        @param sy: the scale factor on y
        @param rel_origin: a list of two float number 
            indicating the relative center 
            (eg. (0.5, 0.5) means the center of object)

        """
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
        """Re-create the surface for rotation.
        
        @param ang: the angle
        @param rel_origin: the same as in create_surface_by_scale()

        """
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
        """Clean the context."""
        cr.save()
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.restore()

    #
    # Functions for manipulating sub-nodes
    #

    def add_node(self, node):
        """Add the node as a sub-node."""
        self.children.append(node)
        node.parent = self

    def remove_node(self, node):
        """Remove the node from sub-nodes."""
        self.children.remove(node)
        node.parent = None

    #
    # Functions for actions
    #

    def add_action(self, name, func, 
            duration=0.0, delay=0.0, update=False, loop=False, cleanup=None):
        """Add an action to this node.
        
        Action is used to handle parameter change according to time,
        no matter it will update the surface or not.

        @param name: the name of this action. 
            This name is used to indentify this action in remove_action().
        @param duration: the duration in seconds
        @param update: should update the surface in each tick?
        @param loop: loop it?
        @param cleanup: the callback function called after the action ends
        
        """

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
        """Remove the specified action."""
        if name in self.action_list:
            del self.action_list[name]

    def reset_actions(self):
        """Remove all actions."""
        self.action_list = {}
        self.action_need_update = False

    def repaint(self):
        """Mark this node to update it's surface in the next tick."""
        self.action_need_update = True

    #
    # Functions for animations
    #

    def set_animation(self, func, 
            duration=0.0, delay=0.0, loop=False, cleanup=None, pend=False):
        """Set the animation of this node.
        
        Basically, animation is the same with action, 
        except that animation always updates the surface,
        and only one animation will be evaluated at one time.
        (That is because letting two animation to update 
        on the same context at once is strange.)

        @param pend: add the animation to the last. 
            It will be evaluated after all other animation being expired.
            (The default value False will cause deleting all other animation.)

        """

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
        """Remove all animation."""
        self.animation_list = []

    #
    # Functions for transforms
    #
    
    SURFACE_CREATED = 0
    SURFACE_CHANGED = 1 << 0
    SURFACE_SCALE   = 1 << 1
    SURFACE_ROTATE  = 1 << 2

    def reset_transforms(self):
        """Reset the transformation to the initial state."""
        self.set_alpha()
        self.set_translation()
        self.surface_changed = Node.SURFACE_CHANGED
    
    def set_scale(self, sx=1.0, sy=1.0, rel_origin=(0.5, 0.5)):
        """Scale the node.
        
        Parameters are the same with create_surface_by_scale().

        """
        self.sx = sx
        self.sy = sy
        self.scale_origin=rel_origin
        self.surface_changed |= Node.SURFACE_SCALE | Node.SURFACE_CHANGED

    def set_rotate(self, ang=0.0, rel_origin=(0.5, 0.5)):
        """Rotate the node.
        
        Parameters are the same with create_surface_by_rotate().

        """
        self.ang=ang
        self.rotate_origin=rel_origin
        self.surface_changed |= Node.SURFACE_ROTATE | Node.SURFACE_CHANGED

    def set_alpha(self, alpha=1.0):
        """Set the opacity of the node."""
        self.alpha=alpha

    def set_translation(self, dx=0.0, dy=0.0):
        """Set the translation of the node.
        
        Note that this call won't affect the logical position of this node.
        It only 'temporarily' moves the node.

        @param dx: delta on x
        @param dy: delta on y

        """
        self.dx = dx
        self.dy = dy

    #
    # Functions to be overwritten in sub-classes
    #
    
    def on_update(self, cr):
        """Overload this method to implement static graphics of this node."""
        pass

    def on_resize(self):
        """Overload this method to implement customized resizing.
        
        Remember to call the original on_resize() in an overloading method.

        """
        evaluate_style(self, self.style)
        self.reset_surface()
        self.repaint()

    def on_tick(self, interval):
        """Overload this method to do things in each tick."""
        pass

    #
    # Core functions
    #

    def _do_update(self, interval):
        """Update the surface."""
        # Use the first animation
        anime = self.animation_list[0]
        if not anime['started']:
            anime['delay'] -= interval
            if anime['delay'] <= 0.0:
                anime['started'] = True

        else:
            # Check it's life
            anime['elapsed'] += interval
            if anime['elapsed'] > anime['duration']:
                if anime['loop']:
                    # XXX: if duration is too small?
                    anime['elapsed'] -= anime['duration']
                else:
                    if anime['cleanup']: anime['cleanup']()
                    self.animation_list.pop(0)
                    return

            phase = anime['elapsed'] / anime['duration']
            # Obtain the context
            cr = self._get_context()
            # Perform this animation
            anime['func'](self, cr, phase)
            self._updated = True

    def _get_context(self):
        """Get the adjusted cairo context of it's surface.
            1. Re-create the surface as needed.
            2. Push the transformation matrix to the context.
            3. Return this modified context.

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
                self.create_surface_by_scale(self.sx, self.sy, 
                        self.scale_origin)
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
        """Update the surface of this node."""
        self._updated = False
        # Try to update using animation
        if len(self.animation_list) > 0:
            self._do_update(interval)

        # If marked as "need to update",
        # and not being updated using animation,
        # update it using the static on_update() method.
        if self.action_need_update and not self._updated:
            cr = self._get_context()
            self.on_update(cr)
            self.action_need_update = False

    def do_update_recursive(self, cr, x, y, interval):
        """Update this node and all sub-nodes."""
        stack = [(self, x, y, self.z_index)]
        queue = []

        # Create the list of nodes
        while stack:
            current, x, y, z = stack.pop(0)
            # The position (x, y, z-index) is inherited from the parent node.
            node_x = x + current.x
            node_y = y + current.y
            z_index = z + current.z_index
            queue.append((current, node_x, node_y, z_index))
            stack = [(node, node_x, node_y, z_index) \
                    for node in current.children] + stack

        # Sort by z-index
        queue.sort(key=lambda tup: -tup[3])

        while queue:
            current, x, y, z = queue.pop(0)
            current.do_update(interval)
            abs_x = x + current.surface_x + current.dx
            abs_y = y + current.surface_y + current.dy
            cr.set_source_surface(current.surface, abs_x, abs_y)
            cr.paint_with_alpha(current.alpha)

    def do_tick(self, interval):
        """Perform actions and on_tick() method of this node."""
        self.on_tick(interval)
        # Loop over all actions
        tmp_list = self.action_list.copy()
        for name, action in tmp_list.iteritems():
            if not action['started']:
                action['delay'] -= interval
                if action['delay'] <= 0.0:
                    action['started'] = True

            else:
                # Check it's life
                action['elapsed'] += interval
                if action['elapsed'] > action['duration']:
                    if action['loop']:
                        # XXX: if duration is too small?
                        action['elapsed'] -= action['duration']
                    else:
                        if action['cleanup']: action['cleanup']()
                        del self.action_list[name]
                        continue

                phase = 0.0 if action['duration'] <= 0.0 \
                            else action['elapsed'] / action['duration']
                # Perform the action
                action['func'](self, interval, phase)
                if action['update']:
                    # Mark as "need to update".
                    # It is cleaned in do_update_recursive().
                    self.action_need_update = True

    def do_tick_recursive(self, interval):
        """Perform do_tick() for this node and all sub-nodes."""
        queue = [self]
        while queue:
            current = queue.pop(0)
            current.do_tick(interval)
            for node in current.children:
                queue.append(node)

    def do_resize_recursive(self):
        """Perform on_resize() for this node and all sub-nodes."""
        queue = [self]
        while queue:
            current = queue.pop(0)
            current.on_resize()
            for node in current.children:
                queue.append(node)

class Game(object):
    """The application class in pnode framework."""
    def __init__(self, title, width, height, fps):
        """Initialize the game.
        
        @param title: the title of window
        @param fps: the desired fps

        """
        self.title = title
        self.width = width
        self.height = height
        self.timer_interval = int(1000.0/fps)

        self.top_node = None

        self.__quit = False
        self.__keymap = set()
        self.__next_keymap = set()

    def quit(self):
        """Quit from game."""
        self.__quit = True

    def key_up(self, keyname):
        """Return true if the specified key is released.
        
        It returns true only at the instance of releasing the key.

        """
        key = gdk.keyval_from_name(keyname)
        return not (key in self.__keymap) and (key in self.__next_keymap)

    def key_down(self, keyname):
        """Return true if the specified key is pressed.

        It returns true only at the instance of pressing the key.

        """
        key = gdk.keyval_from_name(keyname)
        return (key in self.__keymap) and not (key in self.__next_keymap)

    def on_tick(self, interval):
        """Overload this function to do things in each tick."""
        pass
        
    def do_expose(self, widget, event):
        """The expose function used in gtk framework.
        
        Call do_update_recursive() on top node to update all nodes.
        """
        try:
            cr = widget.window.cairo_create()
            self.top_node.do_update_recursive(cr, 0, 0, self.interval)
        except KeyboardInterrupt:
            self.quit()

    def do_timeout(self):
        """The actual 'tick'."""
        try:
            if self.__quit:
                gtk.main_quit()

            # Calculate elapsed time
            last_time = time()
            self.interval = last_time - self.cur_time
            self.cur_time = last_time
            # Handle time events
            self.on_tick(self.interval)
            # Handle time events of nodes
            self.top_node.do_tick_recursive(self.interval)
            # Take a snapshot of the lastest state of keymap
            self.__keymap = self.__next_keymap.copy()
            # Handle frame update
            self.area.queue_draw()
        except KeyboardInterrupt:
            self.quit()

        return True

    def do_key_press(self, widget, event):
        """The function handling key-press-event.
        
        Record the state of key.
        """
        key = event.keyval
        self.__next_keymap.add(key)
        return True

    def do_key_release(self, widget, event):
        """The function handling key-release-event.
        
        Record the state of key.
        """
        key = event.keyval
        if key in self.__next_keymap:
            self.__next_keymap.remove(key)

        return True

    def do_resize(self, widget, allocation):
        """The function handling resize in gtk framework.
        
        Call do_resize_recursive() on top node to resize all nodes.

        """
        self.width = allocation.width
        self.height = allocation.height
        self.top_node.do_resize_recursive()

    def run(self):
        """The main loop of the game."""
        self.cur_time = time()
        self.interval = 0

        window = gtk.Window()
        window.connect('destroy', gtk.main_quit)
        window.connect('key-press-event', self.do_key_press)
        window.connect('key-release-event', self.do_key_release)
        window.set_default_size(self.width, self.height)
        window.set_title(self.title)

        area = gtk.DrawingArea()
        area.connect('expose-event', self.do_expose)
        area.connect('size-allocate', self.do_resize)
        self.area = area

        window.add(area)
        window.show_all()
        
        gobject.timeout_add(self.timer_interval, self.do_timeout)

        gtk.main()
