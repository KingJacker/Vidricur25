import car.servo_handler as sh
from loguru import logger
from adafruit_motor import servo

# pca pins
CHANNEL_CAMERA_FRONT_PAN = 0
CHANNEL_CAMERA_FRONT_TILT = 1
CHANNEL_CAMERA_REAR_PIVOT = 2  

# 3 POSITIONS
    # pan: left, center, right
    # tilt: down, center, up

class CameraServos():
    def __init__(self, pca):
        self.pca = pca

        self.camera_front_horizontal_positions = [0, 90, 180]
        self.camera_front_vertical_positions   = [0, 90, 180]
        self.camera_rear_horizontal_positions = [0, 180]

        # servo setup
        self.min_pulse = 500
        self.max_pulse = 2500
        self.servo_range = 180

        # defining servos
        self.servo_front_horizontal = servo.Servo(self.pca.channels[CHANNEL_CAMERA_FRONT_PAN], min_pulse=self.min_pulse, max_pulse = self.max_pulse, actuation_range=self.servo_range) # no definition of min/ max pulse -> default 180 deg servo
        self.servo_front_vertical   = servo.Servo(self.pca.channels[CHANNEL_CAMERA_FRONT_TILT], min_pulse=self.min_pulse, max_pulse = self.max_pulse, actuation_range=self.servo_range)
        self.servo_rear_horizontal  = servo.Servo(self.pca.channels[CHANNEL_CAMERA_REAR_PIVOT], min_pulse=self.min_pulse, max_pulse = self.max_pulse, actuation_range=self.servo_range)

        # current positions
        self.current_front_horizontal_position = 1
        self.current_front_vertical_position   = 1
        self.current_rear_horizontal_position  = 0

        # starting position
        self.servo_front_horizontal.angle = self.camera_front_horizontal_positions[self.current_front_horizontal_position]
        self.servo_front_vertical.angle   = self.camera_front_vertical_positions[self.current_front_vertical_position]
        self.servo_rear_horizontal.angle  = self.camera_rear_horizontal_positions[self.current_rear_horizontal_position]


    def move_camera_front_horizontal(self, direction):
        if direction == 'left':
            self.current_front_horizontal_position -= 1
        elif direction == 'right':
            self.current_front_horizontal_position += 1

        self.servo_front_horizontal.angle = self.camera_front_horizontal_positions[self.current_front_horizontal_position]

    def move_camera_front_vertical(self, direction):
        if direction == 'down':
            self.current_front_vertical_position -= 1
        elif direction == 'up':
            self.current_front_vertical_position += 1

        self.servo_front_vertical.angle = self.camera_front_vertical_positions[self.current_front_vertical_position]

    def move_camera_rear_horizontal(self, position): # position = 'retracted' or 'deployed' 
        if position == 'retracted':
            self.servo_rear_horizontal.angle = self.camera_rear_horizontal_positions[0]
        elif position == 'deployed':
            self.servo_rear_horizontal.angle = self.camera_rear_horizontal_positions[1]


# class CameraServos():
#     def __init__(self, pca):
#         self.pca = pca

#         # 2 for pan and tilt on cam 1
#         self.servo_pan = sh.SLOW_SERVO(self.pca, CHANNEL_CAMERA_1_PAN, 0, 100, 0, 180, 180, DELAY, STEP)
#         self.servo_tilt = sh.SLOW_SERVO(self.pca, CHANNEL_CAMERA_1_TILT, 0, 100, 0, 180, 180, DELAY, STEP)

#         # 1 for pivot on cam 2
#         self.servo_pivot = sh.SLOW_SERVO(self.pca, CHANNEL_CAMERA_2_PIVOT, 0, 100, 0, 180, 180, DELAY, STEP)

#     async def move(self):
#         asyncio.create_task(self.servo_pan.move())
#         asyncio.create_task(self.servo_tilt.move())
#         asyncio.create_task(self.servo_pivot.move())


