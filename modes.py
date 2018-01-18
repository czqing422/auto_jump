import os
import time
from math import sqrt
from image_process import ImageProcess

RETRY_X, RETRY_Y = 500, 1700
MS_MM_COEFFICIENT = float(600)/27  # (ms/mm)
MS_PIXEL_COEFFICIENT = float(778)/570  # (ms/mm)
SCREENSHOT_NAME = 'czq_screenshot.png'


class BaseMode(object):
    def __init__(self):
        pass

    @staticmethod
    def screenshot(name=SCREENSHOT_NAME):
        os.system('adb shell screencap -p /sdcard/{}'.format(name))
        os.system('adb pull /sdcard/{}'.format(name))
        os.system('adb shell rm /sdcard/{}'.format(name))
        return name

    @staticmethod
    def retry(x=RETRY_X, y=RETRY_Y):
        os.system('adb shell input tap {x} {y}'.format(x=x, y=y))

    @staticmethod
    def _tap(tap_time, x=RETRY_X, y=RETRY_Y):
        os.system('adb shell input swipe {x1} {y1} {x2} {y2} {time}'.format(x1=x, y1=y, x2=x, y2=y, time=tap_time))

    def tap_by_distance(self, distance):
        # 600~2.7
        tap_time = int(distance*MS_MM_COEFFICIENT)
        self._tap(tap_time)

    def get_distance(self):
        raise NotImplemented

    def run(self):
        while True:
            distance = self.get_distance()
            if distance > 0:
                self.tap_by_distance(distance)
            else:
                action = raw_input('invalid input, what to do?(retry/exit)')
                if action == 'retry':
                    self.retry()
                elif action == 'exit':
                    exit()


class ManualMode(BaseMode):
    def get_distance(self):
        return input('input distance(mm):')


class AutoMode(BaseMode):
    def tap_by_distance(self, distance):
        # 778ms~548
        tap_time = int(distance*MS_PIXEL_COEFFICIENT)
        self._tap(tap_time)

    def get_distance(self):
        time.sleep(1.5)
        self.screenshot()
        image_process = ImageProcess()

        rect = image_process.get_player_position()
        player_x, player_y = image_process.get_player_position_by_rect(target='feet', *rect)
        position = image_process.get_player_position_by_rect(target='head', *rect)

        target_x, target_y = image_process.get_target_position(rect)

        return sqrt((target_x-player_x)**2 + (target_y - player_y)**2)
