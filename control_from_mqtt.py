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
        if "0403:6014" in port.hwid: ## FTDI device VID:PID  0403:6014
            return port.device

    return ""

#com_port = list_com_ports()
com_port="COM9"



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
        pass
#        self.log = open("datalog.txt","w")
        
    def on_connect(self, client, userdata,flag, rc):
        print("Connected with result code " + str(rc))  # 接続できた旨表示
        self.client.subscribe("om/real") #　connected -> subscribe
    
    def on_disconnect(self, client, userdata, rc):
        if  rc != 0:
            print("Unexpected disconnection.")
            
    def on_message(self,client, userdata, msg):
#        print("Message",msg.payload)
        json_data = json.loads(msg.payload)
        pos_list = json_data["rotate"]
#        print(json_data,pos_list)
            
        for did in DXL_IDS:
            dxl_comm_result, dxl_error = packet_handler.write4ByteTxRx(port_handler, did, ADDR_GOAL_POSITION, pos_list[did-11])
            if dxl_comm_result != COMM_SUCCESS:
                print("Error on control")
                quit()
        time.sleep(0.01)
        
    
    def connect_mqtt(self):
        self.client = mqtt.Client()  
# MQTTの接続設定
        self.client.on_connect = self.on_connect         # 接続時のコールバック関数を登録
        self.client.on_disconnect = self.on_disconnect   # 切断時のコールバックを登録
        self.client.on_message = self.on_message         # メッセージ到着時のコールバック
        self.client.connect("192.168.207.22", 1883, 60)
#        self.client.loop_start()   # 通信処理開始
        self.client.loop_forever()   # 通信処理開始
            


ADDR_TORQUE_ENABLE = 64  # トルク有効化
ADDR_PRESENT_POSITION = 132  # 現在の位置のアドレス
ADDR_GOAL_POSITION = 116  # 目標位置
ADDR_DRIVE_MODE = 10  # ドライブモード
ADDR_OPERATING_MODE = 11  # 動作モード
ADDR_POSITION_P_GAIN = 84
ADDR_POSITION_I_GAIN = 82
ADDR_POSITION_D_GAIN = 80

LENGTH_PRESENT_POSITION = 4  # データ長（バイト）

# 定数
TORQUE_ENABLE = 1  # トルク有効
TORQUE_DISABLE = 0  # トルク無効
TIME_BASED_PROFILE = 4 # Time based profile
DEFAULT_PROFILE = 0 # 

POSITION_CONTROL_MODE = 3  # 位置制御モード



#fname ="datalog.txt"

def set_position_and_torque():
    for did in DXL_IDS:
        dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, did, ADDR_OPERATING_MODE, POSITION_CONTROL_MODE)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"動作モードの設定に失敗しました: {packet_handler.getTxRxResult(dxl_comm_result)}")
            quit()
        # トルクを有効化
        dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, did, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"トルク有効化に失敗しました: {packet_handler.getTxRxResult(dxl_comm_result)}")
            quit()
        # ドライブモード
        dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, did, ADDR_DRIVE_MODE, DEFAULT_PROFILE)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"モード変更に失敗しました: {packet_handler.getTxRxResult(dxl_comm_result)}")
            quit()
        dxl_comm_result, dxl_error = packet_handler.write2ByteTxRx(port_handler, did, ADDR_POSITION_P_GAIN, 100)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"ゲイン変更に失敗しました: {packet_handler.getTxRxResult(dxl_comm_result)}")
            quit()
        



#ファイルを１行づつ読む

set_position_and_torque()
pos_list = [0,0,0,0,0]
mq = DX_MQTT()
mq.connect_mqtt()


# ポートを閉じる
port_handler.closePort()
