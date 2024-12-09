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

        # set initial motor speed
        self.initial_speed = 0
        self.set_speed(self.initial_speed)
    
    def stop(self):
        self.speed = 0
        self.set_speed(self.speed)
        
    # speed in percent -100 to 100
    def set_speed(self, speed): 
        self.speed = speed
        duty_cycle = self.map_range(self.speed, -100, 100, MIN, MAX)

        logger.info(f"Speed: {duty_cycle} ({self.speed})")
        
        self.pwm.change_duty_cycle(duty_cycle)
        
    def get_speed(self):
        return self.speed

    def map_range(self, value, input_min, input_max, output_min, output_max):
        return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
