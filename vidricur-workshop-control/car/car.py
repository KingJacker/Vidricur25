import json
from loguru import logger
from patterns.singleton import Singleton
from queue import Queue
from car.engine import Engine
from car.wheel import Wheel

class Car(metaclass=Singleton):
    def __init__(self, sio, servo_kit, esc_pwm):
        self.servo_kit = servo_kit
        self.esc_pwm = esc_pwm
        self.sio = sio
        
        # Instanzierung
        self.engine = Engine(self.esc_pwm)
        
        try:
            self.wheel = Wheel(self.servo_kit)
        except Exception as e:
            logger.critical(f'Could not instantiate Wheel: {e}')

        self.max_angle = 0
        self.max_speed = 0

    def start(self):
        logger.info("SETTING START VALUES")
        self.wheel.set_angle_percent(self.wheel.initial_angle)
        self.engine.set_speed(0)

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

        
        elif event["source"] == "webinterface":
            config = event['content']['config']
            self.max_angle = config['max_steering_angle']
            self.max_speed = config['max_speed']
            self.wheel.set_steering_mode(config['steering_mode'])

        else:
            logger.error(f'Received Data without source: {event}')
        

        # Response
        message = {
            'source': 'car',
            'content': {
                'angle': self.wheel.get_angle(),
                'steering_mode': self.wheel.get_steering_mode(),
                'speed': self.engine.get_speed(),
                'car_socket_status': 'true'
            }
            
        }
        logger.success(f'Response: {message}')
        await self.send_message(message)