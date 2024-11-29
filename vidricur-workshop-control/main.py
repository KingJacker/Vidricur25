import asyncio
import socketio
import json
# import gpiod
from rpi_hardware_pwm import HardwarePWM
import subprocess
from loguru import logger
from aiohttp import web
from queue import Queue
from adafruit_servokit import ServoKit


from car.car import Car

####### Servo setup #######
# On the Pi 5, use channels 0 and 1 to control GPIO_12 and GPIO_13, respectively; 
# For Rpi 5, use chip=2
# steering_pwm = HardwarePWM(pwm_channel=0, hz=100, chip=2)
esc_pwm = HardwarePWM(pwm_channel=1, hz=100, chip=2)
try:
    kit = ServoKit(channels=16)
except Exception as e:
    logger.critical(f'Servo Driver not found: {e}')
    kit = None
# kit.servo[0].angle=90

###########################

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

# Initialize car instance
car = Car(sio, kit, esc_pwm)

# If socketio connection is established the connect function is called
@sio.event
def connect(sid, environ):
    logger.info(f"Connected: {sid}")

@sio.event
async def message(sid, data):
    # logger.info(f"Received: \n{data}")
    await car.handleEvent(json.loads(data))

@sio.event
def disconnect(sid):
    print(sid)
    logger.warning(f'Disconnected: {sid}')

FRAME_RATE = 15

# Camera Stream Handler
async def stream_camera(request):
    # Command to stream using libcamera-vid over stdout
    cmd = [
        "libcamera-vid", "-t", "0", "--inline", "--codec", "mjpeg",
        "--framerate", f"{FRAME_RATE}", "-o", "-"
    ]
    # Start camera process
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE#, stderr=asyncio.subprocess.DEVNULL
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




if __name__ == '__main__':
    app.router.add_get('/camera', stream_camera) # Register camera stream route
    web.run_app(app, host="0.0.0.0", port=8080)