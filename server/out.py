#!/usr/bin/python3
# coding: UTF-8

import sys
import bluetooth
import time

address = "B8:27:EB:F9:EF:95"
PORT = 1

sock=bluetooth.BluetoothSocket()
print('PG Start')
sock.connect( ( address , PORT ) )
print('try before')

try:
    while True:
        a = input('0:false 1:true')
        sock.send( a.encode() )
        print(a)
        time.sleep(2)
except KeyboardInterrupt:
    sock.close()
