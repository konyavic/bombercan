#!/usr/bin/python
# -*- coding: utf-8 -*-

"""The topmost executable module of Bombercan."""

import stagesetting
from pnode import Game
from menuscene import MenuScene
from stagescene import StageScene
from printfps import printfps
from audio import AudioManager

class Bombercan(Game):
    """The main class of this game."""
    def __init__(self):
        """Create the main menu."""
        super(Bombercan, self).__init__('BomberCan', 500, 500, 80)

        # Play BGM
        self.audio = AudioManager()
        self.audio.play('bombercan.wav', loop=True)
            
        # Display the main menu
        self.menu = MenuScene(
                parent=self,
                style={},
                audio=self.audio,
                key_up=self.key_up,
                key_down=self.key_down,
                on_game_start=self.game_start
                )

        self.game_reset()

    def game_reset(self):
        self.top_node=self.menu
        self.top_node.do_resize_recursive()

    def game_start(self, mode, stage_num=4):
        if mode == 0:
            settings = stagesetting.stage[stage_num]
            self.stage = StageScene(
                    parent=self,
                    style={},
                    audio=self.audio,
                    map_size=settings['size'], 
                    margin=(20, 20, 20, 20),
                    key_up=self.key_up,
                    key_down=self.key_down,
                    on_game_reset=self.game_reset,
                    on_game_win=lambda: self.game_start(0, stage_num + 1)
                )
            self.stage.parse(settings['str'], settings['blocks'])
        elif mode == 1:
            self.stage = StageScene(
                    parent=self,
                    style={},
                    audio=self.audio,
                    map_size=(15, 15), 
                    margin=(20, 20, 20, 20),
                    key_up=self.key_up,
                    key_down=self.key_down,
                    on_game_reset=self.game_reset,
                    on_game_win=self.game_reset
                )
            self.stage.generate(20, 60)

        self.top_node=self.stage
        self.top_node.do_resize_recursive()

    @printfps()
    def on_tick(self, interval):
        """Do nothing but print the fps."""
        pass

def main():
    """The entry point."""
    try: 
        game = Bombercan()
        game.run()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
