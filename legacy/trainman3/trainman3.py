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
#	3) Automatically Control a modified (8 speed + off) wood stove blower fan based on stove temperature.
#
# Hardware:
#	RaspberryPi Model 3B
#	Sandisk 32GB MicroSD ultra speed flash 
#	3xAdafruit #1778 AD8495 Analog Output K-Type Thermocouple Amplifier
#	1xAdafruit #1085 ADS1115 4 channel 16 bit ADC (Analog to Digital Converter)
#	2xAdafruit #1911 Quad Alphanumeric Display - Red 0.54" Digits w/ I2C Backpack
#	2xAdafruit #2158 Quad Alphanumeric Display - Yellow 0.54" Digits w/ I2C Backpack
#	2xAdafruit #2160 Quad Alphanumeric Display - Pure Green 0.54" Digits w/ I2C Backpack
#	1xSainSmart #20-018-901 4 Channel 5V Solid State Relay Module Board OMRON 240VAC 2A output with resistive fuse phototriac.
#
# OperatingSystem:
#	Raspian Jessie Lite 2017/07/05
# 
# Install:
#	see README-trainman3.txt

####################################
# Site Configuration
####################################

# DisplayAddr: List of LED display addresses used in the system.  
# List contains i2c hexadecimal addressses of the displays that can be discovered using command "i2cdetect -y 1"
# In example below 0x70=Red,0x71=Yellow,0x72=Green,0x73=Blue,0x75=White,0x77=Yellow-Green
displayaddr=[0x70,0x71,0x72,0x73,0x75,0x77]
# Another example 0x70=Red1,0x71=Yellow2,0x72=Green3,0x74=Red4,0x75=Yellow5,0x76=Green6
#displayaddr=[0x70,0x71,0x72,0x74,0x75,0x76]

# Bright: Initial starting brightness of LED Displays. 
# This is an INDEX into brightprofiles (see below) that defines a list of hardware brightnesses.
bright=1

# BrightProfiles: You might notice that LED displays have different light output depending on the color of the display.
# The brightprofile allows you to somewhat even out the light output between displays at a given level of system brightness.
# Each brightness profile is a list of hardware brightnesses that set the brightness of individual LED displays in the system.
# Each element in this list is a list of D brightnesses where D is the number of Displays in the system.
# The first element should be a list of -1 values.  (e.g. [-1,-1,1] for a system with 3 displays. 
# Please note that -1 is not a valid hardware brightness but it signifies that the LED display should be turned completely off
# (by writing spaces to the display).
# Otherwise valid brightness values go from 0 (dim) to 15 (bright).
brightprofiles=[[-1,-1,-1,-1,-1,-1],\
                [0,0,0,0,0,3],\
                [2,2,2,2,2,9],\
                [4,4,4,4,4,15],\
                [9,9,9,9,9,15],\
		[15,15,15,15,15,15]]

# PINFANPRO: BCM GPIO pin number that cycles the fan profile setting.  Push of the button cycles to the next fan profile.
# This GPIO pin is connected through the switch to GND and setup as an interrupt.  This pin is configured to INPUT mode.
PINFANPRO=24

# GPIOFan: List of BCM GPIO pin numbers used to control blower fan. These pins are configured to OUTPUT mode.
# All 4 of the GPIO pins are wired to control 4 SainSmart solid state relays. 
# First number in the list is the gpiopin that controls the on/off relay that CONNECTS or CUTS 120VAC power to the fan motor
# Second number in the list is the gpiopin that controls the relay that shorts the lowest value resistor (12KOhms)
# Third number in the list is the gpiopin that controls the relay that shorts the middle value resistor (27KOhms)
# Forth number in the list is the gpiopin that controls the relay that shorts the highest value resistor (47KOhms)
# The resistors on relays 2,3,4 basically replace the main potentiometer and trim pot from the motor speed control.
# Three resistors are wired in series, 12KOhms + 27KOhms + 47KOhms so shorting out different combinations of relays 2,3,4 
# allow the fan to be run at 8 different fan speeds plus off.  
# There is no amount of resistance that will shutoff the AC motor so the first relay switches the 120VAC power.
gpiofan=[17,27,22,23]

# FanSpeeds: Defines how many fan speeds there are and how to set the Raspberry Pi GPIO Pins for the fan to obtain them.
# Its is a list of 4 values lists. 0=gpiopin off (low), 1=gpiopin on (high) corresponding to gpiofan above which has 4 values.
# Notice there are 9 fanspeeds elements
# The first element [0,0,0,0] defines how to shut the motor off.
# The 2nd element [1,0,0,0] defines how to run the fan at its lowest speed (motor on but no resistors shorted)
# The Last element [1,1,1,1] defines how to run the fan at its highest speed (motor on and all resistors shorted)
fanspeeds=[[0,0,0,0],[1,0,0,0],[1,1,0,0],[1,0,1,0],[1,1,1,0],[1,0,0,1],[1,1,0,1],[1,0,1,1],[1,1,1,1]]

