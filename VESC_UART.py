import serial
import crcmod
import time
import logging
import struct

from VESC_DataValues import VESCDataValues

class VescUart:

    COMM_FW_VERSION = 0
    COMM_JUMP_TO_BOOTLOADER = 1
    COMM_ERASE_NEW_APP = 2
    COMM_WRITE_NEW_APP_DATA = 3
    COMM_GET_VALUES = 4
    COMM_SET_DUTY = 5
    COMM_SET_CURRENT = 6
    COMM_SET_CURRENT_BRAKE = 7
    COMM_SET_RPM = 8
    COMM_SET_POS = 9
    COMM_SET_HANDBRAKE = 10
    COMM_SET_DETECT = 11
    COMM_SET_SERVO_POS = 12
    COMM_SET_MCCONF = 13
    COMM_GET_MCCONF = 14
    COMM_GET_MCCONF_DEFAULT = 15
    COMM_SET_APPCONF = 16
    COMM_GET_APPCONF = 17
    COMM_GET_APPCONF_DEFAULT = 18
    COMM_SAMPLE_PRINT = 19
    COMM_TERMINAL_CMD = 20
    COMM_PRINT = 21
    COMM_ROTOR_POSITION = 22
    COMM_EXPERIMENT_SAMPLE = 23
    COMM_DETECT_MOTOR_PARAM = 24
    COMM_DETECT_MOTOR_R_L = 25
    COMM_DETECT_MOTOR_FLUX_LINKAGE = 26
    COMM_DETECT_ENCODER = 27
    COMM_DETECT_HALL_FOC = 28
    COMM_REBOOT = 29
    COMM_ALIVE = 30
    COMM_GET_DECODED_PPM = 31
    COMM_GET_DECODED_ADC = 32
    COMM_GET_DECODED_CHUK = 33
    COMM_FORWARD_CAN = 34
    COMM_SET_CHUCK_DATA = 35
    COMM_CUSTOM_APP_DATA = 36
    COMM_NRF_START_PAIRING = 37
    COMM_GPD_SET_FSW = 38
    COMM_GPD_BUFFER_NOTIFY = 39
    COMM_GPD_BUFFER_SIZE_LEFT = 40
    COMM_GPD_FILL_BUFFER = 41
    COMM_GPD_OUTPUT_SAMPLE = 42
    COMM_GPD_SET_MODE = 43
    COMM_GPD_FILL_BUFFER_INT8 = 44
    COMM_GPD_FILL_BUFFER_INT16 = 45
    COMM_GPD_SET_BUFFER_INT_SCALE = 46
    COMM_GET_VALUES_SETUP = 47
    COMM_SET_MCCONF_TEMP = 48
    COMM_SET_MCCONF_TEMP_SETUP = 49
    COMM_GET_VALUES_SELECTIVE = 50
    COMM_GET_VALUES_SETUP_SELECTIVE = 51
    COMM_EXT_NRF_PRESENT = 52
    COMM_EXT_NRF_ESB_SET_CH_ADDR = 53
    COMM_EXT_NRF_ESB_SEND_DATA = 54
    COMM_EXT_NRF_ESB_RX_DATA = 55
    COMM_EXT_NRF_SET_ENABLED = 56
    COMM_DETECT_MOTOR_FLUX_LINKAGE_OPENLOOP = 57
    COMM_DETECT_APPLY_ALL_FOC = 58
    COMM_JUMP_TO_BOOTLOADER_ALL_CAN = 59
    COMM_ERASE_NEW_APP_ALL_CAN = 60
    COMM_WRITE_NEW_APP_DATA_ALL_CAN = 61
    COMM_PING_CAN = 62
    COMM_APP_DISABLE_OUTPUT = 63
    COMM_TERMINAL_CMD_SYNC = 64
    COMM_GET_IMU_DATA = 65
    COMM_BM_CONNECT = 66
    COMM_BM_ERASE_FLASH_ALL = 67
    COMM_BM_WRITE_FLASH = 68
    COMM_BM_REBOOT = 69
    COMM_BM_DISCONNECT = 70
    COMM_BM_MAP_PINS_DEFAULT = 71
    COMM_BM_MAP_PINS_NRF5X = 72
    COMM_ERASE_BOOTLOADER = 73
    COMM_ERASE_BOOTLOADER_ALL_CAN = 74
    COMM_PLOT_INIT = 75
    COMM_PLOT_DATA = 76
    COMM_PLOT_ADD_GRAPH = 77
    COMM_PLOT_SET_GRAPH = 78
    COMM_GET_DECODED_BALANCE = 79
    COMM_BM_MEM_READ = 80
    COMM_WRITE_NEW_APP_DATA_LZO = 81
    COMM_WRITE_NEW_APP_DATA_ALL_CAN_LZO = 82
    COMM_BM_WRITE_FLASH_LZO = 83
    COMM_SET_CURRENT_REL = 84
    COMM_CAN_FWD_FRAME = 85
    COMM_SET_BATTERY_CUT = 86
    COMM_SET_BLE_NAME = 87
    COMM_SET_BLE_PIN = 88
    COMM_SET_CAN_MODE = 89
    COMM_GET_IMU_CALIBRATION = 90

    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.crc16 = crcmod.mkCrcFun(0x11021, 0x0000, False, 0x0000)

    def __send_payload(self, payload):

        crc_payload = self.crc16(payload)

        messageSend = bytearray()

        if len(payload) <= 256:
            messageSend.append(2)
            messageSend.append(len(payload))
        else:
            messageSend.append(3)
            messageSend.append((len(payload) >> 8) & 0xFF)
            messageSend.append(len(payload) & 0xFF)

        for i in range(0, len(payload)):
            messageSend.append(payload[i])

        messageSend.append((crc_payload >> 8) & 0xFF)
        messageSend.append(crc_payload & 0xFF)
        messageSend.append(3)

        self.ser.write(messageSend)

        return messageSend

    def __receiveUartMessage(self):

        payload = bytearray()
        message_length = 256
        payload_length = 0

        # TODO: Timeout
        while True:
            if self.ser.inWaiting() > 0:
                payload += self.ser.read(1)

                if len(payload) == 2:
                    if payload[0] == 2:
                        message_length = int(payload[1]) + 5
                    else:
                        raise Exception("Unsuported payload length")

                if len(payload) == message_length:
                    if payload[len(payload)-1] == 3:
                        calc_crc = self.crc16(payload[2:-3])
                        comm_crc = struct.unpack('>H', payload[-3:-1])[0]

                        if calc_crc != comm_crc:
                            raise Exception("CRC did not match! 0x%X != 0x%X" % (calc_crc, comm_crc))

                        return payload[2:-3]
                    else:
                        raise Exception("Last byte is not 3")

    def __processReadpacket(self, payload):
        if (payload[0] == VescUart.COMM_GET_VALUES):
            mask = 0xFFFFFFFF
            return VESCDataValues(payload[1:], mask)

        elif (payload[0] == VescUart.COMM_GET_VALUES_SELECTIVE):
            mask = struct.unpack('>I', payload[1:5])
            return VESCDataValues(payload[5:], mask[0])

        elif (payload[0] == VescUart.COMM_FW_VERSION):
            data = struct.unpack('>ccc', payload[1:4])
            return data

        return None

    def getDataValues(self):
        message = bytearray([VescUart.COMM_GET_VALUES])

        self.__send_payload(message)
        payload = self.__receiveUartMessage()
        return self.__processReadpacket(payload)

    def getFirmwareVersion(self):
        message = bytearray([VescUart.COMM_FW_VERSION])

        self.__send_payload(message)
        payload = self.__receiveUartMessage()
        return self.__processReadpacket(payload)

    def getSelectiveDataValues(self, mask):
        message = struct.pack('>bI', VescUart.COMM_GET_VALUES_SELECTIVE, mask)
        self.__send_payload(message)
        payload = self.__receiveUartMessage()
        return self.__processReadpacket(payload)

    def setDutyCycle(self, dutycycle):
        message = struct.pack('>bI', VescUart.COMM_SET_DUTY, int(dutycycle*1000))
        self.__send_payload(message)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)

    vesc = VescUart('/dev/ttyUSB0')


    while True:
        data = vesc.getFirmwareVersion()
        #data = vesc.getDataValues()
        #print(data.TemperatureFet_C)
        #data = vesc.getSelectiveDataValues(mask=0b00001111)
        print(data)
