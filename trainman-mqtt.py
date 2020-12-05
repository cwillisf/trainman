#!/usr/bin/env python3
#
# Trainman PYTHON script to automate Wood Stove operation
# Copyright (c) 2018 Yodagami, 2020 cwillisf
# License: GPLV3 GNU Public License Version 3
#

####################################
# Import libraries and modules
####################################
from collections import namedtuple, deque
import datetime
import math

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import board
import busio
import paho.mqtt.publish as publish

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, savgol_filter

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
adcgain = 1
num_channels = 1
reportInterval = datetime.timedelta(seconds=30)
bias_voltage = 1.3  # Adafruit says 1.25
mv_per_c = 0.0025  # Adafruit says 0.005

####################################
# Initialize objects
####################################

i2c = busio.I2C(board.SCL, board.SDA)

# for me there's a significant amount of ~2Hz noise on this signal
# at data_rate=128 the magnitude of the noise increases dramatically
ads = ADS.ADS1115(i2c, gain=adcgain, data_rate=32)
channels = [AnalogIn(ads, x) for x in range(num_channels)]

####################################
####################################
# MAIN LOOP
####################################
####################################

print("Starting Main Loop, press Ctrl-C to quit...")


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

def find_first(predicate, list, default=None):
    return next((index for index,value in enumerate(list) if predicate(value)), default)

def trimOldSamples(channelData):
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=5)
    for i in range(num_channels):
        thisChannelData = channelData[i]
        oldCount = len(thisChannelData.times)
        index = find_first(lambda x: x > cutoff, thisChannelData.times)
        if index != None:
            del thisChannelData.times[:index]
            del thisChannelData.voltages[:index]
        newCount = len(thisChannelData.times)
        print("Removed", oldCount - newCount, "samples")

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def main():
    ChannelData = namedtuple('ChannelData', ['times', 'voltages'])

    # channelData is an array of:
    #   a tuple of:
    #     an array of timestamps (use 'datetime64[ns]')
    #     an array of temperatures (use np.float32)
    channelData = [ChannelData([], []) for x in range(num_channels)]
    nextReport = datetime.datetime.now() + reportInterval
    while True:
        for i in range(num_channels):
            voltage = get_voltage(i)
            if voltage is None:
                print("Warning: bad reading from probe " + str(i) + ". Is it disconnected?")
            else:
                channelData[i].times.append(datetime.datetime.now())
                channelData[i].voltages.append(voltage)
        if datetime.datetime.now() > nextReport:
            #print("Processing samples: ", len(channelData[0].times))
            trimOldSamples(channelData)
            for i in range(num_channels):
                npChannelTimes = np.array(
                    channelData[i].times, dtype='datetime64[ns]')
                df = pd.DataFrame({
                    "raw": voltage_to_c(np.array(channelData[i].voltages, dtype=np.float32))
                }, index=pd.DatetimeIndex(npChannelTimes))
                df = df.resample('125ms').bfill()
                #samples_per_second = ads.data_rate
                samples_per_second = 8
                window_deriv = 3 * samples_per_second
                #window_deriv = reportInterval.seconds * samples_per_second * 2 / 3
                window_deriv = math.floor(window_deriv / 2) * 2 + 1
                df['smooth'] = butter_lowpass_filter(df.raw, 0.25, 8)
                df['derivative'] = savgol_filter(df.smooth, window_deriv, 3, deriv=1)
                df.plot()
                plt.savefig('plot.svg')
                plt.clf()
                plt.cla()
                plt.close('all')
                lookback_temp = 5
                try:
                    messages = [
                        ("trainman/" + str(i) + "/temperature", np.average(df.smooth[-1])),
                        ("trainman/" + str(i) + "/derivative", np.average(df.derivative[-1])),
                    ]
                    print(i, len(df.smooth), messages)
                    messages = [(m[0], str(round(m[1], 2))) for m in messages]
                    publish.multiple(messages, hostname="192.168.1.2")
                except OSError:
                    print("Error publishing to MQTT. Skipping.")
            nextReport = datetime.datetime.now() + reportInterval


if __name__ == "__main__":
    main()
