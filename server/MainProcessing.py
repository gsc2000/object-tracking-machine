import os
import sys

import time
import threading
import queue
# import cv2

import GetImage
# import Graphic
import libs.Util as Util
import libs.SubThread as SubThread

import Inferencer
import Control_for_pc as Control
import Bluetooth

# loggerの設定
logger = Util.childLogger("MainProcess")

class MainProcessing(SubThread.SubThread):
    def __init__(self, config, q_img: queue.Queue, lock: threading.Lock) -> None:
        super().__init__("MainProcess")
        # 各種変数
        self.mode = None # モード 解錠or設定
        self.fps = 0 # FPS
        self.timer = 0 # 中心に物体が存在した時間
        self.q_img = q_img # メインスレッドへ画像を渡すためのキュー
        self.lock = lock # 排他制御

        self.cnt = 0 # アプリ処理回数

        # 各クラスのインタンス化
        self.cap = GetImage.GetImage(config) # 画像取得
        self.ai = Inferencer.Object_detector() # AI処理
        self.control = Control.control(config) # 駆動制御
        # self.bluetooth = Bluetooth.bluetooth() # ラズパイ通信用

        self.running = True # 処理ループ

    def run(self):
        logger.info("MainProcess_Process_Start")
        set_timer = 0
        while self.running:
            st_time = time.time()
            # 画像取得
            img = self.cap.shot()

            # YOLOの制御を書く
            lap_time = time.time()
            pred_img, center_pix, num_human_det, center_obj = self.ai.detect(img=img, conf_thres=0.45)
            # logger.debug("YOLO_FPS:\t{:.2f}".format((time.time()-lap_time)**-1))

            if len(center_obj) != 0 and set_timer == 0:
                set_timer = time.time()
            elif len(center_obj) != 0 and set_timer != 0:
                self.timer = time.time()-set_timer
                if self.timer >= 3:
                    logger.info("Set")
                    # self.set_flg = True
                    set_timer = 0

            elif len(center_obj) == 0:
                set_timer = 0

            # モータ制御を書く
            if self.cnt % 5 == 0: #10回ごとにモーター制御を入れる
                dc = self.control.run(center_pix, num_human_det)

            # ラズパイにbluetoothでduty比を送信する
            # self.bluetooth.send(dc)

            self.fps = (time.time()-st_time)**-1
            # logger.info("App_FPS:\t{:.2f}".format(self.fps))

            # GUI表示画像書き換え処理
            self.q_img.put(pred_img)

            self.cnt += 1 # 処理回数カウントUP 何かに使いそう
        logger.info("MainProcess_Thread_End")

    def close(self):
        '''
        終了処理
        '''
        self.running = False
