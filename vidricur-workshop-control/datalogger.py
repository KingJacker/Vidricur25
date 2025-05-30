import json
import os
import datetime
from pathlib import Path

class NDJsonLogger:
	def __init__(self, log_directory="logs", batch_size=20, file_prefix=""):

		self.log_directory = Path(log_directory)
		self.batch_size = max(1, batch_size)  # Ensure batch_size is at least 1
		self.file_prefix = file_prefix

		self._buffer = []
		self._file_handle = None
		self._log_file_path = None

		self._ensure_log_directory_exists()
		self._initialize_log_file()

	def _ensure_log_directory_exists(self):
		try:
			self.log_directory.mkdir(parents=True, exist_ok=True)
			print(f"Log directory: {self.log_directory.resolve()}")
		except OSError as e:
			print(f"Error creating log directory {self.log_directory}: {e}")


	def _generate_filename(self):
		start_time = datetime.datetime.now()
		date_str = start_time.date().isoformat()  # YYYY-MM-DD
		time_str = start_time.strftime("%H-%M-%S")
		filename = f"{self.file_prefix}{date_str}_{time_str}.ndjson"
		return self.log_directory / filename

	def _initialize_log_file(self):
		if self._file_handle:
			self.close()

		self._log_file_path = self._generate_filename()
		try:
			# Open in append mode, create if it doesn't exist
			self._file_handle = open(self._log_file_path, "a", encoding="utf-8")
			print(f"Logging to: {self._log_file_path}")
		except IOError as e:
			print(f"Error opening log file {self._log_file_path}: {e}")
			self._file_handle = None # Ensure it's None if open failed

	def log_data(self, data_dict):
		if not isinstance(data_dict, dict):
			print("Error: log_data expects a dictionary.")
			return

		if not self._file_handle:
			print("Error: Log file is not open. Cannot log data.")
			self._initialize_log_file()
			if not self._file_handle:
				return

		self._buffer.append(data_dict)
		if len(self._buffer) >= self.batch_size:
			self._write_buffer()

	def _write_buffer(self):
		if not self._file_handle:
			print("Error: Log file is not open. Cannot write buffer.")
			return

		if not self._buffer:
			return  # Nothing to write

		try:
			for entry in self._buffer:
				json_string = json.dumps(entry, separators=(",", ":")) # Compact
				self._file_handle.write(json_string + "\n")
			self._file_handle.flush()  # Ensure data is passed to OS buffer
			os.fsync(self._file_handle.fileno())  # Ask OS to write to disk
			self._buffer.clear()
		except IOError as e:
			print(f"Error writing to log file {self._log_file_path}: {e}")
		except TypeError as e:
			print(f"Error serializing data to JSON: {e}. Data: {self._buffer}")
			# Potentially clear buffer or problematic entries if needed

	def close(self):
		print("Closing logger...")
		if self._buffer: # Write any remaining entries
			self._write_buffer()
		if self._file_handle:
			try:
				self._file_handle.close()
				print(f"Closed log file: {self._log_file_path}")
			except IOError as e:
				print(f"Error closing log file {self._log_file_path}: {e}")
			finally:
				self._file_handle = None
		self._buffer.clear()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	def __del__(self):
		# This is a fallback, explicit close() is much better.
		if self._file_handle or self._buffer:
			# print("NDJsonLogger.__del__: Closing due to garbage collection.")
			self.close()
