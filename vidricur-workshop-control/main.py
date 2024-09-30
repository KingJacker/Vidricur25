import asyncio
import socketio
import json
import pigpio

from aiohttp import web
from queue import Queue

from car.car import Car

pigpio.exceptions = True
# Connects to the pigpio service of the Raspberry Pi
# Allows to control the GPIO PINs of the Raspberry Pi
# Documentation: https://abyz.me.uk/rpi/pigpio/python.html
pi = pigpio.pi()

### Only for Demonstration: Virtual Raspberry Pi Board
#from stubs.pi import Pi
#pi = Pi()
###

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

# Initialize car instance
car = Car(sio, pi)
asyncio.run(car.start())

# If socketio connection is established the connect function is called
@sio.event
def connect(sid, environ):
    print("Remote connected with connection id: ", sid)

@sio.event
async def message(sid, data):
    await car.handleEvent(json.loads(data))

@sio.event
def disconnect(sid):
    print('Remote disconnected with connection id: ', sid)

if __name__ == '__main__':
    web.run_app(app, host="0.0.0.0", port=8080)