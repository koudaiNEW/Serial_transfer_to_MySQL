

from asyncio.windows_events import NULL
from re import sub
from threading import Thread
from multiprocessing import Process
from tkinter import EXCEPTION
import time
import serial
import serial.tools.list_ports
import pymysql
import datetime
import struct
import time



def Sensoc():
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) <= 0:
        print("null")
    else:
        print("list on")
        for comport in ports_list:
            print(list(comport)[0], list(comport)[1])

def Choose():
    #目前为固定端口与波特率，可根据需求更改
    ser = serial.Serial("COM9", 9600)    
    if ser.isOpen():                       
        print("successfull")
        print(ser.name)    
    else:
        print("fail")

def bytesToFloat(h1,h2,h3,h4):
    ba = bytearray()
    ba.append(h1)
    ba.append(h2)
    ba.append(h3)
    ba.append(h4)
    return struct.unpack("!f",ba)

def Transfer_Data(txMod, my485, db):
    #串口发送数据，此示例为MODBUS协议读指令
    cmd0 = bytearray([0x00,0x04,0x00,0x00,0x00,0x06,0x71,0xD9])
    cmd1 = bytearray([0x01,0x04,0x00,0x00,0x00,0x0C,0xF0,0x0F])
    cmd2 = bytearray([0x02,0x04,0x00,0x00,0x00,0x0C,0xF0,0x3C])
    cmd3 = bytearray([0x03,0x04,0x00,0x00,0x00,0x0C,0xF1,0xED])
    cmd4 = bytearray([0x04,0x04,0x00,0x00,0x00,0x0C,0xF0,0x5A])

    rxBuff = bytearray()
    successRate = 0.0
    temp = 0.0
    hum = 0.0
    sql = ""
    gatherTime = ""

    if txMod == 0:
        my485.write(cmd0)
    elif txMod == 1:
        my485.write(cmd2)
    elif txMod == 2:
        my485.write(cmd3)
    elif txMod == 3:
        my485.write(cmd4)

    rxBuff = my485.readall()
    try:
        if rxBuff[1] == 0x04 or rxBuff[1] == 0x84:
            rxCount += 1
            rxID = rxBuff[0]
            temp3 = rxBuff[7]
            temp2 = rxBuff[8]
            temp1 = rxBuff[9]
            temp0 = rxBuff[10]
            hum3 = rxBuff[11]
            hum2 = rxBuff[12]
            hum1 = rxBuff[13]
            hum0 = rxBuff[14]
            temp = bytesToFloat(temp3,temp2,temp1,temp0)
            hum = bytesToFloat(hum3,hum2,hum1,hum0)
            #successRate = rxCount/txCount*100
            gatherTime = time.asctime()
            #根据数据结构传输
            sql = "ID:" + str(rxID) + ", Temp: " + str(temp) + ", Hum: " + str(hum) + ", SuccessRate: " + str(successRate) + ", Time: " + str(gatherTime)
            print(sql)
    except:
        print("Get data error")

    sql = "insert into id0_temp(abnormal_data) values (" + sql + ");"

    cursor = db.cursor() #创建游标
    cursor.execute(sql)  #插入数据
    db.commit()  #提交
        
    time.sleep(0.2)


if __name__ == "__main__":
    #固定端口
    my485 = serial.Serial("COM9", 9600,timeout=0.8) 
    print("Serial COM9 on")
    #mysql数据库访问
    db = pymysql.connect(host='192.168.1.61',port=3306,user = "root",password = "",db = "project_7_tempandhum_detector_485")
    print("Database on")

    txMod = 0
    while True :
        Transfer_Data(txMod, my485, db)
        if txMod > 2 :
            txMod = 0
        else:
            txMod += 1
