#!/usr/bin/python
# -*- coding: utf-8 -*-

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
    def __init__(self, parent, style, map_size):
        super(MapContainer, self).__init__(parent, style)
        self.map_size = map_size

        self.__map = [ [ [] for y in xrange(0, self.map_size[1]) ] 
                for x in xrange(0, self.map_size[0]) ]
        self.__delta = {}
        self.__cell = {}
        self.__orig_size = {}
        self.__orig_delta = {}
        self.__orig_z_index = {}

        self.__update_cell_size()
        self.__orig_cell_size = self.__cell_size
    
    def __update_cell_size(self):
        self.__cell_size = min(self.width / self.map_size[0], 
                self.height / self.map_size[1])
        self.__padding = ((self.width - self.__cell_size * self.map_size[0]) / 2,
                (self.height - self.__cell_size * self.map_size[1]) / 2) 

    def __update_pos(self, node, x, y, width, height, z_index):
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
        return -y

    def on_resize(self):
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
        return self.__cell_size

    def add_node(self, node, x, y, dx=0, dy=0):
        Node.add_node(self, node)
        self.__map[x][y].append(node)
        self.__delta[node] = (dx, dy)
        self.__orig_delta[node] = self.__delta[node]
        self.__cell[node] = (x, y)
        self.__orig_size[node] = (node.width, node.height)
        self.__orig_z_index[node] = node.z_index

        pos = self.get_cell_pos(x, y)
        self.__update_pos(node, pos[0], pos[1], 
                node.width, node.height, 
                node.z_index + self.__get_z_index_delta(y))

    def remove_node(self, node):
        Node.remove_node(self, node)
        cell = self.get_cell(node)
        self.__map[cell[0]][cell[1]].remove(node)
        del self.__delta[node]
        del self.__orig_delta[node]
        del self.__cell[node]
        del self.__orig_size[node]
        del self.__orig_z_index[node]

    def get_cell(self, node):
        return self.__cell[node]

    def get_cell_nodes(self, x, y):
        return self.__map[x][y]

    def move_to(self, node, x, y):
        cell = self.get_cell(node)
        self.__map[cell[0]][cell[1]].remove(node)
        self.__map[x][y].append(node)
        self.__cell[node] = (x, y)

        pos = self.get_cell_pos(x, y)
        self.__update_pos(node, pos[0], pos[1], 
                node.width, node.height, 
                self.__orig_z_index[node] + self.__get_z_index_delta(y))

    def move_pos(self, node, delta_x, delta_y):
        dx, dy = self.__delta[node]
        new_x = node.x + delta_x - dx
        new_y = node.y + delta_y - dy

        top_left = self.get_cell_pos(0, 0)
        bottom_right = self.get_cell_pos(self.map_size[0] - 1, 
                self.map_size[1] - 1)

        if new_x < top_left[0]:
            new_x = top_left[0]
        elif new_x > bottom_right[0]:
            new_x = bottom_right[0]
        elif new_y < top_left[1]:
            new_y = top_left[1]
        elif new_y > bottom_right[1]:
            new_y = bottom_right[1]

        half_cell = self.__cell_size / 2
        new_cell = (
                int((new_x - self.__padding[0] + half_cell) / self.__cell_size),
                int((new_y - self.__padding[1] + half_cell) / self.__cell_size)
                )
        new_cell = self.__restrict_pos(*new_cell)
        old_cell = self.get_cell(node)

        self.__map[old_cell[0]][old_cell[1]].remove(node)
        self.__map[new_cell[0]][new_cell[1]].append(node)
        self.__cell[node] = new_cell
        self.__update_pos(node, new_x, new_y, node.width, node.height, 
                (self.__orig_z_index[node] + 
                    self.__get_z_index_delta(new_cell[1]))
                )

    def get_cell_pos(self, x, y):
        return (
                self.__padding[0] + x * self.__cell_size, 
                self.__padding[1] + y * self.__cell_size
                )

    def get_node_pos(self, node):
        delta = self.__delta[node]
        return (node.x - delta[0], node.y - delta[1])

class Label(Node):
    def __init__(self, parent, style, 
            text='', font='', color=(0, 0, 0, 1), bgcolor=(0, 0, 0, 0), 
            margin=(10, 10, 10, 10), center=False):

        super(Label, self).__init__(parent, style)
        self.text = text
        self.font = font
        self.color = color
        self.bgcolor=bgcolor
        # XXX: margin should be merged into node style
        self.margin = margin
        self.center = center

        self._font = pango.FontDescription(self.font)

    def set_text(self, text):
        self.text = text
        self.repaint()

    def on_update(self, cr):
        margin = self.margin
        w = self.width - margin[1] - margin[3]
        h = self.height - margin[0] - margin[2]
        cr.set_source_rgba(*self.bgcolor)
        cr.rectangle(margin[3], margin[0], w, h)
        cr.fill()

        # adjust the size by scaling before showing the text
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
    def __init__(self, parent, style, 
            labels, font='', color=(0, 0, 0, 1), bgcolor=(0, 0, 0, 0), curser=None):

        super(Selections, self).__init__(parent, style)

        self.labels = labels
        self.font = font
        self.color = color
        self.bgcolor = bgcolor

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
            center=True
            ) for i in range(0, len(self.labels)) ]

        for label in self._labels:
            self.add_node(label)

        self.curser = curser
        self.add_node(curser)
        self.select(0)

    def on_update(self, cr):
        cr.set_source_rgba(*self.bgcolor)
        cr.paint()

    def on_resize(self):
        Node.on_resize(self)
        # resize the selected label here to get the updated position
        # XXX: bad approach
        self._labels[self.selected].on_resize()
        self.select(self.selected)

    def select(self, i):
        self.selected = i
        self.curser.set_style({
            'top': self._labels[i].y,
            'left': self._labels[i].x - self._labels[i].height,
            'width': self._labels[i].height,
            'height': self._labels[i].height,
            })

        # XXX: merge into motions
        def _shake(self, interval, phase):
            a = (pi / 8) * (1.0 - phase)
            self.set_rotate(a * sin(phase * 8 * 2 * pi))

        self._labels[self.selected].add_action('shake', _shake, duration=2, update=True)

    def select_up(self):
        i = (self.selected - 1) % len(self.labels)
        self.select(i)

    def select_down(self):
        i = (self.selected + 1) % len(self.labels)
        self.select(i)

class MessageBox(Node):
    def __init__(self, parent, style, opt):
        super(MessageBox, self).__init__(parent, style)
        self.showing = False

    def __draw_box(self, cr, box_width, box_height, alpha):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        cr.set_source_rgba(0, 0, 0, alpha)
        cr.rectangle(0, 0, box_width, box_height)
        cr.fill()

    def on_update(self, cr):
        if self.showing:
            self.__draw_box(cr, self.width, self.height, 0.5)
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
