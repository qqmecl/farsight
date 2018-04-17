import common.settings as settings

class ScaleDetector:
	def __init__(self,io,cart,index):
		self.IO = io
		self.cart = cart
		self.index = index
		self.reset()

	def reset(self):
		self.curOut0 = 0

		self.handOutVal = 0
		self.handInVal = 0

		self.curIn0 = 0
		self.curIn1 = 0

		self.lastDetectTime = 0
		self.detectState = "NORMAL"
		self.detectCache = None

	def check(self,motions):
		motion,isCover = motions[0],motions[1]
		# print(motion,isCover)
		if motion == "PUSH":
			self.curOut0 = self.IO.get_stable_scale()

			# if self.index == 0:
				# print("this push scale is: ",self.curOut0)

		elif motion == "PULL":
			self.lastPullVal = self.IO.get_stable_scale()
		else:
			if not isCover:
				self.handOutVal = self.IO.get_stable_scale()

				# if self.index == 0:
				# 	print("this handout val is: ",self.handOutVal,self.curOut0)
				
				if self.detectState == "PULL_CHECKING":
					# print("pull_checking state")

					delta = self.handOutVal-self.curOut0
					if delta < -50:
						# settings.logger.warning('{0} camera shot Take out {1} with num {2}'.format(checkIndex,settings.items[id]["name"], now_num))
						_id = self.detectCache[0]["id"]
						
						for i in range(self.detectCache[0]["fetch_num"]):
							self.cart.add_item(_id,self.lastDetectTime)

						self.detectState = "NORMAL"
					else:
						if self.index == 0:
							print("scale chane val not enough, so return check!!!",delta)
			else:
				self.handInVal = self.IO.get_stable_scale()

				if self.detectState == "PUSH_CHECKING":
					if self.handInVal - self.handOutVal > 50:
						print("push_checking in back success!!")
						_id = self.detectCache[0]["id"]
						for i in range(self.detectCache[0]["fetch_num"]):
							self.cart.remove_item(_id,self.lastDetectTime)

						self.detectState = "NORMAL"
						self.curOut0 = self.handInVal

	#two judge will not interfere with each other
	def detect_check(self,detectResults):
		detect = detectResults.getDetect()

		if len(detect) > 0:
			direction = detect[0]["direction"]

			self.lastDetectTime = detectResults.getMotionTime("PUSH" if direction is "IN" else "PULL")

			print(detect)
			print("action time is: ",self.lastDetectTime)

			id = detect[0]["id"]
			if settings.items[id]['name'] == "empty_hand":
				print("check empty hand take out")
				detectResults.resetDetect()
				return

			if direction == "OUT":
				self.detectState = "PULL_CHECKING"
			else:
				self.detectState = "PUSH_CHECKING"
			
			self.detectCache = detect

			detectResults.resetDetect()
			detectResults.setActionTime()


