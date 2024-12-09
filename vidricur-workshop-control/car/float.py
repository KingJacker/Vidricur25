class Float():
	def __init__(self, servo_kit, servo_channel_left, servo_channel_right):
		self.servo_left = servo_kit.servo[servo_channel_left]
		self.servo_right = servo_kit.servo[servo_channel_right]

		self.position = None

		### set positions
		self.angle_up = 0
		self.angle_down = 270

		### start postition
		self.up()

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