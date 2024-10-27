import time

SERVO_MAX = 12.5
SERVO_MIN = 2.5
STRAIGHT_FORWARD = 2.5 + 5

class Wheel():
    pwm = None
    duty_cycle = STRAIGHT_FORWARD

    def __init__(self, pwm):
        self.pwm = pwm
        self.pwm.start(self.duty_cycle)

    async def set_angle(self, deg):
        self.duty_cycle = int(((SERVO_MAX - SERVO_MIN) / 180) * deg) + SERVO_MIN
        self.pwm.change_duty_cycle(self.duty_cycle)
        time.sleep(0.2)