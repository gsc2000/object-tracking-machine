# GUI表示関係

import os
import sys

import time

import cv2
import numpy as np

import threading

import libs.Util as Util
import libs.SubThread as SubThread

logger = Util.childLogger(__name__)

class cv2graphic(SubThread.SubThread):
    '''
    画面表示
    '''
    def __init__(self, img_size: tuple, lock:threading.Lock) -> None:
        super().__init__("GUI")
        self.show_img = np.zeros(img_size, dtype="uint8") # 初期画像

        self.running = True


    def run(self):
        logger.info("Graphic_Thread_Start")
        cv2.namedWindow("Show", cv2.WINDOW_NORMAL)
        while self.running:
            print(self.show_img)
            cv2.imshow("Show", self.show_img)

            key = cv2.waitKey(1000)
            if key == ord("q"):
                self.running = False

            # time.sleep(0.1)

        logger.info("Close")
        cv2.destroyAllWindows()