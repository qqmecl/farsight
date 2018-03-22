import os
import multiprocessing
import logging
import uuid

init_url = "https://www.hihigo.shop/api/v1/updateGoodsInfo"
items = {
    '6921168509256': dict(name='农夫山泉矿泉水', price=2.0, weight=575.0),
    '6956416200067': dict(name='美汁源果粒橙', price=5.0, weight=487.0),
    '6920202888883': dict(name='红牛', price=8.0, weight=298.0),
    '6902538006100': dict(name='脉动', price=6.5, weight=546.0),
    '6921581596048': dict(name='三得利乌龙茶', price=6.0, weight=528.0),
    '6920459989463': dict(name='冰糖雪梨', price=6.0, weight=549.0),
    '4891028705949': dict(name='维他柠檬茶', price=7.0, weight=552.0),
    '6901939621271': dict(name='雪碧听装', price=3.5, weight=343.0),
    '6901939621608': dict(name='可口可乐听装', price=3.5, weight=354.0),
    '6925303730574': dict(name='统一阿萨姆奶茶', price=6.5, weight=550.0),
    '6925303754952': dict(name='小茗同学黄色', price=6.5, weight=546.0),
    '6925303714857': dict(name='汤达人豚骨面', price=13.5, weight=184.0),
}


mock_door = False
mock_speaker = False
mock_scale = False
mock_screen = False
http_port = 5000
speaker_on = True
#speaker_on = False

# logger =logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s")
# logger = logging.getLogger(__name__)

logger = multiprocessing.get_logger()
logger.setLevel(logging.WARN)

def get_mac_address():
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:].upper()
    return ":".join([mac[e:e+2] for e in range(0,11,2)])

mac_welcome_page = {'D8:9E:F3:1D:E6:9E': 0x33,
                    'D8:9E:F3:1D:EE:7C': 0x0D,
                    'D8:9E:F3:1E:13:8A': 0x33}

WELCOME_PAGE = mac_welcome_page.get(get_mac_address(), 0x33)
#print(get_mac_address())
if WELCOME_PAGE == 'error':
    logger.info('mac address is wrong')

SAVE_VIDEO_OUTPUT = True
SAVE_DEBUG_OUTPUT = False
SAVE_DETECT_OUTPUT = False

usb_cameras=[]
if os.path.exists("local/config.ini"):
    from configparser import ConfigParser
    config_parser = ConfigParser()
    config_parser.read("local/config.ini")
    for i in range(4):
        content = config_parser.get("usb_cameras","index"+str(i))
        usb_cameras.append(content)
    content = config_parser.get("usb_cameras","index"+str(i))

    SAVE_VIDEO_OUTPUT = config_parser.getboolean("maintain_switch","save_video_output")
else:
    usb_cameras=[
    "/dev/v4l/by-path/pci-0000:00:14.0-usb-0:10:1.0-video-index0",
    "/dev/v4l/by-path/pci-0000:00:14.0-usb-0:9:1.0-video-index0",
    "/dev/v4l/by-path/pci-0000:00:14.0-usb-0:6:1.0-video-index0",#done
    "/dev/v4l/by-path/pci-0000:00:14.0-usb-0:8:1.0-video-index0"
    ]