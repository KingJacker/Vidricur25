from loguru import logger
from adafruit_pca9685 import PWMChannel
import asyncio
import lgpio

class Arm():
	def __init__(self, pca, gpio_handler): #supply gpio_handler!
		self.pca = pca
		self.speed = int(65536 * 0.75)
		self.direction = 0
		self.arm_motor = PWMChannel(pca, 15)
		self.gpio_handler = gpio_handler
		self.pin = 16

		lgpio.gpio_claim_output(self.gpio_handler, self.pin)

	def set_direction(self, direction):
		self.direction = direction
		lgpio.gpio_write(self.gpio_handler, self.pin, self.direction)

		# GPIO erstellen / setzen

	def move(self):
		logger.debug(f"Moving arm, direction: {self.direction}, {self.arm_motor.duty_cycle}")
		self.arm_motor.duty_cycle = self.speed
		
	def stop(self):
		logger.debug(f"Stopped arm")
		self.arm_motor.duty_cycle = 0
	