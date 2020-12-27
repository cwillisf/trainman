#!/usr/bin/env python3
#
# Trainman PYTHON script to automate Wood Stove operation
# Copyright (c) 2018 Yodagami, 2020 cwillisf
# License: GPLV3 GNU Public License Version 3
#

####################################
# Import libraries and modules
####################################
import collections
import queue
import threading
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
max_trend_samples = 10 # trend analysis will be over this many report intervals
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


def voltage_to_c(voltage):
    celsius = (voltage - bias_voltage) / mv_per_c
    return celsius


def c_to_f(celsius):
    return celsius * 9 / 5 + 32


class SampleCollector(threading.Thread):
    """Samples all channels in one thread and delivers in batches to another thread"""

    def __init__(self, num_channels):
        super(SampleCollector, self).__init__()
        self.daemon = True
        self._num_channels = num_channels
        self._sample_lock = threading.Lock()
        self._samples = None
        self.flush_samples()

    def flush_samples(self):
        new_samples = [[] for i in range(self._num_channels)]
        old_samples = None
        with self._sample_lock:
            old_samples = self._samples
            self._samples = new_samples
        return old_samples

    def _get_voltage(self, channel):
        voltage = channels[channel].voltage
        if voltage > 4.5:
            # looks like the probe is disconnected
            return None
        return voltage

    def run(self):
        while True:
            for i in range(self._num_channels):
                voltage = self._get_voltage(i)
                if voltage is None:
                    print("Warning: bad reading from probe " +
                        str(i) + ". Is it disconnected?")
                else:
                    with self._sample_lock:
                        self._samples[i].append(voltage)

class SampleProcessor(threading.Thread):
    """Processes and publishes a batch of samples"""

    def __init__(self, num_channels):
        super(SampleProcessor, self).__init__()
        self.daemon = True
        self._num_channels = num_channels
        self._sampleQueue = queue.SimpleQueue()
        self._trendSamples = [collections.deque() for i in range(self._num_channels)]

    def process(self, samples):
        self._sampleQueue.put(samples)

    def run(self):
        while True:
            samples = self._sampleQueue.get()
            for i in range(self._num_channels):
                channel_samples = samples[i]
                results = self._process_channel(channel_samples, self._trendSamples[i])
                print(i, results)
                try:
                    publish.single("trainman/" + str(i) + "/temperature",
                                round(results['temp_c'], 2), hostname="192.168.1.2")
                except OSError:
                    print("Error publishing to MQTT. Skipping.")

    def _process_channel(self, channel_samples, trend_samples):
        count = len(channel_samples)
        average_v = sum(channel_samples)/count
        average_c = voltage_to_c(average_v)
        trend_samples.append(average_c)
        while len(trend_samples) > max_trend_samples:
            trend_samples.popleft()
        #trend_c = self._get_trend(trend_samples)
        return {
            'count': count,
            'voltage': average_v,
            'temp_c': average_c,
            'temp_f': c_to_f(average_c),
            #'trend_c': trend_c,
            #'trend_f': c_to_f(trend_c)
        }

def main():
    sampler = SampleCollector(num_channels)
    sampler.start()

    processor = SampleProcessor(num_channels)
    processor.start()

    while True:
        time.sleep(reportInterval)
        samples = sampler.flush_samples()
        processor.process(samples)

if __name__ == "__main__":
    main()
