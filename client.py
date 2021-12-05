import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
from bluedot.btcomm import BluetoothClient
# Connect to the sensor
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

def read_info():
    data = master.execute(1, cst.READ_INPUT_REGISTERS, 0, 10)
    print('in')

    voltage = data[0] / 10.0 # [V]
    current = (data[1] + (data[2] << 16)) / 1000.0 # [A]
    power = (data[3] + (data[4] << 16)) / 10.0 # [W]
    energy = data[5] + (data[6] << 16) # [Wh]
    frequency = data[7] / 10.0 # [Hz]
    powerFactor = data[8] / 100.0
    alarm = data[9] # 0 = no alarm
    c.send('Voltage is '+str(voltage))
    c.send(' Current is  '+str(current))
    c.send(' Power is '+str(power)) # active power (V * I * power factor)
    c.send(' Energy is '+str(energy))
    c.send(' Frequency is '+str(frequency))
    c.send(' Power factor is '+str(powerFactor))
    c.send(' Alarm is '+str(alarm))

def data_received(recv_data):
    print(recv_data)
    if recv_data == "買早餐車車被撞":
        read_info()

c = BluetoothClient("raspberrypi", data_received)
c.send("potato")

while (True):
    pass
