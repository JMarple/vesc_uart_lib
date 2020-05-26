Python3 library for communicating with a vesc over USB or UART. 

`vesc = VescUart('/dev/ttyUSB0`)
 
vesc.getFirmwareVersion()
data = vesc.getDataValues()
print(data)`
