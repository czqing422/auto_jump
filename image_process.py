import cv2
import numpy as np
from math import tan, pi, sqrt

DEBUG = False
KERNEL_SIZE = 30
SCREENSHOT_NAME = 'czq_screenshot.png'
SHADOW_COLOR = {
    'lower': [0, 120, 175],
    'upper': [185, 175, 180],
}
BACKGROUND_COLOR = {
    'lower': [0, 200, 254],
    'upper': [185, 255, 255],
}
PLAYER_COLOR = {
    'lower': [65, 45, 45],
    'upper': [100, 75, 75],
}
ROI_Y_MAX = 1200
ROI_Y_MIN = 300
PLAYER_RECT = [0, 0, 73, 208]


class ImageProcess(object):
    def __init__(self, image_name=SCREENSHOT_NAME):
        self.img = cv2.imread(image_name)
        self.height = self.img.shape[0]
        self.width = self.img.shape[1]
        self.img_cpy = self.img

    def refresh_img_cpy(self):
        self.img_cpy = self.img.copy()

    @staticmethod
    def finish():
        cv2.destroyAllWindows()

    @staticmethod
    def show_in_normal_size(window_name, image, wait_time, width=400, height=600):
        origin_height = image.shape[0]
        origin_width = image.shape[1]
        cal_height = width*origin_height/origin_width
        if cal_height < height:
            size = (width, cal_height)
        else:
            size = (height*origin_width/origin_height, height)

        image_in_normal_size = cv2.resize(image, size)
        cv2.imshow(window_name, image_in_normal_size)
        if wait_time > 0:
            cv2.waitKey(wait_time)
        elif wait_time < 0:
            cv2.waitKey()

    @staticmethod
    def get_kernel(size, kernel_type='rect'):
        if kernel_type == 'cross':
            # cross kernel
            kernel = np.zeros((size, size), np.uint8)
            for x in range(size):
                if size % 2 == 0:
                    kernel[x, size/2-1] = 1
                    kernel[size/2-1, x] = 1
                kernel[x, size/2] = 1
                kernel[size/2, x] = 1
            return kernel
        elif kernel_type == 'rect':
            return np.ones((size, size), np.uint8)

    def get_mask(self, color, reverse=False):
        # get mask of ROI
        lower = np.array(color['lower'], dtype='uint8')
        upper = np.array(color['upper'], dtype='uint8')
        mask = cv2.inRange(self.img, lower, upper)
        if reverse:
            mask = cv2.bitwise_not(mask)
        return mask

    def get_triangle_vertex(self, player_x, player_y, angle=30):
        angle = angle * pi / 180
        left_y = player_y + player_x * tan(angle)
        right_y = player_y + (self.width - player_x) * tan(angle)
        return np.array([[player_x, player_y], [0, left_y], [0, self.height], [self.width, self.height],
                         [self.width, right_y]], np.int32)

    def get_rect_vertex(self, y_lower, y_upper):
        return np.array([[0, y_lower], [self.width, y_lower], [self.width, y_upper], [0, y_upper]], np.int32)

    @staticmethod
    def get_player_position_by_rect(x, y, w, h, target):
        if target == 'feet':
            player_x = x + w/2
            player_y = y + h*9/10
        elif target == 'head':
            player_x = x + w/2
            player_y = y
        else:
            print 'invaild target'
            # fixme
            assert 0
        return player_x, player_y

    def get_target_position(self, player_x, player_y):
        # get background mask
        background_mask = self.get_mask(BACKGROUND_COLOR, True)
        shadow_mask = self.get_mask(SHADOW_COLOR, True)
        mask = cv2.bitwise_and(shadow_mask, background_mask)

        # get triangle roi
        pts = self.get_triangle_vertex(player_x, player_y)
        cv2.fillPoly(mask, [pts], 0)
        # cv2.polylines(self.img_cpy, [pts], True, (55, 255, 155), 10)

        # get rect roi
        pts = self.get_rect_vertex(0, ROI_Y_MIN)
        cv2.fillPoly(mask, [pts], 0)
        pts = self.get_rect_vertex(ROI_Y_MAX, self.height)
        cv2.fillPoly(mask, [pts], 0)
        # roi_image = self.img[ROI_Y_MIN:ROI_Y_MAX, :]
        # mask = mask[ROI_Y_MIN:ROI_Y_MAX, :]

        # get contour of the target
        contours = None
        kernel_size = KERNEL_SIZE
        while (contours is None) or (len(contours) != 1):
            # until only one contour is founded
            kernel = self.get_kernel(kernel_size)
            new_mask = cv2.erode(mask, kernel)
            new_mask = cv2.dilate(new_mask, kernel)
            contours, hierarchy = cv2.findContours(new_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            kernel_size += 4
            # fixme
            # assert kernel_size < 60
            if kernel_size > 60:
                break

        # get enclosing circle
        center, radius = cv2.minEnclosingCircle(contours[0])
        center = (int(center[0]), int(center[1]))
        target = (int(center[0]), int(center[1] - radius / 2))

        # show images
        self.refresh_img_cpy()
        if DEBUG:
            img_filtered = cv2.bitwise_and(self.img_cpy, self.img_cpy, mask=new_mask)
            cv2.drawContours(img_filtered, contours, -1, (0, 0, 255), 3)
            cv2.circle(img_filtered, target, 8, (255, 55, 15), 10)
            cv2.circle(img_filtered, center, 8, (55, 255, 155), 10)
            cv2.circle(img_filtered, center, int(radius), (55, 255, 155), 10)
            self.show_in_normal_size('Target', np.hstack([self.img_cpy, img_filtered]), 50, width=800)
        else:
            cv2.drawContours(self.img_cpy, contours, -1, (0, 0, 255), 3)
            cv2.circle(self.img_cpy, center, 8, (55, 255, 155), 10)
            self.show_in_normal_size('Target', self.img_cpy, 50, width=800)

        return target

    @staticmethod
    def judge_rect(target_rect, standard_rect):
        for target_element, standard_element in zip(target_rect[2:], standard_rect[2:]):
            if abs(target_element - standard_element) > 5:
                return False
        else:
            return True

    def get_player_position(self):
        # get mask of the player
        mask = self.get_mask(PLAYER_COLOR)

        # get contours of the player
        kernel = self.get_kernel(KERNEL_SIZE)
        new_mask = cv2.dilate(mask, kernel)
        new_mask = cv2.erode(new_mask, kernel)
        contours, hierarchy = cv2.findContours(new_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # get player rect
        player_rect = None
        for contour in contours:
            candidate_rect = cv2.boundingRect(contour)
            if self.judge_rect(candidate_rect, PLAYER_RECT):
                player_rect = candidate_rect
                break

        # show images
        self.refresh_img_cpy()
        x, y, w, h = player_rect
        p_x, p_y = self.get_player_position_by_rect(target='feet', *player_rect)
        if DEBUG:
            img_filtered = cv2.bitwise_and(self.img_cpy, self.img_cpy, mask=new_mask)
            cv2.drawContours(img_filtered, contours, -1, (0, 0, 255), 3)
            cv2.rectangle(self.img_cpy, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(self.img_cpy, (p_x, p_y), 8, (55, 255, 155), 10)
            self.show_in_normal_size('Player', np.hstack([self.img_cpy, img_filtered]), 50, width=800)
        else:
            cv2.drawContours(self.img_cpy, contours, -1, (0, 0, 255), 3)
            cv2.circle(self.img_cpy, (p_x, p_y), 8, (55, 255, 155), 10)
            self.show_in_normal_size('Player', self.img_cpy, 50)

        return player_rect


if __name__ == '__main__':
    image_process = ImageProcess()

    rect = image_process.get_player_position()
    player_x, player_y = image_process.get_player_position_by_rect(target='feet', *rect)
    position = image_process.get_player_position_by_rect(target='head', *rect)

    target_x, target_y = image_process.get_target_position(*position)

    distance = sqrt((target_x-player_x)**2 + (target_y - player_y)**2)
