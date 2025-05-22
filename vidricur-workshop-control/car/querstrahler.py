from loguru import logger
from adafruit_pca9685 import PWMChannel
import asyncio
import lgpio

class Querstrahler():
	def __init__(self, pca, gpio_handler):
		self.pca = pca
		self.speed = int(65536 * 0.9)
		self.left_direction = 0
		self.right_direction = 0
		self.querstrahler_motor_left = PWMChannel(pca, 13)
		self.querstrahler_motor_right = PWMChannel(pca, 14)
		self.gpio_handler = gpio_handler
		self.motor_direction_pin_left = 20
		self.motor_direction_pin_right = 21

		lgpio.gpio_claim_output(self.gpio_handler, self.motor_direction_pin_left)
		lgpio.gpio_claim_output(self.gpio_handler, self.motor_direction_pin_right)


	def set_left_direction(self, direction):
		self.left_direction = direction
		lgpio.gpio_write(self.gpio_handler, self.motor_direction_pin_left, self.left_direction)

	def set_right_direction(self, direction):
		self.right_direction = direction
		lgpio.gpio_write(self.gpio_handler, self.motor_direction_pin_right, self.right_direction)


	def set_forward(self):
		self.set_left_direction(1)
		self.set_right_direction(1)

	def set_backward(self):
		self.set_left_direction(0)
		self.set_right_direction(0)

	def set_left(self):
		self.set_left_direction(0)
		self.set_right_direction(1)

	def set_right(self):
		self.set_left_direction(1)
		self.set_right_direction(0)

	def move(self, speed):
		self.querstrahler_motor_left.duty_cycle  = int(speed * self.speed)
		self.querstrahler_motor_right.duty_cycle = int(speed * self.speed)

		logger.debug(f"{self.left_direction}, {self.right_direction}, {speed}")
		logger.debug(f"{self.querstrahler_motor_left.duty_cycle}, {self.querstrahler_motor_right.duty_cycle}")

	def stop(self):
		self.querstrahler_motor_left.duty_cycle = 0
		self.querstrahler_motor_right.duty_cycle = 0