#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This modules contains 'controllers' (or 'adaptors') for StageScene.

The idea is that, 
while the objects in module 'objects' are dealing with graphics only,
the make_xxx() functions in this module add control logic to those objects,
then we can use them in StageScene.

"""

from new import instancemethod
from random import random
from math import pi

BLOCK           = 1 << 0
CHARACTER       = 1 << 1
FIRE_BLOCKING   = 1 << 2
BREAKABLE       = 1 << 3
ENEMY           = 1 << 4
PLAYER          = 1 << 5
BOMB            = 1 << 6
FIRE            = 1 << 7
DEAD            = 1 << 8
ITEM            = 1 << 9
BOMB_EATER      = 1 << 10
FLYING          = 1 << 11

def stageobj(flag, node):
    """Set a flag of the node.
    
    @type node: pnode.Node
    @return: the node

    """
    try:
        node.stageobj_flags |= flag
    except AttributeError:
        node.stageobj_flags = flag

    return node

def stageobj_has_flag(flag, node):
    """Test a flag of the node.
    
    @type node: pnode.Node

    """
    try:
        return node.stageobj_flags & flag
    except AttributeError:
        node.stageobj_flags = 0
        return False

#
# fireblocking / breakable
#

def fireblocking(node):
    """Mark the node as a hard block."""
    return stageobj(FIRE_BLOCKING, node)

def is_fireblocking(node):
    return stageobj_has_flag(FIRE_BLOCKING, node)

def is_breakable(node):
    return stageobj_has_flag(BREAKABLE, node)

def make_breakable(stage, node, on_die=None):
    """Make the node into a breakable node 
    that could be destroyed by bombs.
    
    @param on_die: the callback function 
        called when the node is going to be destroyed

    """
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
    """Mark the node as the player."""
    return stageobj(PLAYER, node)

def is_player(node):
    return stageobj_has_flag(PLAYER, node)

def enemy(node):
    """Mark the node as an enemy."""
    return stageobj(ENEMY, node)

def is_enemy(node):
    return stageobj_has_flag(ENEMY, node)

#
# block / character
#

def block(node):
    """Mark the node as a soft block."""
    return stageobj(BLOCK, node)

def is_block(node):
    return stageobj_has_flag(BLOCK, node)

def dead(node):
    """Mark the node as dead."""
    return stageobj(DEAD, node)

def is_dead(node):
    return stageobj_has_flag(DEAD, node)

def is_character(node):
    return stageobj_has_flag(CHARACTER, node)

def make_character(stage, node, 
        speed=4.0, on_move=None, on_stop=None, on_go_die=None):
    """Make the node into a movable character.
    
    @param on_move: the callback function called when it moves
    @param on_stop: the callback function called when it stops
    @param on_go_die: the callback function called 
        when it is destroyed bombs. Use this function to launch animations.

    """

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
        bomb_delay=5, bomb_power=1, bomb_count=1, on_bomb=None):
    """Make the node into a bomber character.
    
    @param on_bomb: the callback function called when it puts bombs

    """

    node.bomb_delay = bomb_delay
    node.bomb_power = bomb_power
    node.bomb_count = bomb_count
    node.cur_bomb_count = 0

    def bomb(self):
        if self.cur_bomb_count >= node.bomb_count:
            return

        self.cur_bomb_count += 1
        stage.put_bomb(*stage.map.get_cell(self),
                delay=self.bomb_delay, power=self.bomb_power, bomber=self)

        if on_bomb: on_bomb()

    node.bomb = instancemethod(bomb, node)
    return node

def make_simpleai(stage, node, timeout=1.0):
    """A stupid AI for enemies.

    Just moving around randomly.
    
    @type stage: stagescene.StageScene

    """
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

def make_bomberai(stage, node, timeout=1.0):
    """A stupid AI for bombers.
    
    Just moving around and put bombs randomly.

    @type stage: stagescene.StageScene

    """
    node.ai_timecount=timeout * random()
    node.ai_old_pos = (node.x, node.y)
    node.is_ai_stopped = False

    def on_tick(self, interval):
        # XXX: need more adjustment
        if self.is_ai_stopped:
            return

        self.ai_timecount += interval
        if (self.ai_timecount < timeout):
            return
        
        self.ai_timecount = 0.0
        self.ai_old_pos = (node.x, node.y)
        if random() > 0.5:
            self.bomb()
            if len(self.dir_queue) > 0:
                dir = self.dir_queue[0]
                if dir == 'up': 
                    dir = 'down'
                elif dir == 'down': 
                    dir = 'up'
                elif dir == 'right': 
                    dir = 'left'
                elif dir == 'left': 
                    dir = 'right'
            else:
                dir = ['up', 'down', 'left', 'right'][int(random() * 4)]
            self.stop()
            self.move(dir)
        else:
            dir = ['up', 'down', 'left', 'right'][int(random() * 4)]
            self.stop()
            self.move(dir)

    def stop_ai(self):
        self.is_ai_stopped = True

    node.on_tick = instancemethod(on_tick, node)
    node.stop_ai = instancemethod(stop_ai, node)
    return node

def make_trackingfloor(stage, node, x, y, on_enter, on_leave):
    """Make the node detect enter and leave event of the player.
    
    Used only by Floor object.
    
    @type node: pnode.Node
    @type stage: stagescene.StageScene
    @param on_enter: the callback function called 
        when the player entered the same cell
    @param on_leave: the callback function called
        when the player left this cell

    """
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

def make_bomb(node, delay, power, bomber, on_explode):
    """Make the node into a bomb.
    
    @type node: pnode.Node
    @param on_explode: the callback function called 
        when the countdown ends

    """
    stageobj(BOMB, node)

    node.bomb_delay = delay
    node.bomb_power = power
    node.bomber = bomber
    
    def on_tick(self, interval):
        self.bomb_delay -= interval
        if self.bomb_delay < 0:
            on_explode()

    node.on_tick = instancemethod(on_tick, node)
    return node

def is_fire(node):
    return stageobj_has_flag(FIRE, node)

def fire(node):
    """Mark the node as a fire caused by bombs."""
    return stageobj(FIRE, node)

def is_item(node):
    return stageobj_has_flag(ITEM, node)

def make_item(stage, node, on_eat=None):
    """Make the node into an item.
    
    @type node: pnode.Node
    @param on_eat: the callback function called 
        when the player ate this item. 
        Use this function to implement the effect of the item.

    """
    stageobj(ITEM, node)

    def eat(self, who):
        if on_eat: on_eat(who)
        stage.map.remove_node(self)
        stage.add_node(self)
        style = self.style
        style['left'] = self.x + stage.map.x
        style['top'] = self.y + stage.map.y
        self.set_style(style)

        # Fly away and rotate
        def _eat_action(self, interval, phase):
            cell_size = stage.map.get_cell_size()
            self.set_alpha(1 - phase)
            self.set_translation(0, -phase * cell_size * 3)
            self.set_rotate(phase * pi * 4)

        self.add_action('eaten', _eat_action, duration=1.5, update=True)

    node.eat = instancemethod(eat, node)

    return node

def bombeater(node):
    """Mark the node as a bombeater enemy."""
    return stageobj(BOMB_EATER, node)

def is_bombeater(node):
    return stageobj_has_flag(BOMB_EATER, node)

def flying(node):
    """Mark the node as a flying enemy."""
    return stageobj(FLYING, node)

def is_flying(node):
    return stageobj_has_flag(FLYING, node)

