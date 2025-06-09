import lgpio
import time
gpio_handler = lgpio.gpiochip_open(4)

pin = 13

try:
    lgpio.gpio_claim_output(gpio_handler, pin, lgpio.SET_PULL_UP)
    while True:
        print(lgpio.gpio_read(gpio_handler, pin))
        time.sleep(0.2)
except Exception as e:
    print(f"error: {e}")
finally:
    lgpio.gpio_free(gpio_handler, pin)
    lgpio.gpiochip_close(gpio_handler)

lgpio.gpio_free(gpio_handler, pin)