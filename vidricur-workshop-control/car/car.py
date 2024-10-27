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
        
        # Creates an engine instance with the GPIO pi instance reference
        self.engine = Engine(self.esc_pwm)
        # Creates a wheel instance with the GPIO instance pi reference
        self.wheel = Wheel(self.steering_pwm)

    async def start(self):
        ## Initial configuration    
        # Wheel straight forward
        await self.wheel.set_angle(90)
        # Engine halt
        await self.engine.setSpeed(0)

        logger.info("SETTING START VALUES")

    async def send_message(self, message):
        await self.sio.emit("message", json.dumps(message))

    async def handleEvent(self, event):
        #logger.info("Event: ", event)
        
        is_action = False
        was_successful = False
        error_message = ""
        
        # If the event is a move event
        if event["action"] == "move":
            # Get angle of the wheels
            angle = int(event["options"]["angle"])
            
            # Decrease the event
            if event["options"]["speed"] == -1:
                # Decrease the engine speed
                await self.engine.decreaseSpeed()
                logger.info("Action - Decrease engine speed")
                is_action = True
                was_successful = True
                
            # Increase the event
            elif event["options"]["speed"] == 1:
                # Increase the engine speed
                await self.engine.increaseSpeed()
                logger.info("Action - Increase engine speed")
                is_action = True
                was_successful = True
            
            # If there is a new angle compared to the current angle
            if self.current_angle != angle:
                # Set new angle of the wheels
                await self.wheel.set_angle(int(event["options"]["angle"]))
                self.current_angle = angle
                logger.info("Action - Set wheel angle: " + str(angle))
                is_action = True
                was_successful = True
                
        # Stop the car event
        elif event["action"] == "stop":
            await self.engine.halt()
            logger.info("Action - Stop")
            is_action = True
            was_successful = True
            
        # If the websocket disconnect -> Emerency halt of the car
        elif event["action"] == "disconnect":
            await self.engine.halt()
            logger.info("Action - Disconnect: Emergency halt!")
            is_action = True
            was_successful = True
        
        current_speed = await self.engine.getSpeed()
        
        # Action reponse
        if (is_action):
            await self.send_message({"ok": was_successful, "error": error_message, "current_angle": self.current_angle, "current_speed": current_speed})
        else:
            await self.send_message({"ok": False, "error": "Invalid action given", "current_angle": self.current_angle, "current_speed": current_speed})
        