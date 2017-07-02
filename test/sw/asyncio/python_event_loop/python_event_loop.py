#!/usr/bin/python3
'''
Documentation, License etc.

@package python_event_loop
'''
import asyncio
import datetime

@asyncio.coroutine
def display_date(loop):
    end_time = loop.time() + 2.0
    while True:
        print(datetime.datetime.now())
        if (loop.time() + 1.0) >= end_time:
            break
        yield from asyncio.sleep(1)
        
loop = asyncio.get_event_loop()
# Blocking call which returns when the display_date() coroutine is done
loop.run_until_complete(display_date(loop))
loop.close()

class MyClass(object):
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.display_date_class())
    
    @asyncio.coroutine
    def display_date_class(self):
        end_time = self.loop.time() + 5.0
        while True:
            print(datetime.datetime.now())
            if (self.loop.time() + 1.0) >= end_time:
                break
            yield from asyncio.sleep(1, loop=self.loop)

myInstance = MyClass()
myInstance.loop.close()
