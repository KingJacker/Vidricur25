from loguru import logger
from adafruit_motor import servo

ANGLE_MIN = 0
ANGLE_MAX = 180
ANGLE_MID = ANGLE_MAX / 2

class Wheel():
    def __init__(self, pca):

        self.servo_front = servo.Servo(pca.channels[0]) # no definition of min/ max pulse -> default 180 deg servo
        self.servo_rear = servo.Servo(pca.channels[1])

        # angles are from -100 to +100
        self.angle_front = 0
        self.angle_rear = 0
        self.steering_mode = 'front-steering'

        # set initial servo position
        self.initial_angle = ANGLE_MID
        self.servo_front.angle = self.initial_angle
        self.servo_rear.angle = self.initial_angle

    def set_angle_percent(self, perc):
        self.angle_front = self.map_range(perc, -100, 100, ANGLE_MIN, ANGLE_MAX)
        self.angle_rear = self.map_range(perc, -100, 100, ANGLE_MAX, ANGLE_MIN) # invert max / min here if necessary

        logger.info(f'Set Angle: {self.angle_front} / {self.angle_rear} ({perc}) Mode: {self.steering_mode}')

        if self.steering_mode == 'front-steering':
            self.servo_front.angle = self.angle_front
        elif self.steering_mode == 'rear-steering':
            self.servo_rear.angle = self.angle_front
        elif self.steering_mode == 'both-steering':
            self.servo_front.angle = self.angle_front
            self.servo_rear.angle = self.angle_rear
        else:
            logger.error("No Steering Mode provided!")

    def get_angle(self):
        return self.angle_front
    
    def set_steering_mode(self, steering_mode):
        self.steering_mode = steering_mode

    def get_steering_mode(self):
        return self.steering_mode

    def map_range(self, value, input_min, input_max, output_min, output_max):
        return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
