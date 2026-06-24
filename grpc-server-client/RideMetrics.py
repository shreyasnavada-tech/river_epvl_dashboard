import time
from enum import Enum

import can
import cantools
import pandas


class testStatusEnum(Enum):
    BUS_INITIALIZED = 0
    DBCLOADED = 1
    MAINFN = 2
    PROCESSING_LOGS = 3
    BUSCleanup = 4
    DEFAULT = 5
    PAUSED = 6
    RESUMED = 7
    COMPLETED = 8


testExecutionStatus = testStatusEnum.DEFAULT


# 1 send #2 rec #3 process the rows

################################################# CHARGING 1 ###################################################

############################################## ORD MIXED MODE ######################################################


def init_pcan():
    global testExecutionStatus
    bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=500000)
    print("PCAN Bus initialized successfully")
    testExecutionStatus = testStatusEnum.BUS_INITIALIZED
    return bus


def load_dbc(dbc_path: str):
    global testExecutionStatus
    db = cantools.database.load_file(dbc_path)
    testExecutionStatus = testStatusEnum.DBCLOADED
    return db


def load_log_file():
    log_file = open("can1_23_log.txt", "a")
    return log_file


def load_data_file():
    df = pandas.read_csv(r"Gen2_sample.csv")
    return df


def send_and_log_message(db, bus, log_file, message_id, data):
    encoded_data = db.encode_message(message_id, data)
    message = can.Message(
        arbitration_id=message_id, data=encoded_data, is_extended_id=False
    )
    bus.send(message)
    hex_data = " ".join(hex(byte) for byte in message.data)
    log_file.write(
        f"Sent message with ID: {hex(message.arbitration_id)}, Data: {hex_data}\n"
    )


def receive_and_log_message(db, bus, log_file):
    while True:
        message = bus.recv()
        hex_data = " ".join(hex(byte) for byte in message.data)
        log_file.write(
            f"Received message with ID: {hex(message.arbitration_id)}, Data: {hex_data}\n"
        )
        if message.arbitration_id == 0x611:
            decoded_message = db.decode_message(0x611, message.data)
            if "Vehicle_Range" in decoded_message:
                vehicle_range = decoded_message["Vehicle_Range"]
                print("Received Vehicle Range:", vehicle_range)


def process_rows(db, bus, log_file, df, start_index, end_index, event):
    for i in range(start_index, end_index):
        if event.is_set():
            print("Waiting for 60 seconds before checking event status")
            global testExecutionStatus
            testExecutionStatus = testStatusEnum.PAUSED
            time.sleep(60)
            continue
        print(i, start_index, end_index)
        row_values = df.iloc[i].to_dict()
        # Battery Status key brake ign kill
        send_and_log_message(
            db,
            bus,
            log_file,
            0x141,
            {
                "STA_BMS_Status": row_values["STA_BMS_Status"],
                "STA_BMS_FaultStatus": row_values["STA_BMS_FaultStatus"],
                "STA_BMS_VCU_AuthStatus": row_values["STA_BMS_VCU_AuthStatus"],
                "STA_DFET_Status": row_values["STA_DFET_Status"],
                "STA_Precharging_Status": row_values["STA_Precharging_Status"],
                "STA_KeyStatus_BMS": row_values["STA_KeyStatus_BMS"],
                "STA_PPINStatus_BMS": row_values["STA_PPINStatus_BMS"],
                "STA_CFET_Status": row_values["STA_CFET_Status"],
                "STA_Load_V_Present": row_values["STA_Load_V_Present"],
                "STA_BatteryFull": row_values["STA_BatteryFull"],
                "STA_OCD_Latch": row_values["STA_OCD_Latch"],
                "STA_OCC_Latch": row_values["STA_OCC_Latch"],
                "STA_CAN_BusOFF_Status": row_values["STA_CAN_BusOFF_Status"],
                "STA_AutoHyber_Timeout_status": row_values[
                    "STA_AutoHyber_Timeout_status"
                ],
                "STA_BMS_SCD": row_values["STA_BMS_SCD"],
                "STA_BMS_MCU_5V_PG": row_values["STA_BMS_MCU_5V_PG"],
                "STA_MCU_14V_PG": row_values["STA_MCU_14V_PG"],
                "STA_PFET_STS": row_values["STA_PFET_STS"],
            },
        )
        time.sleep(0.01)

        # print i;
        # Battery Parameters
        send_and_log_message(
            db,
            bus,
            log_file,
            0x14D,
            {
                "Battery_Current": row_values["Battery_Current"],
                "Battery_Voltage": row_values["Battery_Voltage"],
                "Battery_SOCRelative": row_values["Battery_SOCRelative"],
                "SOH": row_values["SOH"],
            },
        )
        time.sleep(0.01)

        # Motor Status 1
        send_and_log_message(
            db,
            bus,
            log_file,
            0x142,
            {
                "DriveMode_Ack": row_values["DriveMode_Ack"],
                "Power_Stage": row_values["Power_Stage"],
                "Kill_Switch": row_values["Kill_Switch"],
                "Direction": row_values["Direction"],
                "Throttle": row_values["Throttle"],
                "Speed": row_values["Speed"],
                "Drive_Manoeuvre": row_values["Drive_Manoeuvre"],
                "Deratings": row_values["Deratings"],
                "Throttle_takeover_status": row_values["Throttle_takeover_status"],
                "Rolling_counter_MCU": row_values["Rolling_counter_MCU"],
                "LimpHome_Ack": row_values["LimpHome_Ack"],
            },
        )
        time.sleep(0.01)

        # KF SOC
        send_and_log_message(
            db,
            bus,
            log_file,
            0x267,
            {
                "Kalman_Coulomb_SOC": row_values["Kalman_Coulomb_SOC"],
                "Kalman_Filter_SOC": row_values["Kalman_Filter_SOC"],
            },
        )
        time.sleep(0.01)

        kalman_filter_soc_value = row_values.get("Kalman_Filter_SOC", 0)
        print("Kalman_Filter_SOC value:", kalman_filter_soc_value)


def main(event):
    print("Main function started")
    global testExecutionStatus
    testExecutionStatus = testStatusEnum.MAINFN
    bus = init_pcan()
    log_file = load_log_file()
    df = load_data_file()
    dbc_path = r"/Users/nagendrar/Documents/river_dev/vehicle-automation/utility_scripts/grpc-server-client/DBC_Gen2_3_V1_7_09-02-2024_E_PVL.dbc"
    db = load_dbc(dbc_path)

    print("Started receiving and logging messages")

    batch_size = 7000
    testExecutionStatus = testStatusEnum.PROCESSING_LOGS
    for start_index in range(0, 100, batch_size):  # len(df)
        end_index = min(start_index + batch_size, 100)  # lendf
        process_rows(db, bus, log_file, df, start_index, end_index, event)

    print("ORD ride mode completed")
    testExecutionStatus = testStatusEnum.COMPLETED

    log_file.close()

    bus.shutdown()
    testExecutionStatus = testStatusEnum.BUSCleanup


if __name__ == "__main__":
    main("event")
