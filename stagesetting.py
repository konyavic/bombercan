#!/usr/bin/python
# -*- coding: utf-8 -*-

stage = []

stage.append({})
stage[0]['size'] = (7, 7)
stage[0]['blocks'] = 3
stage[0]['str'] = """
xxxxxxx
x@.o Ax
x.x x x
xo   ox
x x x x
xA o Ax
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
stage[2]['size'] = (13, 13)
stage[2]['blocks'] = 20
stage[2]['str'] = """
xxxxxxxxxxxxx
x     x     x
x x.x x x x x
x .@. x  C  x
x x.x x x x x
xoooooxooooox
x x x x x x x
x  A  x  B  x
x xox x x x x
x  A  x  A  x
xoxoxoxoxoxox
x  A     B  x
xxxxxxxxxxxxx
"""

stage.append({})
stage[3]['size'] = (19, 17)
stage[3]['blocks'] = 50
stage[3]['str'] = """
xxxxxxxxxxxxxxxxxxx
x@. x     C       x
x.x x xxxxxxxxx x x
xooox x ..D.. x A x
x x x x x.x.x x x x
x A x x       x   x 
x x x xxxxxxxox x x
x   x x       x A x
x x x x x x x x x x
x A x x   B   x   x
x x x x xxxxxxx x x
x   x x   A   x A x
x x x xxxxx x x x x
x A x     A   x   x
x x xxxxxxxxxxx x x 
x   o    B    o   x
xxxxxxxxxxxxxxxxxxx
"""

stage.append({})
stage[4]['size'] = (23, 15)
stage[4]['blocks'] = 40
stage[4]['str'] = """
xxxxxxxxxxxxxxxxxxxxxxx
x  .       .       .  x
x xDx x x xDx x x xDx x
x  .     A . A     .  x
x x x x xoxoxox x x x x
x    A  o     o  A    x
x x.x x x x.x x x x x x
x .D.   o .@. o   .D. x
x x.x x x x.x x x x x x
x    A  o     o  A    x
x x x x xoxoxox x x x x
x  .     A . A     .  x
x xDx x x xDx x x xDx x
x  .       .       .  x
xxxxxxxxxxxxxxxxxxxxxxx
"""
