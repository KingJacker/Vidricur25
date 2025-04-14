import asyncio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class Sensors():
    def __init__(self, i2c):
        self.ads = ADS.ADS1015(i2c)

        self.cell_1 = AnalogIn(self.ads, ADS.P0)
        self.cell_2 = AnalogIn(self.ads, ADS.P1)
        self.current_voltage = AnalogIn(self.ads, ADS.P2)

    async def get_cell_1_value(self):
        return self.cell_1.value
    
    async def get_cell_2_value(self):
        return self.cell_2.value

    async def get_cell_1_voltage(self):
        return self.cell_1.voltage - 0.084
    
    async def get_cell_2_voltage(self):
        return self.cell_2.voltage -0.04
    

    async def get_current(self):
        # print(f"Raw: {self.current_voltage.value} \n{(self.current_voltage.value - 65536/2)} \n{(self.current_voltage.value - 65536/2) * 5 / 65536}") # 16 bit ADC = 65535 
        return self.current_voltage.voltage -2.5 / 0.04 + 60.448
        # return (self.current_voltage.value - 510) * 5 / 1024 / 0.04 
        # return (self.current_voltage.voltage - 2.5) / 0.04 # may need calibration