import math
from loguru import logger


### FREQ: 100hz

# Duty Cycles
MAX = 18.95
MIN = 12
HALT = 15

STEP = 1


class Engine():
    
    duty_cycle = HALT
    pwm = None

    def __init__(self, pwm):
        self.pwm = pwm
        self.pwm.start(self.duty_cycle)
    
    async def halt(self):
        self.duty_cycle = HALT
        self.pwm.change_duty_cycle(self.duty_cycle)
        
    async def setSpeed(self, perc):

        duty_cycle = await self.map_range(perc, -1, 1, MIN, MAX)

        # Speed from -100% <--> 0% <--> 100%
        # Pulse width is calculated from percentage
        
        # if perc < -80:
        #     perc = -80
        
        # if perc > 100:
        #     perc = 100
        
        # if perc >= 0:
        #     self.duty_cycle = perc * 4 + HALT
        # else:
        #     self.duty_cycle = HALT - (perc * 4)
        
        self.pwm.change_duty_cycle(duty_cycle)
        logger.info(f"Speed: {perc}")
        
    async def getSpeed(self):
        # Pluse width is converted into percentage value from -100% <--> 0% <--> 100%
        logger.info(self.duty_cycle)
        if self.duty_cycle >= HALT:
            return self.map_range(self.duty_cycle, HALT, MAX, 0, 100)
        else:
            return self.map_range(self.duty_cycle, MIN, HALT, -100, 0)


        
        self.pwm.change_duty_cycle(self.duty_cycle)
        logger.info(f"Increasing Motor Speed: {self.duty_cycle}")
        

        

    async def map_range(self, value, input_min, input_max, output_min, output_max):
        return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
