#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe

setup(
        #windows = [
        console = [
            {
                'script':'bombercan.py',
                'icon_resources': [(1, 'Star.ico')]
                }
            ],
        options = {
            'py2exe': {
                'includes': 'cairo, pango, pangocairo, atk, gobject, gio, pyaudio'
                }
            },
        data_files = [
            'stage_bg.png',
            'menu_bg.png',
            'bombercan.wav',
            'explode.wav'
            ]
        )
