# プログラム起動用
import os
import sys

import yaml
import argparse

import Graphic
import libs.Util as Util

def parseArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', type=str,
                        default='../resource/config/config.yaml')

    args = parser.parse_args()
    return args

def main():
    '''
    メイン処理
    '''
    # 引数の取得
    args = parseArgs()

    # コンフィグ読み込み
    # --------------------------------------------------
    with open(args.config) as file:
        CONFIG = yaml.safe_load(file.read())

    # Loggerの設定
    # --------------------------------------------------
    logger = Util.rootLogger(CONFIG["LOG"]["DIR"], CONFIG["LOG"]["LEVEL"])
    logger.info("App_Start")
    logger.debug("Read_Config: {}".format(CONFIG))

    # 初期化処理
    # --------------------------------------------------
    # lock = threading.Lock() # 排他制御
    gui = Graphic.cv2graphic(CONFIG)
    gui.run()

    logger.info("App_Close")

if __name__ == "__main__":
    main()
