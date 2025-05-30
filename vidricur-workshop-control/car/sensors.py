import asyncio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from loguru import logger

# a0 -> cell 1
# a1 -> cell 2
# a3 -> current

class Sensors():
	def __init__(self, i2c):
		self.i2c = i2c
		self.adc_resolution = 32768

		self.ads = ADS.ADS1015(self.i2c)

		self.adc1 = AnalogIn(self.ads, ADS.P0)
		self.adc2 = AnalogIn(self.ads, ADS.P1)
		self.adc3 = AnalogIn(self.ads, ADS.P2)
		self.adc4 = AnalogIn(self.ads, ADS.P3)

		# self.cell_1 = AnalogIn(self.ads, ADS.P0)
		# self.cell_2 = AnalogIn(self.ads, ADS.P1)
		# # self.cell_2 = AnalogIn(self.ads, ADS.P0, ADS.P1) # this is weird
		# self.current_voltage = AnalogIn(self.ads, ADS.P3)




	# for cell voltage a voltage divider was used:
	# R1 = 10k, R2 = 9.1k
	# -> Vin = Vout / 2.1
	async def get_adc1_voltage(self):
		return self.adc1.voltage * 2.1 / 2
	
	async def get_adc2_voltage(self):
		return self.adc2.voltage * 2.1

	async def get_adc3_voltage(self):
		return self.adc3.voltage # not used

	async def get_adc4_voltage(self):
		return (self.adc4.voltage - 2.5) / 0.04
		# return (self.adc4.value - (self.adc_resolution / 2)) * 5 / self.adc_resolution / 0.04 - 0.55 

	# async def get_cell_1_value(self):
	# 	return self.cell_1.value
	
	# async def get_cell_2_value(self):
	# 	return self.cell_2.value

	# async def get_cell_1_voltage(self):
	# 	return self.cell_1.voltage - 0.084
	
	# async def get_cell_2_voltage(self):
	# 	return self.cell_2.voltage -0.04
	

	# Error: +/- 0.1 A
	# async def get_current(self):
	# 	return (self.current_voltage.value - (self.adc_resolution / 2)) * 5 / self.adc_resolution / 0.04 - 0.55 
