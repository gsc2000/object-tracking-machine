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
    def __init__(self, config: tuple, lock:threading.Lock) -> None:
        super().__init__("GUI")
        self.show_img = np.zeros((config["CAMERA"]["RESIZE_X"], config["CAMERA"]["RESIZE_Y"], 3),
                                  dtype="uint8") # 初期画像
        cv2.putText(self.show_img, 'Please Wait', (10, int(config["CAMERA"]["RESIZE_Y"]/2)),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 5,
                    cv2.LINE_AA)

        self.running = True


    def run(self):
        logger.info("Graphic_Thread_Start")
        cv2.namedWindow("Show", cv2.WINDOW_NORMAL)
        while self.running:
            # print(self.show_img.shape)
            cv2.imshow("Show", self.show_img)

            key = cv2.waitKey(1)
            if key == ord("q"):
                self.running = False

            # time.sleep(0.1)

        logger.info("Close")
        cv2.destroyAllWindows()