# FanProfiles: A list of profiles that define stovetop temperature versus speed of the blower fan.
# Each element in this is a fanprofile which is a list of 9 temperature values that determine fan speed at a given temperature.
# The 9 temperatures correspond to the 9 different fanspeeds defined by the fanspeeds list above
# Notice that the temperature values are sorted in ascending order
# First number = Temp to turn fan off, Second = Temp to set fanspeed to 1 (slowest), Last = Temp to set fanspeed to 8 (fastest)
# The first fan profile (example: [525,550,575,600,625,650,675,700,725]) specifies quiet fan operation by waiting
# until the stove is really hot before turning on, and only going full speed when stove is getting really hot at 725F
#
# The last fan profile specifies aggressive fan operation by turning on at a low reasonable temperature and going
# full speed at mid level temperatures.
#
fanprofiles=[[525,550,575,600,625,650,675,700,725],\
             [500,525,550,575,600,625,650,675,700],\
             [480,500,525,550,575,600,625,650,675],\
             [460,480,500,525,550,575,600,625,650],\
             [440,460,480,500,525,550,575,600,625],\
             [420,440,460,480,500,525,550,575,600],\
             [400,420,440,460,480,500,525,550,575],\
             [380,400,420,440,460,480,500,525,550],\
             [360,380,400,420,440,460,480,500,525],\
             [340,360,380,400,420,440,460,480,500]]

# FanPro: This is an index into the fanprofiles which specifies which fanprofile to use to set the blower fan speed.
# (example: 4=[440,460,480,500,525,550,575,600,625]).  
# The initial fanpro setting seen below can be modified by button presses later on in the program.
fanpro=4

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
    messagelist[3] = "FAN"+str(fanspeed)
    messagelist[4] = "FPR"+str(fanpro)
    messagelist[5] = "BRI"+str(bright)

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

# Set speed of blower fan by setting gpiofan pins low/high depending on fanspeed variable
def set_fan_speed(fanspeed):
    print "Setting fanspeed to",fanspeed,fanspeeds[fanspeed]
    for p in range(len(gpiofan)):
	GPIO.output(gpiofan[p],fanspeeds[fanspeed][p])

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

    # Turn off blower fan
    set_fan_speed(0)

    # Clean up GPIO pins
    GPIO.cleanup()

    print ("Done, Exiting")
    quit()
    sys.exit(0)

# Setup handling of Fan Profile Button 
def fanprofile_handler(channel):
    global fanpro			# Global because we modify in this handler
    if GPIO.input(PINFANPRO) == 0:	# Make sure PINFAN actually grounded (caller bug)
        fanpro += 1				# Increase fanpro by 1
        fanpro = fanpro % len(fanprofiles)	# Cycle fanpro back to zero if needed
        print "setting fanpro to",fanpro
        set_display_text()			# Immediately set the display text

####################################
# Initialize variables
####################################
x = 0
fanspeed = 0
displaylist=[]
messagelist=[]

####################################
# Import libraries and modules
####################################
# Import python libraries
import time			# Required for sleep
import signal, sys		# Required for interrupt handler
import RPi.GPIO as GPIO 	# Required to control RaspberryPI GPIO pins


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
# Initialize GPIO boards and pins
####################################
# Initialize GPIO board to BCM mode where pin numbers defined by Broadcom SOC Channel
# You can set this to GPIO.BOARD mode but then you will have to define pins according to pi header (e.g. 1 to 40)
GPIO.setmode(GPIO.BCM)

# Initialize GPIO fan pins to output mode
for p in range(len(gpiofan)):
    GPIO.setup(gpiofan[p], GPIO.OUT)

# Initialize GPIO brightness button to input mode with pull up resistor active
GPIO.setup(PINFANPRO,GPIO.IN,pull_up_down=GPIO.PUD_UP)

####################################
# Install signal and event handlers
####################################
signal.signal(signal.SIGINT, signal_handler)    # Handle keyboard interrupt
signal.signal(signal.SIGTERM, signal_handler)   # Handle kill aka sigterm
GPIO.add_event_detect(PINFANPRO, GPIO.FALLING, callback=fanprofile_handler, bouncetime=200)	# Handle Fan Profile button


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
    print "stovetemp="+str(stovetemp)+" pipetemp="+str(pipetemp)+" roomtemp="+str(roomtemp)+" fanspeed="+str(fanspeed)+" fanpro="+str(fanpro)+" bright="+str(bright)

    # Write text to the LED displays
    set_display_text()

    # Increase or Decrease fan speed depending on stovetop temperature
    fanprofile=fanprofiles[fanpro]
    maxfan=len(fanprofile)-1

    if fanspeed < maxfan and stovetemp >= fanprofile[fanspeed+1]:
        fanspeed += 1
	print 'Increasing Fan To',fanspeed
	set_fan_speed(fanspeed)
    elif fanspeed > 0 and stovetemp <= fanprofile[fanspeed-1]:
        fanspeed -= 1
	print 'Decreasing Fan To',fanspeed
	set_fan_speed(fanspeed)

    # Pause for sleeptime seconds.
    time.sleep(sleeptime)

    # Increment count variable
    x = x + 1

# End of script
