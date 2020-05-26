import sys
import logging
sys.path.append('..')

from VESC_UART import VescUart

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)

    vesc = VescUart('/dev/ttyUSB0')

    while True:
        data = vesc.getDataValues()
        print("{}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}".format(
                data.timestamp,
                data.temperatureFet_C,
                data.averageMotorCurrent,
                data.averageInputCurrent,
                data.motorDutyCycle,
                data.motorRPM,
                data.inputVoltage))
