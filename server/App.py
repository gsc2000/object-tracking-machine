# プログラム起動用
import os
import sys

import yaml

import threading

import time

import Graphic
import GetImage
import ArtificialIntelligence as ai
import Control
import libs.Util as Util

def main():
    '''
    メイン処理
    '''
    # コンフィグ読み込み
    # --------------------------------------------------
    with open('resource/config/config.yaml') as file:
        CONFIG = yaml.safe_load(file.read())

    # Loggerの設定
    # --------------------------------------------------
    logger = Util.rootLogger(CONFIG["LOG"]["DIR"], CONFIG["LOG"]["LEVEL"])
    logger.info("App_Start")
    logger.debug("Read_Config: {}".format(CONFIG))

    # 初期化処理
    # --------------------------------------------------
    lock = threading.Lock() # 排他制御
    gui = Graphic.cv2graphic(CONFIG, lock)
    # gui.start()

    cap = GetImage.GetImage(CONFIG)

    cnt = 0 # メインループカウント
    running = True # メインループフラグ

    # メインループ
    # --------------------------------------------------
    while running:
        # 画像取得
        # def ~: -> Numpy配列
        # lock.acquire()
        img = cap.shot()
        # lock.release()

        # 推論
        detection = ai.Object_detector()
        result = detection.detect(img=img)
        print(result)

        # 画像表示
        gui.show_img = img.copy()

        # YOLO
        # def ~ -> dict

        # 制御

        cnt += 1
        if gui.running == False:
            running = False

        time.sleep(1)

    logger.info("App_Close")

if __name__ == "__main__":
    main()
