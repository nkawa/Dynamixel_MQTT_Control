import time
from datetime import datetime

import serial.tools.list_ports
import json
from paho.mqtt import client as mqtt
import sys
import os

# dynamixel_sdk を使います
from dynamixel_sdk import COMM_SUCCESS, COMM_RX_TIMEOUT,COMM_TX_FAIL, DXL_HIBYTE,DXL_LOBYTE,DXL_LOWORD,DXL_MAKEWORD,DXL_HIWORD
from dynamixel_sdk import PortHandler, PacketHandler, GroupSyncRead, GroupSyncWrite

ADDR_PRESENT_CURRENT = 126  # 現在の電流のアドレス (例: XMシリーズの場合)
LENGTH_PRESENT_CURRENT = 2  # データ長 (2バイト)


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
                print("Port:",port.device," is used.")
                flag = False
            
            if flag:
                return port.device

    return ""

com_port = list_com_ports()

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
        self.pos = [0,0,0,0,1270] # 1270が開いた状態  2634 が閉じた状態
        pass
#        self.log = open("datalog.txt","w")
# Sync Write用のインスタンス
    def setDXPorts(self, port_handler,packetHandler):
        self.groupSyncWrite = GroupSyncWrite(port_handler, packetHandler, ADDR_GOAL_POSITION, 4)

        
    def on_connect(self, client, userdata,flag, rc):
        print("Connected with result code " + str(rc))  # 接続できた旨表示
        self.client.subscribe("om/vrgoogle") #　connected -> subscribe
    
    def on_disconnect(self, client, userdata, rc):
        if  rc != 0:
            print("Unexpected disconnection.")
            
    def on_message(self,client, userdata, msg):
        json_data = json.loads(msg.payload)
        pos_list = json_data["rotate"]
        ctime = datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        print("Message",ctime, pos_list)
#        print(ctime, pos_list)
# もし、goal position の 4 （ツール）が減るときは、モニターを行う仕組みを入れるべき
        if pos_list[4] > 1270 and pos_list[4]-self.pos[4] > 0:
            #まずはチェックする。
            dxl_current, dxl_comm_result, dxl_error = packet_handler.read2ByteTxRx(port_handler, 15, ADDR_PRESENT_CURRENT)
            if dxl_current > 150:
                print("Over Current:",dxl_current, pos_list[4], self.pos[4])
                pos_list[4]=self.pos[4] # ぞれ以上変更しない

        goal_positions = pos_list
        self.pos = pos_list
        for dxl_id, goal_position in zip(DXL_IDS, goal_positions):
            param_goal_position = [DXL_LOBYTE(DXL_LOWORD(goal_position)),
                           DXL_HIBYTE(DXL_LOWORD(goal_position)),
                           DXL_LOBYTE(DXL_HIWORD(goal_position)),
                           DXL_HIBYTE(DXL_HIWORD(goal_position))]
            
            self.groupSyncWrite.addParam(dxl_id, param_goal_position)

        dxl_comm_result = self.groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print(f"通信エラー: {dxl_comm_result}")
            quit()
        
        self.groupSyncWrite.clearParam()
        
    

#        for did in DXL_IDS:
#            dxl_comm_result, dxl_error = packet_handler.write4ByteTxRx(port_handler, did, ADDR_GOAL_POSITION, pos_list[did-11])
#            if dxl_comm_result != COMM_SUCCESS:
#                print("Error on control")
#                quit()
#        time.sleep(0.01)
        
    
    def connect_mqtt(self):
        self.client = mqtt.Client()  
# MQTTの接続設定
        self.client.on_connect = self.on_connect         # 接続時のコールバック関数を登録
        self.client.on_disconnect = self.on_disconnect   # 切断時のコールバックを登録
        self.client.on_message = self.on_message         # メッセージ到着時のコールバック
        self.client.connect("sora2.uclab.jp", 1883, 60)
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
        dxl_comm_result, dxl_error = packet_handler.write2ByteTxRx(port_handler, did, ADDR_POSITION_P_GAIN, 200)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"ゲイン変更に失敗しました: {packet_handler.getTxRxResult(dxl_comm_result)}")
            quit()
        



#ファイルを１行づつ読む

set_position_and_torque()
pos_list = [0,0,0,0,0]
mq = DX_MQTT()
mq.setDXPorts(port_handler,packet_handler)

mq.connect_mqtt()


# ポートを閉じる
port_handler.closePort()
