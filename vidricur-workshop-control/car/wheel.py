import asyncio
from loguru import logger
from adafruit_motor import servo
import car.config_handler as ch

class Wheel():
    def __init__(self, pca, leds):
        self.pca = pca
        self.leds = leds

        # servo setup
        self.min_pulse = 500
        self.max_pulse = 2500
        self.servo_range = 180
        
        # defining servos
        self.servo_front = servo.Servo(self.pca.channels[0], min_pulse=self.min_pulse, max_pulse = self.max_pulse, actuation_range=self.servo_range) # no definition of min/ max pulse -> default 180 deg servo
        self.servo_rear  = servo.Servo(self.pca.channels[1], min_pulse=self.min_pulse, max_pulse = self.max_pulse, actuation_range=self.servo_range)

        # centered position
        # self.servo_center = int(self.servo_range / 2)
        steering_config = ch.get_steering_config()
        logger.debug(steering_config)
        self.servo_center_front = steering_config[0]
        self.servo_center_rear  = steering_config[1]

        self.max_deflection = steering_config[2]

        self.angle_front = 0
        self.angle_rear = 0
        self.steering_mode = 'front-steering'

        # set initial servo position
        self.servo_front.angle = self.servo_center_front
        self.servo_rear.angle  = self.servo_center_rear


    def set_angle(self, value):
        self.deflection = self.max_deflection * value

        self.angle_front = self.deflection + self.servo_center_front
        self.angle_rear  = - self.deflection + self.servo_center_rear

        # logger.info(f"Set Angle FRONT: {self.angle_front} REAR: {self.angle_rear} DEFL:{self.deflection}")

        if self.steering_mode == 'front':
            self.servo_front.angle = self.angle_front
            self.leds.set_steering_front()
        elif self.steering_mode == 'rear':
            self.servo_rear.angle = self.angle_front
            self.leds.set_steering_rear()
        elif self.steering_mode == 'both':
            self.servo_front.angle = self.angle_front
            self.servo_rear.angle = self.angle_rear
            self.leds.set_steering_both()
        elif self.steering_mode == 'skew':
            self.servo_front.angle = self.angle_front
            self.servo_rear.angle = self.angle_front
        else:
            # logger.error("No Steering Mode provided!")
            self.leds.set_steering_none()

    async def get_angle_front(self):
        return int(self.servo_front.angle - self.servo_center_front)
    
    async def get_angle_rear(self):
        return int(self.servo_rear.angle - self.servo_center_rear)
    
    def set_steering_mode(self, steering_mode):
        self.steering_mode = steering_mode

    async def get_steering_mode(self):
        return self.steering_mode

    def set_max_deflection(self, max_deflection):
        # logger.debug(f"Set Max Deflection: {max_deflection}")
        self.max_deflection = int(max_deflection)

    async def get_max_deflection(self):
        return self.max_deflection

    def map_range(self, value, input_min, input_max, output_min, output_max):
        return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
