# to get test and set required servo angles
# source "/home/pi/project/vidricur-2024-team02-control/venv/bin/activate"

from adafruit_pca9685 import PCA9685, PWMChannel
from adafruit_motor import servo
import board

i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50


# ask for channel
channel = int(input("\nSelect Channel: "))
actuation_range = int(input("Set Range: "))
servo = servo.Servo(pca.channels[channel], min_pulse=500, max_pulse = 2500, actuation_range=actuation_range)

print()

while True:
	angle = int(input("Set Angle: "))
	servo.angle = angle


# while True:
# 	request = input("").split("=")
# 	if request[0] == "c" and request[1] <= 15 and request[1] >= 0: # Channel: c=0 (0-16)
# 		servo = servo.Servo(pca.channels[request[1]], min_pulse=500, max_pulse = 2500, actuation_range=180)
# 	else 

