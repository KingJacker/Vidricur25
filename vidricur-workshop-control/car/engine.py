import asyncio
from loguru import logger
from adafruit_pca9685 import PWMChannel

class Engine():
    def __init__(self, pca):
        self.min = 2000 # 0x0700 # 1792
        # self.mid = 3000 # 0x1380 # 4992 (has to be exactly in the middle of min and max)
        self.max = 7000 # 0x2000 # 8192

        self.mid = int(((self.max - self.min) / 2 ) + self.min)

        self.motor = PWMChannel(pca, 4) # index = 4 (channel)
        self.motor.duty_cycle = self.mid # stop (initial motor value)

        self.max_speed = 0
        self.speed = 0
    
    def stop(self):
        self.set_speed(0)
        
    #! TYPE ISSUE
    def set_speed(self, speed):
        if speed > 0: # forward
            self.speed = speed * (self.max_speed / 100) # input speed * max speed to limit throttle
        else: # reverse
            self.speed = speed # reverse speed at full speed (is reduced by esc to 25%)
        self.motor.duty_cycle = int(self.map_range(self.speed, -1, 1, self.min, self.max))
        print(self.motor.duty_cycle)
        
    async def get_speed(self):
        return self.speed * 100 # return as percent

    def set_max_speed(self, max_speed):
        self.max_speed = int(max_speed)

    async def get_max_speed(self):
        return self.max_speed

    def map_range(self, value, input_min, input_max, output_min, output_max):
        return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
