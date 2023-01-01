# 画像関係

import os
import sys

import cv2

import numpy as np

import libs.Util as Util

logger = Util.childLogger(__name__)

class GetImage():
    '''
    画像取得
    '''
    def __init__(self, config: dict) -> None:
        self.cap = cv2.VideoCapture(config["CAMERA"]["ID"])
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
        # self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y','U','Y','V'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config["CAMERA"]["SIZE_X"])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config["CAMERA"]["SIZE_Y"])
        self.cap.set(cv2.CAP_PROP_FPS, config["CAMERA"]["FPS"])

        # フォーマット・解像度・FPSの取得
        fourcc = self.decode_fourcc(self.cap.get(cv2.CAP_PROP_FOURCC))
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        logger.info("Camera_Info:\t[fourcc:{} fps:{}　width:{}　height:{}]".format(fourcc, fps, width, height))

        self.resize_size = (config["CAMERA"]["RESIZE_Y"], config["CAMERA"]["RESIZE_X"])

        self.null_img = np.zeros((config["CAMERA"]["RESIZE_X"], config["CAMERA"]["RESIZE_Y"], 3),
                                  dtype="uint8") # 初期画像

    def shot(self):
        ret, frame = self.cap.read()

        if ret == True:
            img = cv2.resize(frame, self.resize_size)
            # logger.info("Get_Image_Success")
        elif ret == False:
            logger.info("Get_Image_Failure")
            img = self.null_img


        return img

    def decode_fourcc(self, v):
        v = int(v)
        return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])
