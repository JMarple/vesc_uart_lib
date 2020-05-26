import struct
import time
class VESCDataValues:

    def __init__(self, payload, mask):
        self.temperatureFet_C = None
        self.temperatureMotor_C = None
        self.asverageMotorCurrent = None
        self.averageInputCurrent = None
        self.averageMotorID = None
        self.averageMotorIQ = None
        self.motorDutyCycle = None
        self.motorRPM = None
        self.inputVoltage = None
        self.inputAmpHours = None
        self.inputAmpHoursCharged = None
        self.inputWattHours = None
        self.inputWattHoursCharged = None
        self.motorTachometer = None
        self.motorTachometerAbsolute = None
        self.VESCFault = None
        self.PIDPosition = None
        self.controllerID = None
        self.temperature_Mosfet1 = None
        self.temperature_Mosfet2 = None
        self.temperature_Mosfet3 = None
        self.averageMotorVD = None
        self.averageMotorVQ = None

        self.timestamp = time.time() * 1000

        data = self.unpack(payload, mask)
        self.parse(data, mask)

    def unpack(self, payload, mask):
        # If everything is enabled and unmasked, this is the ideal
        # packet.  This is always sent with a normal COMM_GET_VALUES packet.
        # c = 8 bit char
        # h = 16 bit signed integer
        # i = 32 bit signed integer
        ideal_unpack = 'hhiiiihihiiiiiicichhhii'

        masked_unpack = '>'

        for i in range(0, len(ideal_unpack)):
            if (mask & (0x01 << i)) > 0:
                masked_unpack += ideal_unpack[i]

        return struct.unpack(masked_unpack, payload)

    def parse(self, data, mask):
        mask_counter = 0
        for i in range(0, len(data)):

            while (mask & (0x01 << mask_counter)) == 0:
                mask_counter = mask_counter + 1

            self.add_data(data[i], mask_counter)

            mask_counter = mask_counter + 1

    def add_data(self, data, index):
        if (index == 0):    self.temperatureFet_C = int(data) / 10.0
        elif (index == 1):  self.temperatureMotor_C = int(data) / 10.0
        elif (index == 2):  self.averageMotorCurrent = int(data) / 100.0
        elif (index == 3):  self.averageInputCurrent = int(data) / 100.0
        elif (index == 4):  self.averageMotorID = int(data) / 100.0
        elif (index == 5):  self.averageMotorIQ = int(data) / 100.0
        elif (index == 6):  self.motorDutyCycle = int(data) / 1000.0
        elif (index == 7):  self.motorRPM = int(data)
        elif (index == 8):  self.inputVoltage = int(data) / 10.0
        elif (index == 9):  self.inputAmpHours = int(data) / 10000.0
        elif (index == 10): self.inputAmpHoursCharged = int(data) / 10000.0
        elif (index == 11): self.inputWattHours = int(data) / 10000.0
        elif (index == 12): self.inputWattHoursCharged = int(data) / 10000.0
        elif (index == 13): self.motorTachometer = int(data)
        elif (index == 14): self.motorTachometerAbsolute = int(data)
        elif (index == 15): self.VESCFault = bytes(data)
        elif (index == 16): self.PIDPosition = int(data) / 1000000.0
        elif (index == 17): self.controllerID = bytes(data)
        elif (index == 18): self.temperature_Mosfet1 = int(data) / 10.0
        elif (index == 19): self.temperature_Mosfet2 = int(data) / 10.0
        elif (index == 20): self.temperature_Mosfet3 = int(data) / 10.0
        elif (index == 21): self.averageMotorVD = int(data) / 1000.0
        elif (index == 22): self.averageMotorVQ = int(data) / 1000.0
        else: raise Exceptoin("Index is above 21, no data to fill!")

    def __str__(self):
        output = "Parsed Vesc Data:\n"

        output += "Timestamp (ms): {}\n".format(self.timestamp)
        if self.temperatureFet_C is not None: output += "TemperatureFet_C = {}\n".format(self.temperatureFet_C)
        if self.temperatureMotor_C is not None: output += "TemperatureMotor_C = {}\n".format(self.temperatureMotor_C)
        if self.averageMotorCurrent is not None: output += "AverageMotorCurrent = {}\n".format(self.averageMotorCurrent)
        if self.averageInputCurrent is not None: output += "AverageInputCurrent = {}\n".format(self.averageInputCurrent)
        if self.averageMotorID is not None: output += "AverageMotorID = {}\n".format(self.averageMotorID)
        if self.averageMotorIQ is not None: output += "AverageMotorIQ = {}\n".format(self.averageMotorIQ)
        if self.motorDutyCycle is not None: output += "MotorDutyCycle = {}\n".format(self.motorDutyCycle)
        if self.motorRPM is not None: output += "MotorRPM = {}\n".format(self.motorRPM)
        if self.inputVoltage is not None: output += "InputVoltage = {}\n".format(self.inputVoltage)
        if self.inputAmpHours is not None: output += "InputAmpHours = {}\n".format(self.inputAmpHours)
        if self.inputAmpHoursCharged is not None: output += "InputAmpHoursCharged = {}\n".format(self.inputAmpHoursCharged)
        if self.inputWattHours is not None: output += "InputWattHours = {}\n".format(self.inputWattHours)
        if self.inputWattHoursCharged is not None: output += "InputWattHoursCharged = {}\n".format(self.inputWattHoursCharged)
        if self.motorTachometer is not None: output += "MotorTachometer = {}\n".format(self.motorTachometer)
        if self.motorTachometerAbsolute is not None: output += "MotorTachometerAbsolute = {}\n".format(self.motorTachometerAbsolute)
        if self.VESCFault is not None: output += "VESCFault = {}\n".format(self.VESCFault)
        if self.PIDPosition is not None: output += "PIDPosition = {}\n".format(self.PIDPosition)
        if self.controllerID is not None: output += "ControllerID = {}\n".format(self.controllerID)
        if self.temperature_Mosfet1 is not None: output += "Temperature_Mosfet1 = {}\n".format(self.temperature_Mosfet1)
        if self.temperature_Mosfet2 is not None: output += "Temperature_Mosfet2 = {}\n".format(self.temperature_Mosfet2)
        if self.temperature_Mosfet3 is not None: output += "Temperature_Mosfet3 = {}\n".format(self.temperature_Mosfet3)
        if self.averageMotorVD is not None: output += "PIDPosition = {}\n".format(self.averageMotorVD)
        if self.averageMotorVQ is not None: output += "AverageMotorVQ = {}\n".format(self.averageMotorVQ)

        return output
