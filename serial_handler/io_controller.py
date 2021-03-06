import common.settings as settings
from serial_handler.door_lock import DoorLockHandler
# from serial_handler.speaker import Speaker
# from serial_handler.scale import WeightScale
if settings.android_screen:
    from serial_handler.screen import Screen
else:
    from serial_handler.screen_double import Screen

import common.settings as settings
from common.queue import Queue
import tornado.ioloop
import time
import numpy as np

class IO_Controller:#统一管理所有IO设备，增加代码清晰度
    def __init__(self):
        self.blocking = False

        #连接各个串口
        if not settings.android_screen:
            from serial_handler.speaker import Speaker
            self.speaker = Speaker()

        if settings.has_scale:
            from serial_handler.scale import WeightScale
            self.scale = WeightScale()

        self.screen = Screen()
        #门和锁
        self.doorLock = DoorLockHandler()

        self.scale_vals = Queue(6)
        self.stable_scale_val = 0

        if settings.has_scale:
            scaleUpdate = tornado.ioloop.PeriodicCallback(self._check_weight_scale,100)
            scaleUpdate.start()

    def _check_weight_scale(self):
        self.scale_vals.enqueue(int(self.scale.read()*1000))

        vals = self.scale_vals.getAll()
        _min = min(vals)
        _max = max(vals)

        meanVal=np.sum(vals)

        meanVal -= _min
        meanVal -= _max

        _len = len(vals) - 2

        if _len > 0:
            self.stable_scale_val = int(meanVal/_len)


    def get_stable_scale(self):
        return self.stable_scale_val

    '''
    	speaker部分接口
    '''
    def say_welcome(self):
        self.speaker.say_welcome()

    def say_goodbye(self):
        self.speaker.say_goodbye()
    '''
    	speaker部分接口
    '''



    '''
    	screen部分接口
    '''
    def change_to_welcome_page(self):
        self.screen.change_to_page(Screen.WELCOME_PAGE)

    def change_to_inventory_page(self):
        self.screen.change_to_page(Screen.INVENTORY_PAGE)

    def change_to_processing_page(self):
        self.screen.change_to_page(Screen.PROCESSING_PAGE)

    def change_to_thank_page(self):
        
        self.screen.change_to_page(Screen.THANK_PAGE)
    
    def update_screen_item(self,isAdd,itemId):
    	self.screen.update_item(isAdd,itemId)
    '''
    	screen部分接口
    '''
    '''
        android screen interface
    '''
    def add_item(self, itemId):
        self.screen.Add_item(name = settings.items[itemId]['name'], price = settings.items[itemId]['price'], number = 1)

    def remove_item(self, itemId):
        self.screen.remove_item(name = settings.items[itemId]['name'], number = 1)





    '''
    	Door的接口
    '''
    def is_door_open(self, curside):

        if settings.lock_version == 2:
            return self.doorLock.is_door_open(curside)
        else:
            return self.doorLock.old_is_door_open(curside)


    def is_door_lock(self, debugTime = None, curSide = None):
        # return self.doorLock.is_door_lock()
        if settings.lock_version == 2:
            return self.doorLock.is_door_lock()
        else:
            if debugTime:
                return True if time.time() - debugTime > 7 else False
            else:
                return not self.is_door_open(curSide)


    # def both_door_closed(self, curside):
    #     return self.doorLock.both_door_closed() #peihuo

    def lock_up_door_close(self, curside):
        if settings.lock_version == 2:
            return self.doorLock.lock_up_door_close(curside)
        else:
            return True
            
    def lock_down_door_open(self, curside):
        return self.doorLock.lock_down_door_open(curside)

    def reset_lock(self, side):
        self.doorLock.reset_lock(curside)
    '''
    	Door的接口
    '''



    '''
    	Lock部分接口
    '''
    def unlock(self,side):
        self.doorLock.unlock(side)
    '''
    	Door与Lock部分接口
    '''
    

 