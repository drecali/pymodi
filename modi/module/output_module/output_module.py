import time

from enum import IntEnum
from typing import Tuple, List
from modi.module.module import Module
from modi.util.msgutil import parse_message, parse_data


class OutputModule(Module):
    def __init__(self, id_, uuid, msg_send_q):
        super().__init__(id_, uuid, msg_send_q)

    class PropertyDataType(IntEnum):
        INT = 0
        FLOAT = 1
        STRING = 2
        RAW = 3
        DISPLAY_VAR = 4

    def __parse_set_message(self, destination_id: int,
                            property_type: IntEnum,
                            property_values: Tuple,
                            property_data_type: IntEnum) -> List[str]:
        """Generate set_property json serialized message

        :param destination_id: Id of the destination module
        :type destination_id: int
        :param property_type: Property Type
        :type property_type: IntEnum
        :param property_values: Property values
        :type property_values: Tuple
        :param property_data_type: Property Data Type
        :type property_data_type: IntEnum
        :return: List of json messages
        :rtype: List[str]
        """
        data_list = []
        if property_data_type == self.PropertyDataType.INT:
            data_list.append(parse_data(property_values, 'int'))
        elif property_data_type == self.PropertyDataType.FLOAT:
            data_list.append(parse_data(property_values, 'float'))
        elif property_data_type == self.PropertyDataType.STRING:
            for i in range(0, len(property_values), 8):
                chunk = str(property_values)[i:i + 8]
                data_list.append(parse_data(chunk, 'string'))
        elif property_data_type == self.PropertyDataType.RAW:
            data_list.append(parse_data(property_values, 'raw'))
        elif property_data_type == self.PropertyDataType.DISPLAY_VAR:
            data_list.append(parse_data(property_values, 'display_var'))
        else:
            raise RuntimeError("Not supported property data type.")

        messages = []
        for data in data_list:
            messages.append(
                parse_message(0x04, property_type, destination_id, data)
            )
        return messages

    def _set_property(self, destination_id: int,
                      property_type: IntEnum, property_values: Tuple,
                      property_data_type: IntEnum
                      = PropertyDataType.INT) -> None:
        """Send the message of set_property command to the module

        :param destination_id: Id of the destination module
        :type destination_id: int
        :param property_type: Property Type
        :type property_type: IntEnum
        :param property_values: Property Values
        :type property_values: Tuple
        :param property_data_type: Property Data Type
        :type property_data_type: IntEnum
        :return: None
        """
        messages = self.__parse_set_message(
            destination_id,
            property_type,
            property_values,
            property_data_type)

        for message in messages:
            self._msg_send_q.put(message)
        time.sleep(0.001)

    @staticmethod
    def _validate_property(nb_values: int, value_range: Tuple = None):
        def check_value(setter):
            def set_property(self, value):
                if nb_values > 1 and isinstance(value, int):
                    raise ValueError(f"{setter.__name__} needs {nb_values} "
                                     f"values")
                elif value_range and nb_values == 1 and not (
                        value_range[1] >= value >= value_range[0]):
                    raise ValueError(f"{setter.__name__} should be in range "
                                     f"{value_range[0]}~{value_range[1]}")
                elif value_range and nb_values > 1:
                    for val in value:
                        if not (value_range[1] >= val >= value_range[0]):
                            raise ValueError(f"{setter.__name__} "
                                             f"should be in range"
                                             f" {value_range[0]}~"
                                             f"{value_range[1]}")
                setter(self, value)

            return set_property

        return check_value
