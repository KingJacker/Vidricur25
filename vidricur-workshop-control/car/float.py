# floats
from adafruit_motor import servo
from loguru import logger

class Float():
    def __init__(self, pca):

        self.servo_left = servo.Servo(pca.channels[2], min_pulse=500, max_pulse = 2500, actuation_range=360)
        self.servo_right = servo.Servo(pca.channels[3], min_pulse=500, max_pulse = 2500, actuation_range=360)

        self.up_pos = 25
        self.down_pos = 290

        self.state = None

    def set_float(self, config):
        if config == "down":
            self.float_down()
        elif config == "up":
            self.float_up()
        else:
            logger.error("float not defined")
    
    def float_up(self):
        self.servo_left.angle = self.up_pos
        self.servo_right.angle = self.up_pos
        self.state = "UP"

    def float_down(self):
        self.servo_left.angle = self.down_pos
        self.servo_right.angle = self.down_pos
        self.state = "DOWN"
    
    def get_float_state(self):
        logger.debug(self.state)
        return self.state