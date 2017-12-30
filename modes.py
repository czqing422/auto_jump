import os

RETRY_X, RETRY_Y = 500, 1700
LINEAR_COEFFICIENT = float(600)/27  # (ms/mm)
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
    def _tap(time, x=RETRY_X, y=RETRY_Y):
        os.system('adb shell input swipe {x1} {y1} {x2} {y2} {time}'.format(x1=x, y1=y, x2=x, y2=y, time=time))

    def tap_by_distance(self, distance):
        # 600~2.7
        time = int(distance*LINEAR_COEFFICIENT)
        self._tap(time)

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
    def get_distance(self):
        pass

    def image_process(self, image_name=SCREENSHOT_NAME):
        pass
