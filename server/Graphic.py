# GUI表示関係

import os
import sys

import time

import cv2
import numpy as np

import threading

import MainProcessing
import libs.Util as Util
import libs.SubThread as SubThread

logger = Util.childLogger(__name__)

# cv2.setNumThreads(0)

class cv2graphic():
    '''
    画面表示
    '''
    def __init__(self, config: tuple) -> None:
        '''
        Initialize
        '''
        # GUI設定の格納
        self.win_name = "Show"
        self.width = config["CAMERA"]["RESIZE_X"]
        self.hight = config["CAMERA"]["RESIZE_Y"]
        self.ini_win_size = config["CAMERA"]["INI_WIN_SIZE"]
        self.running = True

        # GUI初期画像の作成
        self.show_img = np.zeros((self.hight, self.width, 3),
                                  dtype="uint8")
        cv2.putText(self.show_img, 'Please Wait', (10, int(self.hight/2)),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 5,
                    cv2.LINE_AA)

        # GUIウィンドウの表示
        cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)
        # cv2.resizeWindow(self.win_name, self.ini_win_size, int(self.ini_win_size*self.hight/self.width))
        cv2.setWindowProperty(self.win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow(self.win_name, self.show_img) # 初期画像の表示

        # サブスレッド作成・開始
        self.lock = threading.Lock() # 排他制御用
        self.thread = MainProcessing.MainProcessing(self, config, self.lock)
        self.thread.start()

        logger.info("Active_Thread:\t{}".format(SubThread.ActiveThread()))

    def run(self):
        logger.info("Graphic_Start")

        # メインループ
        # --------------------------------------------------
        while self.running:
            # print(self.show_img.shape)
            # logger.debug("Show_image")
            cv2.imshow(self.win_name, self.show_img)
            key = cv2.waitKey(100) # 0.1秒ごとに画面更新
            if key == ord("q"): # キーボードのQが押されたら終了
                self.thread.running = False # サブスレッドを停止させる
                self.running = False

                self.close()

        logger.info("Graphic_End")

    def close(self):
        cv2.destroyAllWindows()