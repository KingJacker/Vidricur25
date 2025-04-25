# dir(x) to get class attributes of x
from loguru import logger
from adafruit_motor import servo

PWM_CHANNELS = {
    "CH00": {"min_pulse": 500, "max_pulse": 2500, "actuation_range": 180}, # steering front
    "CH01": {"min_pulse": 500, "max_pulse": 2500, "actuation_range": 180}, # steering rear
    "CH02": {"min_pulse": 500, "max_pulse": 2500, "actuation_range": 360}, # float left
    "CH03": {"min_pulse": 500, "max_pulse": 2500, "actuation_range": 360}, # float right
    "CH04": {"min_pulse": None, "max_pulse": None, "actuation_range": None},
    "CH05": {"min_pulse": None, "max_pulse": None, "actuation_range": None},
    "CH06": {"min_pulse": None, "max_pulse": None, "actuation_range": None},
    "CH07": {"min_pulse": None, "max_pulse": None, "actuation_range": None},
    "CH08": {"min_pulse": None, "max_pulse": None, "actuation_range": None},
    "CH09": {"min_pulse": None, "max_pulse": None, "actuation_range": None},
    "CH10": {"min_pulse": None, "max_pulse": None, "actuation_range": None},
    "CH11": {"min_pulse": None, "max_pulse": None, "actuation_range": None},
    "CH12": {"min_pulse": None, "max_pulse": None, "actuation_range": None},
    "CH13": {"min_pulse": None, "max_pulse": None, "actuation_range": None},
    "CH14": {"min_pulse": None, "max_pulse": None, "actuation_range": None},
    "CH15": {"min_pulse": None, "max_pulse": None, "actuation_range": None}
}

# get servo info 
def get_channel(channel):
    return PWM_CHANNELS[f"CH{channel:02d}"]


# init servo


# set servo pos