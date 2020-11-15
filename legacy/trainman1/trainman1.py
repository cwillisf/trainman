#! /usr/bin/python -u
#
# Trainman PYTHON script to automate Wood Stove operation
# Copyright (c) 2018 Yodagami
# License: GPLV3 GNU Public License Version 3
#
# "You don't get it do you, I built this place. Down here I make the rules. Down here I make the threats. Down here... I'm God."
# -The Trainman to Neo, The Matrix Revolutions
#
# Description:
#	Simple woodstove monitoring and automation script
#
# Features:
#	1) Monitor wood stove temperatures using up to 3 K-Type Grounded or Ungrounded thermocouples.  
#
# Hardware:
#	RaspberryPi Model 3B
#	Sandisk 32GB MicroSD ultra speed flash 
#	3xAdafruit #1778 AD8495 Analog Output K-Type Thermocouple Amplifier
#	1xAdafruit #1085 ADS1115 4 channel 16 bit ADC (Analog to Digital Converter)
#
# OperatingSystem:
#	Raspian Jessie Lite 2017/07/05
# 
# Install:
#	See README-trainman1.txt

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
adcgains=[1,1,1]

sleeptime=1.0	# Number of seconds to wait between iterations of the main loop

####################################
# Initialize variables
####################################
x = 0

####################################
# Import libraries and modules
####################################
# Import python libraries
import time			# Required for sleep

# Import Adafruit modules that drive the hardware
import Adafruit_ADS1x15		# Required for ADS1x15 Analog to Digital Converter

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

# Main loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*4
    volts  = [0]*4
    tempc  = [0]*4
    tempf  = [0]*4
    for i in range(len(adcgains)):
        # Read the specified ADC channel using the appropriate gain value
        values[i] = adc.read_adc(i, gain=adcgains[i])

	# Convert ADC values to voltages depending on gain value:
	# For gain=1:   16 bit value -32768 to 32767 is -4.096 to 4.096 volts
	# For gain=2/3: 16 bit value -32768 to 32767 is -6.144 to 6.144 volts
	if adcgains[i] == 1:
		volts[i] = values[i] / float(32767) * 4.096 
        elif adcgains[i] == 2/3: 
		volts[i] = values[i] / float(32767) * 6.144
	else:
		raise ValueError('Invalid adcgain. Only use values 1 or 2/3 in adcgains list')

	# Convert voltages values to temperature C
	tempc[i] = (volts[i] - 1.25) / 0.005

	# Convert temperature C to temperature F
	tempf[i] = int(round(tempc[i] * 9 / 5 + 32, 0))
	if (tempf[i] < -200): tempf[i] = "-"

    # Set easy to read variable from the tempf array
    stovetemp = tempf[0]
    pipetemp  = tempf[1]
    roomtemp  = tempf[2]

    # Print variables. + concatination and str() to gets rid of extra spaces after = symbols
    print "stovetemp="+str(stovetemp)+" pipetemp="+str(pipetemp)+" roomtemp="+str(roomtemp)

    # Pause for sleeptime seconds.
    time.sleep(sleeptime)

    # Increment count variable
    x = x + 1

# End of script
