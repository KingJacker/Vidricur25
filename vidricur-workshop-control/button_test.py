import lgpio
import time
gpio_handler = lgpio.gpiochip_open(4)

pin = 1

try:
    lgpio.gpio_claim_output(gpio_handler, pin)
    while True:
        print(lgpio.gpio_read(gpio_handler, pin))
        time.sleep(0.2)
except Exception as e:
    print(f"error: {e}")
finally:
    lgpio.gpio_free(gpio_handler, pin)

lgpio.gpio_free(gpio_handler, pin)