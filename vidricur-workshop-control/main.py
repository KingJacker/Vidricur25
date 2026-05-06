"""
Main application file for the vehicle.

This application uses aiohttp and python-socketio to create a web server for
remote control.

GRACEFUL SHUTDOWN FOR SYSTEMD:
The `aiohttp.web.run_app` function automatically handles SIGINT (Ctrl+C) and
SIGTERM (from `systemd stop ...`). When it receives one of these signals, it
triggers the application's cleanup sequence.

All resource cleanup logic (stopping motors, releasing GPIOs, de-initializing
I2C devices) is placed in the `on_cleanup` function. This ensures that even
when the script is stopped as a service, all hardware is left in a safe and
clean state.
"""
import asyncio
import socketio
import json
from loguru import logger
from aiohttp import web
import subprocess
import lgpio
import datetime

from datalogger import NDJsonLogger

import board
from adafruit_pca9685 import PCA9685, PWMChannel

from car.car import Car

import car.config_handler as ch
from car.led_handler import LEDS

print(
	"""
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
"""
)

# --- Global Hardware and Logger Initialization ---
# These are defined globally so they can be accessed in the cleanup function.
dataLogger = NDJsonLogger()
gpio_handler = None
i2c = None
pca = None
leds = None
car = None

try:
	gpio_handler = lgpio.gpiochip_open(4)
	leds = LEDS(gpio_handler)
	leds.set_disconnected()

	i2c = board.I2C()  # uses board.SCL and board.SDA
	pca = PCA9685(i2c)
	pca.frequency = 50

	# --- Socket.IO and Web App Setup ---
	sio = socketio.AsyncServer(
		logger=False, engineio_logger=False, ping_interval=0.1, ping_timeout=0.5
	)
	app = web.Application()
	sio.attach(app)

	# Initialize car instance after all hardware is ready
	car = Car(sio, pca, i2c, leds, gpio_handler)

except Exception as e:
	logger.critical(f"CRITICAL ERROR during hardware initialization: {e}")
	logger.critical(
		"Application cannot start. Please check hardware connections."
	)
	# Clean up any partially initialized resources before exiting
	if pca:
		pca.deinit()
	if i2c:
		i2c.deinit()
	if gpio_handler:
		lgpio.gpiochip_close(gpio_handler)
	raise  # Stop the script

# Tasks
stream_task = None

# --- Socket.IO Event Handlers ---
@sio.event
def connect(sid, environ):
	global stream_task
	logger.success(f"Connected: {sid}")
	stream_task = asyncio.create_task(stream_data())
	leds.set_connected()


@sio.event
async def command(sid, command):
	await car.command_handler(json.loads(command))
	await leds.set_receiving()


@sio.event
def disconnect(sid):
	global stream_task
	if stream_task:
		stream_task.cancel()
	logger.warning(f"Disconnected: {sid}")
	logger.info("Client disconnected. Stopping motors for safety.")
	car.engine.stop()
	car.arm.stop()
	car.querstrahler.stop()
	leds.set_disconnected()


@sio.event
async def get_config(sid, id):
	logger.debug(f"Received config request: {id}")
	config_data = ch.read_config()
	config_data["request_id"] = id
	await sio.emit("config_response", config_data)


@sio.event
async def set_config(sid, new_config):
	logger.debug(f"Received new config: {new_config}")
	config_data = ch.write_config(new_config)


@sio.event
async def set_control(sid, new_control):
	logger.debug(f"Received new control settings: {new_control}")
	if new_control["steering-mode"] is not None:
		car.wheel.set_steering_mode(new_control["steering-mode"])
	car.wheel.set_max_deflection(new_control["max-deflection"])
	car.engine.set_max_speed(new_control["max-speed"])

	if new_control["lights"]:
		car.leds.enable_light()
	else:
		car.leds.disable_light()

	car.magnet_balken.set_pos(new_control["magnet-balken-pos"])


# --- Background Tasks ---
async def stream_data():
	"""Stream car data back to the web client."""
	logger.info("Starting data stream task.")
	while True:
		try:
			data = {
				"timestamp": datetime.datetime.now(
					datetime.timezone.utc
				).isoformat(),
				"selected-steering-mode": await car.wheel.get_steering_mode(),
				"cpu_temp": await get_temp(),
				"cell_1": await car.sensors.get_adc1_voltage(),
				"cell_2": await car.sensors.get_adc2_voltage(),
				"current": await car.sensors.get_adc4_voltage(),
				"engine": await car.engine.get_speed(),
				"steering-front": await car.wheel.get_angle_front(),
				"steering-rear": await car.wheel.get_angle_rear(),
				"float-left": await car.float.get_float_left(),
				"float-right": await car.float.get_float_right(),
				"arm": await car.arm.get_pos(),
				"magnet-state": car.magnet.get_magnet_active(),
				"leds-state": car.leds.get_light_status(),
				"max-deflection": await car.wheel.get_max_deflection(),
				"max-speed": await car.engine.get_max_speed(),
				"magnet-balken-pos": car.magnet_balken.get_pos(),
			}
			dataLogger.log_data(data)
			await sio.emit("data_stream", data)
			await asyncio.sleep(0.3)
		except asyncio.CancelledError:
			logger.info("Data stream task cancelled.")
			break
		except Exception as e:
			logger.error(f"Error in data stream: {e}")
			await asyncio.sleep(2) # Wait before retrying on error


