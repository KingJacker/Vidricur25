
# PWM control PIN of the servo
SERVO_PIN = 20

# Maximum pulse width where the servo is stearing right
SERVO_MAX = 1750
# Minimum pulse width where the servo is stearning left
SERVO_MIN = 1250
# Pluse width where the servo is straight forward
STRAIGHT_FORWARD = 1500

class Wheel():
    
    pi = None

    def __init__(self, pi):
        self.pi = pi
        
        # Set the pulse width of the PWM Pin
        # More about: https://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
        self.pi.set_servo_pulsewidth(SERVO_PIN, STRAIGHT_FORWARD)

    async def set_angle(self, deg):
        # Converts 0-180 degress to pluse width between 1250 and 1750
        pulsewidth = int(((SERVO_MAX - SERVO_MIN) / 180) * deg) + SERVO_MIN
        # Set the pulse width of the PWM Pin
        # More about: https://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
        self.pi.set_servo_pulsewidth(SERVO_PIN, pulsewidth)