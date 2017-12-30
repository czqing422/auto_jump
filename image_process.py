from PIL import Image
SCREENSHOT_NAME = 'czq_screenshot.png'


def image_process(image_name=SCREENSHOT_NAME):
    distance = 0
    try:
        img = Image.open(image_name)
    except IOError:
        print 'failed to open image'
        distance = -1
    img.show()
    return distance


if __name__ == '__main__':
    image_process()
