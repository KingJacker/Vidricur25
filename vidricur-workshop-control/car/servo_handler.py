from loguru import logger
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685, PWMChannel
import board
import time

# def servo_move(pca, channel, min_duty, max_duty, range, delay, step, target_angle):
# 	this_servo = servo.Servo(pca.channels[channel], min_pulse=min_duty, max_pulse=max_duty, actuation_range=range)
	
# 	while round(this_servo.angle) != target_angle:
# 		print(round(this_servo.angle,1))
# 		if target_angle > this_servo.angle:
# 			this_servo.angle = this_servo.angle + step
# 			time.sleep(delay)
# 		elif target_angle < this_servo.angle:
# 			this_servo.angle = this_servo.angle - step
# 			time.sleep(delay)
# 		else:
# 			this_servo.angle = target_angle



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

	def move(self, angle):
		self.angle = angle
		self.target_us = self.map_range(self.angle, 0, self.range, self.min_duty, self.max_duty) # to micro seconds
		self.target_duty = int(self.target_us / 20000 * self.pca_resolution) # to actual pca duty



		while abs(self.target_duty - self.servo.duty_cycle) >= 15:
			current_pos = self.servo.duty_cycle
			

			if self.target_duty > current_pos:
				self.servo.duty_cycle = current_pos + self.step
				time.sleep(self.delay)

			elif self.target_duty < current_pos:
				self.servo.duty_cycle = current_pos - self.step
				time.sleep(self.delay)

			else:
				print("target == current")
				self.servo.duty_cycle = self.target_duty

			print(current_pos, self.target_duty)


	def map_range(self, value, input_min, input_max, output_min, output_max):
		return output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))

	def get_duty_cycle(self):
		return self.servo.duty_cycle

	# def duty_to_pwm(self, duty_cycle):
	# 	return



i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50

channel = 0
min_duty = 500
max_duty = 2500
range = 360

delay = 0.01
step = 20 # doesnt work if lower than 20 ( sometimes it does!? )

servo = SLOW_SERVO(pca, channel, min_duty, max_duty, range, delay, step)

# servo.move(float(input("Target Angle: ")))
servo.move(100)


#  500 ->   0 deg
# 2500 -> 360 deg