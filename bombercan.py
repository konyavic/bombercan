#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

from pnode import Game
from menuscene import MenuScene
from stagescene import StageScene

from printfps import printfps

class Bombercan(Game):
    def __init__(self):
        Game.__init__(self, 'BomberCan', 500, 500, 80)

        def game_start():
            self.top_node=self.stage
            self.top_node.do_resize_recursive()

        def game_reset():
            self.top_node=self.menu
            self.top_node.do_resize_recursive()

            self.stage = StageScene(
                    parent=self,
                    style={},
                    opt={
                        '$map size': [15, 15], 
                        '$margin': [20, 20, 20, 20],
                        '$bgimg': 'stage_bg.png',
                        '@key up': self.key_up,
                        '@key down': self.key_down,
                        '@game reset': game_reset}
                    )


        self.menu = MenuScene(
                parent=self,
                style={},
                opt={
                    '$bgimg': 'menu_bg.png',
                    '@key up': self.key_up,
                    '@key down': self.key_down,
                    '@game start': game_start}
                )

        game_reset()

    @printfps()
    def on_tick(self, interval):
        pass

if __name__ == '__main__':
    try: 
        game = Bombercan()
        game.run()
    except KeyboardInterrupt:
        pass
