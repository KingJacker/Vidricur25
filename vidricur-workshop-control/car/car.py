import json
from loguru import logger
from patterns.singleton import Singleton
from car.engine import Engine
from car.wheel import Wheel
from car.float import Float
from car.sensors import Sensors
from car.arm import Arm
from car.magnet import Magnet
from car.querstrahler import Querstrahler
from car.magnet_balken import MagnetBalken
from car.camera_servos import CameraServos
import asyncio

class Car(metaclass=Singleton):
	def __init__(self, sio, pca, i2c, leds, gpio_handler):
		self.pca = pca
		self.sio = sio
		self.i2c = i2c
		self.leds = leds
		self.gpio_handler = gpio_handler

		# SENSORS
		try:
			self.sensors = Sensors(i2c)
		except Exception as e:
			logger.warning(f'Could not Instantiate Sensor: {e}')
		
		# ENGINE
		try:
			self.engine = Engine(self.pca)
		except Exception as e:
			logger.critical(f'Could not Instantiate Engine: {e}')
			exit(1)

		# WHEEL
		try:
			self.wheel = Wheel(self.pca, self.leds)
		except Exception as e:
			logger.critical(f'Could not Instantiate Wheel: {e}')
			exit(1)

		# FLOAT
		try: 
			self.float = Float(self.pca)
		except Exception as e:
			logger.critical(f'Could not instantiate Float: {e}')
			exit(1)

		# ARM
		try:
			self.arm = Arm(self.pca, self.gpio_handler)
		except Exception as e:
			logger.critical(f'Could not Instantiate Arm: {e}')
			exit(1)

		# magnet balken
		try: 
			self.magnet_balken = MagnetBalken(self.pca)
		except Exception as e:
			logger.critical(f'Could not Instantiate Magnet Balken: {e}')
			exit(1)

		# CameraServos
		try: 
			self.camera_servos = CameraServos(self.pca)
		except Exception as e:
			logger.critical(f'Could not Instantiate Camera Servos: {e}')
			exit(1)

		# MAGNET
		self.magnet = Magnet(self.gpio_handler)

		# QUERSTRAHLER
		self.querstrahler = Querstrahler(self.pca, self.gpio_handler)

	async def send_message(self, message): #? is this obsolete
		await self.sio.emit("message", json.dumps(message))



	async def command_handler(self, command):
		# logger.debug(command)

		# STOP
		if command['space'] != 0:
			self.engine.stop()
		
		# FORWARD / BACKWARD
		if command['w'] > 0 and command['s'] == 0 and command['p'] == 0:
			self.engine.set_speed(command['w'])
		elif command['s'] > 0 and command['w'] == 0 and command['p'] == 0:
			self.engine.set_speed(-1 * command['s']) # reverse with * -1
		else:
			self.engine.set_speed(0)
		
		# LEFT / RIGHT
		if command['a'] > 0 and command['d'] == 0:
			self.wheel.set_angle(command['a'])
		elif command['d'] > 0 and command['a'] == 0:
			self.wheel.set_angle(-1 * command['d'])
		else:
			self.wheel.set_angle(0)


		# Float up / down
		if command['e'] == 1 and command['q'] == 0:
			self.float.set_direction(-1) # down
		elif command['e'] == 0 and command['q'] == 1:
			self.float.set_direction(1) # up
		else:
			self.float.set_direction(0) # stop

		# Camera Rear
		if command['n'] == 1 and command['m'] == 0:
			self.camera_servos.set_direction_rear(-1) # down
		elif command['n'] == 0 and command['m'] == 1:
			self.camera_servos.set_direction_rear(1) # up
		else:
			self.camera_servos.set_direction_rear(0) # stop


		# Camera Front
		if command['t'] == 1 and command['g'] == 0:
			self.camera_servos.set_direction_front(-1) # down
		elif command['t'] == 0 and command['g'] == 1:
			self.camera_servos.set_direction_front(1) # up
		else:
			self.camera_servos.set_direction_front(0) # stop

		# Schwenkarm
		if command['f'] == 1 and command['r'] == 0 and self.arm.is_homed:
			self.arm.set_direction(1)
			self.arm.move()
		elif command['r'] == 1 and command['f'] == 0 and self.arm.is_homed:
			self.arm.set_direction(0) # reverse with * -1
			self.arm.move()
		elif self.arm.is_homed:
			self.arm.set_direction(0)
			self.arm.stop()

		# MAGNET 
		if command['u'] == 1 and command['j'] == 0:
			self.magnet.set_magnet_inactive()
		elif command['j'] == 1 and command['u'] == 0:
			self.magnet.set_magnet_active()
		else:
			pass

		# QUERSTRAHLER
		if command['p'] == 1:
			if command['w'] > 0 and command['s'] == 0:
				self.querstrahler.set_forward()
				self.querstrahler.move(command['w'])
			elif command['s'] > 0 and command['w'] == 0:
				self.querstrahler.set_backward()
				self.querstrahler.move(command['s'])
			elif command['a'] > 0 and command['d'] == 0:
				self.querstrahler.set_left()
				self.querstrahler.move(command['a'])
			elif command['d'] > 0 and command['a'] == 0:
				self.querstrahler.set_right()
				self.querstrahler.move(command['d'])
			else:
				self.querstrahler.stop()
		else:
			self.querstrahler.stop()
	
	async def start_servo_movers(self):
		logger.info("STARTING SERVO MOVERS")
		self.home_task = asyncio.create_task(self.arm.home())
		self.float_task = asyncio.create_task(self.float.move())
		self.camera_task = asyncio.create_task(self.camera_servos.move())
		# camera servos