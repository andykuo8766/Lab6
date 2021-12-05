import serial
import modbus_tk.defines as cst
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time


from bluedot.btcomm import BluetoothClient
from modbus_tk import modbus_rtu


def gpio_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_A,GPIO.OUT)
    GPIO.setup(pin_B,GPIO.OUT)

    GPIO.output(pin_A, GPIO.LOW)
    GPIO.output(pin_B, GPIO.LOW)

def pzem_init():
    sensor = serial.Serial(
                        #port='/dev/PZEM_sensor',
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
    return master, sensor

def read_pzem(master):
    data = master.execute(1, cst.READ_INPUT_REGISTERS, 0, 10)

    voltage = data[0] / 10.0 # [V]
    current = (data[1] + (data[2] << 16)) / 1000.0 # [A]
    power = (data[3] + (data[4] << 16)) / 10.0 # [W]
    energy = data[5] + (data[6] << 16) # [Wh]
    frequency = data[7] / 10.0 # [Hz]
    powerFactor = data[8] / 100.0
    alarm = data[9] # 0 = no alarm
    
    msg = ''

    # msg += 'Voltage [V]: ' + str(voltage) + '\n'
    # msg += 'Current [A]: ' + str(current) + '\n'
    # msg += 'Power [W]: ' + str(power) + '\n'  # active power (V * I * power factor)
    # msg += 'Energy [Wh]: ' + str(energy) + '\n'
    # msg += 'Frequency [Hz]: ' + str(frequency) + '\n'
    # msg += 'Power factor []: '+ str(powerFactor) + '\n'
    # msg += 'Alarm : ' + str(alarm) + '\n'

    msg += f"{current}安培和{power}瓦"

    return msg

pin_A = 14
pin_B = 15

m, s = pzem_init()
gpio_init()

def data_received(data):
    msg = ''
    print()
    print(f'key : {data}')
    if data == '01':
        print('close left')
        print('open right')
        GPIO.output(pin_A, GPIO.LOW)
        GPIO.output(pin_B, GPIO.HIGH)
    elif data == '10':
        print('open left')
        print('close right')
        GPIO.output(pin_A, GPIO.HIGH)
        GPIO.output(pin_B, GPIO.LOW)
    elif data == '11':
        print('open left')
        print('open right')
        GPIO.output(pin_A, GPIO.HIGH)
        GPIO.output(pin_B, GPIO.HIGH)
    elif data == '00':
        print('close left')
        print('close right')
        GPIO.output(pin_A, GPIO.LOW)
        GPIO.output(pin_B, GPIO.LOW)
    else:
        print('error key')
        msg = 'sever get error key'
        c.send(msg)
        return
    time.sleep(3)
    msg = read_pzem(m)
    c.send(msg)

c = BluetoothClient("raspberrypi", data_received)


try:
    print('press Ctrl-C to stop')
    while (True):
        pass
except KeyboardInterrupt:
    print('Program terminated')
finally:
    GPIO.cleanup()
    m.close()
    if s.is_open:
        s.close()
