#!/usr/bin/python
# -*- coding: utf-8 -*-

from time import time
from functools import wraps

def printfps(second=1.0, counter=5):
    """A decorator to output the avg. number of calls in a period on the function.

    Keyword arguments:

    second -- the period to print fps

    counter -- the number of counters (average is taken on the total of all counters)

    """
    def _printfps(f):
        f._fps_counters = [0 for i in range(0, counter)]
        f._fps_cur_counter = 0
        f._fps_last_time = time()

        @wraps(f)
        def __printfps(*args, **kw):
            ret = f(*args, **kw)
            cur_time = time()
            elapsed_time = cur_time - f._fps_last_time
            if elapsed_time < second:
                f._fps_counters[f._fps_cur_counter] += 1    
            else:
                f._fps_last_time = cur_time
                f._fps_cur_counter = (f._fps_cur_counter + 1) % counter
                total_count = 0
                for count in f._fps_counters:
                    total_count += count
                print 'fps =', total_count / float(second * counter)
                f._fps_counters[f._fps_cur_counter] = 1 # reset

            return ret 
        
        return __printfps
    
    return _printfps
