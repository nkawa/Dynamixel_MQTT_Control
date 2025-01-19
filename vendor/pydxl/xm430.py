"""MX-28 servo usage."""
from .dynamixel import Dynamixel
from .register import Register


class XM430(Dynamixel):
    """Class for MX-28 servo."""

    # https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/
    # xm-430/#control-table-of-eeprom-area
    model_number = Register(address=0, size=2)
    model_information = Register(address=2, size=4)
    firmware_version = Register(address=6)
    id_ = Register(address=7, write=True)
    baud_rate = Register(address=8, write=True)
    return_delay_time = Register(address=9, write=True)
    drive_mode = Register(address=10, write=True)
    operating_mode = Register(address=11, write=True)
    secondary_id = Register(address=12, write=True)
    protocol_type = Register(address=13, write=True)
    homing_offset = Register(address=20, write=True, size=4)
    moving_threshold = Register(address=24, write=True, size=4)
    temperature_limit = Register(address=31, write=True)
    max_voltage_limit = Register(address=32, write=True, size=2)
    min_voltage_limit = Register(address=34, write=True, size=2)
    pwm_limit = Register(address=36, write=True, size=2)
    current_limit = Register(address=38, write=True, size=2)
    velocity_limit = Register(address=40, write=True, size=4)
    max_position_limit = Register(address=48, write=True, size=4)
    min_position_limit = Register(address=52, write=True, size=4)
    startup_configuration = Register(address=60, write=True)
    shutdown = Register(address=63, write=True)

    # https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/
    # xm-430/#control-table-of-ram-area
    torque_enable = Register(address=64, write=True)
    led = Register(address=65, write=True)
    status_return_level = Register(address=68, write=True)
    registered_instruction = Register(address=69, write=True)
    hardware_error_status = Register(address=70)
    velocity_i_gain = Register(address=76, write=True, size=2)
    velocity_p_gain = Register(address=78, write=True, size=2)
    position_d_gain = Register(address=80, write=True, size=2)
    position_i_gain = Register(address=82, write=True, size=2)
    position_p_gain = Register(address=84, write=True, size=2)
    feedforward_2nd_gain = Register(address=88, write=True, size=2)
    feedforward_1st_gain = Register(address=90, write=True, size=2)
    bus_watchdog = Register(address=98, write=True)
    goal_pwm = Register(address=100, write=True, size=2)
    goal_current = Register(address=102, write=True, size=2)
    goal_velocity = Register(address=104, write=True, size=4)
    profile_acceleration = Register(address=108, write=True, size=4)
    profile_velocity = Register(address=112, write=True, size=4)   
    goal_position = Register(address=116, write=True, size=4)
    real_time_tick = Register(address=120, size=2)
    moving = Register(address=122)
    moving_status = Register(address=123)
    present_pwm = Register(address=124, size=2)
    present_current = Register(address=126, size=2)
    present_velocity = Register(address=128, size=4)
    present_position = Register(address=132, size=4)
    velocity_trajectory = Register(address=136, size=4)
    position_trajectory = Register(address=140, size=4)
    present_input_voltage = Register(address=144, size=2)
    present_temperature = Register(address=146)
    backup_ready = Register(address=147)
    indirect_address_1 = Register(address=168, size=2)
    indirect_address_2 = Register(address=170, size=2)
    indirect_address_3 = Register(address=172, size=2)

    indirect_data_1 = Register(address=224)
    indirect_data_2 = Register(address=225)
    indirect_data_3 = Register(address=226)
