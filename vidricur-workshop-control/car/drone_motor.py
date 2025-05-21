from adafruit_pca9685 import PWMChannel

class DroneMotor():
    def __init__(self, pca, channel):
        self.motor = PWMChannel(pca, channel)
        self.min_duty = 2600
        self.max_duty = 6500
        self.duty_cycle = 0


    def set_duty_cycle(self, duty_cycle):
        self.motor.duty_cycle = duty_cycle

    def get_duty_cycle(self):
        return self.motor.duty_cycle

    def stop(self):
        self.set_duty_cycle(0)

