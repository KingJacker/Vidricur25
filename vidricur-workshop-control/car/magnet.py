import lgpio
from loguru import logger

class Magnet():
    def __init__(self, gpio_handler):
        self.h = gpio_handler
        self.magnet_pin = 12
        self.magnet_active = False

        lgpio.gpio_claim_output(self.h, self.magnet_pin)
        self.set_magnet_inactive()

    def set_magnet_active(self):
        lgpio.gpio_write(self.h, self.magnet_pin, 1)
        self.magnet_active = True
        logger.info("MAGNET ON")

    def set_magnet_inactive(self):
        lgpio.gpio_write(self.h, self.magnet_pin, 0)
        self.magnet_active = False
        logger.info("MAGNET OFF")

    def get_magnet_active(self):
        return self.magnet_active

