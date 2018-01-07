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
#	2) Display temperatures and other metrics on alphanumeric LED displays that are readable from across the room.
#
# Hardware:
#	RaspberryPi Model 3B
#	Sandisk 32GB MicroSD ultra speed flash 
#	3xAdafruit #1778 AD8495 Analog Output K-Type Thermocouple Amplifier
#	1xAdafruit #1085 ADS1115 4 channel 16 bit ADC (Analog to Digital Converter)
#	2xAdafruit #1911 Quad Alphanumeric Display - Red 0.54" Digits w/ I2C Backpack
#	2xAdafruit #2158 Quad Alphanumeric Display - Yellow 0.54" Digits w/ I2C Backpack
#	2xAdafruit #2160 Quad Alphanumeric Display - Pure Green 0.54" Digits w/ I2C Backpack
#
# OperatingSystem:
#	Raspian Jessie Lite 2017/07/05
# 
# Install:
#	See README-trainman2-txt

####################################
# Site Configuration
####################################

# DisplayAddr: List of LED display addresses used in the system.  
# List contains i2c hexadecimal addressses of the displays that can be discovered using command "i2cdetect -y 1"
# Text is set in function set_display_text() so modify that function to match the displays
# In example below 0x70=Red,0x71=Yellow,0x72=Green,0x73=Blue,0x75=White,0x77=Yellow-Green
displayaddr=[0x70,0x71,0x72,0x73,0x75,0x77]
# Another example 0x70=Red1,0x71=Yellow2,0x72=Green3,0x74=Red4,0x75=Yellow5,0x76=Green6
#displayaddr=[0x70,0x71,0x72,0x74,0x75,0x76]

# Bright: Initial starting brightness of LED Displays. 
# This is an INDEX into brightprofiles (see below) that defines a list of hardware brightnesses.
bright=3

# BrightProfiles: You might notice that LED displays have different light output depending on the color of the display.
# The brightprofile allows you to even out the light output between displays at a given level of system brightness.
# Each brightness profile is a list of hardware brightnesses that set the brightness of individual LED displays in the system.
# Each element in this list is a list of D brightnesses where D is the number of Displays in the system.
# The first element should be a list of -1 values.  (e.g. [-1,-1,1] for a system with 3 displays. 
# Please note that -1 is not a valid hardware brightness but it signifies that the LED display should be turned completely off
# (by writing spaces to the display).  Otherwise valid brightness values go from 0 (dim) to 15 (bright).
brightprofiles=[[-1,-1,-1,-1,-1,-1],\
                [0,0,0,1,2,7],\
                [2,2,2,3,5,15],\
                [4,4,4,7,9,15],\
                [9,9,9,15,15,15],\
		[15,15,15,15,15,15]]

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
# Normal Functions
####################################

# Set display brightness given a display object and a brightness value from -1 to 15
# -1 = off, 0 to 15 and use the set_brightness method of the object to set hardware brightness to 0 to 15.
# REDO THIS COMMENT FOR BRIGHTPROFILE
def set_display_brightness(bright):
    brightlist=brightprofiles[bright]
    for d in range(len(displaylist)):
        hwbright=brightlist[d]
        if hwbright >= 0 and hwbright <= 15:
            displaylist[d].set_brightness(hwbright)

# Set the text on the LED displays
def set_display_text():
    # Set the displays to the desired string
    messagelist[0] = str(stovetemp) + "F"
    messagelist[1] = str(pipetemp) + "F"
    messagelist[2] = str(roomtemp) + "F"
    messagelist[3] = "BRI" + str(bright)
    messagelist[4] = "WHGT"
    messagelist[5] = "YGRN"

    # Blank the displays if hardware brightness is -1, otherwise display desired values
    brightlist=brightprofiles[bright]
    for m in range(len(messagelist)):
	if brightlist[m]==-1:
            messagelist[m] = "    "

    # Clear the display buffers.
        for d in range(len(displaylist)):
            displaylist[d].clear()

    pos = 0
    # Print 4 character strings to the display buffers.
    for d in range(len(displaylist)):
        displaylist[d].print_str(messagelist[d][pos:pos+4])

    # Write the display buffers to the hardware. Catch IO Errors and print IO Error message
    for d in range(len(displaylist)):
        try:
            displaylist[d].write_display()
        except IOError:
            print "IOERROR"

####################################
# Interrupt Handlers
####################################

# Install keyboard interrupt handler 
def signal_handler(signal, frame):
    print ("Caught Interrupt, running Deinitializing")

    # Clear the display buffers.
    for d in range(len(displaylist)):
        displaylist[d].clear()

    # Write the display buffers to the hardware. 
    for d in range(len(displaylist)):
        try:
            displaylist[d].write_display()
        except IOError:
            print "IOERROR"

    print ("Done, Exiting")
    quit()
    sys.exit(0)

####################################
# Initialize variables
####################################
x = 0
displaylist=[]
messagelist=[]

####################################
# Import libraries and modules
####################################
# Import python libraries
import time			# Required for sleep
import signal, sys		# Required for interrupt handler

# Import Adafruit modules that drive the hardware
import Adafruit_ADS1x15				# Required for ADS1x15 Analog to Digital Converter
from Adafruit_LED_Backpack import AlphaNum4	# Required for 14 segment AlphaNumeric Display 

####################################
# Initialize objects
####################################

# Create instance of an ADS1115 ADC (16-bit)
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)

# Create instances of displays with a specific I2C address and/or bus.
# Also create empty string in messagelist for each display
for d in range(len(displayaddr)):
    displaylist.append(AlphaNum4.AlphaNum4(address=displayaddr[d], busnum=1))
    messagelist.append("    ")

# Initialize the displays
for d in range(len(displaylist)):
    displaylist[d].begin()

# Set brightness of all displays
set_display_brightness(bright)

####################################
# Install signal and event handlers
####################################
signal.signal(signal.SIGINT, signal_handler)    # Handle keyboard interrupt
signal.signal(signal.SIGTERM, signal_handler)   # Handle kill aka sigterm

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
    print "stovetemp="+str(stovetemp)+" pipetemp="+str(pipetemp)+" roomtemp="+str(roomtemp)+" bright="+str(bright)

    # Write text to the LED displays
    set_display_text()

    # Pause for sleeptime seconds.
    time.sleep(sleeptime)

    # Increment count variable
    x = x + 1

# End of script
