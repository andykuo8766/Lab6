# Reading PZEM-004t power sensor (new version v3.0) through Modbus-RTU protocol over TTL UART
# Run as:
# python3 pzem_004t.py

# To install dependencies: 
# pip install modbus-tk
# pip install pyserial

import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
from bluedot.btcomm import BluetoothClient
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)
GPIO.setup(2,GPIO.OUT)
GPIO.output(2, GPIO.LOW)

def data_received(data):
    print(data)
c=BluetoothClient("Pi7", data_receive)


while True:
    GPIO.output(GPIO.HIGH)
# Connect to the sensor
    sensor = serial.Serial(
#                       port='/dev/PZEM_sensor',modbus_rtu.RtuMaster(sensor)
           # master.set_timeout(2.0)

            port='/dev/ttyUSB0',
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=1,
            xonxoff=0
             )

    master = modbus_rtu.RtuMaster(sensor)
    master.set_timeout(2.0)
    master.set_verbose(True)

    data = master.execute(1, cst.READ_INPUT_REGISTERS, 0, 10)

    voltage = data[0] / 10.0 # [V]
    current = (data[1] + (data[2] << 16)) / 1000.0 # [A]
    power = (data[3] + (data[4] << 16)) / 10.0 # [W]
    energy = data[5] + (data[6] << 16) # [Wh]
    frequency = data[7] / 10.0 # [Hz]
    powerFactor = data[8] / 100.0
    alarm = data[9] # 0 = no alarm

    c.send('電流 [安培]: ', current)
    c.send('電壓 [伏特]: ', voltage)
    c.send('功率 [瓦]: ', power) # active power (V * I * power factor)
    c.send('能量 [瓦時]: ', energy)
    c.send('頻率 [赫茲]: ', frequency)
    c.send('功率因子 : ', powerFactor)
    c.send('警示 : ', alarm)
    
    master.close()
    if sensor.is_open:
        sensor.close()
while True:
    pass
