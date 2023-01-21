#!/usr/bin/python
# coding: UTF-8

import sys
import time
import bluetooth

address = "F4:5C:89:C4:C7:12"
port = 1

sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )

sock.bind( ( "", port ) )
sock.listen( 1 )

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

  except:
    sock.close()
    sock_client.close()
    break