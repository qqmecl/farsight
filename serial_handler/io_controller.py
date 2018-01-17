
import settings

if settings.mock_door:
    from serial_handler.mock import DoorLockHandler
else:
    from serial_handler.door_lock import DoorLockHandler

if settings.mock_speaker:
    from serial_handler.mock import Speaker
else:
    from serial_handler.speaker import Speaker

if settings.mock_scale:
    from serial_handler.mock import WeightScale
else:
    from serial_handler.scale import WeightScale

if settings.mock_screen:
    from serial_handler.mock import Screen
else:
    from serial_handler.screen import Screen

import tornado.ioloop
class IO_Controller:#统一管理所有IO设备，增加代码清晰度
    def __init__(self, door_port,speaker_port,scale_port,screen_port ):
        self.blocking = False

        # 连接各个串口
        self.speaker = Speaker(port=speaker_port)
        self.scale = WeightScale(port=scale_port)
        self.screen = Screen(port=screen_port)

        #门和锁
        self.doorLock = DoorLockHandler(port=door_port)

        self.val_scale = self._check_weight_scale()
        # self.envoked = False



    def start(self):
        scaleUpdate = tornado.ioloop.PeriodicCallback(self._check_weight_scale,100)
        scaleUpdate.start()

    def _check_weight_scale(self):
        import time
        # print("before time is:",time.time())
        self.val_scale = self.scale.read()[0]
        # print("after time is:",time.time())

    

    def get_scale_val(self):
    	return self.val_scale

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

    def update_screen_item(self,isAdd,itemId):
    	self.screen.update_item(isAdd,itemId)
    '''
    	screen部分接口
    '''





    '''
    	Door的接口
    '''
    def is_door_open(self,side):
        return self.doorLock.is_door_open(side)

    def both_door_closed(self):
        return self.doorLock.both_door_closed()
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
    

 