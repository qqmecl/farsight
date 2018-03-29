import time
import multiprocessing
from common import settings

class Queue:
    def __init__(self,limit):
        self.items = []
        self.maxLimit = limit

    def isEmpty(self):
        return self.items == []

    def empty(self):
        self.items=[]

    def enqueue(self, item):
        if self.size() == self.maxLimit:
            self.dequeue()
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

    def print(self):
        for i in range(len(self.items)):
            print(self.items[i])

#Theoritically,the ac
#single pipeline check about detecting.
class DetectResult:
    def __init__(self):
        self.window = Queue(30)
        self.logger = multiprocessing.get_logger()
        self.reset()
        self.resetDetect()
        self.curMarkTime = time.time()

    def checkData(self,index,data):
        for motion,detects in data.items():
            count=0
            for val in detects:
            #(confidence,itemId,cur_time) one
                (_id,_time)=(val[1],val[2])
                settings.logger.info('check ,{0},{1},by time ,{2}'.format(index,settings.items[_id]["name"],_time))
                count+=1

            self.window.enqueue(detects)

            # if motion is not "None":
            #     print("current motion is: ",motion)
            if motion == "PUSH":#Action start or Action done.
                if self.detectState == "PULL_CHECKING":
                    # print("From push state detect pull checking last!!!!!")
                    self.takeOutCheck()
                    self.reset()
                else:
                    # id,num,_time = self.getMaxNum()
                    # print("put back check: ",id,num,_time)
                    while(not self.window.isEmpty()):
                        # pop = self.window.dequeue()
                        # print(pop)
                        self.loadData(self.window.dequeue())

                    # id,num,_time = self.getMaxNum()
                    # print("put back after check: ",id,num,_time)
                    detectId,num,t_ime = self.getCurrentDetection(True)
                    if detectId is not None:
                        self.detect.append({"direction":"IN","id":detectId,"num":num,"time":t_ime})
                    else:#empty push
                        self.window.empty()#清空window

                    self.reset()

                self.lastMotion = motion
                #TODO
            elif motion == "PULL":
                # print("Last motion is: ",self.lastMotion)
                if self.lastMotion == "PUSH":
                    self.detectState = "PULL_CHECKING"
                    self.actionTime = time.time()
                    # print("action time is: ",self.actionTime)

                    limit=3#limit 
                    while(not self.window.isEmpty() and limit >0):
                        pop = self.window.dequeue()
                        # cv.imwrite()
                        self.loadData(pop)
                        limit-=1
                    # print("pull checking start time : ",self.actionTime)

                self.lastMotion = motion
            elif motion == "None":
                # print("self.detectState is ",self.detectState)
                if self.detectState == "PULL_CHECKING":
                    #filter time less situation.

                    self.takeOutCheck(timeCheck=True)
                    #TODO
                    #Check action ending state.


    def takeOutCheck(self,timeCheck=False):
        while(not self.window.isEmpty()):
            pop = self.window.dequeue()
            isAdd = True
            for val in pop:
                _time=val[2]
                if timeCheck and self.curMarkTime > _time:
                    isAdd = False
                break
            if isAdd:
                self.loadData(pop)
            # else:
                # print("not load data")

        detectId,num,t_ime = self.getCurrentDetection(False)
        if detectId is not None:
            # print("TAKE OUT: ",settings.items[detectId])
            result = {"direction":"OUT","id":detectId,"num":num,"time":t_ime}
            # self.callback(self.closet,result)
            self.detect.append(result)
            self.reset()

    def getCurrentDetection(self,isLast):#these parameters would significantly improve the performance of detect rate!
        id,num,_time = self.getMaxNum()

        # if isLast:
        # if id is not None:
            # print(settings.items[id]["name"],num,_time)
        #     else:
        #         print(id,num,_time)
        
        # threshold1,threshold2,threshold3 = 3,4,3
        
        back_threshold,out_inTimethreshold,out_timeout_threshold = 0,1,2

        if id is not None:
            if isLast:#in item check
                if num > back_threshold: # 原来是3
                    return id,num,_time
                else:
                    self.reset()
            else:#out item check
                now_time = time.time()

                if now_time-self.actionTime < 1:#25*0.7=17
                    if num > out_inTimethreshold: # 原来是4
                        # print("less time check: ",num)
                        return id,num,_time
                else:
                    if num > out_timeout_threshold: # 原来是3 bigger than 0.5 second and
                        # print("more time check: ",num) 
                        return id,num,_time
                    else:
                        # print("out time out is: ",now_time)
                        self.reset()

        return None,None,None

#Dynamic adjusting phase.

    def loadData(self,detects):
        for val in detects:
            #(confidence,itemId,cur_time) one
            (_id,time)=(val[1],val[2])
            # print("check ",settings.items[_id]["name"],"by time ",time)
            new_num = self.processing[_id]["num"] + 1
            self.processing[_id]["time"] = ((self.processing[_id]["time"]*self.processing[_id]["num"])+time)/new_num
            self.processing[_id]["num"] = new_num
            
    def reset(self):
        self.detectState = "NORMAL"
        self.actionTime = time.time()
        self.processing = {}
        self.lastMotion = None
        for k,item in settings.items.items():
            self.processing[k]=dict(num=0,time=0)


    def setActionTime(self):
        self.curMarkTime = time.time()

    def getMaxNum(self):
        maxId,count ="",0
        for k,v in self.processing.items():
            if v["num"] > count:
                count=v["num"]
                maxId=k

        if count >0:
            return (maxId,count,self.processing[maxId]["time"])
        else:
            return (None,None,None)

    def getDetect(self):
        return self.detect

    def resetDetect(self):
        self.detect=[]



