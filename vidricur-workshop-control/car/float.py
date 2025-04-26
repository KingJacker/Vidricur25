import asyncio
# from adafruit_motor import servo
from loguru import logger
import car.config_handler as ch
import car.servo_handler as sh

CHANNEL_LEFT  = 2
CHANNEL_RIGHT = 3
MIN_DUTY =  500
MAX_DUTY = 2500
RANGE = 360

DELAY = 0.005
STEP = 20

class Float():
    def __init__(self, pca):
        self.pca = pca

        # Load Config
        try:
            config = ch.get_float_config() # left up, left down, right up, right down
            self.up_pos_left, self.down_pos_left, self.up_pos_right, self.down_pos_right = config
        except Exception as e:
            logger.error(f"Could not load Float Config: {e}")


        # Initialize Servos as SLOW_SERVOS
        self.servo_left  = sh.SLOW_SERVO(self.pca, CHANNEL_LEFT , MIN_DUTY, MAX_DUTY, RANGE, DELAY, STEP)
        self.servo_right = sh.SLOW_SERVO(self.pca, CHANNEL_RIGHT, MIN_DUTY, MAX_DUTY, RANGE, DELAY, STEP)

        # Initial Position
        self.state = None


    # value: -1, 0, +1 to move down, stop, move up
    async def move(self, dir):
        logger.info(f"Moving Float Servos: {dir}")
        await self.servo_left.move_dir(dir, 67, 320)
        await self.servo_right.move_dir(-1*dir, 10, 260)

    
    async def get_float_left(self):
        return int(self.servo_left.angle)
    
    async def get_float_right(self):
        return int(self.servo_right.angle)