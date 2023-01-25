# GUI表示関係

import os
import sys

import time

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import numpy as np
import keyboard
import asyncio
import json
import yaml

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
    def __init__(self, config: dict) -> None:
        '''
        Initialize
        '''
        self.mode = None # 初期モード
        # 0:解錠モード
        # 1:設定モード
        self.q_img = queue.Queue() # サブスレッドから画像をもらうためのキュー

        # GUI設定の格納
        self.win_name = "Show"
        self.width = config["CAMERA"]["RESIZE_X"]
        self.height = config["CAMERA"]["RESIZE_Y"]
        self.center = (int(self.width/2), int(self.height/2))
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        win_size = int(self.height/4)

        # キー関係
        self.regi_frame = (self.center[0]-win_size, self.center[1]-win_size,
                           self.center[0]+win_size, self.center[1]+win_size)
        self.num_key = config["KEY"]["NUM"]
        # クラス読み込み
        with open(config["KEY"]["CLASS"], encoding='utf-8') as file:
            self.classes = yaml.safe_load(file.read())
        # print(self.classes)

        # ロゴ読み込み
        self._logo = cv2.imread(config["LOGO"]["PATH"], cv2.IMREAD_UNCHANGED)
        boot_logo = cv2.resize(self._logo, (int(self.height/2), int(self.height/2)))
        self._logo_size_x = config["LOGO"]["SIZE_X"]
        self._logo_size_y = config["LOGO"]["SIZE_Y"]
        self._logo = cv2.resize(self._logo, (self._logo_size_y, self._logo_size_x))

        # GUI初期画像の作成
        self._show_img = np.zeros((self.height, self.width, 3),
                                   dtype="uint8")
        top = int(self.height/4)
        bottom = int(3*self.height/4)
        left = int(self.width/2)-int(self.height/4)
        right = int(self.width/2)+int(self.height/4)
        self._show_img[top:bottom, left:right] = boot_logo[:,:,:3]
        # cv2.putText(img=self._show_img,
        #             text='Please Wait',
        #             org=(10, int(self.height/2)),
        #             fontFace=self.font,
        #             fontScale=4,
        #             color=(255, 255, 255),
        #             thickness=5,
        #             lineType=cv2.LINE_AA)


        # GUIウィンドウの表示
        cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL|cv2.WINDOW_KEEPRATIO)
        if config["CAMERA"]["FULLSCREEN"]:
            cv2.setWindowProperty(self.win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN) #フルスクリーン表示
        cv2.imshow(self.win_name, self._show_img) # 初期画像の表示

        # サブスレッド作成・開始
        self.lock = threading.Lock() # 排他制御用
        self.thread = MainProcessing.MainProcessing(config, self.regi_frame,
                                                    self.q_img, self.lock)
        self.thread.start()

        logger.info("Active_Thread:\t{}".format(SubThread.ActiveThread()))
        self.running = True

    def run(self):
        logger.info("Graphic_Start")

        # メインループ
        # --------------------------------------------------
        while self.running:
            # メインプロセスのモード設定
            self.mode = self.thread.mode

            # 画像の更新
            self.update()

            # GUI表示画像の更新
            cv2.imshow(self.win_name, self._show_img)
            cv2.waitKey(10) # 0.1秒ごとに画面更新

            if keyboard.is_pressed("shift+s"):
                self.changeMode()
                time.sleep(0.5)
            elif keyboard.is_pressed("l"):
                if self.mode == 0:
                    # lock
                    self.thread.lock_io = True
                    pass
            elif keyboard.is_pressed("esc"):
                self.close()
                time.sleep(0.5)

        logger.info("Graphic_End")

    def changeMode(self):
        now_mode = self.thread.mode
        if self.thread.mode == 0:
            self.thread.mode = 1 # 設定モードへ
        elif self.thread.mode == 1:
            self.thread.mode = 0 # 解錠モードへ

        logger.info("Mode_Change:\t{}->{}".format(now_mode, self.mode))

    def update(self):
        """
        表示画像のアップデート
        """
        try:
            self._show_img = self.q_img.get(timeout=0.1)
            # ロゴ挿入
            top = 10
            bottom = self._logo_size_y+top
            left = self.width-(self._logo_size_x+10)
            right = self.width-10

            in_logo = self._show_img[top:bottom, left:right]*(1-self._logo[:, :, 3:]/255)+ \
                      self._logo[:, :, :3]*self._logo[:, :, 3:]/255
            self._show_img[top:bottom, left:right] = in_logo

            # モードによって変わる部分を表示
            if self.mode == 0:
                self.unlock()
            elif self.mode == 1:
                self.setting()

            # 共通の情報を表示
            self.fps()
            self.showMode()
            self.key_frame()

        except queue.Empty as e:
            pass

    def fps(self):
        """
        FPSの表示
        """
        cv2.putText(img=self._show_img,
                    text="FPS:{:.2f}".format(self.thread.fps),
                    org=(self.width-80, self.height-15),
                    fontFace=self.font,
                    fontScale=0.5,
                    color=(0, 255, 0),
                    thickness=2,
                    lineType=cv2.LINE_AA)

    def key_frame(self):
        """
        登録枠を表示
        """
        # 説明文を表示
        cv2.putText(img=self._show_img,
                    text="Put object in the frame",
                    org=(self.regi_frame[0], self.regi_frame[1]-5),
                    fontFace=self.font,
                    fontScale=0.5,
                    color=(255, 255, 255),
                    thickness=1,
                    lineType=cv2.LINE_AA)
        cv2.rectangle(img=self._show_img,
                      pt1=(self.regi_frame[0], self.regi_frame[1]),
                      pt2=(self.regi_frame[2], self.regi_frame[3]),
                      color=(255, 255, 255),
                      thickness=2,
                      lineType=cv2.LINE_4)
    def showMode(self):
        """
        モードの表示
        """
        if self.mode == 0:
            mode_txt = "UNLOCK"
            color = (0, 255, 0)
        elif self.mode == 1:
            mode_txt = "SETTING"
            color = (255, 0, 0)

        cv2.putText(img=self._show_img,
                    text="MODE: "+mode_txt,
                    org=(5, 30),
                    fontFace=self.font,
                    fontScale=1,
                    color=color,
                    thickness=3,
                    lineType=cv2.LINE_AA)

    def unlock(self):
        '''
        解錠モードのGUI
        '''
        no_show = False
        status = self.thread.auth_status
        if status == 50:
            text = "Already set!!!"
            org = (self.center[0]-110, self.center[1])
            color = (0, 0, 255)
        elif status == 2:
            text = "Set!"
            org = (self.center[0]-30, self.center[1])
            color = (0, 255, 0)
        elif status == 4:
            text = "Open!!!"
            org = (self.center[0]-60, self.center[1])
            color = (0, 255, 0)
        elif status == 51:
            text = "Only One!!!"
            org = (self.center[0]-90, self.center[1])
            color = (0, 0, 255)
        elif status == 10:
            text = "Auth Failure"
            org = (self.center[0]-100, self.center[1])
            color = (0, 0, 255)
        elif status == 1:
            text = "{:.0f}".format(self.thread.timer)
            org = (self.center[0], self.center[1])
            color = (0, 255, 255)
        else:
            no_show = True

        if not no_show:
            cv2.putText(img=self._show_img,
                        text=text,
                        org=org,
                        fontFace=self.font,
                        fontScale=1,
                        color=color,
                        thickness=2,
                        lineType=cv2.LINE_AA)
        self.keyInfo(self.thread.auth_key)


    def setting(self):
        '''
        設定モードのGUI
        '''
        no_show = False
        status = self.thread.reg_status
        if status == 50:
            text = "Registered!!!"
            org = (self.center[0]-100, self.center[1])
            color = (0, 0, 255)
        elif status == 2:
            text = "Register!"
            org = (self.center[0]-90, self.center[1])
            color = (0, 255, 0)
        elif status == 4:
            text = "All Register!"
            org = (self.center[0]-100, self.center[1])
            color = (0, 255, 0)
        elif status == 51:
            text = "Only One!!!"
            org = (self.center[0]-90, self.center[1])
            color = (0, 0, 255)
        elif status == 1:
            text = "{:.0f}".format(self.thread.timer)
            org = (self.center[0], self.center[1])
            color = (0, 255, 255)
        else:
            no_show = True

        if not no_show:
            cv2.putText(img=self._show_img,
                        text=text,
                        org=org,
                        fontFace=self.font,
                        fontScale=1,
                        color=color,
                        thickness=2,
                        lineType=cv2.LINE_AA)
        self.keyInfo(self.thread.new_key)

    def keyInfo(self, key):
        # 登録されているキー情報
        if self.mode == 0:
            color = (0, 255, 0)
        if self.mode == 1:
            color = (255, 0, 0)

        top_key = 100
        for i in range(self.num_key):
            try:
                key_idx = key["key{}".format(i)]
            except:
                break
            if key_idx == None:
                reg_class = None
            else:
                reg_class = self.classes["names"][key_idx]

            cv2.putText(img=self._show_img,
                        text="Key: {}".format(reg_class),
                        org=(5, top_key),
                        fontFace=self.font,
                        fontScale=0.75,
                        color=color,
                        thickness=2,
                        lineType=cv2.LINE_AA)
            top_key += 40


    def close(self):
        self.running = False
        cv2.destroyAllWindows()