async def get_temp():
	try:
		result = subprocess.run(
			["vcgencmd", "measure_temp"],
			capture_output=True,
			text=True,
			check=True,
		)
		return float(result.stdout.strip()[5:9])
	except Exception as e:
		logger.warning(f"Could not read CPU temperature: {e}")
		return -1


# --- Application Startup and Cleanup Hooks ---
async def on_startup(app):
	"""Tasks to run when the aiohttp application starts."""
	logger.info("Application starting up...")
	app["servo_task"] = asyncio.create_task(car.start_servo_movers())


async def on_cleanup(app):
	"""
	This function is CRITICAL for graceful shutdown.
	aiohttp calls this automatically when it receives SIGINT or SIGTERM.
	"""
	logger.warning("Shutdown signal received. Starting graceful cleanup...")

	# 1. Stop all moving parts to ensure safety
	logger.info("Stopping all motors and actuators...")
	if car:
		car.engine.stop()
		car.arm.stop()
		car.querstrahler.stop()

	# 2. Cancel all background tasks
	logger.info("Cancelling background tasks...")
	for task_name in ["servo_task"]:
		task = app.get(task_name)
		if task:
			task.cancel()
			try:
				await task
			except asyncio.CancelledError:
				logger.info(f"Task '{task_name}' cancelled successfully.")

	# 3. Release all hardware resources in reverse order of initialization
	logger.info("Releasing hardware resources...")
	try:
		if leds:
			leds.free_leds()
			logger.info("LEDs freed.")
		if car.arm:
			car.arm.free_pins()
			logger.info("Arm freed.")
		if pca:
			pca.deinit()
			logger.info("PCA9685 Servo Driver de-initialized.")
		if i2c:
			i2c.deinit()
			logger.info("I2C bus de-initialized.")
		if gpio_handler:
			lgpio.gpiochip_close(gpio_handler)
			logger.info("lgpio chip handle closed.")
	except Exception as e:
		logger.error(f"Error during hardware resource cleanup: {e}")

	logger.success("Cleanup complete. Application has shut down.")


app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)


FRAME_RATE = 15

# Camera Stream Handler
async def stream_camera(request):
    # Command to stream using libcamera-vid over stdout
    cmd = [
        "libcamera-vid", "-t", "0", "--inline", "--codec", "mjpeg",
        "--framerate", f"{FRAME_RATE}", "-o", "-"
    ]
    # Start camera process
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
    )

    # Stream frames in MJPEG format
    async def frame_generator():
        buffer = b""
        try:
            while True:
                chunk = await proc.stdout.read(4096)  # Increased chunk size
                if not chunk:
                    break
                buffer += chunk
                # Look for frame boundaries
                while b'\xff\xd9' in buffer:  # JPEG EOF marker
                    frame_end = buffer.index(b'\xff\xd9') + 2
                    frame = buffer[:frame_end]
                    buffer = buffer[frame_end:]
                    yield (b"--frame\r\n"
                           b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        except asyncio.CancelledError:
            pass
        finally:
            proc.kill()

    # Return the response with multipart MJPEG stream
    return web.Response(body=frame_generator(), content_type="multipart/x-mixed-replace; boundary=frame")

# Register camera stream route
app.router.add_get('/camera', stream_camera)


FRAME_RATE = 15

# Camera Stream Handler
async def stream_camera1(request):
    # Command to stream using libcamera-vid over stdout
    cmd = [
        "libcamera-vid", "-t", "0", "--inline", "--codec", "mjpeg",
        "--framerate", f"{FRAME_RATE}","--camera","1", "-o", "-"
    ]
    # Start camera process
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
    )

    # Stream frames in MJPEG format
    async def frame_generator():
        buffer = b""
        try:
            while True:
                chunk = await proc.stdout.read(4096)  # Increased chunk size
                if not chunk:
                    break
                buffer += chunk
                # Look for frame boundaries
                while b'\xff\xd9' in buffer:  # JPEG EOF marker
                    frame_end = buffer.index(b'\xff\xd9') + 2
                    frame = buffer[:frame_end]
                    buffer = buffer[frame_end:]
                    yield (b"--frame\r\n"
                           b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        except asyncio.CancelledError:
            pass
        finally:
            proc.kill()

    # Return the response with multipart MJPEG stream
    return web.Response(body=frame_generator(), content_type="multipart/x-mixed-replace; boundary=frame")

# Register camera stream route
app.router.add_get('/camera1', stream_camera1)


# --- Main Execution ---
if __name__ == "__main__":
	logger.info("Starting web server on host 0.0.0.0, port 8080")
	# web.run_app handles SIGINT/SIGTERM and triggers the on_cleanup sequence.
	web.run_app(app, host="0.0.0.0", port=8080)
