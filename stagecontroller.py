#!/usr/bin/python
# -*- coding: utf-8 -*-

from new import instancemethod
from random import random

BLOCKING    = 1 << 0
FATAL       = 1 << 1
BREAKABLE   = 1 << 2
CHARACTER   = 1 << 3

def stageobj(flag, obj):
    try:
        obj.stageobj_flags |= flag
    except AttributeError:
        obj.stageobj_flags = flag

    return obj

def stageobj_has_flag(flag, obj):
    try:
        return obj.stageobj_flags
    except AttributeError:
        obj.stageobj_flags = 0
        return False

def blocking(obj):
    return stageobj(BLOCKING, obj)

def is_blocking(obj):
    return stageobj_has_flag(BLOCKING, obj)

def fatal(obj):
    return stageobj(FATAL, obj)

def is_fatal(obj):
    return stageobj_has_flag(FATAL, obj)

def breakable(obj):
    return stageobj(BREAKABLE, obj)

def is_breakable(obj):
    return stageobj_has_flag(BREAKABLE, obj)

def bomb():
    pass

def is_character(obj):
    return stageobj_has_flag(CHARACTER, obj)

def character(stage, node, 
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

    def die(self):
        if on_die: on_die()

    # setup methods
    node.move = instancemethod(move, node)
    node.stop = instancemethod(stop, node)
    node.die = instancemethod(die, node)
    return node

def bombmaker(stage, node,
        bomb_delay=5, bomb_power=2, bomb_count=1, on_bomb=None):

    node.bomb_delay = bomb_delay
    node.bomb_power = bomb_power
    node.bomb_count = bomb_count

    def bomb(self):
        stage.place_bomb(*stage.map.get_cell(self), 
                delay=self.bomb_delay, power=self.bomb_power)

        if on_bomb: on_bomb()

    node.bomb = instancemethod(bomb, node)
    return node

def simpleai(stage, node, timeout=3.0):
    node.timecount=timeout

    def on_tick(self, interval):
        self.timecount += interval
        if self.timecount < timeout:
            return
        
        self.timecount = 0.0
        dir = ['up', 'down', 'left', 'right'][int(random() * 4)]
        self.stop()
        self.move(dir)

    node.on_tick = instancemethod(on_tick, node)
    return node
