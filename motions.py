#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import pi
from math import cos
from new import instancemethod

def use_basic_motions(node):
    def scale(self, end_scale, duration, 
            start_scale=(1.0, 1.0), rel_origin=(0.5, 0.5), harmonic=False, 
            delay=0.0, loop=False, cleanup=None):

        delta_scale = (
                end_scale[0] - start_scale[0],
                end_scale[1] - start_scale[1])

        def _scale(self, interval, phase):
            self.set_scale(
                    start_scale[0] + delta_scale[0] * phase,
                    start_scale[1] + delta_scale[1] * phase,
                    rel_origin)

        def _scale_harmonic(self, interval, phase):
            phase = (0.5 - 0.5 * cos(phase * pi * 2))
            self.set_scale(
                    start_scale[0] + delta_scale[0] * phase,
                    start_scale[1] + delta_scale[1] * phase,
                    rel_origin)

        if harmonic:
            self.add_action('scale', _scale_harmonic, 
                    duration, delay, True, loop, cleanup)
        else:
            self.add_action('scale', _scale, 
                    duration, delay, True, loop, cleanup)

    node.scale = instancemethod(scale, node)

    def rotate(self, duration, 
            end_ang=(2 * pi), start_ang=0, rel_origin=(0.5, 0.5),
            delay=0.0, loop=False, cleanup=None):

        delta = end_ang - start_ang

        def _rotate(self, interval, phase):
            self.set_rotate(start_ang + delta * phase)

        self.add_action('rotate', _rotate, 
                duration, delay, True, loop, cleanup)

    node.rotate = instancemethod(rotate, node)
