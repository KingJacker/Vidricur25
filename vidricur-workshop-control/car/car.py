import json
from loguru import logger
from patterns.singleton import Singleton
from car.engine import Engine
from car.wheel import Wheel
from car.float import Float
from car.sensors import Sensors
import asyncio

class Car(metaclass=Singleton):
    def __init__(self, sio, pca, i2c, leds):
        self.pca = pca
        self.sio = sio
        self.i2c = i2c
        self.leds = leds

        # SENSORS
        try:
            self.sensors = Sensors(i2c)
        except Exception as e:
	        logger.warning(f'Could not get Sensor: {e}')
        
        # ENGINE
        self.engine = Engine(self.pca)
        
        # WHEEL
        try:
            self.wheel = Wheel(self.pca, self.leds)
        except Exception as e:
            logger.critical(f'Could not Instantiate: {e}')

        # FLOAT
        try: 
            self.float = Float(self.pca)
        except Exception as e:
            logger.critical(f'Could not instantiate Float: {e}')

    async def send_message(self, message): #? is this obsolete
        await self.sio.emit("message", json.dumps(message))

    async def command_handler(self, command):
        # logger.debug(command)

        # STOP
        if command['space'] != 0:
            self.engine.stop()
        
        # FORWARD / BACKWARD
        if command['w'] > 0 and command['s'] == 0:
            self.engine.set_speed(command['w'])
        elif command['s'] > 0 and command['w'] == 0:
            self.engine.set_speed(-1 * command['s']) # reverse with * -1
        else:
            self.engine.set_speed(0)
        
        # LEFT / RIGHT
        if command['a'] > 0 and command['d'] == 0:
            self.wheel.set_angle(command['a'])
        elif command['d'] > 0 and command['a'] == 0:
            self.wheel.set_angle(-1 * command['d'])
        else:
            self.wheel.set_angle(0)


        # Float up / down
        if command['e'] == 1 and command['q'] == 0:
            self.float.set_direction(-1) # down
        elif command['e'] == 0 and command['q'] == 1:
            self.float.set_direction(1) # up
        else:
            self.float.set_direction(0) # stop
    
    async def start_servo_movers(self):
        logger.info("STARTING SERVO MOVERS (FLOATS)")
        self.float_task = asyncio.create_task(self.float.move())