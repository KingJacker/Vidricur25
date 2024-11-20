import json
from loguru import logger
from patterns.singleton import Singleton
from queue import Queue
from car.engine import Engine
from car.wheel import Wheel

class Car(metaclass=Singleton):

    engine = None
    wheel = None

    def __init__(self, sio, servo_kit, esc_pwm):
        self.servo_kit = servo_kit
        self.esc_pwm = esc_pwm
        self.sio = sio
        
        self.engine = Engine(self.esc_pwm)
        self.wheel = Wheel(self.servo_kit)

        self.max_angle = 0
        self.max_speed = 0

    async def start(self):
        await self.wheel.set_angle_percent(0)
        await self.engine.setSpeed(0)

        logger.info("SETTING START VALUES")

    async def send_message(self, message):
        await self.sio.emit("message", json.dumps(message))

    async def handleEvent(self, event):
        logger.debug(event)

        # CONTROl EVENT
        if event["source"] == "control":
            control = event['content']['control']
            
            # STOP
            if control['space'] != 0:
                await self.engine.halt()
                logger.info("Action: Stop")
            
            # FORWARD / BACKWARD
            if control['w'] > 0 and control['s'] == 0:
                await self.engine.setSpeed(control['w'] * self.max_speed)
                logger.info("Action: Forward")
            elif control['s'] > 0 and control['w'] == 0:
                await self.engine.setSpeed(-1 * control['s'] * self.max_speed)
                logger.info("Action: Backward")
            else:
                await self.engine.setSpeed(0)
                # logger.info("Action: Reset Speed")
            
            # LEFT / RIGHT
            if control['a'] > 0 and control['d'] == 0:
                perc = control['a'] * self.max_angle
                await self.wheel.set_angle_percent(perc)
                logger.info(f"Action: Left ({perc})")
            elif control['d'] > 0 and control['a'] == 0:
                perc = -1 * control['d'] * self.max_angle
                await self.wheel.set_angle_percent(perc)
                logger.info(f"Action: Right ({perc})")
            else:
                await self.wheel.set_angle_percent(0)
                # logger.info("Action: Reset Angle")

        
        elif event["source"] == "webinterface":
            config = event['content']['config']
            self.max_angle = config['max_steering_angle']
            self.max_speed = config['max_speed']
            await self.wheel.set_steering_mode(config['steering_mode'])

        else:
            logger.error(f'Received Data without source: {event}')
        
        # # Action reponse
        # if (is_action):
        #     await self.send_message({"source": "car", "ok": was_successful, "error": error_message, "current_angle": self.current_angle, "current_speed": current_speed})
        # else:
        #     await self.send_message({"source": "car", "ok": False, "error": "Invalid action given", "current_angle": self.current_angle, "current_speed": current_speed})
        