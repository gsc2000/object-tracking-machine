import os
import sys

import time
import threading

import GetImage
import Graphic
import libs.Util as Util
import libs.SubThread as SubThread

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
        # self.ai = ArtificialIntelligence.yolo(config)

        # Control.py内のクラス モータコントロール用
        # 下記はイメージ
        # self.control = Control.control(config)

        logger.info("MainProcess_Thread_Start")

    def run(self):
        logger.info("MainProcess_Process_Start")
        while self.running:
            # 画像取得
            # def ~: -> Numpy配列
            # logger.debug("Image_Get")
            img = self.cap.shot()

            # YOLOの制御を書く
            # logger.debug("YOLO")
            # def ~ -> dict
            # pred = self.ai.detect(img)

            # predの結果から人を囲っている画像を作成
            # YOLOのライブラリでできる気がしたけど要確認
            # logger.debug("Detect_image_create")
            # 下記はイメージ
            detect_img = img.copy() # とりあえず。ほんとはなんかのメソッドの戻り値を格納
            # GUI表示画像書き換え
            self.ui.show_img = detect_img

            # モータ制御を書く
            # logger.debug("Motor_Control")
            # 下記はイメージ
            # self.control.run() モータが動く

            self.cnt += 1 # 処理回数カウントUP 何かに使いそう

            if self.ui.running == False: # UIで停止処理が実行された場合 メインスレッドが死ぬと止まるのであんまり関係ないかも
                # self.lock.acquire()
                self.close()
                logger.info("MainProcess_Thread_End")

            time.sleep(0.1) # とりあえず記載

        # self.lock.release()

    def close(self):
        '''
        終了処理
        '''
        self.running = False
