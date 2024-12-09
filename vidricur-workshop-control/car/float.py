class Float():
	def __init__(self, servo_kit, servo_channel_left, servo_channel_right, angle_up, angle_down):
		self.servo_left = servo_kit.servo[servo_channel_left]
		self.servo_right = servo_kit.servo[servo_channel_right]

		self.angle_up = angle_up
		self.angle_down = angle_down

		self.position = None	

	def down(self):
		self.servo_left.angle = self.angle_down
		self.servo_right.angle = -1 * self.angle_down
		self.position = 'down'
	
	def up(self):
		self.servo_left.angle = self.angle_up
		self.servo_right.angle = -1 * self.angle_up
		self.position = 'up'

	def get_position(self):
		return self.position