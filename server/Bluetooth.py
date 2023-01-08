#!/usr/bin/python3
# coding: UTF-8

import sys
import bluetooth
import time

class bluetooth():
    def __init__(self):
        # ラズパイのMACアドレス　configから設定したい
        self.address = "B8:27:EB:F9:EF:95"
        self.PORT = 1
        self.sock=bluetooth.BluetoothSocket()
        print('PG Start')

    def send(self,dc):
        self.sock.connect( ( self.address , self.PORT ) )
        self.sock.send( dc.encode() )
        self.sock.close()
        return 'sent'
