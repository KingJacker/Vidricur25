import json
from loguru import logger
from patterns.singleton import Singleton
from car.engine import Engine
from car.wheel import Wheel
from car.float import Float
from car.sensors import Sensors

class Car(metaclass=Singleton):
    def __init__(self, sio, pca, i2c):
        self.pca = pca
        # self.esc_pwm
        self.sio = sio
        self.i2c = i2c

        # SENSORS
        self.sensors = Sensors(i2c)
        
        # ENGINE
        # self.engine = Engine(self.esc_pwm)
        
        # WHEEL
        try:

            self.wheel = Wheel(self.pca)
        except Exception as e:
            logger.critical(f'Could not Instantiate: {e}')

        # FLOAT
        try: 
            self.float = Float(self.pca)
        except Exception as e:
            logger.critical(f'Could not instantiate Float: {e}')

        self.max_angle = 0
        self.max_speed = 0

    async def send_message(self, message):
        await self.sio.emit("message", json.dumps(message))

    async def command_handler(self, command):
        logger.debug(command)

        # # STOP
        # if command['space'] != 0:
        #     self.engine.stop()
        #     logger.info("Action: Stop")
        
        # # FORWARD / BACKWARD
        # if command['w'] > 0 and command['s'] == 0:
        #     self.engine.set_speed(command['w'] * self.max_speed)
        #     # logger.info("Action: Forward")
        # elif command['s'] > 0 and command['w'] == 0:
        #     self.engine.set_speed(-1 * command['s'] * self.max_speed)
        #     # logger.info("Action: Backward")
        # else:
        #     self.engine.set_speed(0)
        #     # logger.info("Action: Reset Speed")
        
        # LEFT / RIGHT
        if command['a'] > 0 and command['d'] == 0:
            steering_value = command['a']
            self.wheel.set_angle(steering_value)
            # logger.info(f"Action: Left ({steering_value})")
        elif command['d'] > 0 and command['a'] == 0:
            steering_value = -1 * command['d']
            self.wheel.set_angle(steering_value)
            # logger.info(f"Action: Right ({steering_value})")
        else:
            self.wheel.set_angle(0)
            # logger.info("Action: Reset Angle")

