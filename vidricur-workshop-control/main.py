import asyncio
import socketio
import json
# import gpiod
from rpi_hardware_pwm import HardwarePWM

from aiohttp import web
from queue import Queue

from car.car import Car

# On the Pi 5, use channels 0 and 1 to control GPIO_12 and GPIO13, respectively; 
# use channels 2 and 3 to control GPIO_18 and GPIO_19, respectively
# For Rpi 5, use chip=2
steering_pwm = HardwarePWM(pwm_channel=0, hz=100, chip=2)
esc_pwm = HardwarePWM(pwm_channel=1, hz=100, chip=2)

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

# Initialize car instance
car = Car(sio, steering_pwm, esc_pwm)
asyncio.run(car.start())

# If socketio connection is established the connect function is called
@sio.event
def connect(sid, environ):
    print("Remote connected with connection id: ", sid)

@sio.event
async def message(sid, data):
    print(f"Received: {data}")
    await car.handleEvent(json.loads(data))

@sio.event
def disconnect(sid):
    print('Remote disconnected with connection id: ', sid)

if __name__ == '__main__':
    web.run_app(app, host="0.0.0.0", port=8080)