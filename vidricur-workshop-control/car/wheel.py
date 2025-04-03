import asyncio
from loguru import logger
from adafruit_motor import servo

class Wheel():
    def __init__(self, pca):
        # servo setup
        self.min_pulse = 500
        self.max_pulse = 2500
        self.servo_range = 180
        
        # defining servos
        self.servo_front = servo.Servo(pca.channels[0], min_pulse=self.min_pulse, max_pulse = self.max_pulse, actuation_range=self.servo_range) # no definition of min/ max pulse -> default 180 deg servo
        self.servo_rear  = servo.Servo(pca.channels[1], min_pulse=self.min_pulse, max_pulse = self.max_pulse, actuation_range=self.servo_range)

        # centered position
        self.servo_center = int(self.servo_range / 2)

        self.max_deflection = 0

        # angles are from -100 to +100
        self.angle_front = 0
        self.angle_rear = 0
        self.steering_mode = 'front-steering'

        # set initial servo position
        self.initial_angle = self.servo_range
        self.servo_front.angle = self.initial_angle
        self.servo_rear.angle  = self.initial_angle


    def set_angle(self, value):
        self.deflection = self.max_deflection * value

        self.angle_front = self.deflection + self.servo_center
        self.angle_rear  = self.deflection + self.servo_center

        logger.info(f"Set Angle FRONT: {self.angle_front} REAR: {self.angle_rear} DEFL:{self.deflection}")

        if self.steering_mode == 'front':
            self.servo_front.angle = self.angle_front
        elif self.steering_mode == 'rear':
            self.servo_rear.angle = self.angle_front
        elif self.steering_mode == 'both':
            self.servo_front.angle = self.angle_front
            self.servo_rear.angle = self.angle_rear
        else:
            logger.error("No Steering Mode provided!")

    async def get_angle_front(self):
        return self.angle_front
    
    async def get_angle_rear(self):
        return self.angle_rear
    
    def set_steering_mode(self, steering_mode):
        self.steering_mode = steering_mode

    async def get_steering_mode(self):
        return self.steering_mode

    def set_max_deflection(self, max_deflection):
        logger.debug(f"Set Max Deflection: {max_deflection}")
        self.max_deflection = int(max_deflection)

    async def get_max_deflection(self):
        return self.max_deflection

    def map_range(self, value, input_min, input_max, output_min, output_max):
        return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
