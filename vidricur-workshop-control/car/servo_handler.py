from loguru import logger
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685, PWMChannel
import board
import asyncio

class SLOW_SERVO():
	def __init__(self, pca, channel, min_duty, max_duty, range, delay, step):
		self.pca = pca
		self.channel = channel
		self.min_duty = min_duty # actually us
		self.max_duty = max_duty # --//--
		self.range = range
		self.delay = delay
		self.step = step
		
		self.pca_resolution = 65536

		self.target_duty = None

		self.servo = PWMChannel(pca, channel)

		self.angle = self.get_angle()


	# moves to target angle
	async def move(self, angle):
		self.angle = angle
		self.target_us = self.map_range(self.angle, 0, self.range, self.min_duty, self.max_duty) # to micro seconds
		self.target_duty = int(self.target_us / 20000 * self.pca_resolution) # to actual pca duty

		while abs(self.target_duty - self.servo.duty_cycle) >= 15:
			current_duty = self.servo.duty_cycle
			

			if self.target_duty > current_duty:
				self.servo.duty_cycle = current_duty + self.step
				await asyncio.sleep(self.delay)


			elif self.target_duty < current_duty:
				self.servo.duty_cycle = current_duty - self.step
				await asyncio.sleep(self.delay)

			else:
				print("target == current")
				self.servo.duty_cycle = self.target_duty

			print(current_duty, self.target_duty)

	# dir: -1, 0, +1
	# min, max: angles <= range
	async def move_dir(self, direction, min_angle, max_angle):
		# self.angle = round(self.get_angle())
		move_min_duty = self.angle_to_duty(min_angle)
		move_max_duty = self.angle_to_duty(max_angle)
		current_duty = self.servo.duty_cycle

		potential_next_duty = current_duty + (self.step * direction)
		clamped_next_duty = max(move_min_duty, min(potential_next_duty, move_max_duty))

		if clamped_next_duty != current_duty:
			self.servo.duty_cycle = clamped_next_duty
			current_duty = clamped_next_duty

			await asyncio.sleep(self.delay)

			self.angle = self.get_angle()
			logger.debug(f"Angle: {self.angle:.2f}")

		else:
			current_angle = self.get_angle()
			logger.debug(f"Float Servo {self.channel} at limit")

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