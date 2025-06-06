import asyncio
from loguru import logger
from adafruit_motor import servo

class MagnetBalken():
	def __init__(self, pca):
		self.pca = pca

		# servo setup
		self.min_pulse = 500
		self.max_pulse = 2500
		self.servo_range = 270
		self.servo_channel = 6

		# positions	
		self.down = 0
		self.mid = 90
		self.up = 180

		self.initial = self.mid

		self.current_pos = "mid"

		# defining servos
		self.servo = servo.Servo(self.pca.channels[self.servo_channel], min_pulse=self.min_pulse, max_pulse = self.max_pulse, actuation_range=self.servo_range)
		self.servo.angle = self.initial

	def set_pos(self, pos):
		if pos == "down":
			self.current_pos = "down"
			self.servo.angle = self.down
		elif pos == "mid":
			self.current_pos = "mid"
			self.servo.angle = self.mid
		elif pos == "up":
			self.current_pos = "up"
			self.servo.angle = self.up
	
	def get_pos(self):
		return self.current_pos