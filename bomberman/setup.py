#!/usr/bin/python

from distutils.core import setup
import py2exe

setup(
        #windows = [
        console = [
            {
                'script':'main.py',
                'icon_resources': [(1, 'Star.ico')]
                }
            ],
        options = {
            'py2exe': {
                'includes': 'cairo, pango, pangocairo, atk, gobject, gio'
                }
            },
        )
