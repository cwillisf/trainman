#!/usr/bin/env python3
#
# Trainman PYTHON script to automate Wood Stove operation
# Copyright (c) 2018 Yodagami, 2020 cwillisf
# License: GPLV3 GNU Public License Version 3
#
# "You don't get it do you, I built this place. Down here I make the rules. Down here I make the threats. Down here... I'm God."
# -The Trainman to Neo, The Matrix Revolutions
#
# Description:
#        Simple woodstove monitoring and automation script
#
# Features:
#        1) Monitor wood stove temperatures using up to 3 K-Type Grounded or Ungrounded thermocouples.  
#
# Hardware:
#        RaspberryPi Model 3B
#        Sandisk 32GB MicroSD ultra speed flash 
#        3xAdafruit #1778 AD8495 Analog Output K-Type Thermocouple Amplifier
#        1xAdafruit #1085 ADS1115 4 channel 16 bit ADC (Analog to Digital Converter)
#
# OperatingSystem:
#        Raspian Jessie Lite 2017/07/05
# 
# Install:
#        See README-trainman1.txt

####################################
# Site Configuration
####################################

# ADCGains: A list of gains for each digitized channel on the Analog Digital Converter.
# There should be one comma separated number for each digitized thermocouple in the system.
# You may want to use a gain of 2/3 for a high temperature chimney probe (digitize voltage from 0 to 6.144V),
# but this will be limited to 5 volts if you supply 5VDC to the AD8495 Thermocouple amplifier. (K-Thermocouple reading up to 1382F)
# OTHERWISE, leave gains at 1 to allow the ADC to digitize voltages from 0 to 4.096VDC (K-Thermocouple reading up to 1056F)
# This should be enough temperature range for the top of a wood stove or the surface of a double wall chimney pipe.
# Using other gain values (e.g. 2,4,8,16) will likely overdrive the ADC when digitizing a K-Thermocouple amp.
adcgains=[2/3]
reportInterval = 30 # seconds
bias_voltage = 1.3 # Adafruit says 1.25
mv_per_c = 0.0025 # Adafruit says 0.005

####################################
# Import libraries and modules
####################################
# Import python libraries
import time                        # Required for sleep

# Import Adafruit modules that drive the hardware
import Adafruit_ADS1x15                # Required for ADS1x15 Analog to Digital Converter

import paho.mqtt.publish as publish

####################################
# Initialize objects
####################################

# Create instance of an ADS1115 ADC (16-bit)
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)

####################################
####################################
## MAIN LOOP
####################################
####################################

print('Starting Main Loop, press Ctrl-C to quit...')

def get_voltage(channel):
    gain = adcgains[channel]
    sample = adc.read_adc(channel, gain=gain)
    if sample > 0.75 * 32768:
        return None
    voltage = sample / float(gain) * 4.096 / 32767.0
    return voltage

def voltage_to_c(voltage):
    celsius = (voltage - bias_voltage) / mv_per_c
    return celsius

def c_to_f(celsius):
    return celsius * 9 / 5 + 32

tempCount = len(adcgains)
samples = [[] for i in range(tempCount)]
nextReport = time.time() + reportInterval
while True:
    for i in range(tempCount):
        voltage = get_voltage(i)
        if voltage is None:
            print("Warning: bad reading from probe " + str(i) + ". Is it disconnected?")
        else:
            samples[i].append(get_voltage(i))
    if time.time() > nextReport:
        count = len(samples[0])
        if count > 0:
            averages_v = [sum(x)/len(x) for x in samples]
            averages_c = [voltage_to_c(x) for x in averages_v]
            averages_f = [c_to_f(x) for x in averages_c]
            print(str(count) + ": " + str(averages_v) + "V => " + str(averages_c) + "C => " + str(averages_f) + "F")
            for i in range(tempCount):
                try:
                    publish.single("trainman/" + str(i) + "/temperature", round(averages_c[i], 2), hostname="192.168.1.2")
                except OSError:
                    print("Error publishing to MQTT. Skipping.")
            samples = [[] for i in range(tempCount)]
            nextReport = time.time() + reportInterval
