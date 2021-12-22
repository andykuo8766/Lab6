from bluedot.btcomm import BluetoothClient

import RPi.GPIO as GPIO
from time import sleep

import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

GPIO.setmode(GPIO.BCM)
GPIO.setup(2,GPIO.OUT)
GPIO.setup(3,GPIO.OUT)

GPIO.output(2, GPIO.LOW)
GPIO.output(3, GPIO.LOW)
def pzem():
    sensor = serial.Serial(
    #                       port='/dev/PZEM_sensor',
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

    pzem_data = 'Voltage [V]: '+str(voltage)+'\nCurrent [A]: '+str(current)+'\nPower [W]: '+str(power)+'\nEnergy [Wh]: '+str(energy)+'\nfrequency [Hz]: '+str(frequency)+'\nPower factor []: '+str(powerFactor)+'\nAlarm : '+str(alarm)

    try:
        master.close()
        if sensor.is_open:
            sensor.close()
    except:
        pass
    return pzem_data

def data_received(data):
    if data == 'open pzem':
        print('recieved control message from Server')
        GPIO.output(2, GPIO.HIGH)
        GPIO.output(3, GPIO.HIGH)
    else: 
        print(data)

c = BluetoothClient("B8:27:EB:DC:1F:E6", data_received)

c.send("start")
sleep(1)
pzem_data = pzem()
print('sending PZEM004T datas to Server...')
c.send(pzem_data)
print('task completed')


while (True):
    pass


