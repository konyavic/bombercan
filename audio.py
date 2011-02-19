#!/usr/bin/python
# -*- coding: utf-8 -*-

import wave
import thread

import pyaudio

class AudioManager(object):
    def __init__(self):
        self.tracks = {}
        self.p = pyaudio.PyAudio()
        self.chunk = 1024

    def play(self, filename, loop=False):
        def run():
            wf = wave.open(filename, 'rb')

            # open stream
            p = self.p
            stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

            while True:
                # read data
                data = wf.readframes(self.chunk)

                # play stream
                while data != '':
                    stream.write(data)
                    data = wf.readframes(self.chunk)

                if loop:
                    wf.rewind()
                else:
                    break

            stream.close()
            #p.terminate()

        thread.start_new_thread(run, ())
