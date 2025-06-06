from loguru import logger
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685, PWMChannel
import board
import asyncio

class SLOW_SERVO():
	def __init__(self, pca, channel, min_duty, max_duty, min_angle, max_angle, range, delay, step):
		self.pca = pca
		self.channel = channel
		self.min_duty = min_duty # actually us
		self.max_duty = max_duty # --//--
		self.range = range
		self.delay = delay
		self.step = step
		self.min_angle = min_angle
		self.max_angle = max_angle
		
		self.pca_resolution = 65536

		self.move_min_duty = self.angle_to_duty(min_angle)
		self.move_max_duty = self.angle_to_duty(max_angle)

		self.target_duty = None
		self.current_duty = None
		self.direction = None

		self.active = False

		self.servo = PWMChannel(pca, channel)

		self.angle = self.get_angle()




	def set_direction(self, direction):
		self.direction = direction

		if self.direction != 0:
			self.active = True
		else:
			self.active = False

	# dir: -1, 0, +1
	# min, max: angles <= range
	async def move(self):
		try:
			logger.info(f"SERVO ({self.channel}) STARTED")
			while True:
				if self.active:
					self.current_duty = self.servo.duty_cycle
					potential_next_duty = self.current_duty + (self.step * self.direction)
					clamped_next_duty = max(self.move_min_duty, min(potential_next_duty, self.move_max_duty))

					if clamped_next_duty != self.current_duty:
						self.servo.duty_cycle = clamped_next_duty
						self.current_duty = clamped_next_duty
						await asyncio.sleep(self.delay)
					else:
						logger.debug(f"Float Servo {self.channel} at limit")
						await asyncio.sleep(0.5)
					logger.debug(f"MOVING({self.channel}): {self.direction}")
					
				else:
					await asyncio.sleep(0.5) # wait to check again if active
				
		except Exception as e:
			logger.error(f"Error Moving Servo: {e}")

	def map_range(self, value, input_min, input_max, output_min, output_max):
		return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))

	def get_duty_cycle(self):
		return self.servo.duty_cycle

	def get_angle(self):
		pca_duty = self.servo.duty_cycle
		us = pca_duty * 20000 / self.pca_resolution
		angle = self.map_range(us, self.min_duty, self.max_duty, 0, self.range)
		return angle

	def angle_to_duty(self, angle):
		us = self.map_range(angle, 0, self.range, self.min_duty, self.max_duty) # to micro seconds
		pca_duty = int(us / 20000 * self.pca_resolution) # to actual pca duty
		return pca_duty