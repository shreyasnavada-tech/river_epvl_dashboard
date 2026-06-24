import os
import subprocess
import time
from datetime import datetime
from threading import Event

from PCANBasic import *

# Dummy val. Remove before running on windows
PCAN_USBBUS1 = ""
PCAN_BAUD_500K = ""


class CANLogger:
    def __init__(
        self, app_path, log_path, channel=PCAN_USBBUS1, baudrate=PCAN_BAUD_500K
    ):
        self.app_path = app_path
        self.log_path = log_path
        self.channel = channel
        self.baudrate = baudrate
        self.pcan = PCANBasic()
        self.stop_event = Event()
        self.log_started = False
        self.clean_exit = False

    def launch_application(self):
        try:
            subprocess.Popen([self.app_path])
            print(" Application started.")
        except FileNotFoundError:
            print(f" Could not find application at: {self.app_path}")
            exit(1)

    def initialize_pcan(self):
        print(" Waiting for pcan to initialize...")
        while True:
            result = self.pcan.Initialize(self.channel, self.baudrate)
            if result == PCAN_ERROR_OK:
                print(" PCAN initialized at 500 kbps.")
                break
            else:
                error_text = self.pcan.GetErrorText(result)[1].decode()
                print(f"Retrying PCAN Initialization: {error_text}")
                time.sleep(1)

    def read_can_messages(self):
        with open(self.log_path, "w") as log_file:
            print("📡 Listening for CAN messages...")
            while not self.stop_event.is_set():
                status, msg, timestamp = self.pcan.Read(self.channel)

                if status == PCAN_ERROR_OK:
                    can_id = msg.ID
                    now = datetime.now()
                    timestamp_str = now.strftime("%H:%M:%S:%f")[:-3]
                    formatted_id = f"0x{can_id:X}"
                    data = " ".join(f"{byte:02X}" for byte in msg.DATA[: msg.LEN])
                    log_line = f"{timestamp_str} CAN ID {formatted_id}  {data}"

                    if not self.log_started and can_id == 0x7C1:
                        self.log_started = True
                        print("Detected 0x7C1 — started logging.")
                        log_file.write(log_line + "\n")
                        log_file.flush()
                    elif self.log_started:
                        print(log_line)
                        log_file.write(log_line + "\n")
                        log_file.flush()

                        if (
                            can_id == 0x7F3
                            and msg.LEN >= 2
                            and msg.DATA[0] == 0x00
                            and msg.DATA[1] == 0xAA
                        ):
                            os.system(
                                f"taskkill /im {os.path.basename(self.app_path)} /f"
                            )
                            print(" Application closed due to 0x7F1 with 00 AA.")
                            self.clean_exit = True
                            self.stop_event.set()
                            break

                elif status != PCAN_ERROR_QRCVEMPTY:
                    error_text = self.pcan.GetErrorText(status)[1].decode()
                    print(f" Read Error: {error_text}")

                time.sleep(0.001)

    def send_can_message(self, can_id=0x7C1, data=(0x00, 0x00)):
        """Send a CAN message with the given ID and 2-byte data"""
        msg = TPCANMsg()
        msg.ID = can_id
        msg.LEN = 2
        msg.MSGTYPE = PCAN_MESSAGE_STANDARD
        msg.DATA = data + (0x00,) * (8 - len(data))  # Pad to 8 bytes

        result = self.pcan.Write(self.channel, msg)
        if result == PCAN_ERROR_OK:
            print(
                f"📤 Sent CAN message 0x{can_id:X} with data: {' '.join(f'{b:02X}' for b in data)}"
            )
        else:
            error_text = self.pcan.GetErrorText(result)[1].decode()
            print(f" Failed to send CAN message: {error_text}")

    def cleanup(self):
        self.pcan.Uninitialize(self.channel)
        print("PCAN disconnected.")
        if self.clean_exit:
            subprocess.Popen(["notepad.exe", self.log_path])

    def run(self):
        self.launch_application()
        self.initialize_pcan()
        self.read_can_messages()
        self.cleanup()


if __name__ == "__main__":
    app_path = r"C:\Users\PavanKalyan\Documents\Gen2_Boot_loader\R_BootLoader_G2.exe"
    log_path = r"C:\Users\PavanKalyan\Documents\can_log.txt"

    logger = CANLogger(app_path, log_path)

    try:
        logger.run()
    except KeyboardInterrupt:
        logger.stop_event.set()
        print("Interrupted by user. Exiting...")
