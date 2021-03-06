import time
import common.settings as settings
from common.queue import Queue

class DetectResult:
    def __init__(self):
        self.window = Queue(60)
        self.reset()
        self.resetDetect()

        self.latestFrameTime = None
        
    def getMotionTime(self,_type):
        return self.motionTime[_type]

    def checkData(self,index,data,frame_time):
        self.latestFrameTime = frame_time

        for motion,detects in data.items():
            # motion = motion[0]

            if motion == "PUSH" or motion == "PULL":
                #filter multi pull and push situation.
                if abs(frame_time-self.lastMotionTime[motion]) < 0.2:
                    motion = "None"

                print("evoke motion: ",index,motion,frame_time)
 
            # if len(detects) == 0:
            #     pass
                # settings.logger.info('{0} camera shot {1} by time {2}'.format(index,"None",frame_time))
            # else:
                # for val in detects:
                    # (_id,_time)=(val[1],val[2])#(confidence,itemId,cur_time) one
            _id = detects
                    # print(_id)
            settings.logger.info('{0} camera shot {1} by time {2}'.format(index,settings.items[_id]["name"],frame_time))
            
            self.window.enqueue(detects)
            
            if motion == "PUSH" or motion == "PULL":
                # print("{} camera detect_result got motion {} by time {}".format(index,motion,frame_time))
                self.motionTime[motion]=frame_time
                
            if motion == "PUSH":#Action start or Action done.
                if self.detectState == "PULL_CHECKING":
                    self.takeOutCheck(frame_time)
                    self.reset()
                else:
                    while(not self.window.isEmpty()):
                        self.loadData(self.window.dequeue(), frame_time)

                    detectId,num,_time,fetch_num = self.getCurrentDetection(True)

                    # print("put back after check: ",detectId,num,_time)
                    if detectId is not None:
                        self.detect.append({"direction":"IN","id":detectId,"num":num,"time":_time,"fetch_num":fetch_num})
                    else:#empty push
                        self.window.empty()#清空window

                    self.reset()

                self.lastMotion = motion
                #TODO
            elif motion == "PULL":
                # if self.lastMotion == "PUSH":
                self.detectState = "PULL_CHECKING"

                self.actionTime = self.motionTime["PULL"]

                limit=3
                while(self.window.size()>limit):
                    pop = self.window.dequeue()

                self.lastMotion = motion
            elif motion == "OUT":
                if self.detectState == "PULL_CHECKING":
                    self.takeOutCheck(frame_time)

    def takeOutCheck(self, frame_time, timeCheck=False):
        while(not self.window.isEmpty()):
            pop = self.window.dequeue()
            for val in pop:
                self.loadData(pop, frame_time)

        detectId,num,t_ime,fetch_num = self.getCurrentDetection(False)
        if detectId is not None:
            result = {"direction":"OUT","id":detectId,"num":num,"time":t_ime,"fetch_num":fetch_num}
            self.detect.append(result)
            self.reset()

    def getCurrentDetection(self,isLast):
        id,num,_time,fetch_num = self.getMaxNum()

        back_threshold,out_inTimethreshold,out_timeout_threshold = 1,2,0

        if id is not None:
            if isLast:
                if num > back_threshold: # 原来是3
                    return id,num,_time,fetch_num
                else:
                    self.reset()
            else:
                delta = self.latestFrameTime-self.actionTime

                if delta < 1:
                    if num > out_inTimethreshold:
                        settings.logger.warning("withIn {} time got {} catch".format(delta,num))
                        return id,num,_time,fetch_num
                else:
                    if num > out_timeout_threshold:
                        settings.logger.warning("outtime {} time got {} catch".format(delta,num))
                        return id,num,_time,fetch_num
                    else:
                        self.reset()

        return None,None,None,None

    def loadData(self,detects, time):
        # count={}
        # for val in detects:
        _id = detects
        # count[_id]=0

        # for val in detects:
            # _id=val
            # count[_id]+=1

            # if _id == '6921168509256001':
        new_num = self.processing[_id]["num"] + 1
        self.processing[_id]["time"] = ((self.processing[_id]["time"]*self.processing[_id]["num"])+time)/new_num
        self.processing[_id]["num"] = new_num
        self.processing[_id]["fetch_num"] = self.processing[_id]["fetch_num"]

            
    def reset(self):
        self.detectState = "NORMAL"
        self.actionTime = time.time()
        self.processing = {}
        self.lastMotion = None
        for k,item in settings.items.items():
            self.processing[k]=dict(num=0,time=0,fetch_num=0)

    def getMaxNum(self):
        maxId,count ="",0
        for k,v in self.processing.items():
            if v["num"] > count:
                count=v["num"]
                maxId=k

        if count >0:
            return (maxId,count,self.processing[maxId]["time"],self.processing[maxId]["fetch_num"])
        else:
            return (None,None,None,None)

    def getDetect(self):
        return self.detect

    def resetDetect(self):
        self.detect=[]
        self.motionTime={"PULL":0,"PUSH":0}
        self.lastMotionTime={"PULL":0,"PUSH":0}