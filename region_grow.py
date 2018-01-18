import time
import cv2
# from image_process import ImageProcess, ROI_Y_MIN, ROI_Y_MAX
import numpy as np

# 9*9 grid
GROW_DIRECTION = [
    (0, 1),
    (1, 0),
    (0, -1),
    (-1, 0),
]

POSITIVE_PIXEL = 200
NEGATIVE_PIXEL = 50
NOT_SEARCHED_PIXEL = 0

FINISHED = 0

K = 3

ROI_Y_MAX = 1200
ROI_Y_MIN = 300


# output: mask 0:not searched; 1:negative; 2:positive
class RegionGrow(object):
    def __init__(self, src):
        self.src_height = src.shape[0]
        self.src_width = src.shape[1]
        self.img = cv2.resize(src, (self.src_width/K, self.src_height/K))
        self.height = self.img.shape[0]
        self.width = self.img.shape[1]
        self.img_cpy = self.img
        self.seed_buffer = {(0, 0)}
        self.mask = np.zeros((self.height, self.width, 1), dtype=np.uint8)

        self.count = 0
        self.last_count = 0

    @staticmethod
    def _are_similar_pixels(p1, p2):
        for channel1, channel2 in zip(p1, p2):
            if abs(int(channel1) - int(channel2)) > 2:
                return False
        return True

    def count_one_more(self):
        self.count += 1
        percent = self.count * 100 / self.width / (ROI_Y_MAX - 0)
        if percent % 20 == 0 and percent != self.last_count:
            self.last_count = percent
            print percent

    def run(self):
        while len(self.seed_buffer) > 0:
            seed_x, seed_y = self.seed_buffer.pop()
            for direction in GROW_DIRECTION:
                candidate_x = seed_x + direction[0]
                candidate_y = seed_y + direction[1]

                if 0 <= candidate_x < self.width and 0 / K <= candidate_y < ROI_Y_MAX / K\
                        and self.mask[candidate_y][candidate_x][0] == NOT_SEARCHED_PIXEL:
                    # self.count_one_more()
                    seed = self.img[seed_y][seed_x]
                    candidate = self.img[candidate_y][candidate_x]
                    for channel1, channel2 in zip(seed, candidate):
                        if abs(int(channel1) - int(channel2)) > 2:
                            self.mask[candidate_y][candidate_x][0] = NEGATIVE_PIXEL
                            break
                    else:
                        self.mask[candidate_y][candidate_x][0] = POSITIVE_PIXEL
                        self.seed_buffer.add((candidate_x, candidate_y))

        return cv2.resize(self.mask, (self.src_width, self.src_height))


if __name__ == '__main__':
    img = cv2.imread('czq_screenshot.png')
    region_grow = RegionGrow(img)

    start_time = time.time()
    print 'start'

    mask = region_grow.run()
    # ImageProcess.show_in_normal_size('mask', mask, 0)

    delta_time = time.time() - start_time
    print delta_time

    cv2.waitKey()
