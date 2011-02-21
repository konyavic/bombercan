#!/usr/bin/python
# -*- coding: utf-8 -*-

stage = []

stage.append({})
stage[0]['size'] = (7, 7)
stage[0]['blocks'] = 3
stage[0]['str'] = """
xxxxxxx
x@.o Ax
x.x xox
xo    x
x x x x
x Ao Ax
xxxxxxx
"""

stage.append({})
stage[1]['size'] = (19, 11)
stage[1]['blocks'] = 50
stage[1]['str'] = """
xxxxxxxxxxxxxxxxxxx
xA               Ax
x x x x x x x x x x
x    A   o  oB    x
x x x x x.x xox x x 
x      o.@.o      x
x x x x x.x x x x x
x    A   o   A    x
x x x x x x x x x x
xB               Ax
xxxxxxxxxxxxxxxxxxx
"""

stage.append({})
stage[2]['size'] = (19, 11)
stage[2]['blocks'] = 50
stage[2]['str'] = """
xxxxxxxxxxxxxxxxxxx
xA       C       Ax
x x x x x x x x x x
x    A   o  oB    x
x x x x x.x xox x x 
x      o.@.o      x
x x x x x.x x x x x
x    A   o   A    x
x x x x x x x x x x
xB               Ax
xxxxxxxxxxxxxxxxxxx
"""
