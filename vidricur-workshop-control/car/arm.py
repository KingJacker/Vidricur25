from loguru import logger
from adafruit_pca9685 import PWMChannel
import asyncio
import lgpio
import time


class Arm():
	def __init__(self, pca, gpio_handler): #supply gpio_handler!
		self.pca = pca
		self.speed = int(65536 * 0.75)
		self.homing_speed = int(65536 * 0.25)
		self.direction = 0
		self.arm_motor = PWMChannel(pca, 15)
		self.gpio_handler = gpio_handler
		self.motor_pin = 16
		self.endstop_pin = 13
		self.encoder_pin_A = 8
		self.encoder_pin_B = 7
		self.homing = False
		self.is_homed = False
		self.stopping = False

		lgpio.gpio_claim_output(self.gpio_handler, self.motor_pin)
		lgpio.gpio_claim_output(self.gpio_handler, self.endstop_pin, lgpio.SET_PULL_UP)
		# lgpio.gpio_claim_output(self.gpio_handler, self.encoder_pin_A)
		# lgpio.gpio_claim_output(self.gpio_handler, self.encoder_pin_B)

		# self.encoder = rotaryio.IncrementalEncoder(self.encoder_pin_A, self.encoder_pin_B)
		# self.last_position = None
	
	# async def encoder(self):
	# 	while True:
	# 		position = enc.position
	# 		if last_position == None or position != last_position:
	# 			logger.debug(position)
	# 		last_position = position


	def free_pins(self):
		lgpio.gpio_free(self.gpio_handler, self.motor_pin)
		lgpio.gpio_free(self.gpio_handler, self.endstop_pin)

	#Homing Sequence
	async def home(self):
		self.homing = True
		while self.homing and not self.stopping:
			logger.debug("Arm Homing")
			endstop = lgpio.gpio_read(self.gpio_handler, self.endstop_pin)
			logger.debug(endstop)
			if endstop == 0: # 0 is pressed
				logger.debug("Arm hit Endstop")
				self.stop()
				logger.debug("Arm Homed")
				self.is_homed = True  # allow normal control
				self.homing = False   # stop loop
			else:
				lgpio.gpio_write(self.gpio_handler, self.motor_pin, 1) # direction 1 is towards home
				self.arm_motor.duty_cycle = self.homing_speed
				self.homing = True   # continue loop until endstop
			asyncio.sleep(0.1)


	def set_direction(self, direction):
		self.direction = direction
		lgpio.gpio_write(self.gpio_handler, self.motor_pin, self.direction)

	def move(self):
		logger.debug(f"Moving arm, direction: {self.direction}, {self.arm_motor.duty_cycle}")
		self.arm_motor.duty_cycle = self.speed
		
	def stop(self):
		# logger.debug(f"Stopped arm")
		self.stopping = True
		self.arm_motor.duty_cycle = 0
	
	async def get_pos(self):
		return "None"

	