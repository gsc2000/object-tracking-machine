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
    def __init__(self, camera_id: int, resize_size: tuple) -> None:
        self.cap = cv2.VideoCapture(camera_id)
        self.resize_size = resize_size

    def shot(self):
        ret, frame = self.cap.read()

        if ret == True:
            logger.info("Get_Image_Success")
        elif ret == False:
            logger.info("Get_Image_Failure")

        frame = np.full(self.resize_size, 200, dtype="uint8") # テスト用
        img = frame.copy()

        return img
