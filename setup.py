#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe

setup(
        #windows = [
        console = [
            {
                'script':'bomberman.py',
                'icon_resources': [(1, 'Star.ico')]
                }
            ],
        options = {
            'py2exe': {
                'includes': 'cairo, pango, pangocairo, atk, gobject, gio'
                }
            },
        data_files = [
            'stage_bg.png',
            'menu_bg.png'
            ]
        )
