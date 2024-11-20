import asyncio
from loguru import logger

SERVO_MAX = 12.5
SERVO_MIN = 2.5
STRAIGHT_FORWARD = 2.5 + 5

ANGLE_MIN = 0
ANGLE_MAX = 174
ANGLE_MID = ANGLE_MAX / 2

class Wheel():
    pwm = None
    duty_cycle = STRAIGHT_FORWARD

    def __init__(self, pwm):
        self.pwm = pwm

        #* Hardware PWM
        # self.pwm.start(self.duty_cycle)

    async def set_angle(self, deg):
        #* Hardware PWM
        # self.duty_cycle = int(((SERVO_MAX - SERVO_MIN) / 180) * deg) + SERVO_MIN
        # self.pwm.change_duty_cycle(self.duty_cycle)

        #* Servokit (i2c board)
        self.pwm.servo[0].angle = deg

        await asyncio.sleep(0.2)

    async def set_angle_percent(self, perc):
        angle = await self.map_range(perc, -1, 1, ANGLE_MIN, ANGLE_MAX)
        # logger.info(f'Set Angle: {angle} ({perc})')
        self.pwm.servo[0].angle = angle

    async def map_range(self, value, input_min, input_max, output_min, output_max):
        return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
