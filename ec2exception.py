class EC2Exception(Exception):
	def __init__(self,msg):
		self.msg = msg
	def __str__(self):
		print self.msg	