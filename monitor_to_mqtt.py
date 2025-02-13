import time
from datetime import datetime

import serial.tools.list_ports
import json
from paho.mqtt import client as mqtt
import sys
import os

# dynamixel_sdk を使います
from dynamixel_sdk import PortHandler, PacketHandler
from dynamixel_sdk import COMM_SUCCESS, COMM_RX_TIMEOUT,COMM_TX_FAIL


def list_com_ports():
    # 利用可能なポートを取得
    ports = serial.tools.list_ports.comports()
    available_ports = []

    for port in ports:
        # ポート情報をリストに追加
#        available_ports.append({
#            "device": port.device,            # デバイス名 (例: "COM3")
#            "description": port.description,  # デバイスの説明
#            "hwid": port.hwid                 # ハードウェアID
#        })
        print("Chcking port:",port.device)
        if "0403:6014" in port.hwid: ## FTDI device VID:PID  0403:6014
            flag = True
            try:
                with serial.Serial(port.device) as ser:
                    pass
            except serial.SerialException as e:
                flag = False
            
            if flag:
                return port.device

    return ""

com_port = list_com_ports() #  今使えるポートを返すはず


ADDR_TORQUE_ENABLE = 64  # トルク有効化


port_handler = PortHandler(com_port)
packet_handler = PacketHandler(2.0)

if port_handler.openPort():
    print("Opne port",com_port)
    if port_handler.setBaudRate(4_000_000):
        print("Set Baud")
else:
    print("Can't open!",com_port)
    quit()
    
DXL_IDS = [11,12,13,14,15]


def set_position_and_torque():
    for did in DXL_IDS:
#        dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, did, ADDR_OPERATING_MODE, )
#        if dxl_comm_result != COMM_SUCCESS:
#            print(f"動作モードの設定に失敗しました: {packet_handler.getTxRxResult(dxl_comm_result)}")
#            quit()
        # トルクを有効化
#        print("Set torque 0",did)
        dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, did, ADDR_TORQUE_ENABLE, 0)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"トルク有効化に失敗しました: {packet_handler.getTxRxResult(dxl_comm_result)}")
            quit()

set_position_and_torque()
        

def ping_id(DXL_ID):   
    dxl_model_number, dxl_comm_result, dxl_error = packet_handler.ping(port_handler, DXL_ID)

    if dxl_comm_result == COMM_SUCCESS:
        print(f"ID {DXL_ID} のDynamixelが応答しました。")
        print(f"モデル番号: {dxl_model_number}")
    elif dxl_comm_result == COMM_RX_TIMEOUT:
        print(f"ID {DXL_ID} からの応答がタイムアウトしました。")
    elif dxl_comm_result == COMM_TX_FAIL:
        print(f"ID {DXL_ID} にPingを送信できませんでした。")
    else:
        print(f"エラーが発生しました。コード: {dxl_comm_result}")
    
#dl, res = packet_handler.broadcastPing(port_handler)
#print(dl)

class DX_MQTT:
    def __init__(self):
        self.log = open("datalog.txt","w")
        
    def on_connect(self, client, userdata,flag, rc):
        print("Connected with result code " + str(rc))  # 接続できた旨表示
#        self.client.subscribe("/state") #　connected -> subscribe
    
    def on_disconnect(self, client, userdata, rc):
        if  rc != 0:
            print("Unexpected disconnection.")
    def on_message(self,client, userdata, msg):
        print("Message",msg.payload)
    
    def connect_mqtt(self):
        self.client = mqtt.Client()  
# MQTTの接続設定
        self.client.on_connect = self.on_connect         # 接続時のコールバック関数を登録
        self.client.on_disconnect = self.on_disconnect   # 切断時のコールバックを登録
        self.client.on_message = self.on_message         # メッセージ到着時のコールバック
        self.client.connect("192.168.207.22", 1883, 60)
        self.client.loop_start()   # 通信処理開始
#        self.client.loop_forever()   # 通信処理開始
            



ADDR_PRESENT_POSITION = 132  # 現在の位置のアドレス
LENGTH_PRESENT_POSITION = 4  # データ長（バイト）

mq = DX_MQTT()
mq.connect_mqtt()

pos_list = [0,0,0,0,0]
while True:
    for did in DXL_IDS:
        dxl_position, dxl_comm_result, dxl_error = packet_handler.read4ByteTxRx(port_handler, did, ADDR_PRESENT_POSITION)
        if dxl_comm_result == COMM_SUCCESS:
            pos_list[did-11]=dxl_position        
        else:
            print("Error read:",did,dxl_comm_result, dxl_error)
#            quit()
    ctime = datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")        
    print(ctime,pos_list)
    mq.log.write(json.dumps({"time":ctime,"real":pos_list})+"\n")

    mq.client.publish("om/real",json.dumps({"rotate":pos_list}))
    #pos_list を　MQTT で送る


# ポートを閉じる
port_handler.closePort()
