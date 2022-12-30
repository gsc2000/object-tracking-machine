# プログラム起動用
import os
import sys

import threading

import time

import Graphic
import GetImage
import libs.Util as Util

def main():
    '''
    メイン処理
    '''
    # コンフィグ読み込み
    # --------------------------------------------------
    CONFIG = Util.read_json("server/config/config.json")

    # Loggerの設定
    # --------------------------------------------------
    logger = Util.rootLogger(CONFIG["LOG_DIR"], CONFIG["LOG_LEVEL"])
    logger.info("App_Start")
    logger.debug("Read_Config: {}".format(CONFIG))

    # 初期化処理
    # --------------------------------------------------
    lock = threading.Lock() # 排他制御
    gui = Graphic.cv2graphic((CONFIG["IMG_SIZE_X"], CONFIG["IMG_SIZE_Y"]), lock)
    gui.start()

    cap = GetImage.GetImage(CONFIG["CAMERA_ID"], (CONFIG["RESIZE_SIZE_X"], CONFIG["RESIZE_SIZE_Y"]))

    cnt = 0 # メインループカウント
    running = True # メインループフラグ

    # メインループ
    # --------------------------------------------------
    while running:
        # 画像取得
        # def ~: -> Numpy配列
        img = cap.shot()

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