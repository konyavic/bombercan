#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A simple sound interface.

There are some problems with module pyaudio on Linux.
This module should be replaced with a better library in the future.

"""

import wave
import thread

import pyaudio

class AudioManager(object):
    """A simple class to interface pyaudio."""
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.chunk = 1024

    def play(self, filename, loop=False):
        """Play a wave track."""
        def run():
            stream = None
            try:
                wf = wave.open(filename, 'rb')
    
                # Open stream
                p = self.p
                stream = p.open(format =
                        p.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True)

                while True:
                    # Read data
                    data = wf.readframes(self.chunk)

                    # Play stream
                    while data != '':
                        stream.write(data)
                        data = wf.readframes(self.chunk)

                    if loop:
                        wf.rewind()
                    else:
                        break
            except Exception:
                pass

            if stream:
                stream.close()

        thread.start_new_thread(run, ())
