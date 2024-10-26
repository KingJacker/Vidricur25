import math



### FREQ: 100hz

# Duty Cycles
MAX = 19
MIN = 12
HALT = 15

STEP = 0.05


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
        # Speed from -100% <--> 0% <--> 100%
        # Pulse width is calculated from percentage
        
        if perc < -80:
            perc = -80
        
        if perc > 100:
            perc = 100
        
        if perc >= 0:
            self.duty_cycle = perc * 4 + HALT
        else:
            self.duty_cycle = HALT - (perc * 4)
        
        self.pwm.change_duty_cycle(self.duty_cycle)
        print(f"Setting Motor PWM: {self.duty_cycle}")
        
    async def getSpeed(self):
        # Pluse width is converted into percentage value from -100% <--> 0% <--> 100%
        
        if self.duty_cycle >= HALT:
            return int((self.duty_cycle - HALT) / 4)
        else:
            return (100 - int((abs(self.duty_cycle) - HALT) / 4))
        
    async def increaseSpeed(self):
        # Increase current pulse width
        self.duty_cycle += STEP
        
        # If new pulse width reaches the maximum it is set to maximum
        if self.duty_cycle > MAX:
            self.duty_cycle = MAX

        
        self.pwm.change_duty_cycle(self.duty_cycle)
        print(f"Increasing Motor Speed: {self.duty_cycle}")
        
    async def decreaseSpeed(self):
        # Decrease current pulse width
        self.duty_cycle -= STEP
        
        # If new pulse width reaches the minimum it is set to minimum
        if self.duty_cycle < MIN:
            self.duty_cycle = MIN

        self.pwm.change_duty_cycle(self.duty_cycle)
        
    async def stop(self):
        self.pwm.change_duty_cycle(self.duty_cycle)
