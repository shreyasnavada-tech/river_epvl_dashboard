import time
from threading import Thread

import can
from dbc_parser_pt import DBCParser
from excel_parser import ExcelParse

# Virtual CAN reciever for loop test
# send a message
# message = can.Message(arbitration_id=123, is_extended_id=False,
#                         data=[0x11, 0x22, 0x33])
# # bus.send(message, timeout=0.2)

# bus1 = can.interface.Bus('test', interface='virtual')
# bus2 = can.interface.Bus('test', interface='virtual')

sender_bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=500000)
sender_msg_list = {
    "MotorStatus_1": 0x142,
    "MotorStatus_2": 0x143,
    "MotorStatus_3": 0x144,
    "Motorstatus_4": 0x145,
}

parse = DBCParser(r"C:\Users\Nagendra R\Downloads\DBC_Gen2_New CAN IDs V1.2.dbc")


def send_recv_can_msgs(file, message):

    xl = ExcelParse(file, message)
    sig_tree = parse.get_signal_tree(message)

    dumd = [xl.fetch_coloumn_values(signal, True) for signal in sig_tree]

    tp_val = list(map(list, zip(*dumd)))

    for val in tp_val:
        payload = {sig_tree[ind]: data for ind, data in enumerate(val)}
        pl_load = parse.encode_message(message, payload)
        s_msg = can.Message(
            arbitration_id=sender_msg_list[message], data=pl_load, is_extended_id=False
        )
        sender_bus.send(s_msg)

        # Setting sender frequency to 10ms
        time.sleep(0.0083)


t1 = Thread(target=send_recv_can_msgs, args=("throttle_sml.xlsx", "MotorStatus_1"))
t2 = Thread(target=send_recv_can_msgs, args=("throttle_sml.xlsx", "MotorStatus_2"))
t3 = Thread(target=send_recv_can_msgs, args=("throttle_sml.xlsx", "MotorStatus_3"))
t4 = Thread(target=send_recv_can_msgs, args=("throttle_sml.xlsx", "Motorstatus_4"))

t1.start()
t2.start()
t3.start()
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()

sender_bus.shutdown()
