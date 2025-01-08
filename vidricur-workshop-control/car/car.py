import json
from loguru import logger
from patterns.singleton import Singleton
from queue import Queue
from car.engine import Engine
from car.wheel import Wheel
from car.float import Float

class Car(metaclass=Singleton):
    def __init__(self, sio, pca, esc_pwm):
        self.pca = pca
        self.esc_pwm = esc_pwm
        self.sio = sio
        
        # ENGINE
        self.engine = Engine(self.esc_pwm)
        
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

    async def handleEvent(self, event):
        logger.debug(event)

        # CONTROl EVENT
        if event["source"] == "control":
            control = event['content']['control']
            
            # STOP
            if control['space'] != 0:
                self.engine.stop()
                logger.info("Action: Stop")
            
            # FORWARD / BACKWARD
            if control['w'] > 0 and control['s'] == 0:
                self.engine.set_speed(control['w'] * self.max_speed)
                logger.info("Action: Forward")
            elif control['s'] > 0 and control['w'] == 0:
                self.engine.set_speed(-1 * control['s'] * self.max_speed)
                logger.info("Action: Backward")
            else:
                self.engine.set_speed(0)
                # logger.info("Action: Reset Speed")
            
            # LEFT / RIGHT
            if control['a'] > 0 and control['d'] == 0:
                perc = control['a'] * self.max_angle
                self.wheel.set_angle_percent(perc)
                logger.info(f"Action: Left ({perc})")
            elif control['d'] > 0 and control['a'] == 0:
                perc = -1 * control['d'] * self.max_angle
                self.wheel.set_angle_percent(perc)
                logger.info(f"Action: Right ({perc})")
            else:
                self.wheel.set_angle_percent(0)
                # logger.info("Action: Reset Angle")
            
            # Floats
            if control['float'] == 'up':
                self.float.up()
            else:
                self.float.down()

        
        elif event["source"] == "webinterface":
            config = event['content']['config']
            self.max_angle = config['max_steering_angle']
            self.max_speed = config['max_speed']
            self.wheel.set_steering_mode(config['steering_mode'])
            self.float.set_float(config['float'])
            logger.debug(event)

        else:
            logger.error(f'Received Data without source: {event}')
        

        # Response
        message = {
            'source': 'car',
            'content': {
                'angle': self.wheel.get_angle(),
                'steering_mode': self.wheel.get_steering_mode(),
                'speed': self.engine.get_speed(),
                'car_socket_status': 'true',
                'max_angle': self.max_angle,
                'max_speed': self.max_speed,
<<<<<<< HEAD
                'float_state': self.float.get_float_state()
=======
                'float_position': self.float.get_position()
>>>>>>> a1cc58826eae6e2b3fed5c6c6397d08a951fe4f3
            }
            
        }
        logger.success(f'Response: {message}')
        await self.send_message(message)