#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module contains objects that handle the graphics 
and control logic altogether by themselves.

"""

from math import pi
from math import sin

import gtk
import gtk.gdk as gdk
import gobject
import cairo
import pango
import pangocairo

from pnode import Node
from objects import Bomb

class MapContainer(Node):
    """The core of the tile-based stage.
    
    Basically, it has a matrix of cells.
    Objects could be added into this container, 
    without conforming to the size of a cell.
    This contianer will remember the size when the object was added,
    and automatically resize it when on_resize() occurs.

    Moreover, it also provides "smooth move" of objects between cells.
    Objects moving between cells do not have to "jump", 
    but could shift smoothly from one cell to another.

    Determining which cell does the object belong to 
    is important for collision detection.
    In this implementation, when an object is moving to the next cell, 
    it still "belongs" to the original cell
    until it becomes half in the next cell and half in the original cell.
    Then, in the next step, it will run into the next cell.

    """
    def __init__(self, parent, style, map_size):
        """Initialize the map (the matix of cells) and 
        dictionaries for resizing.

        @param map_size: the size of this map
        @type map_size: a list of two integers

        """
        super(MapContainer, self).__init__(parent, style)
        self.map_size = map_size

        self.__map = [ [ [] for y in xrange(0, self.map_size[1]) ] 
                for x in xrange(0, self.map_size[0]) ]

        # The hash key of dictionaries bellow are objects
        # delta = object's actual position - cell's position
        self.__delta = {}   
        self.__cell = {}    # the reference to the cell
        
        # Due to resize, the size, delta, and z-index will change.
        # The original value are stored in dictionaries bellow.
        self.__orig_size = {}       # object's original size
        self.__orig_delta = {}      # object's original delta
        self.__orig_z_index = {}    # object's original z-index

        self.__update_cell_size()
        self.__orig_cell_size = self.__cell_size
    
    def __update_cell_size(self):
        """Update the cell size of this container (after resize)."""
        self.__cell_size = min(self.width / self.map_size[0], 
                self.height / self.map_size[1])
        self.__padding = ((self.width - self.__cell_size * self.map_size[0]) / 2,
                (self.height - self.__cell_size * self.map_size[1]) / 2) 

    def __update_pos(self, node, x, y, width, height, z_index):
        """Update the position (style) of target object."""
        dx, dy = self.__delta[node]
        style = {
                'left': x + dx,
                'top': y + dy,
                'width': width,
                'height': height,
                'z-index': z_index
                }
        node.set_style(style)

    def __restrict_pos(self, x, y):
        """Check and adjust the input position 
        if it exceed the size of this map.
        
        @return: the adjusted cell

        """
        if x < 0:
            x = 0
        elif x >= self.map_size[0]:
            x = self.map_size[0] - 1

        if y < 0:
            y = 0
        elif y >= self.map_size[1]:
            y = self.map_size[1] - 1

        return (x, y)

    def __get_z_index_delta(self, y):
        """Return the adjustment to z-index.
        
        Currently it simply returns the inverse of the y value 
        of it's position.

        @return: the adjustment to z-index

        """
        return -y

    def on_resize(self):
        """Perform the magic of resize.
        
        It first calculates the ratio of change, 
        then apply the change to all sub-objects.

        """
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
                    self.__update_pos(node, pos[0], pos[1], 
                            new_width, new_height, node.z_index)
    
    def get_cell_size(self):
        """Return the cell size of this map."""
        return self.__cell_size

    def add_node(self, node, x, y, dx=0, dy=0):
        """Add the object to target cell, with optional delta.

        The position and z-index of this object will be adjusted.
        
        @param x: x index of target cell
        @param y: y index of target cell
        @param dx: the delta on x to the position of target cell
        @param dy: the delta on y to the position of target cell

        """
        ratio = float(self.__cell_size) / self.__orig_cell_size
        Node.add_node(self, node)
        self.__map[x][y].append(node)
        self.__delta[node] = (dx, dy)
        self.__orig_delta[node] = (dx / ratio, dy / ratio)
        self.__cell[node] = (x, y)
        self.__orig_size[node] = (node.width / ratio, node.height / ratio)
        self.__orig_z_index[node] = node.z_index

        pos = self.get_cell_pos(x, y)
        self.__update_pos(node, pos[0], pos[1], 
                node.width, node.height, 
                node.z_index + self.__get_z_index_delta(y))

    def remove_node(self, node):
        """Remove the object from the map.

        Also clean up the dictionary.

        """
        Node.remove_node(self, node)
        cell = self.get_cell(node)
        self.__map[cell[0]][cell[1]].remove(node)
        del self.__delta[node]
        del self.__orig_delta[node]
        del self.__cell[node]
        del self.__orig_size[node]
        del self.__orig_z_index[node]

    def get_cell(self, node):
        """Return the cell which target object belongs to.
        
        @return: a list of two integers representing the index of the cell
        """
        return self.__cell[node]

    def get_cell_nodes(self, x, y):
        """Return all objects in target cell.
        
        @return: a list of pnode.Node
        """
        return self.__map[x][y]

    def move_to(self, node, x, y):
        """Move the object to target cell.
        
        Compared with move_pos(), 
        this method will make the object suddenly "jump" to target cell.

        """
        cell = self.get_cell(node)
        self.__map[cell[0]][cell[1]].remove(node)
        self.__map[x][y].append(node)
        self.__cell[node] = (x, y)

        pos = self.get_cell_pos(x, y)
        self.__update_pos(node, pos[0], pos[1], 
                node.width, node.height, 
                self.__orig_z_index[node] + self.__get_z_index_delta(y))

    def move_pos(self, node, delta_x, delta_y):
        """Move the object smoothly.

        This function will change the belonging cell 
        of target object automatically.

        @param delta_x: the delta on x 
        @param delta_y: the delta on y

        """
        dx, dy = self.__delta[node]
        new_x = node.x + delta_x - dx
        new_y = node.y + delta_y - dy

        top_left = self.get_cell_pos(0, 0)
        bottom_right = self.get_cell_pos(self.map_size[0] - 1, 
                self.map_size[1] - 1)

        # Restrict the new position in the range of this map
        if new_x < top_left[0]:
            new_x = top_left[0]
        elif new_x > bottom_right[0]:
            new_x = bottom_right[0]
        elif new_y < top_left[1]:
            new_y = top_left[1]
        elif new_y > bottom_right[1]:
            new_y = bottom_right[1]

        # Calculate the new cell it should belongs to
        half_cell = self.__cell_size / 2
        new_cell = (
                int((new_x - self.__padding[0] + half_cell) / self.__cell_size),
                int((new_y - self.__padding[1] + half_cell) / self.__cell_size)
                )
        new_cell = self.__restrict_pos(*new_cell)
        old_cell = self.get_cell(node)

        # Move the object from old cell to new cell
        self.__map[old_cell[0]][old_cell[1]].remove(node)
        self.__map[new_cell[0]][new_cell[1]].append(node)
        self.__cell[node] = new_cell
        self.__update_pos(node, new_x, new_y, node.width, node.height, 
                (self.__orig_z_index[node] + 
                    self.__get_z_index_delta(new_cell[1]))
                )

    def get_cell_pos(self, x, y):
        """Return the position of target cell."""
        return (
                self.__padding[0] + x * self.__cell_size, 
                self.__padding[1] + y * self.__cell_size
                )

    def get_node_pos(self, node):
        """Return the position of target object WITHOUT delta."""
        delta = self.__delta[node]
        return (node.x - delta[0], node.y - delta[1])

class Label(Node):
    """The basic object to display text."""
    def __init__(self, parent, style, 
            text='', font='', color=(0, 0, 0, 1), bgcolor=(0, 0, 0, 0), 
            margin=(10, 10, 10, 10), center=False):
        """Initialize the label.
        
        @param text: the text to be displayed
        @param font: the description of font (in pango format)
        @param color: the rgba value of text color
        @param bgcolor: the rgba value of background color
        @param margin: the margin between the border and the text 
            (in this order: up, right, down, left)
        @param center: should center the text?

        """
        super(Label, self).__init__(parent, style)
        self.text = text
        self.font = font
        self.color = color
        self.bgcolor=bgcolor
        # XXX: "margin" should be merged into node style
        self.margin = margin
        self.center = center

        self._font = pango.FontDescription(self.font)

    def set_text(self, text):
        """Set the text."""
        self.text = text
        self.repaint()

    def on_update(self, cr):
        margin = self.margin
        w = self.width - margin[1] - margin[3]
        h = self.height - margin[0] - margin[2]

        # Draw the background
        cr.set_source_rgba(*self.bgcolor)
        cr.rectangle(margin[3], margin[0], w, h)
        cr.fill()

        # Adjust the size by scaling before showing the text
        cr.set_source_rgba(*self.color)
        cr.move_to(0, 0)
        pcr = pangocairo.CairoContext(cr)
        layout = pcr.create_layout()
        layout.set_text(self.text)
        layout.set_font_description(self._font)
        size = layout.get_pixel_size()
        factor = min(w / float(size[0]), h / float(size[1]))
        if self.center:
            cr.move_to(
                    ((self.width - factor * size[0]) / 2.0), 
                    ((self.height - factor * size[1]) / 2.0))
        else:
            cr.move_to(margin[3], margin[0])

        cr.scale(factor, factor)
        pcr.show_layout(layout)
    
class Selections(Node):
    """The menu that has several selections."""
    def __init__(self, parent, style, 
            labels, font='', color=(0, 0, 0, 1), bgcolor=(0, 0, 0, 0), 
            margin=(10, 10, 10, 10), cursor=None, center=True):
        """Initialize the menu.
        
        @param labels: a list of strings
        @param font: the description of font (in pango format)
        @param color: the rgba value of text color
        @param bgcolor: the rgba value of background color
        @param margin: the margin of each label
        @param cursor: the object to be used as the cursor
        @param center: should center the text?

        """

        super(Selections, self).__init__(parent, style)

        self.labels = labels
        self.font = font
        self.color = color
        self.bgcolor = bgcolor

        # Create the label component for each label
        self._labels = [ Label(
            parent=self,
            style={
                'top': str(i * 100 / float(len(self.labels))) + '%',
                'height': str(100 / float(len(self.labels))) + '%',
                'align': 'center'
                },
            text=self.labels[i],
            color=self.color,
            font=self.font,
            margin=margin,
            center=center
            ) for i in range(0, len(self.labels)) ]

        for label in self._labels:
            self.add_node(label)

        if cursor:
            self.cursor = cursor
            self.add_node(cursor)
        else:
            self.cursor = None

        self.select(0)

    def on_update(self, cr):
        # Draw the background
        cr.rectangle(0, 0, self.width, self.height)
        cr.set_source_rgba(*self.bgcolor)
        cr.fill()

    def on_resize(self):
        Node.on_resize(self)
        # Resize the selected label here to get the updated position for cursor
        # XXX: bad approach
        self._labels[self.selected].on_resize()
        self.select(self.selected)

    def select(self, i):
        """Select target option.
        
        Also make the selected text shake.
        """
        self.selected = i
        if self.cursor:
            self.cursor.set_style({
                'top': self._labels[i].y,
                'left': self._labels[i].x - self._labels[i].height,
                'width': self._labels[i].height,
                'height': self._labels[i].height}
                )

        # XXX: "shake" should be merged into motions
        def _shake(self, interval, phase):
            a = (pi / 8) * (1.0 - phase)
            self.set_rotate(a * sin(phase * 8 * 2 * pi))

        self._labels[self.selected].add_action('shake', _shake, duration=2, update=True)

    def select_up(self):
        """Select upward."""
        i = (self.selected - 1) % len(self.labels)
        self.select(i)

    def select_down(self):
        """Select downward."""
        i = (self.selected + 1) % len(self.labels)
        self.select(i)

class MessageBox(Node):
    """A prototype for message box (to be implemented)."""
    def __init__(self, parent, style):
        super(MessageBox, self).__init__(parent, style)
        self.showing = False

        self.label = Label(self, {}, text=u' ', font='MS Gothic', 
                color=(1, 1, 1, 1), center=True)
        self.add_node(self.label)
        self.label.set_alpha(0)

    def set_text(self, text):
        self.label.set_text(text)

    def _draw_box(self, cr, box_width, box_height, alpha):
        cr.set_source_rgba(0, 0, 0, alpha)
        cr.rectangle(0, 0, box_width, box_height)
        cr.fill()

    def on_update(self, cr):
        if self.showing:
            self._draw_box(cr, self.width, self.height, 0.5)

    def show(self, b):
        def show_animation(self, cr, phase):
            self._draw_box(cr,
                    self.width * 2 * min(0.5, phase), 
                    self.height * 2 * max(0.05, phase - 0.5), 
                    0.5 * phase)

        def hide_animation(self, cr, phase):
            self._draw_box(cr,
                    self.width * (1 - phase), 
                    self.height * (1 - phase), 
                    0.5 * (1 - phase))

        self.showing = b
        if b:
            self.reset_animations()
            self.set_animation(show_animation, duration=0.5, loop=False, 
                    cleanup=lambda: self.label.set_alpha(1))
        else:
            self.reset_animations()
            self.set_animation(hide_animation, duration=0.1, loop=False,
                    cleanup=lambda: self.label.set_alpha(0))

    def toggle(self):
        if self.showing:
            self.show(False)
        else:
            self.show(True)
