#!/usr/bin/python
# coding: UTF-8

import sys
import time
import bluetooth
import RPi.GPIO as GPIO

#GPIOの初期設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

lock = GPIO.PWM(20, 50) #GPIO20をPWM設定、周波数は50Hz
cover = GPIO.PWM(21, 50) #GPIO21をPWM設定、周波数は50Hz
lock.start(0.0) #Duty Cycle 0%
cover.start(0.0) #Duty Cycle 0%

#少しずつ回転
for degree in range(-90, 0):
  dc = 2.5 + (12.0-2.5)/180*(degree+90)
  cover.ChangeDutyCycle(dc)
  time.sleep(0.03)
  # cover.ChangeDutyCycle(0.0)#一旦DutyCycle0%にする

lock.ChangeDutyCycle(12) #初期degree=90[°]

#PCのMACアドレス　configから設定したい
address = "A4:CF:99:6C:D4:65" #新しいMAC
# address = "F4:5C:89:C4:C7:12" #古いMAC
port = 1
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )

sock.bind( ( "", port ) )
sock.listen( 1 )
# sock.settimeout( 5 )

while ( True ):
    try:
        print ("Connect....")
        sock_client,address = sock.accept()
        print("Connected")
        break
    except bluetooth.BluetoothError :
        print ("Connection Failed")
        sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        time.sleep ( 1 )

while( True ):
  try:
        print("受信待ち")
        data_ = sock_client.recv(16)
        data  = data_.decode()
        if data == 0:
          #少しずつ回転
          for degree in range(-90, 0):
            dc = 2.5 + (12.0-2.5)/180*(degree+90)
            cover.ChangeDutyCycle(dc)
            time.sleep(0.03)
            # cover.ChangeDutyCycle(0.0)#一旦DutyCycle0%にする
          degree = 90
          dc = 2.5 + (12.0-2.5)/180*(degree+90) #角度をDutyCycleに変換
          #DutyCycle dc%
          lock.ChangeDutyCycle(dc)
          time.sleep(1)
          print("close")
        elif data == 1:
          degree = 0
          dc = 2.5 + (12.0-2.5)/180*(degree+90) #角度をDutyCycleに変換
          #DutyCycle dc%
          p.ChangeDutyCycle(dc)
          time.sleep(1)
          for degree in range(0, -90):
            dc = 2.5 + (12.0-2.5)/180*(degree+90)
            cover.ChangeDutyCycle(dc)
            time.sleep(0.03)
            # cover.ChangeDutyCycle(0.0)#一旦DutyCycle0%にする
          print("open")

  except KeyboardInterrupt:
    sock.close()
    sock_client.close()
    break

  except:
    sock.close()
    sock_client.close()
    break
