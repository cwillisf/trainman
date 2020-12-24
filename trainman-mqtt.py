#!/usr/bin/env python3
#
# Trainman PYTHON script to automate Wood Stove operation
# Copyright (c) 2018 Yodagami, 2020 cwillisf
# License: GPLV3 GNU Public License Version 3
#

####################################
# Import libraries and modules
####################################
import time

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import board
import busio
import paho.mqtt.publish as publish

####################################
# Configuration
####################################

# ADCGains: A list of gains for each digitized channel on the Analog Digital Converter.
# There should be one comma separated number for each digitized thermocouple in the system.
# You may want to use a gain of 2/3 for a high temperature chimney probe (digitize voltage from 0 to 6.144V),
# but this will be limited to 5 volts if you supply 5VDC to the AD8495 Thermocouple amplifier. (K-Thermocouple reading up to 1382F)
# OTHERWISE, leave gains at 1 to allow the ADC to digitize voltages from 0 to 4.096VDC (K-Thermocouple reading up to 1056F)
# This should be enough temperature range for the top of a wood stove or the surface of a double wall chimney pipe.
# Using other gain values (e.g. 2,4,8,16) will likely overdrive the ADC when digitizing a K-Thermocouple amp.
adcgain = 2/3
num_channels = 1
reportInterval = 30  # seconds
bias_voltage = 1.3  # Adafruit says 1.25
mv_per_c = 0.0025  # Adafruit says 0.005

####################################
# Initialize objects
####################################

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, gain=adcgain)

channels = [AnalogIn(ads, x) for x in range(num_channels)]

####################################
####################################
# MAIN LOOP
####################################
####################################

print('Starting Main Loop, press Ctrl-C to quit...')


def get_voltage(channel):
    voltage = channels[channel].voltage
    if voltage > 4.5:
        # looks like the probe is disconnected
        return None
    return voltage


def voltage_to_c(voltage):
    celsius = (voltage - bias_voltage) / mv_per_c
    return celsius


def c_to_f(celsius):
    return celsius * 9 / 5 + 32

def main():
    samples = [[] for i in range(num_channels)]
    nextReport = time.time() + reportInterval
    while True:
        for i in range(num_channels):
            voltage = get_voltage(i)
            if voltage is None:
                print("Warning: bad reading from probe " +
                    str(i) + ". Is it disconnected?")
            else:
                samples[i].append(voltage)
        if time.time() > nextReport:
            count = len(samples[0])
            if count > 0:
                averages_v = [sum(x)/len(x) for x in samples]
                averages_c = [voltage_to_c(x) for x in averages_v]
                averages_f = [c_to_f(x) for x in averages_c]
                print(str(count) + ": " + str(averages_v) + "V => " +
                    str(averages_c) + "C => " + str(averages_f) + "F")
                for i in range(num_channels):
                    try:
                        publish.single("trainman/" + str(i) + "/temperature",
                                    round(averages_c[i], 2), hostname="192.168.1.2")
                    except OSError:
                        print("Error publishing to MQTT. Skipping.")
                samples = [[] for i in range(num_channels)]
                nextReport = time.time() + reportInterval

if __name__ == "__main__":
    main()
