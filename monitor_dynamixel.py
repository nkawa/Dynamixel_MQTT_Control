import time

import serial.tools.list_ports

# dynamixel_sdk を使います
from dynamixel_sdk import PortHandler, PacketHandler
from dynamixel_sdk import COMM_SUCCESS, COMM_RX_TIMEOUT,COMM_TX_FAIL



# どうも  protocol version2 には簡単には対応できない。（CRCなどもあるし）
#from vendor import pydxl
#from vendor.pydxl  import XM430, SerialLink


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
# How to automatically find Com port?


com_port = list_com_ports()


port_handler = PortHandler(com_port)
packet_handler = PacketHandler(2.0)

if port_handler.openPort():
    print("Opne port",com_port)
    if port_handler.setBaudRate(1_000_000):
        print("Set Baud")
else:
    print("Cant open!")
    quit()
    
DXL_ID = 11

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


ADDR_PRESENT_POSITION = 132  # 現在の位置のアドレス
LENGTH_PRESENT_POSITION = 4  # データ長（バイト）

while True:
    dxl_position, dxl_comm_result, dxl_error = packet_handler.read4ByteTxRx(port_handler, DXL_ID, ADDR_PRESENT_POSITION)

    if dxl_comm_result == COMM_SUCCESS:
        dxl_angle = (dxl_position / 4095.0) * 360.0
        print(f"現在の位置（生データ）: {dxl_position}, 角度：{dxl_angle}")
        
    else:
        quit()


# ポートを閉じる
port_handler.closePort()
