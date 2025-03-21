import asyncio
import socketio
import json
from rpi_hardware_pwm import HardwarePWM
from loguru import logger
from aiohttp import web
import subprocess

import board
from adafruit_pca9685 import PCA9685

from car.car import Car

import car.config_handler as ch

####### Servo setup #######
# On the Pi 5, use channels 0 and 1 to control GPIO_12 and GPIO_13, respectively; 
# For Rpi 5, use chip=2
esc_pwm = HardwarePWM(pwm_channel=1, hz=100, chip=2)
try:
	i2c = board.I2C()  # uses board.SCL and board.SDA
	pca = PCA9685(i2c)
	pca.frequency = 50
except Exception as e:
	logger.critical(f'Servo Driver not found: {e}')

###########################

sio = socketio.AsyncServer(ping_interval=0.5, ping_timeout=1)
app = web.Application()
sio.attach(app)

# Initialize car instance
car = Car(sio, pca, esc_pwm)

# Tasks
stream_task = None

# If socketio connection is established the connect function is called
@sio.event
def connect(sid, environ):
	global stream_task
	logger.success(f"Connected: {sid}")
	stream_task = asyncio.create_task(stream_data())

@sio.event
async def command(sid, command):
	await car.command_handler(json.loads(command))

@sio.event
def disconnect(sid):
	global stream_task
	if stream_task:
		stream_task.cancel()
	logger.warning(f'Disconnected: {sid}')
	logger.critical('Shutting down Motor')
	car.engine.stop()


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

# DATA STREAM
async def stream_data():
	"""
	Stream back Car data to be displayed in the webclient
	- All Channel Positions [16]
	- Sensor Values [3]
	- Steering Mode [1]
	- cpu temps
	"""
	while True:
		data = {"cpu_temp": await get_temp()} # example data
		await sio.emit("data_stream", data)
		await asyncio.sleep(1)

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

# @sio.on("update_config")
# async def handle_get_config(sid, new_config):
#     config_data = ch.write_config(new_config)
#     print(f"Received config update {new_config}")

# @sio.on("get_pwm_channel")
# async def handle_get_config(sid, channel):
#     config_data = ch.write_config(data)
#     print(f"Received config update {data}")
#     print(f"Updated Config: {config_data}")


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




if __name__ == '__main__':
	# app.router.add_get('/camera', stream_camera) # Register camera stream route
	web.run_app(app, host="0.0.0.0", port=8080)