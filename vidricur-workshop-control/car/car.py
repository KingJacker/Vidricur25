import json
from loguru import logger
from patterns.singleton import Singleton
from queue import Queue
from car.engine import Engine
from car.wheel import Wheel

# Event types:
# Move event: Instruction to move the car
# JSON Request: {"action": "move", "options": {"speed": [-1, 0, 1], "angle": [0-180]}}
# JSON Response: {"ok": [true|false], "error": "", "current_angle": [0-180], "current_speed": [-100-100]}

# Stop event: Stop movement of the car
# JSON Request: {"action": "stop"}
# JSON Response: {"ok": [true|false], "error": "", "current_angle": [0-180], "current_speed": [-100-100]}

# Disconnect event: Car control is disconnected from the remote
# JSON Request: {"action": "disconnect"}
# JSON Response: {"ok": [true|false], "error": "", "current_angle": [0-180], "current_speed": [-100-100]}

class Car(metaclass=Singleton):

    engine = None
    wheel = None
    current_angle = 0

    def __init__(self, sio, steering_pwm, esc_pwm):
        self.steering_pwm = steering_pwm
        self.esc_pwm = esc_pwm
        self.sio = sio
        
        self.engine = Engine(self.esc_pwm)
        self.wheel = Wheel(self.steering_pwm)

        self.max_angle = 0.5
        self.max_speed = 0



    async def start(self):
        await self.wheel.set_angle(90)
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

        # if event["source"] == "remote":
        #     logger.debug(event)


        # is_action = False
        # was_successful = False
        # error_message = ""
        
        # # If the event is a move event
        # if event["action"] == "move":
        #     # Get angle of the wheels
        #     angle = int(event["options"]["angle"])
            
        #     # Decrease the event
        #     if event["options"]["speed"] == -1:
        #         # Decrease the engine speed
        #         await self.engine.decreaseSpeed()
        #         logger.info("Action - Decrease engine speed")
        #         is_action = True
        #         was_successful = True
                
        #     # Increase the event
        #     elif event["options"]["speed"] == 1:
        #         # Increase the engine speed
        #         await self.engine.increaseSpeed()
        #         logger.info("Action - Increase engine speed")
        #         is_action = True
        #         was_successful = True
            
        #     # If there is a new angle compared to the current angle
        #     if self.current_angle != angle:
        #         # Set new angle of the wheels
        #         await self.wheel.set_angle(int(event["options"]["angle"]))
        #         self.current_angle = angle
        #         logger.info("Action - Set wheel angle: " + str(angle))
        #         is_action = True
        #         was_successful = True
                
        # # Stop the car event
        # elif event["action"] == "stop":
        #     await self.engine.halt()
        #     logger.info("Action - Stop")
        #     is_action = True
        #     was_successful = True
            
        # # If the websocket disconnect -> Emerency halt of the car
        # elif event["action"] == "disconnect":
        #     await self.engine.halt()
        #     logger.info("Action - Disconnect: Emergency halt!")
        #     is_action = True
        #     was_successful = True
        
        # current_speed = await self.engine.getSpeed()
        
        # # Action reponse
        # if (is_action):
        #     await self.send_message({"source": "car", "ok": was_successful, "error": error_message, "current_angle": self.current_angle, "current_speed": current_speed})
        # else:
        #     await self.send_message({"source": "car", "ok": False, "error": "Invalid action given", "current_angle": self.current_angle, "current_speed": current_speed})
        