import json
from json import JSONDecodeError

import cv2
import numpy as np
import mss
import time
import datetime


class MinimapScanner:
    def __init__(self, map_images, monitor, gui_instance, window_size=10, tolerance=0.30):
        self.map_images = map_images
        self.monitor = self.load_position_from_file(monitor)
        self.window_size = window_size
        self.tolerance = tolerance
        self.gui_instance = gui_instance
        self.bounding_box = None
        self.cached_map_image = None
        self.cached_map_path = None

    def capture_minimap(self):
        with mss.mss() as sct:
            screenshot = sct.grab(self.monitor)
            img = np.array(screenshot)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return gray

    def find_best_match(self, query_img):
        best_map_path = None
        best_score = 0

        for map_image_path in self.map_images:
            score = self.compare_images(query_img, map_image_path)

            if score > best_score:
                best_score = score
                best_map_path = map_image_path

        if best_score > 20:
            self.cached_map_path = best_map_path
            self.cached_map_image = cv2.imread(best_map_path, cv2.IMREAD_GRAYSCALE)
            return best_map_path
        else:
            return None

    def compare_images(self, query_img, map_image_path):
        map_image = cv2.imread(map_image_path, cv2.IMREAD_GRAYSCALE)

        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(query_img, None)
        kp2, des2 = sift.detectAndCompute(map_image, None)

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        return len(good_matches)

    def update_rectangle(self, query_img):
        if self.bounding_box:
            x, y, w, h = self.bounding_box
            map_image = self.cached_map_image[y:y + h, x:x + w]
            offset_x, offset_y = x, y  # Remember the offset
        else:
            map_image = self.cached_map_image
            offset_x, offset_y = 0, 0

        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(query_img, None)
        kp2, des2 = sift.detectAndCompute(map_image, None)

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        good = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good.append(m)

        if len(good) > 4:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            h, w = query_img.shape
            pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M)

            x, y, w, h = cv2.boundingRect(dst)

            # Update bounding box
            padding = 15  # Adjust this value as needed
            self.bounding_box = (
            max(0, x + offset_x - padding), max(0, y + offset_y - padding), w + 2 * padding, h + 2 * padding)

            return x + offset_x, y + offset_y, w, h

        return None, None, None, None

    def start_continuous_scanning(self, best_map_path, update_callback):
        while self.gui_instance.scanning_active and not self.gui_instance.stop_event.is_set():
            query_img = self.capture_minimap()

            x, y, w, h = self.update_rectangle(query_img)
            if x is not None and y is not None and w is not None and h is not None:
                update_callback(x, y, w, h)

            time.sleep(float(self.gui_instance.update_interval))

    def load_position_from_file(self, monitor):
        try:
            with open('minimap_position.json', 'r') as file:
                try:
                    json_position = json.load(file)
                    return json_position
                except JSONDecodeError:
                    return monitor
        except FileNotFoundError:
            return monitor