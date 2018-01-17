
import settings
import time
import multiprocessing

class UpDownNotMatchError(Exception):
    pass


#根据识别结果结合重力传感器方向判断识别结果
class DetectResult:
    def __init__(self,action,doorSide):
    	self.reset(action,doorSide)

    def put(self,detect):#在放置每一帧的时候顺便进行判断
        XThreshold = [340,340,230,230]
        index = detect["index"]

        # print("why not here")

        if index < 2 and detect["XAxis"] < XThreshold[index]:
            # print("returnreutenrlej")

            return

        if index >= 2 and detect["XAxis"] > XThreshold[index]:
            # print("returnreutenrlej")

            return

        (_id,time,XAxis)=(detect["itemId"],detect["time"],detect["XAxis"])



        # if index < 2:#left side
        #     if XAxis - self.upDetect[_id]["X"] < 0:
        #             self.upDetect[_id]["In"] += 1
        #         else:
        #             self.upDetect[_id]["Out"] += 1

        # print("index ,XAxis is :",index,XAxis)

        if index % 2 == 0:#up position
            self.upDetect[_id]["num"] += 1
            
            if self.upDetect[_id]["time"] < time:
                self.upDetect[_id]["time"] = time#upate time

            if XAxis - self.upDetect[_id]["X"] < 0:
                if index == 0:
                    self.upDetect[_id]["In"] += 1
                else:
                    self.upDetect[_id]["Out"] += 1


            if XAxis - self.upDetect[_id]["X"] > 0:
                if index == 0:
                    self.upDetect[_id]["Out"] += 1
                else:
                    self.upDetect[_id]["In"] += 1

            self.upDetect[_id]["X"] = XAxis
        else:#down position
            self.downDetect[_id]["num"] += 1
            if self.downDetect[_id]["time"] < time:
                self.downDetect[_id]["time"] = time#upate time

            if self.downDetect[_id]["X"] - XAxis > 0:
                if index == 1:
                    self.downDetect[_id]["In"] += 1
                else:
                    self.downDetect[_id]["Out"] += 1


            if self.downDetect[_id]["X"] - XAxis < 0:
                if index == 1:
                    self.downDetect[_id]["Out"] += 1
                else:
                    self.downDetect[_id]["In"] += 1

            self.downDetect[_id]["X"] = XAxis

    def getDirection(self):
        return self.direction

    def setDirection(self,direction):
        self.direction = direction

    def debugTest(self):
        
        for k,val in self.upDetect.items():
            if val["num"] >0:
                print("                           ")
                print("Debug upDetect is : ",k,val["num"],val["time"],val["Out"],val["In"])
                print("                           ")


        for k,num in self.downDetect.items():
            if val["num"] >0:
                print("                           ")
                print("Debug downDetect is : ",k,val["num"],val["time"])
                print("                              ")

    def getLabel(self):
        self.logger.info("-----------------------------")
        for k,val in self.upDetect.items():
            if val["num"] >0:
                print("Final upDetect is : ",k,val["num"],val["time"],val["Out"],val["In"])


        for k,num in self.downDetect.items():
            if val["num"] >0:
                print("Final downDetect is : ",k,val["num"],val["time"],val["Out"],val["In"])
        
        self.logger.info("["+self.direction,settings.items[self.labelId]["name"]+"]")
        self.logger.info("-----------------------------")
        
        return self.labelId

    def reset(self,action,doorSide):
        self.logger = multiprocessing.get_logger()

        if action == 1:
            self.direction = "IN"
        else:
            self.direction = "OUT"
            
        self.judgeComplete = False

        self.doorSide = doorSide

        # self.initScaleVal = initScaleVal

        #结果集，即上侧判断出多少个不同的id及对应次数
        self.upDetect = {}
        self.downDetect = {}
        for k,item in settings.items.items():
            self.upDetect[k]=dict(num=0,time=0,Out=0,In=0,X=0)
            self.downDetect[k]=dict(num=0,time=0,Out=0,In=0,X=0)


        # print(self.upDetect)
        self.upLabel = ""
        self.downLabel = ""
        self.labelId = ""

    def getMax(self,isUp):
        val=self.upDetect if isUp else self.downDetect

        maxId,count ="",0
        for k,v in val.items():
            if v["num"] > count:
                count=v["num"]
                maxId=k

        if count >0:
            direction = "OUT" if val[maxId]["Out"] >= val[maxId]["In"] else "IN"
            result = (maxId,count,val[maxId]["time"],direction)
            return result
        else:
            return (None,None,None,None)

    def isComplete(self):
        upId,upNum,upTime,upDirection = self.getMax(True)
        downId,downNum,downTime,downDirection= self.getMax(False)


        timeThreshold = 0.2
        if downNum == None:
            if upNum == None:
                return False
            else:
                self.labelId = upId
                if time.time() - upTime >timeThreshold:
                    self.setDirection(upDirection)
                    return True
        else:
            if upNum == None:
                self.labelId = downId
                if time.time() - downTime > timeThreshold:
                    self.setDirection(downDirection)
                    return True
            else:
                if downNum > upNum:
                    self.labelId = downId
                    if time.time() - downTime > timeThreshold:
                        self.setDirection(downDirection)
                        return True
                else:
                    self.labelId = upId
                    if time.time() - upTime > timeThreshold:
                        self.setDirection(upDirection)
                        return True
    	# if self.upLabel is not "":
    	# 	if self.downLabel is "":#相信上面的检测结果
    	# 		self.labelId = self.upLabel
    	# 		return True
    	# 	else:
    	# 		if self.upLabel is self.downLabel:
    	# 			self.labelId = self.upLabel
    	# 			return True
    	# 		else:#
    	# 			raise UpDownNotMatchError("上下摄像头判断结果不一致!!")
    	# else:
	    # 	if self.downLabel is not "":
    	# 		self.labelId = self.downLabel
    	# 		return True

    	# return False


