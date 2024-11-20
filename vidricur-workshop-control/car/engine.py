import math
from loguru import logger


### FREQ: 100hz

# Duty Cycles
MAX = 19
MIN = 11
HALT = 15

STEP = 1


class Engine():
    pwm = None

    def __init__(self, pwm):
        self.pwm = pwm
        self.pwm.start(HALT)
    
    async def halt(self):
        self.duty_cycle = HALT
        self.pwm.change_duty_cycle(self.duty_cycle)
        
    async def setSpeed(self, perc):
        duty_cycle = await self.map_range(perc, -100, 100, MIN, MAX)
        logger.info(f"Speed: {duty_cycle} ({perc})")
        
        self.pwm.change_duty_cycle(duty_cycle)
        
        


    async def map_range(self, value, input_min, input_max, output_min, output_max):
        return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
