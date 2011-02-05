#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node

class MapContainer(Node):
    def __init__(self, parent, style, opt):
        Node.__init__(self, parent, style)

        # input attributes
        self.map_size = opt['$map size']

        # private attributes
        self.__map = [[ [] for y in xrange(0, self.map_size[1]) ] for x in xrange(0, self.map_size[0]) ]
        self.__delta = {}
        self.__cell = {}
        self.__orig_size = {}
        self.__orig_delta = {}
        self.__orig_z_index = {}

        self.__update_cell_size()
        self.__orig_cell_size = self.__cell_size
    
    def __update_cell_size(self):
        self.__cell_size = min(self.width / self.map_size[0], self.height / self.map_size[1])
        self.__padding = (
                (self.width - self.__cell_size * self.map_size[0]) / 2,
                (self.height - self.__cell_size * self.map_size[1]) / 2
                )

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
                    self.__update_pos(node, pos[0], pos[1], new_width, new_height, node.z_index)
    
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
        self.__update_pos(node, pos[0], pos[1], node.width, node.height, node.z_index + self.__get_z_index_delta(y))

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
        self.__update_pos(node, pos[0], pos[1], node.width, node.height, self.__orig_z_index[node] + self.__get_z_index_delta(y))

    def move_pos(self, node, delta_x, delta_y):
        dx, dy = self.__delta[node]
        new_x = node.x + delta_x - dx
        new_y = node.y + delta_y - dy

        top_left = self.get_cell_pos(0, 0)
        bottom_right = self.get_cell_pos(self.map_size[0] - 1, self.map_size[1] - 1)
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
                self.__orig_z_index[node] + self.__get_z_index_delta(new_cell[1]))

    def get_cell_pos(self, x, y):
        return (
                self.__padding[0] + x * self.__cell_size, 
                self.__padding[1] + y * self.__cell_size
                )

    def get_node_pos(self, node):
        delta = self.__delta[node]
        return (node.x - delta[0], node.y - delta[1])