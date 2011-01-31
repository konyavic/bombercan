#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

from pnode import Game
from menuscene import MenuScene
from stagescene import StageScene

fps_counters = [0 for i in range(0, 5)]
fps_cur_counter = 0
last_time = time.time()

def print_fps():
    global fps_counter, fps_cur_counter, last_time
    cur_time = time.time()
    elapsed_time = cur_time - last_time
    if elapsed_time > 1:
        last_time = cur_time
        fps_cur_counter = (fps_cur_counter + 1) % 5

        total_count = 0
        for count in fps_counters:
            total_count += count

        print 'fps =', float(total_count) / 5
        fps_counters[fps_cur_counter] = 1   # reset
    else:
        fps_counters[fps_cur_counter] += 1

class Bomberman(Game):
    def __init__(self):
        Game.__init__(self, 'Bomberman', 500, 500, 80)

        stage = StageScene(
                parent=self,
                style={},
                opt={
                    '$map size': [15, 15], 
                    '$margin': [20, 20, 20, 20],
                    '$bgimg': 'stage_bg.png',
                    '@key up': self.key_up,
                    '@key down': self.key_down
                    }
                )

        def start_game():
            self.top_node=stage
            self.top_node.do_resize_recursive()

        menu = MenuScene(
                parent=self,
                style={},
                opt={
                    '$bgimg': 'menu_bg.png',
                    '@key up': self.key_up,
                    '@key down': self.key_down,
                    '@start game': start_game
                    }
                )
        self.top_node = menu

    def on_tick(self, interval):
        print_fps()

if __name__ == '__main__':
    game = Bomberman()
    try:
        game.run()
    except KeyboardInterrupt:
        game.quit()
