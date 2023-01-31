import os
import sys

import time
import threading
import queue
# import cv2
import json

import GetImage
# import Graphic
import libs.Util as Util
import libs.SubThread as SubThread

import Inferencer
import Control_for_pc as Control
import Bluetooth
import Key

# loggerの設定
logger = Util.childLogger(__name__)

class MainProcessing(SubThread.SubThread):
    def __init__(self, config: dict, reg_frame: tuple,
                 q_img: queue.Queue, lock: threading.Lock) -> None:
        super().__init__("MainProcess")
        # 各種変数
        self.mode = 0 # モード 解錠or設定
        self.fps = 0 # FPS
        self.timer = config["KEY"]["COUNT"]
        self.reg_status = None
        self.auth_status = None
        self.reg_key = None
        self.auth_key = None
        self.new_key = None
        self.pre_mode = None
        self.flg_change = False
        self.open_io = False # GUIからのLOCK要求受信用
        self.close_io = False # モータへのOPEN要求送信用
        self.send_flg = False

        self.q_img = q_img # メインスレッドへ画像を渡すためのキュー
        self.lock = lock # 排他制御

        self.cnt = 0 # アプリ処理回数

        mac = config["DEVICE"]["MAC"] # Bluetooth接続デバイスのMACアドレス

        # 各クラスのインタンス化
        self.cap = GetImage.GetImage(config) # 画像取得
        self.ai = Inferencer.Object_detector() # AI処理
        # self.control = Control.control(config) # 駆動制御
        self.bluetooth = Bluetooth.mybluetooth(mac) # ラズパイ通信用
        self.set_key = Key.Unlock(config, reg_frame)
        self.save_key = Key.Savekey(config, reg_frame)

        self.running = True # 処理ループ

    def run(self):
        self.lock.acquire()
        logger.info("MainProcess_Process_Start")
        # キーの取得
        self.reg_key: dict = self.save_key.reg_key
        self.lock.release()
        while self.running:
            # logger.debug(self.open_io)
            st_time = time.time()
            # キーの取得
            self.auth_key:dict = self.set_key.auth_key
            self.reg_key: dict = self.save_key.reg_key
            self.new_key: dict = self.save_key.new_key
            # 画像取得
            img = self.cap.shot()

            # YOLOの制御を書く
            lap_time = time.time()
            pred_img, center_pix, num_human_det, obj = self.ai.detect(img=img, conf_thres=0.45)
            # logger.debug("YOLO_FPS:\t{:.2f}".format((time.time()-lap_time)**-1))

            # キー処理
            self.keyProc(obj)

            self.q_img.put(pred_img)

            self.cnt += 1 # 処理回数カウントUP 何かに使いそう
        logger.info("MainProcess_Thread_End")

    def keyProc(self, obj):
        # 前回からモードが変更されているか確認
        if self.pre_mode == None:
            pass
        elif self.pre_mode == self.mode:
            self.flg_change = False
        elif self.pre_mode != self.mode:
            self.flg_change = True
        self.pre_mode = self.mode

        if self.mode == 1:
            self.timer, self.reg_status = self.save_key.run(self.flg_change, obj)
            if self.reg_status == 5: # 全てのキー登録が完了したら解錠モードへ戻す
                self.mode = 0
                self.save_key.init()
        elif self.mode == 0:
            # キー認証処理
            self.timer, self.auth_status = self.set_key.run(self.flg_change, obj, self.reg_key)
            # print(self.auth_status)
            # モータ制御を書く
            if self.mode == 0 and self.auth_status == 4:
                if not self.send_flg:
                    self.bluetooth.open_send()
                    logger.debug("Open_send")
                    self.send_flg = True

            if self.send_flg:
                if self.close_io:
                    self.bluetooth.close_send()
                    logger.debug("Close_send")
                    self.close_io = False
                    self.send_flg = False
                    self.set_key.init()

    def close(self):
        '''
        終了処理
        '''
        self.running = False
