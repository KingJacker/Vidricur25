import asyncio
# from adafruit_motor import servo
from loguru import logger
import car.config_handler as ch
import car.servo_handler as sh

# CHANNEL_FRONT  = 2
CHANNEL_REAR = 5
MIN_DUTY =  500
MAX_DUTY = 2500
RANGE_REAR = 360

DELAY = 0.1
STEP = 40

REAR_MIN = 75
REAR_MAX = 180

class CameraServos():
	def __init__(self, pca):
		self.pca = pca

		# Initialize Servos as SLOW_SERVOS
		self.servo_cam_front  = sh.SLOW_SERVO(self.pca, CHANNEL_REAR , MIN_DUTY, MAX_DUTY, REAR_MIN, REAR_MAX, RANGE_REAR, DELAY, STEP)



	async def move(self):
		asyncio.create_task(self.servo_cam_front.move())

	def set_direction_rear(self, direction):
		self.servo_cam_front.set_direction(direction)

	
	async def get_cam_front(self):
		return int(self.servo_left.angle)
	
	async def get_cam_rear(self):
		return int(self.servo_right.angle)