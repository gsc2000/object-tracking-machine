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
        self.width = config["CAMERA"]["RESIZE_X"]
        self.hight = config["CAMERA"]["RESIZE_Y"]

        self.show_img = np.zeros((self.hight, self.width, 3),
                                  dtype="uint8") # 初期画像
        cv2.putText(self.show_img, 'Please Wait', (10, int(self.hight/2)),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 5,
                    cv2.LINE_AA)

        self.win_name = "Show"
        self.ini_win_size = config["CAMERA"]["INI_WIN_SIZE"]

        self.running = True


    def run(self):
        logger.info("Graphic_Thread_Start")
        cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)
        # cv2.resizeWindow(self.win_name, self.ini_win_size, int(self.ini_win_size*self.hight/self.width))
        cv2.setWindowProperty(self.win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        while self.running:
            # print(self.show_img.shape)
            cv2.imshow("Show", self.show_img)

            key = cv2.waitKey(1)
            if key == ord("q"):
                self.running = False

            # time.sleep(0.1)

        logger.info("Close")
        cv2.destroyAllWindows()