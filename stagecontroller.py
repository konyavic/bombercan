#!/usr/bin/python
# -*- coding: utf-8 -*-

from new import instancemethod
from random import random

BLOCK           = 1 << 0
CHARACTER       = 1 << 1
FIRE_BLOCKING   = 1 << 2
BREAKABLE       = 1 << 3
ENEMY           = 1 << 4
PLAYER          = 1 << 5
BOMB            = 1 << 6
FIRE            = 1 << 7
DEAD            = 1 << 8

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

#
# fireblocking / breakable
#

def fireblocking(node):
    return stageobj(FIRE_BLOCKING, node)

def is_fireblocking(node):
    return stageobj_has_flag(FIRE_BLOCKING, node)

def is_breakable(node):
    return stageobj_has_flag(BREAKABLE, node)

def make_breakable(stage, node, on_die=None):
    stageobj(BREAKABLE, node)

    def die(self):
        stage.map.remove_node(node)
        if on_die: on_die()

    node.die = instancemethod(die, node)
    return node

#
# player / enemy
#

def player(node):
    return stageobj(PLAYER, node)

def is_player(node):
    return stageobj_has_flag(PLAYER, node)

def enemy(node):
    return stageobj(ENEMY, node)

def is_enemy(node):
    return stageobj_has_flag(ENEMY, node)

#
# block / character
#

def block(node):
    return stageobj(BLOCK, node)

def is_block(node):
    return stageobj_has_flag(BLOCK, node)

def dead(node):
    return stageobj(DEAD, node)

def is_dead(node):
    return stageobj_has_flag(DEAD, node)

def is_character(node):
    return stageobj_has_flag(CHARACTER, node)

def make_character(stage, node, 
        speed=4.0, on_move=None, on_stop=None, on_go_die=None):

    stageobj(CHARACTER, node)
    node.speed = speed
    node.dir_queue = []

    def move_action(self, interval, phase):
        if len(self.dir_queue) == 0:
            return

        delta = interval * self.speed * stage.map.get_cell_size()
        dir = self.dir_queue[0]
        if dir == 'up':
            stage.move_object(self, 0, -delta)
        elif dir == 'down':
            stage.move_object(self, 0, delta)
        elif dir == 'left':
            stage.move_object(self, -delta, 0)
        elif dir == 'right':
            stage.move_object(self, delta, 0)

    def move(self, dir):
        if dir in self.dir_queue:
            self.dir_queue.remove(dir)

        self.dir_queue.insert(0, dir)
        self.add_action('move', move_action, loop=True)
        if on_move: on_move(dir)
    
    def stop(self, dir=None):
        # XXX: key event may be lost
        if len(self.dir_queue) > 0 and dir == self.dir_queue[0]:
            self.dir_queue.pop(0)
            if on_stop: on_stop(dir)
            if len(self.dir_queue) > 0:
                dir = self.dir_queue[0]
                if on_move: on_move(dir)
            else:
                self.remove_action('move')
        elif dir in self.dir_queue:
            self.dir_queue.remove(dir)
        else:
            self.reset_actions()
            if on_stop: 
                on_stop('up')
                on_stop('down')
                on_stop('right')
                on_stop('left')

    def go_die(self):
        dead(self)
        if on_go_die:
            on_go_die()
        else:
            self.die()

    node.move = instancemethod(move, node)
    node.stop = instancemethod(stop, node)
    node.go_die = instancemethod(go_die, node)
    return node

def make_bomber(stage, node,
        bomb_delay=5, bomb_power=3, bomb_count=1, on_bomb=None):

    node.bomb_delay = bomb_delay
    node.bomb_power = bomb_power
    node.bomb_count = bomb_count

    def bomb(self):
        stage.put_bomb(*stage.map.get_cell(self), 
                delay=self.bomb_delay, power=self.bomb_power)

        if on_bomb: on_bomb()

    node.bomb = instancemethod(bomb, node)
    return node

def make_simpleai(stage, node, timeout=1.0):
    node.ai_timecount=timeout * random()
    node.ai_old_pos = (node.x, node.y)
    node.is_ai_stopped = False

    def on_tick(self, interval):
        if self.is_ai_stopped:
            return

        self.ai_timecount += interval
        # XXX
        #if (self.ai_timecount < timeout
        #        and self.ai_old_pos != (self.x, self.y)):
        if (self.ai_timecount < timeout):
            return
        
        self.ai_timecount = 0.0
        self.ai_old_pos = (node.x, node.y)
        dir = ['up', 'down', 'left', 'right'][int(random() * 4)]
        self.stop()
        self.move(dir)

    def stop_ai(self):
        self.is_ai_stopped = True

    node.on_tick = instancemethod(on_tick, node)
    node.stop_ai = instancemethod(stop_ai, node)
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

#
# fire and bomb
#

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

def is_fire(node):
    return stageobj_has_flag(FIRE, node)

def fire(node):
    return stageobj(FIRE, node)
