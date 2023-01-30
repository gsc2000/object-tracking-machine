import os
import sys

import time
import threading
import cv2

import GetImage
import Graphic
import libs.Util as Util
import libs.SubThread as SubThread

import ArtificialIntelligence
import Control
import Bluetooth

# loggerの設定
logger = Util.childLogger("MainProcess")

class MainProcessing(SubThread.SubThread):
    def __init__(self, ui, config, lock: threading.Lock) -> None:
        super().__init__("MainProcess")

        # 設定の格納
        self.ui = ui # GUI

        self.lock = lock # 排他制御

        self.running = True # 処理ループ
        self.cnt = 0 # 処理回数カウント

        # 各クラスのインタンス化を下記に記載
        # GetImage.py内のクラス 画像取得用
        self.cap = GetImage.GetImage(config)

        # ArtificialIntelligence.py内のクラス AI処理用
        # 下記はイメージ
        self.ai = ArtificialIntelligence.Object_detector()

        # Control.py内のクラス モータコントロール用
        # 下記はイメージ
        self.control = Control.control(config)

        # Bluetooth.py内のクラス　ラズパイ通信用
        # self.bluetooth = Bluetooth.bluetooth()

        # logger.info("MainProcess_Thread_Start")

    def run(self):
        logger.info("MainProcess_Process_Start")
        while self.running:
            st_time = time.time()
            # 画像取得
            # def ~: -> Numpy配列
            # logger.debug("Image_Get")
            img = self.cap.shot()

            # YOLOの制御を書く
            # logger.debug("YOLO")
            # def ~ -> dict
            yolo_time = time.time()
            pred_img, center_pix, num_human_det = self.ai.detect(img=img, conf_thres=0.4)
            yolo_fps = 1/time.time()-yolo_time
            logger.debug("YOLO_Time:{}".format(yolo_fps))

            # predの結果から人を囲っている画像を作成
            # YOLOのライブラリでできる気がしたけど要確認
            # logger.debug("Detect_image_create")

            # モータ制御を書く
            # logger.debug("Motor_Control")
            # if self.cnt % 5 == 0: #10回ごとにモーター制御を入れる
            #     dc = self.control.run(center_pix, num_human_det)

            # ラズパイにbluetoothで"open"or"close"を送信する
            lock_status = "0"
            self.bluetooth.send(locl_status)

            self.cnt += 1 # 処理回数カウントUP 何かに使いそう

            if self.ui.running == False: # UIで停止処理が実行された場合 メインスレッドが死ぬと止まるのであんまり関係ないかも
                # self.lock.acquire()
                self.close()
                logger.info("MainProcess_Thread_End")

            # time.sleep(0.1) # とりあえず記載
            lap_time = time.time()-st_time
            fps = 1/lap_time
            logger.info("Lap_Time:\t{}".format(fps))
            # GUI表示画像書き換え
            self.ui.show_img = pred_img
            cv2.putText(self.ui.show_img, "FPS:{:.2f}".format(fps),
                        (10, 25),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 1,
                        cv2.LINE_AA)

        # self.lock.release()

    def close(self):
        '''
        終了処理
        '''
        self.running = False
