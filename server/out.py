#!/usr/bin/python3
# coding: UTF-8

import sys
import bluetooth
import time

address = "B8:27:EB:F9:EF:95"
PORT = 1

sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
print('PG Start')
sock.connect( ( address , PORT ) )
print('try before')

try:
    while True:
        a = input('1 から 5 までの数字を入力してください>>')
        if a.isdecimal() == True:
            if int(a) > 0 and int(a) < 6:
                sock.send( str(a) )
                print(a)
            else:
                if int(a) == 6:
                    sock.send( str(a) )
                    print(a)
                    time.sleep(2)
                    break
                else:
                    print('指定の数字ではありません')
        else:
            print('入力が数字ではありません')

except KeyboardInterrupt:
    sock.close()
