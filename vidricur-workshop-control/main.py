import asyncio
import socketio
import json
from loguru import logger
from aiohttp import web
import subprocess
import lgpio


import board
from adafruit_pca9685 import PCA9685, PWMChannel

from car.car import Car

import car.config_handler as ch
from car.led_handler import LEDS

print("""
.
.
.
.    ██╗   ██╗██╗██████╗ ██████╗ ██╗ ██████╗██╗   ██╗██████╗ 
.    ██║   ██║██║██╔══██╗██╔══██╗██║██╔════╝██║   ██║██╔══██╗
.    ██║   ██║██║██║  ██║██████╔╝██║██║     ██║   ██║██████╔╝
.    ╚██╗ ██╔╝██║██║  ██║██╔══██╗██║██║     ██║   ██║██╔══██╗
.     ╚████╔╝ ██║██████╔╝██║  ██║██║╚██████╗╚██████╔╝██║  ██║
.      ╚═══╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝
.
.
.    Starting Vehicle...
.
""")

######## LED Setup ########

gpio_handler = lgpio.gpiochip_open(4)

leds = LEDS(gpio_handler)
leds.set_disconnected()

###########################

####### Servo setup #######
try:
	i2c = board.I2C()  # uses board.SCL and board.SDA
	pca = PCA9685(i2c)
	pca.frequency = 50
except Exception as e:
	logger.critical(f'Servo Driver not found: {e}')
	raise

###########################

sio = socketio.AsyncServer(ping_interval=0.1, ping_timeout=0.3)
app = web.Application()
sio.attach(app)

# Initialize car instance
car = Car(sio, pca, i2c, leds, gpio_handler)

# servo_task = None
# try:
# 	servo_task = asyncio.create_task(car.start_servo_movers())
# except Exception as e:
# 	if servo_task:
# 		servo_task.cancel()
# 	logger.error(e)

# Tasks
stream_task = None
# servo_task = None

# If socketio connection is established the connect function is called
@sio.event
def connect(sid, environ):
	global stream_task
	# global servo_task
	logger.success(f"Connected: {sid}")
	stream_task = asyncio.create_task(stream_data())
	# servo_task = asyncio.create_task(car.start_servo_movers())
	leds.set_connected()


@sio.event
async def command(sid, command):
	await car.command_handler(json.loads(command))
	await leds.set_receiving()

@sio.event
def disconnect(sid):
	global stream_task
	# global servo_task
	if stream_task:
		stream_task.cancel()
	# if servo_task:
	# 	servo_task.cancel()
	logger.warning(f'Disconnected: {sid}')
	logger.critical('Shutting down Motor')
	car.engine.stop()
	leds.set_disconnected()
	car.querstrahler.stop()

@sio.event
async def get_config(sid, id):
	"""
	Get config and send it back, to be displayed in the webclient
	"""
	logger.debug(f"Received config request: {id}")
	config_data = ch.read_config()
	
	config_data["request_id"] = id
	await sio.emit("config_response", config_data)

@sio.event
async def set_config(sid, new_config):
	"""
	set updated config
	"""
	logger.debug(f"Received new config: {new_config}")
	config_data = ch.write_config(new_config)

@sio.event
async def set_control(sid, new_control):
	"""
	set updated control infos
	"""
	logger.debug(f"Received new config: {new_control}")
	if new_control["steering-mode"] != None:
		car.wheel.set_steering_mode(new_control["steering-mode"])
	car.wheel.set_max_deflection(new_control["max-deflection"])
	car.engine.set_max_speed(new_control["max-speed"])

# DATA STREAM
async def stream_data():
	"""
	Stream back Car data to be displayed in the webclient
	"""
	while True:
		data = {
			"selected-steering-mode": await car.wheel.get_steering_mode(),
			"cpu_temp": await get_temp(),
			"battery": {
				"cell_1": await car.sensors.get_cell_1_voltage(), 
				"cell_2": await car.sensors.get_cell_2_voltage()
			},
			"current": await car.sensors.get_current(),
			"engine": await car.engine.get_speed(),
			"steering": {
				"front": await car.wheel.get_angle_front(),
				"rear": await car.wheel.get_angle_rear()
			},
			"float": {
				"left": await car.float.get_float_left(),
				"right": await car.float.get_float_right()
			},
			"arm": 123,
			"magnet-state": car.magnet.get_magnet_active(),
			"leds-state": "na",
			"max-deflection": await car.wheel.get_max_deflection(),
			"max-speed": await car.engine.get_max_speed()
		}
		await sio.emit("data_stream", data)
		await asyncio.sleep(0.3)

async def get_temp():
	try:
		result = subprocess.run(
			["vcgencmd", "measure_temp"],
			capture_output=True,
			text=True,
			check=True
		)
		return float(result.stdout.strip()[5:9])
	except Exception as e:
		return e


FRAME_RATE = 15

# Camera Stream Handler
# async def stream_camera(request):
# 	# Command to stream using libcamera-vid over stdout
# 	cmd = [
# 		"libcamera-vid", "-t", "0", "--inline", "--codec", "mjpeg",
# 		"--framerate", f"{FRAME_RATE}", "-o", "-"
# 	]
# 	# Start camera process
# 	proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE#, stderr=asyncio.subprocess.DEVNULL
# 	)

# 	# Stream frames in MJPEG format
# 	async def frame_generator():
# 		buffer = b""
# 		try:
# 			while True:
# 				chunk = await proc.stdout.read(4096)  # Increased chunk size
# 				if not chunk:
# 					break
# 				buffer += chunk
# 				# Look for frame boundaries
# 				while b'\xff\xd9' in buffer:  # JPEG EOF marker
# 					frame_end = buffer.index(b'\xff\xd9') + 2
# 					frame = buffer[:frame_end]
# 					buffer = buffer[frame_end:]
# 					yield (b"--frame\r\n"
# 						   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
# 		except asyncio.CancelledError:
# 			pass
# 		finally:
# 			proc.kill()

# 	# Return the response with multipart MJPEG stream
# 	return web.Response(body=frame_generator(), content_type="multipart/x-mixed-replace; boundary=frame")

async def on_startup(app):
	app['servo_task'] = asyncio.create_task(car.start_servo_movers())

async def on_cleanup(app):
	servo_task = app.get('servo_task')
	if servo_task:
		servo_task.cancel()
		try:
			await servo_task
		except asyncio.CancelledError:
			pass

app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

if __name__ == '__main__':
	# app.router.add_get('/camera', stream_camera) # Register camera stream route
	web.run_app(app, host="0.0.0.0", port=8080)