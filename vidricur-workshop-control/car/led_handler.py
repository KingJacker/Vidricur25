import lgpio
import asyncio

LED_PINS = [5,6,22,27,23,24]


# the leds used are on when pulled low!
# 0 -> ON
# 1 -> OFF
class LEDS():
	def __init__(self):
		self.h = lgpio.gpiochip_open(4)

		# Connection Status LEDS
		self.status_red   = LED_PINS[3]
		self.status_green = LED_PINS[2]

		# Steering Mode Indicators
		self.steering_green = LED_PINS[0]
		self.steering_red   = LED_PINS[1]

		# TODO
		# Magnet State Indicator
		# self.magnet_green
		# self.magnet_red

		# initialize gpios
		lgpio.gpio_claim_output(self.h, self.status_red)
		lgpio.gpio_claim_output(self.h, self.status_green)

		# set initial values
		lgpio.gpio_write(self.h, self.status_green, 0)
		asyncio.run(asyncio.sleep(0.1))

		lgpio.gpio_write(self.h, self.status_green, 1)
		lgpio.gpio_write(self.h, self.status_red, 0)
		asyncio.run(asyncio.sleep(0.1))

		lgpio.gpio_write(self.h, self.status_red, 1)


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

