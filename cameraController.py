import cv2
from threading import Thread
import time
import common.settings as settings
import queue
from detect.motion import MotionDetect
import tornado.ioloop
from detect.scaleDetector import ScaleDetector
from common.shelter import Shelter


class VideoStream:
    def __init__(self,src,callback):
        self.src = src
        self.stream = cv2.VideoCapture(settings.usb_cameras[src])

        if settings.camera_version == 2:
            self.stream.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(*'MJPG'))

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH,settings.camera_width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT,settings.camera_height)
        self.call_back = callback
        self.isSending = False

        self.updateScheduler = tornado.ioloop.PeriodicCallback(self.update,5)
        self.updateScheduler.start()

        # self.cnt = 0
        self.motionChecker = MotionDetect()
        self.shelter = Shelter()

    def update(self):
        if self.isSending:
            # self.cnt+=1
            ret,frame = self.stream.read()
            if ret:
                # self.cnt+=1
                # if self.cnt == 99:
                #     self.cnt = 0

                centerX = int(settings.detect_baseLine[self.src])
                image = cv2.cvtColor(frame[:, centerX - 10: centerX + 10], cv2.COLOR_BGR2GRAY)
                # self.shelter.shadow(image)
                motionType = self.motionChecker.checkInput(frame[:,centerX-10:centerX+10],time.time())
                # if motionType[0] != 'None':
                #     print(motionType)

                # if self.cnt %3 == 0 or motionType != "None":
                self.call_back(self.src,frame,motionType)

    def setSending(self,state):
        self.isSending = state
        if not state:
            self.motionChecker.reset()
            self.shelter.reset()


class CameraController:
    def __init__(self,input_queue):
        self.cameras = {}
        self.frames_queues = input_queue
        self.videoWriter={}
        # self.cnt = 0
        # self.lastTime = time.time()
        for i in range(settings.camera_number):
            self.cameras[i] = VideoStream(i,self.sendFrame)


        if settings.has_scale:
            self.scaleDetector = ScaleDetector()



    def getScaleDetector(self):
        return self.scaleDetector

    def startCameras(self,cameras):
        self.curCameras = cameras
        for src in cameras:
            self.cameras[src].setSending(True)
            if settings.logger.checkSaveVideo():
                self.videoWriter[src] = cv2.VideoWriter(settings.logger.getSaveVideoPath()+str(src)+".avi",
                    cv2.VideoWriter_fourcc(*'XVID'),25, (settings.camera_width,settings.camera_height))


    def stopCameras(self):
        for src in self.curCameras:
            self.cameras[src].setSending(False)
            if settings.logger.checkSaveVideo():
                self.videoWriter[src].release()


    def sendFrame(self,src,frame,motionType):
        if settings.has_scale:
            self.scaleDetector.check(motionType)

        try:
            # self.cnt+=1
            # cur=time.time()
            # if cur - self.lastTime>1.0:
            #     print("send ",self.cnt," frame cur second")
            #     self.cnt=0
            #     self.lastTime = cur

            # if frame.shape[0] != 480 or frame.shape[1] != 640 or frame.shape[2] != 3:
                # return

            if settings.logger.checkSaveVideo():
                self.videoWriter[src].write(frame)


            if settings.is_offline and src==0:
                cv2.imshow("frame",frame)
                cv2.waitKey(1)


            if src > 1:
                frame = frame[:, :settings.detect_baseLine[src]+10]
            else:
                frame = frame[:, settings.detect_baseLine[src]-10:]

            self.frames_queues.put((frame,src,time.time(),motionType))

        except queue.Full:
            settings.logger.info('[FULL] input_q')
            pass