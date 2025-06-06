import lgpio
import asyncio
import time

LED_PINS = [5,6,22,27,23,24]
LED_GREEN =  [5, 22, 23]
LED_RED =  [6, 27, 24]

LIGHT = 26

# the leds used are on when pulled low!
# 0 -> ON
# 1 -> OFF
class LEDS():
	def __init__(self, gpio_handler):
		self.h = gpio_handler
		self.light_state = "na"

		# Connection Status LEDS
		self.status_red   = LED_PINS[3]
		self.status_green = LED_PINS[2]

		# Steering Mode Indicators
		self.steering_green = LED_PINS[0]
		self.steering_red   = LED_PINS[1]

		self.light = LIGHT

		# TODO
		# Magnet State Indicator
		# self.magnet_green
		# self.magnet_red

		# set initial values
		self.startup_sequence()


		lgpio.gpio_write(self.h, self.status_red, 1) # start as disconnected


	def startup_sequence(self):
		# initialize gpios
		lgpio.gpio_claim_output(self.h, self.status_red)
		lgpio.gpio_claim_output(self.h, self.status_green)
		lgpio.gpio_claim_output(self.h, self.light)

		# animation

		# OFF
		for led in LED_PINS:
			lgpio.gpio_write(self.h, led, 1) # LED Off

		# ALL GREEN
		for led in LED_GREEN:
			lgpio.gpio_write(self.h, led, 0)
		time.sleep(0.5)

		# OFF
		for led in LED_PINS:
			lgpio.gpio_write(self.h, led, 1) # LED Off

		# ALL RED
		for led in LED_RED:
			lgpio.gpio_write(self.h, led, 0)
		time.sleep(0.5)

		# OFF
		for led in LED_PINS:
			lgpio.gpio_write(self.h, led, 1) # LED Off

		for i in range(0,8):
			self.enable_light()
			time.sleep(0.02)
			self.disable_light()
			time.sleep(0.02)



### CONNECTION LEDS ### 

	def set_connected(self):
		lgpio.gpio_write(self.h, self.status_green, 0)

	def set_disconnected(self):
		lgpio.gpio_write(self.h, self.status_green, 1)
		lgpio.gpio_write(self.h, self.status_red, 0)

	async def set_receiving(self):
		lgpio.gpio_write(self.h, self.status_red, 0)
		await asyncio.sleep(0.01)
		lgpio.gpio_write(self.h, self.status_red, 1)



### STEERING LEDS ### 
	
	def set_steering_front(self):
		lgpio.gpio_write(self.h, self.steering_green, 0)
		lgpio.gpio_write(self.h, self.steering_red, 1)

	def set_steering_rear(self):
		lgpio.gpio_write(self.h, self.steering_green, 1)
		lgpio.gpio_write(self.h, self.steering_red, 0)

	def set_steering_both(self):
		lgpio.gpio_write(self.h, self.steering_green, 0)
		lgpio.gpio_write(self.h, self.steering_red, 0)

	def set_steering_none(self):
		lgpio.gpio_write(self.h, self.steering_green, 1)
		lgpio.gpio_write(self.h, self.steering_red, 1)



### MAGNET LEDS ### 

	# def set_magnet_on(self):
	# 	lgpio.gpio_write(self.h, self.magnet_green, 0)
	# 	lgpio.gpio_write(self.h, self.magnet_red, 1)
	
	# def set_magnet_off(self):
	# 	lgpio.gpio_write(self.h, self.magnet_green, 1)
	# 	lgpio.gpio_write(self.h, self.magnet_red, 0)


	def enable_light(self):
		self.light_state = "ON"
		lgpio.gpio_write(self.h, self.light, 1)
	
	def disable_light(self):
		self.light_state = "OFF"
		lgpio.gpio_write(self.h, self.light, 0)

	def get_light_status(self):
		return self.light_state