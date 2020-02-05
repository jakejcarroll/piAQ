#!/usr/bin/env python

import time
try:
    from pms5003 import PMS5003, ReadTimeoutError
except ReadTimeoutError:
    from pms5003 import PMS5003, ReadTimeoutError
from bme280 import BME280
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
import atexit
import ads1015
import RPi.GPIO as GPIO
from enviroplus import gas

from losantmqtt import Device

# construct losant device
device = Device("5e11e6330ac5cc0007fc1265", "0ac1cea1-a88d-4a4f-a209-55411611f9d9", "b5196aaacf877f153a86c08084c00cc85cac70402452d6e9f466e3b63bb7b671")

pms5003 = PMS5003()

def pm1():
    readings = pms5003.read()
    pm1_reading = (readings.pm_ug_per_m3(1.0))
    pm1_reading = "{:.0f}".format(pm1_reading)
    return float(pm1_reading)
    pm1_reading.flush()

def pm25():
    readings = pms5003.read()
    pm25_reading = (readings.pm_ug_per_m3(2.5))
    pm25_reading = "{:.0f}".format(pm25_reading)
    return float(pm25_reading)
    pm25_reading.flush()
    
def pm10():
    readings = pms5003.read()
    pm10_reading = (readings.pm_ug_per_m3(10.0))
    pm10_reading = "{:.0f} ".format(pm10_reading)
    return float(pm10_reading)
    pm10_reading.flush()


#BME sensor functions

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)
    
def humidity():
    humidity = bme280.get_humidity()
    return humidity
    humidity.flush()
    
def pressure():
     pressure = bme280.get_pressure()
     return pressure
     pressure.flush()
     
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp
    
def temp():
    temperature = (bme280.get_temperature())
    factor = 0.7
    cpu_temps = [get_cpu_temperature()] * 5
    cpu_temp = get_cpu_temperature()
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    comp_temp = temperature - ((avg_cpu_temp - temperature) / factor)
    return comp_temp
    temperature.flush()

# Connect to Losant
device.connect(blocking=False)

def main():
    while True:
        device.loop()
        if device.is_connected():
            device.send_state({"Temperature": temp()})
            device.send_state({"humidity": humidity()})
            device.send_state({"pressure": pressure()})
            device.send_state({"pm1": pm1()})
            device.send_state({"pm25": pm25()})
            device.send_state({"pm10": pm10()})
        time.sleep(5)
        
main()
