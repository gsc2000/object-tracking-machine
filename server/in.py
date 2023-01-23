#!/usr/bin/python
# coding: UTF-8

import sys
import time
import bluetooth

#PCのMACアドレス　configから設定したい
# address = "A4:CF:99:6C:D4:65" #新しいMAC
address = "F4:5C:89:C4:C7:12" #古いMAC
port = 1
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )

sock.bind( ( "", port ) )
sock.listen( 1 )
sock.settimeout( 5 )

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
        data_ = sock_client.recv(16)
        # data  = data_.decode("UTF-8")
        data  = data_.decode()
        print(data)

        # for i in data:
        #
        #     if( i == "1" ):
        #         print("One")
        #     elif( i == "2" ):
        #         print("Two")
        #     elif( i == "3" ):
        #         print("Three")
        #     elif( i == "4" ):
        #         print("Four")
        #     elif( i == "5" ):
        #         print("Five")
        #     else:
        #         print("THE END")
        #         sock.close()
        #         sock_client.close()
        #         break

  except KeyboardInterrupt:
    sock.close()
    sock_client.close()
    break

  except socket.error:
    sock.close()
    sock_client.close()
    print ("connection timed out!")
    break

  except:
    sock.close()
    sock_client.close()
    break
