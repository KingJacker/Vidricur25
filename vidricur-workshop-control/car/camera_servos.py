import asyncio
# from adafruit_motor import servo
from loguru import logger
import car.config_handler as ch
import car.servo_handler as sh

CHANNEL_FRONT  = 8
CHANNEL_REAR = 5
MIN_DUTY =  500
MAX_DUTY = 2500
RANGE_REAR = 360
RANGE_FRONT = 180

DELAY = 0.1
STEP = 40

FRONT_MIN = 0
FRONT_MAX = 180

REAR_MIN = 75
REAR_MAX = 180

class CameraServos():
	def __init__(self, pca):
		self.pca = pca

		# Initialize Servos as SLOW_SERVOS
		self.servo_cam_rear  = sh.SLOW_SERVO(self.pca, CHANNEL_REAR , MIN_DUTY, MAX_DUTY, REAR_MIN, REAR_MAX, RANGE_REAR, DELAY, STEP)
		self.servo_cam_front = sh.SLOW_SERVO(self.pca, CHANNEL_FRONT , MIN_DUTY, MAX_DUTY, FRONT_MIN, FRONT_MAX, RANGE_FRONT, DELAY, STEP)



	async def move(self):
		asyncio.create_task(self.servo_cam_rear.move())
		asyncio.create_task(self.servo_cam_front.move())

	def set_direction_rear(self, direction):
		self.servo_cam_rear.set_direction(direction)
	
	def set_direction_front(self, direction):
		self.servo_cam_front.set_direction(direction)

	
	async def get_cam_front(self):
		return int(self.servo_cam_front.angle)
	
	async def get_cam_rear(self):
		return int(self.servo_cam_rear.angle)