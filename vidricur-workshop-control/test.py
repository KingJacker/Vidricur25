from datalogger import NDJsonLogger
import datetime
import time


data = {
	"selected_steering_mode": 1,
	"cpu_temp": 2,
	"battery": {
		"cell_1": 3, 
		"cell_2": 4
	},
	"current": 5,
	"engine": 6,
	"steering": {
		"front": 7,
		"rear": 8
	},
	"float": {
		"left": 9,
		"right": 10
	},
	"arm": 123,
	"magnet-state": 11,
	"leds-state": 12,
	"max-deflection": 13,
	"max-speed": 14
}

# --- Example Usage ---
if __name__ == "__main__":
	# Example 1: Basic usage
	print("--- Example 1: Basic ---")
	logger1 = NDJsonLogger(batch_size=3, file_prefix="a_")
	for i in range(10):
		logger1.log_data(data)
		time.sleep(0.5) # Simulate time passing
	logger1.close()
	print("-" * 20)

	# # Example 2: Using as a context manager (recommended)
	# print("\n--- Example 2: Context Manager ---")
	# try:
	#     with NDJsonLogger(
	#         log_directory="logs/special_run", batch_size=2, file_prefix="test_run_"
	#     ) as logger2:
	#         logger2.log_data({"event": "start", "time": datetime.datetime.now().isoformat()})
	#         logger2.log_data({"sensor": "temp", "value": 25.5})
	#         logger2.log_data({"sensor": "pressure", "value": 1012}) # This will trigger a write
	#         logger2.log_data({"event": "stop", "time": datetime.datetime.now().isoformat()})
	#         # Remaining data in buffer will be written on __exit__
	#     print("Context manager example finished.")
	# except Exception as e:
	#     print(f"Error in context manager example: {e}")
	# print("-" * 20)

	# # Example 3: Data that cannot be serialized
	# print("\n--- Example 3: Unserializable Data ---")
	# with NDJsonLogger(batch_size=2, file_prefix="error_test_") as logger3:
	#     logger3.log_data({"value": 1})
	#     logger3.log_data({"value": datetime.datetime}) # This is a class, not an instance
	# print("Unserializable data example finished.")
	# print("-" * 20)
