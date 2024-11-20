import asyncio
from loguru import logger

ANGLE_MIN = 0
ANGLE_MAX = 174
ANGLE_MID = ANGLE_MAX / 2

class Wheel():
    servos = None

    def __init__(self, servo_kit):
        self.servo_front = servo_kit.servo[0]
        self.servo_rear = servo_kit.servo[1]

        # angles are from -1 to +1
        self.angle_front = 0
        self.angle_rear = 0

        self.steering_mode = 'front-steering'

    async def set_angle_percent(self, perc):
        self.angle_front = await self.map_range(perc, -100, 100, ANGLE_MIN, ANGLE_MAX)
        self.angle_rear = await self.map_range(perc, -100, 100, ANGLE_MAX, ANGLE_MIN) # inverese

        logger.info(f'Set Angle: {self.angle_front} / {self.angle_rear} ({perc}) Mode: {self.steering_mode}')

        if self.steering_mode == 'front-steering':
            self.servo_front.angle = self.angle_front
        elif self.steering_mode == 'rear-steering':
            self.servo_rear.angle = self.angle_front
        elif self.steering_mode == 'both-steering':
            self.servo_front.angle = self.angle_front
            self.servo_rear.angle = self.angle_front
        else:
            logger.error("No Steering Mode provided!")
    
    async def set_steering_mode(self, steering_mode):
        self.steering_mode = steering_mode

    async def map_range(self, value, input_min, input_max, output_min, output_max):
        return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
