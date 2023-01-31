#!/usr/bin/python3
# coding: UTF-8

import sys
import bluetooth
import time

class bluetooth():
    def __init__(self, mac):
        # ラズパイのMACアドレス　configから設定したい
        self.address = mac
        self.PORT = 1
        self.sock=bluetooth.BluetoothSocket()
        self.sock.connect((self.address, self.PORT))
        print('PG Start')

    def open_send(self):
        try:
            self.sock.send(bytes(1))
        except:
            self.sock.close()

    def close_send(self):
        try:
            self.sock.send(bytes(0))
        except:
            self.sock.close()
