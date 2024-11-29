import math
from loguru import logger


### FREQ: 100hz

# Duty Cycles
MAX = 19
MIN = 11
HALT = 15

class Engine():
    pwm = None

    def __init__(self, pwm):
        self.pwm = pwm
        self.pwm.start(HALT)
        
        self.speed = 0
    
    async def stop(self):
        self.duty_cycle = HALT
        self.pwm.change_duty_cycle(self.duty_cycle)
        
    # speed in percent -100 to 100
    async def set_speed(self, speed): 
        self.speed = speed
        duty_cycle = self.map_range(self.speed, -100, 100, MIN, MAX)

        logger.info(f"Speed: {duty_cycle} ({self.speed})")
        
        self.pwm.change_duty_cycle(duty_cycle)
        
    async def get_speed(self):
        return self.speed

    def map_range(self, value, input_min, input_max, output_min, output_max):
        return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
