import math

# This is an engine control for the Brushless System Combo: https://shop.robitronic.com/de/hobbywing-xerun-justock-combo-g3-hw38020321
# The controlling instance is based on https://gitlab.fhnw.ch/makerstudio/sw-vidricur

# Connect the ESC to the GPIO PIN 4
ESC = 4

# Maximum pluse width
# This value depends on the drive you use: https://gitlab.fhnw.ch/makerstudio/sw-vidricur
# More about: https://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
MAX = 1900

# Minimum pulse width
# This value depends on the drive you use: https://gitlab.fhnw.ch/makerstudio/sw-vidricur
# More about: https://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
MIN = 1200 
#MIN = 1220  # change this if your ESC's min value is different or leave it be

# Neural pulse width -> Stops the engine
# This value depends on the drive you use: https://gitlab.fhnw.ch/makerstudio/sw-vidricur
# More about: https://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
HALT = 1500

# Step to increase or decrease the pulse width 
STEP = 5


class Engine():
    
    pulsewidth = HALT
    pi = None

    def __init__(self, pi):
        self.pi = pi
    
    async def halt(self):
        self.pulsewidth = HALT
        # Set the pulse width of the PWM Pin
        # More about: https://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
        self.pi.set_servo_pulsewidth(ESC, self.pulsewidth)
        
    async def setSpeed(self, perc):
        # Speed from -100% <--> 0% <--> 100%
        # Pulse width is calculated from percentage
        
        if perc < -80:
            perc = -80
        
        if perc > 100:
            perc = 100
        
        if perc >= 0:
            self.pulsewidth = perc * 4 + HALT
        else:
            self.pulsewidth = HALT - (perc * 4)
        
        # Set the pulse width of the PWM Pin
        # More about: https://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
        self.pi.set_servo_pulsewidth(ESC, self.pulsewidth)
        
    async def getSpeed(self):
        # Pluse width is converted into percentage value from -100% <--> 0% <--> 100%
        
        if self.pulsewidth >= HALT:
            return int((self.pulsewidth - HALT) / 4)
        else:
            return (100 - int((abs(self.pulsewidth) - HALT) / 4))
        
    async def increaseSpeed(self):
        # Increase current pulse width
        self.pulsewidth += STEP
        
        # If new pulse width reaches the maximum it is set to maximum
        if self.pulsewidth > MAX:
            self.pulsewidth = MAX

        print(self.pulsewidth)
        
        # Set the pulse width of the PWM Pin
        # More about is https://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
        self.pi.set_servo_pulsewidth(ESC, self.pulsewidth)
        
    async def decreaseSpeed(self):
        # Decrease current pulse width
        self.pulsewidth -= STEP
        
        # If new pulse width reaches the minimum it is set to minimum
        if self.pulsewidth < MIN:
            self.pulsewidth = MIN
            
        print(self.pulsewidth)
        # Set the pulse width of the PWM Pin
        # More about is https://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
        self.pi.set_servo_pulsewidth(ESC, self.pulsewidth)
        
        
    async def stop(self):
        # Set the pulse width of the PWM Pin
        # More about is https://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
        self.pi.set_servo_pulsewidth(ESC, 0)
