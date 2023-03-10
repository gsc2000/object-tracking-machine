# 制御関係
import time
# import RPi.GPIO as GPIO


class control():
    def __init__(self, config: dict) -> None:
        self.resize_size = config["CAMERA"]["RESIZE_X"]
        self.target = int(self.resize_size) / 2
        self.range = 60

        # #GPIOの初期設定
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(4, GPIO.OUT)
        # p = GPIO.PWM(4, 50) #GPIO4をPWM設定、周波数は50Hz
        # p.start(0.0) #Duty Cycle 0%
        # p.ChangeDutyCycle(12) #初期degree=90[°]

    def run(self, center_pix, num_human_det):
        '''
        サーボモータを制御
        '''
        if num_human_det <= 0:
            return center_pix, num_human_det
        for i in range(num_human_det):
            degree = int((self.target-center_pix[i])/self.target*self.range) # +:反時計回り　-:時計回り
            degree += 90 # 0-180に変換
            dc = 2.5 + (12.0-2.5)/180*(degree+90) #角度をDutyCycleに変換
        #DutyCycle dc%
        # p.ChangeDutyCycle(dc)
        # print(degree, dc)
        return dc
