from typing import Any, Dict, List, Optional

from cantools import database
from cantools.database.can.message import Message
from cantools.database.can.signal import Signal


class DBCParser:
    def __init__(self, dbc_name):
        """This class is a wrapper around cantools dbc to simplify encoding and decoding"""
        self.db = database.load_file(dbc_name)
        self.dbc_file_path = dbc_name

    def encode_message(self, signal_name: str | int, payload: dict) -> bytearray:
        """
        This method encodes the given message into bytearray format

        Args:
            signal_name: str|int = This can be either the name of the signal or the ID of the signal in DECIMAL not HEX
            payload: dict = Dict of keys as signal names and the corresponding values

            Ex - encode_message('VehicleCurrentLimits', {'Discharge_Limit_VCU': 96, 'Regen_Limit': 1280})
            or encode_message(326, {'Discharge_Limit_VCU': 96, 'Regen_Limit': 1280})

        Returns:
            bytearray of the payload: b'\x01\x45\x23\x00\x11'
        """
        return self.db.encode_message(signal_name, payload)

    def decode_message(
        self,
        signal_name: int | str,
        response: List | bytearray,
        allow_truncated: bool = True,
        enum_strings: bool = False,
    ) -> Dict:
        """
        This method decodes the given message into human readable format i.e a dict

        Args:
            signal_name: str|int = This can be either the name of the signal or the ID of the signal in DECIMAL not HEX
            response: List | bytearray = Data as a list or a bytearray

            Ex - decode_message('VehicleCurrentLimits', b'\x01\x45\x23\x00\x11')
            or decode_message(326, b'\x01\x45\x23\x00\x11')
            or decode_message(326, [96,00,40,18,00,00, 00, 00])

            allow_truncated: bool = Allows parsing CAN data without 8 bytes - [96,00,40,18,00]
            enum_strings: bool = False - If set to True, values will be strings instead of raw values Ex: Kill SWITCH SRO for value 93 in Error_code_0
                                         If set to False, values will be raw values. Ex: 93 in Error_code_0

        Returns:
            Dict of the parsed data - {'Discharge_Limit_VCU': 96, 'Regen_Limit': 1280}
        """
        if isinstance(response, List):
            response = bytearray(response)
        return self.db.decode_message(
            signal_name,
            response,
            allow_truncated=allow_truncated,
            decode_choices=enum_strings,
        )

    def get_message_by_name(self, message_name: str) -> Message:
        """
        Find the message object for given frame id

        Args:
            message_name: Name of the signal Ex - Motor_status

        Returns:
            Message object - get_message_by_name('MotorStatus_2')
                return value = ('MotorStatus_2', 0x143, False, 8, None)
        """
        return self.db.get_message_by_name(message_name)

    def get_signal_tree(self, message_name: str) -> List:
        """
        This method returns all the signal in the given frame as a list

        Args:
            message_name: Name of the signal Ex - Motor_status

        Returns:
            A list of all the signals in a given frame - get_signal_tree('Battery_Deration_Model_Output4')
            ['Heat_Stored_pcm', 'Htc_casing_ambient', 'RMS_Cell_Heat_Gen_j']
        """
        sig_val = self.get_message_by_name(message_name)
        return sig_val.signal_tree

    def get_all_messages(self) -> List:
        """Get all messages in the DBC file"""
        return self.db.messages

    def get_messages_by_id(self, can_id: Any) -> Message:
        """
        The can id values should be hex values and not strings - 0x27b
        This method returns a message object. To obtain the following parameters, use the methods.
        Get CAN ID  = data.frame_id
        Name = data.name
        length = data.length
        signal_list = data.signal_tree
        """
        data = self.db.get_message_by_frame_id(can_id)
        return data

    def get_signals_for_the_message(self, message: Message) -> List:
        """
        This method returns the list of signals.
        ['ECU_ID_HW_DIS', 'Year_HW_DIS', 'Month_DIS', 'HW_MSB_DIS', 'HW_LSB_DIS', 'HW_DIS', 'SW_SubVersion_HW_DIS', 'Vehicle_Batch_HW_DIS']
        """
        return message.signal_tree

    def get_signal_data(self, message: Message, signal_name) -> Optional[List[Signal]]:
        """
        This method loops through a list of signal and returns the required signal object
        Methods supported -
        Max value = signal.maximum
        Min value = signal.minimum
        length = signal.length
        start_byte = signal.start
        end_byte = start_byte + length
        unit = signal.unit
        scale = signal.scale
        offset = signal.offset
        """
        for signal in message.signals:
            if signal.name == signal_name:
                return signal

    def get_all_can_id_list(self) -> List:
        """
        Returns the list of all CAN IDs of the DBC in the form of int values
        """
        all_can_id = []
        for msg in self.get_all_messages():
            all_can_id.append(msg.frame_id)
        return all_can_id


if __name__ == "__main__":
    parse = DBCParser(
        r"/Users/nagendrar/Documents/river_dev/vehicle-automation/utility_scripts/DBC_Gen2_3_V1_7_09-02-2025_E_PVL.dbc"
    )
    # print(parse.get_message_by_name('MotorStatus_2'))
    # print(parse.get_signal_tree('Battery_Deration_Model_Output4'))
    print(parse.decode_message("VehicleCurrentLimits", [96, 00, 40, 10]))
    print(parse.decode_message(326, [96, 00, 40, 18, 00, 00, 00, 00]))
    print(parse.get_all_can_id_list())
