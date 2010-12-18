#!/usr/bin/python

from distutils.core import setup
import py2exe

setup(
        console=['main.py'],
        options = {
            'py2exe': {
                'includes': 'cairo, pango, pangocairo, atk, gobject, gio'
                }
            },
        )
