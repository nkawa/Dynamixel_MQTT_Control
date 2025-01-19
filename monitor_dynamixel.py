import time

from vendor import pydxl
from vendor.pydxl  import XM430, SerialLink

link = SerialLink(
    device="COM11", baudrate=1_000_000, protocol_version=2.0
)

servo = XM430(identifier=11, serial_link=link)
servo.ping()
#servo.led = True

#servo.torque_enable = True
#servo.goal_position = 2000
#print(servo.goal_position)
#time.sleep(3)
##servo.goal_position = 1500
#time.sleep(3)
#servo.torque_enable = False

#link.close()