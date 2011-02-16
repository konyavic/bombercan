#!/usr/bin/python
# -*- coding: utf-8 -*-

from pnode import Game
from menuscene import MenuScene
from stagescene import StageScene
from printfps import printfps

class Bombercan(Game):
    def __init__(self):
        super(Bombercan, self).__init__('BomberCan', 500, 500, 80)

        def game_start():
            self.top_node=self.stage
            self.top_node.do_resize_recursive()

        def game_reset():
            self.top_node=self.menu
            self.top_node.do_resize_recursive()

            self.stage = StageScene(
                    parent=self,
                    style={},
                    map_size=(15, 15), 
                    margin=(20, 20, 20, 20),
                    key_up=self.key_up,
                    key_down=self.key_down,
                    on_game_reset=game_reset
                    )

        self.menu = MenuScene(
                parent=self,
                style={},
                key_up=self.key_up,
                key_down=self.key_down,
                on_game_start=game_start
                )

        game_reset()

    @printfps()
    def on_tick(self, interval):
        pass

def main():
    try: 
        game = Bombercan()
        game.run()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
