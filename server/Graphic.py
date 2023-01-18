# GUI表示関係

import os
import sys

import time

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import numpy as np

import threading
import queue

import MainProcessing
import libs.Util as Util
import libs.SubThread as SubThread

logger = Util.childLogger(__name__)

class cv2graphic():
    '''
    画面表示
    '''
    def __init__(self, config: tuple) -> None:
        '''
        Initialize
        '''
        self.mode = 0 # 初期モード
        # 0:解錠モード
        # 1:設定モード
        self.q_img = queue.Queue() # サブスレッドから画像をもらうためのキュー

        # GUI設定の格納
        self.win_name = "Show"
        self.width = config["CAMERA"]["RESIZE_X"]
        self.height = config["CAMERA"]["RESIZE_Y"]
        self.center = (int(self.width/2), int(self.height/2))

        # GUI初期画像の作成
        self.show_img = np.zeros((self.height, self.width, 3),
                                  dtype="uint8")
        cv2.putText(self.show_img, 'Please Wait', (10, int(self.height/2)),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 5,
                    cv2.LINE_AA)

        # GUIウィンドウの表示
        cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)
        # cv2.setWindowProperty(self.win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN) #フルスクリーン表示
        cv2.imshow(self.win_name, self.show_img) # 初期画像の表示

        # サブスレッド作成・開始
        self.lock = threading.Lock() # 排他制御用
        self.thread = MainProcessing.MainProcessing(config, self.q_img, self.lock)
        self.thread.start()

        logger.info("Active_Thread:\t{}".format(SubThread.ActiveThread()))
        self.running = True

    def run(self):
        logger.info("Graphic_Start")

        # メインループ
        # --------------------------------------------------
        while self.running:
            # メインプロセスのモード設定
            self.thread.mode = self.mode

            # 画像の更新
            self.updateImg()

            # GUI表示画像の更新
            cv2.imshow(self.win_name, self.show_img)
            key = cv2.waitKey(10) # 0.1秒ごとに画面更新

            if key == 27: # ESCが押されたら終了
                self.thread.running = False # サブスレッドを停止させる
                self.running = False
                self.close()
            elif key == ord("s"): # 設定モードに移行
                self.mode = 1
            elif key == ord("u"): # 解錠モードに移行
                self.mode = 0

        logger.info("Graphic_End")

    def updateImg(self):
        try:
            self.show_img = self.q_img.get(timeout=0.1)
            if self.mode == 0:
                self.unlock()
            elif self.mode == 1:
                self.setting()

            # FPS表示
            cv2.putText(self.show_img, "FPS:{:.2f}".format(self.thread.fps),
                        (self.width-200, 25),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 1,
                        cv2.LINE_AA)
        except queue.Empty as e:
            pass

    def unlock(self):
        '''
        解錠モードのGUI
        '''
        cv2.putText(self.show_img, "UNLOCK MODE",
                    (10, 25),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2,
                    cv2.LINE_AA)

    def setting(self):
        '''
        設定モードのGUI
        '''
        # 現在のモードを表示
        cv2.putText(self.show_img, "SETTING MODE",
                    (10, 25),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2,
                    cv2.LINE_AA)
        # 説明文を表示
        cv2.putText(self.show_img, "WAKUNAI",
                    (10, 50),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2,
                    cv2.LINE_AA)
        # 登録枠を表示
        win_size = int(self.height/4)
        cv2.rectangle(self.show_img,
                      (self.center[0]-win_size, self.center[1]-win_size),
                      (self.center[0]+win_size, self.center[1]+win_size),
                      (255, 255, 255), thickness=2, lineType=cv2.LINE_4)
        cv2.putText(self.show_img, "{:.0f}".format(self.thread.timer),
                    (self.center[0], self.center[1]),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2,
                    cv2.LINE_AA)

    def close(self):
        cv2.destroyAllWindows()
