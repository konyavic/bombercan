#!/usr/bin/python
# -*- coding: utf-8 -*-

from new import instancemethod
from random import random

MOVE_BLOCKING   = 1 << 0
FIRE_BLOCKING   = 1 << 1
FATAL           = 1 << 2
BREAKABLE       = 1 << 3
CHARACTER       = 1 << 4
ENEMY           = 1 << 5
PLAYER          = 1 << 6
BOMB            = 1 << 7

def stageobj(flag, node):
    try:
        node.stageobj_flags |= flag
    except AttributeError:
        node.stageobj_flags = flag

    return node

def stageobj_has_flag(flag, node):
    try:
        return node.stageobj_flags & flag
    except AttributeError:
        node.stageobj_flags = 0
        return False

def blocking(node):
    return stageobj(MOVE_BLOCKING, node)

def is_blocking(node):
    return stageobj_has_flag(MOVE_BLOCKING, node)

def fireblocking(node):
    return stageobj(FIRE_BLOCKING, node)

def is_fireblocking(node):
    return stageobj_has_flag(FIRE_BLOCKING, node)

def fatal(node):
    return stageobj(FATAL, node)

def is_fatal(node):
    return stageobj_has_flag(FATAL, node)

def player(node):
    return stageobj(PLAYER, node)

def is_player(node):
    return stageobj_has_flag(PLAYER, node)

def enemy(node):
    return stageobj(ENEMY, node)

def is_enemy(node):
    return stageobj_has_flag(ENEMY, node)

def is_breakable(node):
    return stageobj_has_flag(BREAKABLE, node)

def make_breakable(stage, node, on_die=None):
    stageobj(BREAKABLE, node)

    def die(self):
        stage.map.remove_node(node)
        if on_die: on_die()

    node.die = instancemethod(die, node)
    return node

def is_character(node):
    return stageobj_has_flag(CHARACTER, node)

def make_character(stage, node, 
        speed=4.0, on_move=None, on_stop=None, on_die=None):

    stageobj(CHARACTER, node)
    node.speed = speed

    def move(self, dir):
        def move_action(self, interval):
            delta = interval * self.speed * stage.map.get_cell_size()
            if dir == 'up':
                stage.move_object(self, 0, -delta)
            elif dir == 'down':
                stage.move_object(self, 0, delta)
            elif dir == 'left':
                stage.move_object(self, -delta, 0)
            elif dir == 'right':
                stage.move_object(self, delta, 0)

        self.add_action(dir, move_action, loop=True, update=False)
        if on_move: on_move(dir)
    
    def stop(self, dir=None):
        # XXX
        if dir:
            self.remove_action(dir)
            if on_stop: on_stop(dir)
        else:
            self.remove_action('up')
            self.remove_action('down')
            self.remove_action('right')
            self.remove_action('left')
            if on_stop: 
                on_stop('up')
                on_stop('down')
                on_stop('right')
                on_stop('left')

    node.move = instancemethod(move, node)
    node.stop = instancemethod(stop, node)
    return node

def make_bomber(stage, node,
        bomb_delay=5, bomb_power=3, bomb_count=1, on_bomb=None):

    node.bomb_delay = bomb_delay
    node.bomb_power = bomb_power
    node.bomb_count = bomb_count

    def bomb(self):
        stage.place_bomb(*stage.map.get_cell(self), 
                delay=self.bomb_delay, power=self.bomb_power)

        if on_bomb: on_bomb()

    node.bomb = instancemethod(bomb, node)
    return node

def make_simpleai(stage, node, timeout=3.0):
    node.ai_timecount=timeout * random()
    node.ai_old_pos = (node.x, node.y)

    def on_tick(self, interval):
        self.ai_timecount += interval
        if (self.ai_timecount < timeout
                and self.ai_old_pos != (self.x, self.y)):
            return
        
        self.ai_timecount = 0.0
        self.ai_old_pos = (node.x, node.y)
        dir = ['up', 'down', 'left', 'right'][int(random() * 4)]
        self.stop()
        self.move(dir)

    node.on_tick = instancemethod(on_tick, node)
    return node

def make_trackingfloor(stage, node, x, y, on_enter, on_leave):
    node.entered = False

    def on_tick(self, interval):
        map = stage.map
        player = stage.player
        is_same_pos = ((x, y) == map.get_cell(player))
        if is_same_pos and not self.entered:
            self.entered = True
            on_enter()
        elif not is_same_pos and self.entered:
            self.entered = False
            on_leave()

    node.on_tick = instancemethod(on_tick, node)
    return node

def is_bomb(node):
    return stageobj_has_flag(BOMB, node)

def make_bomb(node, delay, power, on_explode):
    stageobj(BOMB, node)

    node.bomb_delay = delay
    node.bomb_power = power
    
    def on_tick(self, interval):
        self.bomb_delay -= interval
        if self.bomb_delay < 0:
            on_explode()

    node.on_tick = instancemethod(on_tick, node)
    return node
