#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module contains the game scene 'StageScene', 
the core of this game.

"""

from random import random

import gtk
import gtk.gdk as gdk
import gobject
import cairo

from pnode import Node
from objects import *
from effects import *
from uicomponents import *
from stagecontroller import *

# The z-index table
layers = {
        'floor': -100,
        'object': -300,
        'effect': -500,
        'message': -600
        }

# Fire will exist for # seconds
FIRE_LASTING=1.5

class StageScene(Node):
    """The game scene resposible for one stage."""
    def create_map(self):
        """Create the map container.
        
        Should be called before other create_xxx() methods.

        """
        self.map = MapContainer(
                parent=self,
                style={
                    'top': self.margin[0],
                    'right': self.margin[1],
                    'bottom': self.margin[2],
                    'left': self.margin[3],
                    'aspect': 1.0,
                    'align': 'center',
                    'vertical-align': 'center' 
                    },
                map_size=self.map_size
                )
        self.add_node(self.map)

    def create_floor(self):
        """Create a floor object in all cells."""
        def _on_enter(obj):
            return lambda: obj.play_blink(duration=1, loop=True)
        def _on_leave(obj):
            return lambda: obj.play_fadeout(duration=1)

        cell_size = self.map.get_cell_size()
        for x in xrange(0, self.map_size[0]):
            for y in xrange(0, self.map_size[1]):
                obj = Floor(
                        parent=self.map,
                        style={
                            'width': cell_size,
                            'height': cell_size,
                            'z-index': layers['floor'] }
                        )
                # Make it blinking when the player stays on it
                make_trackingfloor(self, obj, x, y, 
                        on_enter=_on_enter(obj),
                        on_leave=_on_leave(obj)
                        )
                self.map.add_node(obj, x, y)

    def create_player_at(self, x, y):
        """Create the player at the specified cell.
        
        @return: the player object
        
        """
        cell_size = self.map.get_cell_size()
        obj = Can(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size * 2, 
                    'z-index': layers['object'] }
                )
        # I am a player
        player(obj)
        # I am a movable character
        make_character(self, obj, 
                on_move=lambda dir: obj.play_moving(duration=0.2, loop=True),
                on_stop=lambda dir: obj.reset_animations())
        # I could be destroyed by bombs
        make_breakable(self, obj, 
                on_die=lambda: self.game_lose())
        # I can put bombs
        make_bomber(self, obj)

        self.map.add_node(obj, x, y, 0, -cell_size)
        return obj

    #
    # Functions for enemy creation
    #

    def create_enemy_normal_at(self, x, y):
        """Create a basic enemy at specified cell.
        
        @return: the enemy object

        """
        cell_size = self.map.get_cell_size()
        obj = Bishi(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size, 
                    'z-index': layers['object'] }
                )
        # I am an enemy
        enemy(obj)
        # The Motion upon the death
        def _on_go_die():
            # Stop everything
            obj.stop_ai()
            obj.reset_animations()
            obj.reset_actions()
            obj.reset_transforms()
            # Shrink smaller and die
            obj.scale((0.5, 0.5), duration=2.0, cleanup=obj.die)

        make_character(self, obj, speed=3.0, 
                on_move=lambda dir: obj.rotate(duration=2, loop=True),
                on_stop=lambda dir: obj.reset_animations(),
                on_go_die=_on_go_die)
        make_breakable(self, obj)
        # I have a simple stupid AI
        make_simpleai(self, obj)

        self.map.add_node(obj, x, y, 0, 0)
        return obj

    def create_enemy_bombeater_at(self, x, y):
        """Create a enemy that can eat bombs at specified cell.
        
        @return: the enemy object

        """
        cell_size = self.map.get_cell_size()
        obj = Drop(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size, 
                    'z-index': layers['object'] }
                )
        enemy(obj)
        # I can eat bombs
        bombeater(obj)
        def _on_go_die():
            obj.stop_ai()
            obj.reset_animations()
            obj.reset_actions()
            obj.reset_transforms()
            obj.scale((0.5, 0.5), duration=2.0, cleanup=obj.die)

        make_character(self, obj, speed=3.0, 
                on_move=lambda dir: obj.play_moving(duration=2, loop=True),
                on_stop=lambda dir: obj.reset_animations(),
                on_go_die=_on_go_die)
        make_breakable(self, obj)
        make_simpleai(self, obj)

        self.map.add_node(obj, x, y, 0, 0)
        return obj

    def create_enemy_flying_at(self, x, y):
        """Create a enemy that can fly over blocks at specified cell.
        
        @return: the enemy object

        """
        cell_size = self.map.get_cell_size()
        obj = Ameba(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size, 
                    'z-index': layers['object'] }
                )
        enemy(obj)
        # I can fly!
        flying(obj)
        def _on_go_die():
            obj.stop_ai()
            obj.reset_animations()
            obj.reset_actions()
            obj.reset_transforms()
            obj.scale((0.5, 0.5), duration=2.0, cleanup=obj.die)

        make_character(self, obj, speed=1.0, 
                on_move=lambda dir: obj.play_moving(duration=1.0, loop=True),
                on_stop=lambda dir: obj.reset_animations(),
                on_go_die=_on_go_die)
        make_breakable(self, obj)
        make_simpleai(self, obj)

        self.map.add_node(obj, x, y, 0, 0)
        return obj

    def create_enemy_bomber_at(self, x, y):
        """Create a enemy that can put bombs, at specified cell.
        
        @return: the enemy object
        
        """
        cell_size = self.map.get_cell_size()
        obj = BadCan(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size * 2, 
                    'z-index': layers['object'] }
                )
        enemy(obj)
        def _on_go_die():
            obj.stop_ai()
            obj.reset_animations()
            obj.reset_actions()
            obj.reset_transforms()
            obj.rotate(duration=0.5, cleanup=obj.die)

        make_character(self, obj, speed=3.0, 
                on_move=lambda dir: obj.play_moving(duration=0.2, loop=True),
                on_stop=lambda dir: obj.reset_animations(),
                on_go_die=_on_go_die)
        make_breakable(self, obj)
        # I can put bombs, with a stupid AI
        make_bomber(self, obj)
        make_bomberai(self, obj)


        self.map.add_node(obj, x, y, 0, -cell_size)
        return obj

    def create_enemies(self, count):
        """Create [count] enemies with random type."""
        self.enemies = []

        while count > 0:
            # Randomly select a cell
            x = int(random() * self.map_size[0])
            y = int(random() * self.map_size[1])

            # If it has been filled with something, choose another cell
            if self.is_filled(x, y):
                continue

            # Randomly select a type of enemy to generate
            r = int(random() * 10)
            if 4 < r and r < 8:
                enemy = self.create_enemy_bombeater_at(x, y)
            elif r == 8:
                enemy = self.create_enemy_flying_at(x, y)
            elif r == 9:
                enemy = self.create_enemy_bomber_at(x, y)
            else:
                enemy = self.create_enemy_normal_at(x, y)

            # Create dummy objects to prevent enemies 
            # from concentrating at one place
            self.create_dummy_obj_at(x - 1, y)
            self.create_dummy_obj_at(x + 1, y)
            self.create_dummy_obj_at(x, y - 1)
            self.create_dummy_obj_at(x, y + 1)

            self.enemies.append(enemy)
            count -= 1

    def create_hard_block_at(self, x, y):
        """Create a hard block at specified cell.
        
        @return: the hard block object

        """
        cell_size = self.map.get_cell_size()
        obj = HardBlock(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size * 2, 
                    'z-index': layers['object'] }
                )
        # I am a hard block, I can stop the fire without being destroyed
        fireblocking(block(obj))

        self.map.add_node(obj, x, y, 0, -cell_size)
        return obj

    def create_hard_blocks(self):
        """Create hard blocks in a grid form."""
        for x in xrange(1, self.map_size[0], 2):
            for y in xrange(1, self.map_size[1], 2):
                self.create_hard_block_at(x, y)

    def create_soft_block_at(self, x, y):
        """Create a soft block at specified cell.
        
        @return: the soft block object
        
        """
        cell_size = self.map.get_cell_size()
        obj = SoftBlock(
                parent=self.map,
                style={
                    'width': cell_size, 
                    'height': cell_size * 2, 
                    'z-index': layers['object'] }
                )
        # I am a soft block
        block(obj)
        # Randomly put an item after I dead
        make_breakable(self, obj, 
                on_die=lambda: self.put_item_random(x, y))

        self.map.add_node(obj, x, y, 0, -cell_size)
        return obj

    def create_soft_blocks(self, count):
        """Randomly create [count] soft blocks.
        
        Cells that has been filled with more than one object 
        (exactly, more than the Floor object) will not be chosen.

        """
        while count > 0:
            x = int(random() * self.map_size[0])
            y = int(random() * self.map_size[1])
            if self.is_filled(x, y):
                continue

            self.create_soft_block_at(x, y)
            count -= 1

    def create_dummy_obj_at(self, x, y):
        """Create a dummy object at specified cell.

        This dummy object is used to avoid soft blocks.

        """
        if not (0 <= x and x < self.map_size[0] and
                0 <= y and y < self.map_size[1]):
            return

        # Because every node needs to create it's surface,
        # create a smallest surface with only 1x1 px.
        # XXX: bad approach
        obj = Node(self.map, {'width': 1, 'height': 1})
        self.map.add_node(obj, x, y)
        try:
            self.dummies.append(obj)
        except AttributeError:
            self.dummies = [obj]

    def clear_dummy_obj(self):
        """Clear dummy objects after the creation of stage."""
        for d in self.dummies:
            self.map.remove_node(d)

        self.dummies = []

    def __init__(self, parent, style, 
            audio, map_size, margin, key_up, key_down, 
            on_game_reset, on_game_win):

        super(StageScene, self).__init__(parent, style)

        # The size of map
        self.map_size = map_size

        # The same as in MenuScene
        self.audio = audio
        self.margin = margin
        self.key_up = key_up
        self.key_down = key_down

        # Function on_game_reset is called after the player lose.
        # Function on_game_win is called after the player win.
        self.on_game_reset = on_game_reset
        self.on_game_win = on_game_win
        self.win = False
        self.lose = False
        
        # The message box to display win / lose
        self.msg = MessageBox(
                self, 
                style={
                    'width': '80%',
                    'height': '30%',
                    'align': 'center',
                    'vertical-align': 'center',
                    'z-index': layers['message']},
                )
        self.add_node(self.msg)

        # The background image
        self.texture = {}
        self.texture['bgimg'] = cairo.ImageSurface.create_from_png('stage_bg.png')

    def generate(self, n_enemies, n_blocks):
        """Randomly generate a new stage."""
        self.create_map()
        self.create_floor()
        self.player = self.create_player_at(0, 0)
        self.create_dummy_obj_at(0, 1)
        self.create_dummy_obj_at(1, 0)
        self.create_soft_block_at(0, 2)
        self.create_soft_block_at(2, 0)
        self.create_hard_blocks()        
        self.create_enemies(n_enemies)
        self.create_soft_blocks(n_blocks)        
        self.clear_dummy_obj()

    def parse(self, stage_str, n_blocks):
        """Parse a string to generate the stage.
        
        The format of stage_str:
            - 'x': hard block
            - 'o': soft block
            - '.': dummy object
            - '@': player
            - 'A': normal enemy
            - 'B': bomb eater
            - 'C': flying enemy
            - 'D': bomber enemy

        @param n_blocks: the bumber of soft blocks to be randomly generated
            after the stage has being loaded

        """
        self.enemies = []
        self.create_map()
        self.create_floor()

        stage_str = stage_str.strip()
        rows = stage_str.split('\n')
        for y in xrange(0, self.map_size[1]):
            for x in xrange(0, self.map_size[0]):
                c = rows[y][x]
                if c == 'x':
                    self.create_hard_block_at(x, y)
                elif c == '@':
                    self.player = self.create_player_at(x, y)
                elif c == '.':
                    self.create_dummy_obj_at(x, y)
                elif c == 'o':
                    self.create_soft_block_at(x, y)
                elif c == 'A':
                    e = self.create_enemy_normal_at(x, y)
                    self.enemies.append(e)
                elif c == 'B':
                    e = self.create_enemy_bombeater_at(x, y)
                    self.enemies.append(e)
                elif c == 'C':
                    e = self.create_enemy_flying_at(x, y)
                    self.enemies.append(e)
                elif c == 'D':
                    e = self.create_enemy_bomber_at(x, y)
                    self.enemies.append(e)
                elif c == ' ':
                    pass

        self.create_soft_blocks(n_blocks)        
        self.clear_dummy_obj()

    def on_update(self, cr):
        """Simply display the background image.
        
        The same as in MenuScene.

        """
        scale_width = self.width / float(self.texture['bgimg'].get_width())
        scale_height = self.height / float(self.texture['bgimg'].get_height())
        if scale_width < scale_height:
            scale = scale_height
        else:
            scale = scale_width

        new_width = self.texture['bgimg'].get_width()*scale
        new_height = self.texture['bgimg'].get_height()*scale
        x = (self.width - new_width)/2
        y = (self.height - new_height)/2

        cr = cairo.Context(self.surface)
        cr.scale(scale, scale)
        cr.set_source_rgb(0, 0, 0)
        cr.paint()
        cr.set_source_surface(self.texture['bgimg'], x, y)
        cr.paint_with_alpha(0.7)

    def game_win(self):
        """Display the winnig message."""
        self.win = True
        self.msg.set_text(u'YOU WIN <Press Space>')
        self.msg.show(True)

    def game_lose(self):
        """Display the losing message and stop player from doing anything."""
        self.lose = True
        self.player.reset_animations()
        self.player.reset_actions()
        self.msg.set_text(u'YOU LOSE <Press Space>')
        self.msg.show(True)

    def on_tick(self, interval):
        """Check the player input, 
        and check the status of the player and enemies.
        
        """
        if not self.win and not self.lose:
            # Moving the player around
            if self.key_up('Left'): self.player.move('left')
            if self.key_up('Up'): self.player.move('up')
            if self.key_up('Right'): self.player.move('right')
            if self.key_up('Down'): self.player.move('down')

            if self.key_down('Left'): self.player.stop('left')
            if self.key_down('Up'): self.player.stop('up')
            if self.key_down('Right'): self.player.stop('right')
            if self.key_down('Down'): self.player.stop('down')

            if self.key_up('z'): self.player.bomb()

        # Win / lose
        if self.win and self.key_up('space'): self.on_game_win()
        if self.lose and self.key_up('space'): self.on_game_reset()

        #
        # XXX: should be merged into character's check() method
        #

        # Check player's status
        if not self.lose and not self.win:
            cell = self.map.get_cell(self.player)
            for n in self.map.get_cell_nodes(*cell):
                if is_enemy(n):
                    # Ran into an enemy
                    self.game_lose()
                elif is_fire(n):
                    # Ran into the fire of bomb
                    self.game_lose()
                elif is_item(n):
                    # Eat the item
                    n.eat(self.player)

        # Check enemies' status
        tmp = self.enemies
        for e in tmp:
            cell = self.map.get_cell(e)
            for n in self.map.get_cell_nodes(*cell):
                if is_fire(n) and not is_dead(n):
                    # Ran into the fire of bomb
                    e.go_die()
                    self.enemies.remove(e)
                    break
                elif is_bombeater(e) and is_bomb(n):
                    # The bombeater eat the bomb
                    n.bomber.cur_bomb_count -= 1
                    self.map.remove_node(n)
                    continue

        # Check the winning condition
        if len(self.enemies) == 0 and not self.win:
            self.game_win()

    def is_filled(self, x, y):
        """Return true 
        if the cell has been filled with more than one object.
        
        """
        if not (0 <= x and x < self.map_size[0]
                and 0 <= y and y < self.map_size[1]):
            return False

        # Is there something else than Floor?
        return (len(self.map.get_cell_nodes(x, y)) > 1)

    def is_blocked(self, node, x, y):
        """Check whether the target cell is blocked,
        according to the character who is moving.

        @param node: the node entering this cell
        @type node: pnode.Node

        """
        # Is it outside the map?
        if not (0 <= x and x < self.map_size[0]
                and 0 <= y and y < self.map_size[1]):
            return True

        # Check individual nodes in the cell
        for target in self.map.get_cell_nodes(x, y):
            if is_bombeater(node) and is_bomb(target):
                # Bombeater can move over a bomb
                continue
            elif is_flying(node) and not is_bomb(target):
                # Flying enemy can not fly over a bomb
                # (It is designed in order to kill them easier)
                continue
            elif is_block(target):
                return True
            elif is_player(node) and is_player(target):
                return True
            elif is_enemy(node) and is_enemy(target):
                return True

        return False

    def move_object(self, node, dx, dy):
        """Check the target cell whether it is blocked or not,
        and move the object in the map.
        
        Some adjustion is applied to make turning smoother.

        @param node: the node being moved
        @type node: pnode.Node
        @param dx: the delta in x
        @param dy: the delta in y

        """
        if dx == 0 and dy == 0:
            return

        map = self.map
        cell = map.get_cell(node)
        pos = map.get_node_pos(node)
        current_cell_pos = map.get_cell_pos(*cell)
        cell_size = map.get_cell_size()
        is_blocked = self.is_blocked
        current_cell_delta_x = current_cell_pos[0] - pos[0]
        current_cell_delta_y = current_cell_pos[1] - pos[1]
        blocked_x = False
        blocked_y = False

        # Detect and handle collision
        if dx > 0 and is_blocked(node, cell[0] + 1, cell[1]):
            dx = min(current_cell_delta_x, dx)
            blocked_x = True
        elif dx < 0 and is_blocked(node, cell[0] - 1, cell[1]):
            dx = max(current_cell_delta_x, dx)
            blocked_x = True
        
        if dy > 0 and is_blocked(node, cell[0], cell[1] + 1):
            dy = min(current_cell_delta_y, dy)
            blocked_y = True
        elif dy < 0 and is_blocked(node, cell[0], cell[1] - 1):
            dy = max(current_cell_delta_y, dy)
            blocked_y = True

        # Smooth if needed
        if dx == 0 and not blocked_y:
            dx = current_cell_delta_x

        if dy == 0 and not blocked_x:
            dy = current_cell_delta_y

        map.move_pos(node, dx, dy)

    def put_bomb(self, x, y, delay, power, bomber):
        """Create a bomb at the specified cell.

        Should be called by a bomber.

        @param bomber: the bomber putting bombs
        @type bomber: pnode.Node with make_bomber()

        """
        nodes = self.map.get_cell_nodes(x, y)
        for n in nodes:
            if is_bomb(n):
                # There is already a bomb in the cell
                return False

        # Create the bomb
        cell_size = self.map.get_cell_size()
        bomb = Bomb(
                parent=self.map,
                style={
                    'width': cell_size,
                    'height': cell_size,
                    'z-index': layers['object'] }
                )
        block(bomb)
        # XXX: should be merged into make_bomb()
        def _on_die():
            bomber.cur_bomb_count -= 1
            self.explode(bomb, x, y, power)

        make_breakable(self, bomb, on_die=_on_die)
        make_bomb(bomb, delay, power, bomber,
                on_explode=lambda: bomb.die())
        # Start counting
        bomb.count()
        self.map.add_node(bomb, x, y)

        return True

    def put_fireitem(self, x, y):
        """Put a fire item at specified cell."""
        cell_size = self.map.get_cell_size()
        obj = FireItem(parent=self.map,
                style={
                    'width': cell_size,
                    'height': cell_size,
                    'z-index': layers['object'] }
                )
        def _on_eat(character):
            self.audio.play('kan.wav')
            # Increment the bomb power of this character
            character.bomb_power += 1

        make_breakable(self, obj)
        make_item(self, obj, on_eat=_on_eat)
        self.map.add_node(obj, x, y)

    def put_bombitem(self, x, y):
        """Put a bomb item at specified cell."""
        cell_size = self.map.get_cell_size()
        obj = BombItem(parent=self.map,
                style={
                    'width': cell_size,
                    'height': cell_size,
                    'z-index': layers['object'] }
                )
        def _on_eat(character):
            self.audio.play('kan.wav')
            # Increment the number of bombs of this character
            character.bomb_count += 1

        make_breakable(self, obj)
        make_item(self, obj, on_eat=_on_eat)
        self.map.add_node(obj, x, y)

    def put_item_random(self, x, y):
        """Randomly put an item or not."""
        r = int(random() * 10)
        if 3 < r and r <= 6:
            self.put_fireitem(x, y)
        elif 6 < r and r <= 9:
            self.put_bombitem(x, y)

    def explode(self, node, x, y, power):
        """This method do all the jobs when a bomb explode.
            1. Calculate the path of fire.
            2. Destroy things on the path.
            3. Put 'fire objects' to kill characters who entered the path later.
            4. Display the effect.

        @param node: the bomb that has been exploded (currently not using)
        @type node: pnode.Node with make_bomb()

        """
        # Play SE
        self.audio.play('explode.wav')

        # Step 1-3
        cell_size = self.map.get_cell_size()
        def _search_and_break(nodes):
            def _shake(self, interval, phase):
                a = (pi / 8) * (1.0 - phase)
                self.set_rotate(a * sin(phase * 8 * 2 * pi))

            for n in nodes:
                # Make it shaking
                n.add_action('shake', _shake, duration=2, update=True)
                if is_player(n):
                    # The player is dead, you lose
                    self.game_lose()
                elif is_fireblocking(n):
                    # The fire is blocked by a hard block
                    return (True, -1)
                elif is_bomb(n):
                    # Explode another bomb
                    # Method die() first removes the node from the map, 
                    # so it won't be an endless recursion.
                    n.die()
                elif is_character(n) and not is_dead(n):
                    # Kill the enemy
                    n.go_die()
                    if is_enemy(n):
                        self.enemies.remove(n)
                elif is_breakable(n):
                    # Destroy the soft block
                    n.die()
                    return (True, 0)

            return (False, 0)

        def _put_fire(x, y):
            # Put an invisible fire object to target cell.
            # This fire object may destroy characters coming in.
            # XXX: invisible object
            _fire = Node(self.map, {'width': 1, 'height': 1})
            fire(_fire)
            self.map.add_node(_fire, x, y)
            def _die_latter(node, interval, phase):
                pass

            # Let the fire disppear after FIRE_LASTING seconds
            _fire.add_action('die', _die_latter, delay=FIRE_LASTING, 
                    cleanup=lambda: self.map.remove_node(_fire))

        #
        # Search in four directions
        #

        tmp_x, adjust = x, 0
        for tmp_x in xrange(x, max(x - power - 1, -1), -1):
            nodes = self.map.get_cell_nodes(tmp_x, y)
            stopped, adjust = _search_and_break(nodes)
            _put_fire(tmp_x, y)
            if stopped: 
                break

        fire_left = x - tmp_x + adjust

        tmp_x, adjust = x, 0
        for tmp_x in xrange(x, min(x + power + 1, self.map_size[0])):
            nodes = self.map.get_cell_nodes(tmp_x, y)
            stopped, adjust = _search_and_break(nodes)
            _put_fire(tmp_x, y)
            if stopped: 
                break

        fire_right = tmp_x - x + adjust

        tmp_y, adjust = y, 0
        for tmp_y in xrange(y, max(y - power - 1, -1), -1):
            nodes = self.map.get_cell_nodes(x, tmp_y)
            stopped, adjust = _search_and_break(nodes)
            _put_fire(x, tmp_y)
            if stopped: 
                break

        fire_up = y - tmp_y + adjust

        tmp_y, adjust = y, 0
        for tmp_y in xrange(y, min(y + power + 1, self.map_size[1])):
            nodes = self.map.get_cell_nodes(x, tmp_y)
            stopped, adjust = _search_and_break(nodes)
            _put_fire(x, tmp_y)
            if stopped: 
                break

        fire_down = tmp_y - y + adjust
                
        # Step 4

        # Put the effect
        width = (fire_left + fire_right + 1) * cell_size
        height = (fire_up + fire_down + 1) * cell_size
        explosion = ExplosionEffect(
                parent=self.map,
                style={
                    'width': width,
                    'height': height,
                    'z-index': layers['effect'] },
                fire=(fire_up, fire_right, fire_down, fire_left),
                get_cell_size=self.map.get_cell_size,
                on_die=lambda: self.map.remove_node(explosion)
                )
        self.map.add_node(explosion, x, y, -fire_left * cell_size, -fire_up * cell_size)

        # Also make the effect shaking
        def _shake(self, interval, phase):
            a = (pi / 8) * (1.0 - phase)
            self.set_rotate(a * sin(phase * 8 * 2 * pi))
        explosion.add_action('shake', _shake, duration=2, update=True)

