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
#	3) Automatically Control a modified (8 speed + off) Pacific Energy wood stove blower fan according to stove temperature.
#	4) Acquire and display room temperature using an OW-Server 1-wire to Ethernet Server and 1-wire temperature sensor.
#	5) Automate simple operation of Air Control Lever using stepper motor, initially regulated by pipe temperature.
#	6) Automate complex Air Control based on stove and pipe temperature.  Calculate and display stove state.
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
#	1xEmbedded Data Systems OW-Server 1-wire to Ethernet Server
#	1xEmbedded Data Systems OW-ENV-T DS18B20 Wall Mount Temperature Sensor
#	1xAdafruit #2348 DC & Stepper Motor Hat for Raspberry Pi       
#	1xAdafruit #324 Stepper Motor NEMA-17 size 200 steps/rev, 12V 350mA
#	1xOpenbuilds 1185-Set Mini V Gentry Set
#	1xOpenbuilds VSlot Rail, Timing Belt, Pully, Freewheel, etc
#
# OperatingSystem:
#	Raspian Jessie Lite 2017/07/05
# 
# Install:
#	sudo apt-get install python-pip
#	sudo pip install pysnmp

####################################
# Site Configuration
####################################

# DisplayAddr: List of LED display addresses used in the system.  
# List contains i2c hexadecimal addressses of the displays that can be discovered using command "i2cdetect -y 1"
# In example below 0x70=Red-3VDC,0x71=Yellow-3VDC,0x72=Green-3VDC,0x74=Red-5VDC,0x75=Yellow-5VDC,0x76=Green-5VDC
displayaddr=[0x70,0x71,0x72,0x74,0x75,0x76]

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
# In example below I just use Red, Yellow and Green so same brightness value used for all.
brightprofiles=[[-1,-1,-1,-1,-1,-1],\
                [0,0,0,0,0,0],\
                [2,2,2,2,2,2],\
                [4,4,4,4,4,4],\
                [9,9,9,9,9,9],\
		[15,15,15,15,15,15]]

# PINBRIGHT: BCM GPIO pin number that cycles the display brightness setting.  Push of the button cycles to the next brightness profile.
# This GPIO pin is connected through the switch to GND and setup as an interrupt.  This pin is configured to INPUT mode.
PINBRIGHT=13

# PINFANPRO: BCM GPIO pin number that cycles the fan profile setting.  Push of the button cycles to the next fan profile.
# This GPIO pin is connected through the switch to GND and setup as an interrupt.  This pin is configured to INPUT mode.
PINFANPROUP=8
PINFANPRODN=7

# PINAIRPRO: BCM GPIO pin number that cycles the air profile setting.  Push of the button cycles to the next air profile.
PINAIRPRO = 16

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
# Each element in this list is a fanprofile which is a list of 9 temperature values that determine fan speed at a given temperature.
# The 9 temperatures correspond to the 9 different fanspeeds defined by the fanspeeds list above
# Notice that the temperature values are sorted in ascending order
# First number = Temp to turn fan off, Second = Temp to set fanspeed to 1 (slowest), Last = Temp to set fanspeed to 8 (fastest)
# The first fan profile (example: [525,550,575,600,625,650,675,700,725]) specifies quiet fan operation by waiting
# until the stove is really hot before turning on, and only going full speed when stove is getting overheated at 800F
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
# (example: [550,575,600,625,650,675,700,725,750]).  
# The initial fanpro setting seen below can be modified by button presses later on in the program.
fanpro=2

# ADCGains: A list of gains for each digitized channel on the Analog Digital Converter.
# There should be one comma separated number for each digitized thermocouple in the system.
# You may want to use a gain of 2/3 for a high temperature chimney probe (digitize voltage from 0 to 6.144V),
# but this will be limited to 5 volts if you supply 5VDC to the AD8495 Thermocouple amplifier. (K-Thermocouple reading up to 1382F)
# OTHERWISE, leave gains at 1 to allow the ADC to digitize voltages from 0 to 4.096VDC (K-Thermocouple reading up to 1056F)
# This should be enough temperature range for the top of a wood stove or the surface of a double wall chimney pipe.
# Using other gain values (e.g. 2,4,8,16) will likely overdrive the ADC when digitizing a K-Thermocouple amp.
adcgains=[1,1,1]

# SleepTime: Number of seconds to wait between iterations of the main loop
sleeptime=1.0

# OWS One Wire Server Configuration: Setup to read a One-Wire temperature server and temperature sensor.  
# There are many ways to accomplish the acquistion of room temperature.  I just happen to have this One-Wire server
# setup for other projects so might as well just use the existing temperature sensor and server.
# This code supports a single temperature sensor but is easily adaptable for more if required.
# Room temperature is displayed on the top Green LED display.
# Room temperature is also used by air profiles to automatically reduce stove burn rate as room heats up!
owhost      = "10.62.62.62"			# IP address of the OWServer
owoid       = "iso.3.6.1.4.1.31440.10.5.1.1.1"	# Use snmp walk to figure this out oid of room temperature
owcommunity = "public"				# Default is typically public

# Air control temperatures
pipemin  = 225		# Minimum pipetemp for good secondary burn
pipemax  = 525		# Maximum pipetemp for safe burn
stovemin = 400		# Minimum stovetemp for efficient burn
#stovemax = 600		# Maximum stovetemp for burn rate now derived from airprofile
cooltemp = 100		# Cool temperature 

# Air Control Variables: Used by aircontrol stepper motor
airsteps = 430		# Number of MICRO steps used to move air control lever all the way left or right

# Air Profiles: Allow control over the stovemax parameter which enables macro management of the air control.
# The higher the stovemax value greater the tendency for more air, more combustion and for the stove to run hotter.
# Micro management of the air control lever is still done by the stepper motor and stovetemp.
# Stovemin = 100% air (fully open), Stovemax = 0% air (fully closed), linear progression between these two temps.
# The first 15 profiles automatically reduce stovemax as the room heats up
# The last 5 profiles fixes stovemax values regardless of roomtemp.
# First element is the display character (e.g. Bottom Red LEDs: 650F (fixed), or 582B (auto program baker))
# Second and Third elements are the cool and warm room temperatures.
# Fourth and Fifth elements are the high and low stovemax parameters.
# Auto A= Outside temps in the 50s, B=40s, C=30s, D=20s, E=10s
airprofiles=[["A",70,75.0,500,500],\
             ["B",69,75.5,520,510],\
             ["C",68,76.0,540,520],\
             ["D",67,76.5,560,530],\
             ["E",66,77.0,580,540],\
             ["F",65,77.5,600,550],\
             ["G",64,78.0,620,560],\
             ["H",63,78.5,640,570],\
             ["I",62,79.0,660,580],\
             ["J",61,79.5,680,590],\
             ["K",60,80.0,700,600],\
             ["L",59,80.5,720,610],\
             ["M",58,81.0,740,620],\
             ["N",57,81.5,760,630],\
             ["O",56,82.0,780,640],\
             ["=",60,80.0,750,750],\
             ["=",60,80.0,700,700],\
             ["=",60,80.0,650,650],\
             ["=",60,80.0,600,600],\
             ["=",60,80.0,550,550]]

# AirPro: This is an index into the airprofiles which specifies which airprofile to use for aircontrol
# (example: [C,64,76,650,540]
# The initial airpro setting seen below can be modified by button presses later on in the program.
airpro=8 	# Initial profile I

####################################
# Normal Functions
####################################

# Read Analog Digital Converter to get thermocouple voltages
# Calculate temperatures and return the tempf array [stovetemp,pipetemp,thirdtemp,forthtemp]
# The ADC reads up to 4 digitized voltages.  The trainman board supports up to three thermocouple amps.
def read_adc():
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

    # Return all temperatures
    return tempf

# Set display brightness given a display object and a brightness value from -1 to 15
# -1 = off, 0 to 15 and use the set_brightness method of the object to set hardware brightness to 0 to 15.
# Brightprofiles is used to set individual brightness for each LED.   Red, yellow and green LED give all about the same
# brightness, but white is too bright,  blue is too dim and yellow-green is very dim.   Use the brightprofiles array
# to even out the brightness when using these other colors.
def set_display_brightness(bright):
    brightlist=brightprofiles[bright]
    for d in range(len(displaylist)):
        hwbright=brightlist[d]
        if hwbright >= 0 and hwbright <= 15:
            displaylist[d].set_brightness(hwbright)

# Set the text on the LED displays
def set_display_text():
    # Set the displays to the desired string
    messagelist[0] = str(stovetemp)+"F"
    messagelist[1] = str(pipetemp)+"F"
    messagelist[2] = str(int(roomtemp*10)).rstrip()+"F"
    messagelist[3] = str(stovemax)+str(airchar)
    messagelist[4] = state
    messagelist[5] = "F"+str(fanspeed)+"P"+str(fanpro)

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

# Automatically control fan speed according to stovetop temperature and fanprofile setting.  
# Fan control limited to one speed up or down, unless the pipetemp is too hot
def control_fan():
    global fanspeed

    fanprofile=fanprofiles[fanpro]
    maxfan=len(fanprofile)-1

    # If pipetemp goes over pipemax then set fan to max speed instantaneously. 
    # Abrupt fan noise might alert someone that the pipe temps are too hot.
    if (pipetemp >= pipemax):
            fanspeed = 8
       	    print 'Increasing Fan To MAX',fanspeed
	    set_fan_speed(fanspeed)
    else:
        if fanspeed < maxfan and stovetemp >= fanprofile[fanspeed+1]:
            fanspeed += 1
       	    print 'Increasing Fan To',fanspeed
	    set_fan_speed(fanspeed)
        elif fanspeed > 0 and stovetemp <= fanprofile[fanspeed-1]:
            fanspeed -= 1
	    print 'Decreasing Fan To',fanspeed
	    set_fan_speed(fanspeed)

# Get the temperature in farenheit from an OWServer given the OID and the Community name
# Returns value in F rounded to 1 decimal place
# If any kind of error then return tempf which is the previous temperature read
def get_owserver_tempf(owhost,oid,community,tempf):
    print "Getting OWServer",owhost,oid,tempf

    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(
	    SNMP.getCmd(SNMP.SnmpEngine(), SNMP.CommunityData(community, mpModel=1),
	    SNMP.UdpTransportTarget((owhost, 161)), SNMP.ContextData(),
            SNMP.ObjectType(SNMP.ObjectIdentity(oid)))
        )
    except:
        print "Caught SNMP Error, returning tempf",tempf
        return tempf

    if errorIndication:
        print(errorIndication)
        return tempf
    elif (errorStatus):
        print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        return tempf
    else:
	tempc = float(varBinds[0][1])
	tempf = round(tempc * 1.8 + 32,1)
	return tempf

# Control air lever.  
#   Air is the current air setting. Aircontrol is the new air setting:
#   airsteps = lever to left (Maximum Air) thru 0 = lever to right (Minimum Air)
#   This routine only moves the air control in "5 micro steps" at a time.
#   If there are less than 5 microsteps difference between aircontrol and air the function returns 0 (false)
def control_air(aircontrol):
    global air, airsteps

    aircontrol = max(min(airsteps,aircontrol),0)	# Limit new airsetting airsteps >= aircontrol >= 0
    steps = 5						# Number of steps to change

    # Limit steps changed by exactly steps at a time
    if (aircontrol - air) >= steps:
        print "Increasing aircontrol by",steps
        myStepper.step(steps, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)
        air += steps
        return 1	# Air increased

    if (aircontrol - air) <= -steps:
        print "Decreasing aircontrol by",steps
        myStepper.step(steps, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP)
        air -= steps
        return -1	# Air reduced
    
    return 0 		# Air not moved

# Calculate stovemax using roomtemp, Limit: smaxhigh >= stovemax >= 0, with a linear relationship between the two.
def calc_stovemax():
    global airchar

    airprofile=airprofiles[airpro]
    airchar  = airprofile[0]
    roomcool = airprofile[1]
    roomwarm = airprofile[2]
    smaxhigh = airprofile[3]
    smaxlow  = airprofile[4]

    return int(max(min(smaxhigh,(roomtemp-roomcool)*(smaxlow-smaxhigh)/(roomwarm-roomcool)+smaxhigh),smaxlow))

# Determine stove state which is shown on the bottom yellow LED display.
def calc_stove_state():
    airpercent = format(int(min(99,100 * air / airsteps)), '02d')

    if (pipetemp > pipemin) or (stovetemp > stovemin):
        if pipeair < stoveair: 
            state = "PI"+str(airpercent)
        else:
            state = "ST"+str(airpercent)
    elif (pipetemp < cooltemp) and (stovetemp < cooltemp):
        state = "COOL"
    else:
	# Draw a straight line from cooltemp,cooltemp to pipemin,stovemin
	# If stovetemp is below this line then its heating up else its cooling down 
        stoveline=(stovemin-cooltemp)/(pipemin-cooltemp)*(pipetemp-cooltemp)+cooltemp
        if stovetemp < stoveline:
             if pipetemp < (pipemin + cooltemp)/2:
                 state="IGNT"
             elif stovetemp < (stovemin + cooltemp)/2:
                 state="BURN"
             else:
                 state="HEAT"
        else:
             if stovetemp > (stovemin + cooltemp)/2:
                 state="HOT "
             else:
                 state="WARM"
    return state

####################################
# Interrupt Handlers
####################################

# Install keyboard interrupt handler 
def signal_handler(signal, frame):
    print ("Caught Interrupt, running Deinitializing")

    # Turn off motors
    print ("Turning off Motors")
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)

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

# Setup handling of Brightness Button
def brightness_handler(channel):
    global bright			# Global because we modify in this handler
    if GPIO.input(PINBRIGHT) == 0:	# Make sure PINBRIGHT actually grounded (caller bug)
        bright += 1				# Increase brightness by 1
        bright = bright % len(brightprofiles)	# Cycle bright back to zero if needed
        print "setting brightness to",bright
        set_display_brightness(bright)		# Immediately set the display brightness
        set_display_text()			# Immediately set the display text

# Setup handling of Fan Profile Up Button 
def fanprofileup_handler(channel):
    global fanpro			# Global because we modify in this handler
    global bright			# Global because we modify in this handler
    if GPIO.input(PINFANPROUP) == 0:	# Make sure PINFANPROUP actually grounded (caller bug)
        fanpro += 1				# Increase fanpro by 1
        fanpro = min(fanpro,len(fanprofiles)-1)	# Set upper limit based on size of fanprofiles
        bright = min(fanpro,1)			# Turn on display with bright=1
        print "setting fanpro to",fanpro
        set_display_text()			# Immediately set the display text

# Setup handling of Fan Profile Down Button 
def fanprofiledn_handler(channel):
    global fanpro			# Global because we modify in this handler
    global bright			# Global because we modify in this handler
    if GPIO.input(PINFANPRODN) == 0:	# Make sure PINFANPRODN actually grounded (caller bug)
        fanpro -= 1				# Decrease fanpro by 1
        fanpro = max(fanpro,0)			# Set lower limit of 0
        bright = cmp(fanpro,0)			# Turn off display if fanpro==0
        print "setting fanpro to",fanpro
        set_display_text()			# Immediately set the display text

# Setup handling of Air Profile Button
def airprofile_handler(channel):
    global airpro			# Global because we modify in this handler
    global stovemax			# Global because we modify in this handler
    if GPIO.input(PINAIRPRO) == 0:	# Make sure PINAIRPRO actually grounded (caller bug)
        airpro += 1				# Increase airpro by 1
        airpro = airpro % len(airprofiles)	# Cycle airpro back to zero if needed
        print "setting airpro to",airpro
	stovemax=calc_stovemax()		# Immediately recalc stovemax
        set_display_text()			# Immediately set the display text

####################################
# Initialize variables
####################################
x = 0
fanspeed = 0
displaylist=[]
messagelist=[]
state="INIT"	
air=airsteps	# Air control should be fully open on program start
airpercent=99	# Air control percentage range from 99 to 00 (2 digits with leading zero)
roomtemp = 68	# Some dummy room temperature until temperature sucessfully read from owserver
airmoved = 0	# Air control moved in previous iteration (0=No, -1=Decreased, +1=Increased)
airage   = 0	# How many iterations since air checked

####################################
# Import libraries and modules
####################################
# Import python libraries
import time			# Required for sleep
import signal, sys		# Required for interrupt handler
import RPi.GPIO as GPIO 	# Required to control RaspberryPI GPIO pins
import pysnmp.hlapi as SNMP	# Required for owserver 1-wire temperature sensors

# Import Adafruit modules that drive the hardware
import Adafruit_ADS1x15					# Required for ADS1x15 Analog to Digital Converter
from Adafruit_LED_Backpack import AlphaNum4		# Required for 14 segment AlphaNumeric Display 
from Adafruit_MotorHAT import Adafruit_MotorHAT		# Required for Stepper Motor Controller
from Adafruit_MotorHAT import Adafruit_StepperMotor	# Required for Stepper Motor Controller

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

# Initialize MotorHat for Stepper Motor
print "Initializing MotorHat"
mh = Adafruit_MotorHAT()		# Create motorhat object
myStepper = mh.getStepper(200, 1)	# 200 steps/rev, motor port #1
myStepper.setSpeed(30)			# 30 RPM

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
GPIO.setup(PINBRIGHT,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(PINFANPROUP,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(PINFANPRODN,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(PINAIRPRO,GPIO.IN,pull_up_down=GPIO.PUD_UP)

####################################
# Install signal and event handlers
####################################
signal.signal(signal.SIGINT, signal_handler)    # Handle keyboard interrupt
signal.signal(signal.SIGTERM, signal_handler)   # Handle kill aka sigterm
GPIO.add_event_detect(PINBRIGHT,   GPIO.FALLING, callback=brightness_handler, bouncetime=200)	# Handle Brightness button
GPIO.add_event_detect(PINFANPROUP, GPIO.FALLING, callback=fanprofileup_handler, bouncetime=200)	# Handle Fan Profile up button
GPIO.add_event_detect(PINFANPRODN, GPIO.FALLING, callback=fanprofiledn_handler, bouncetime=200)	# Handle Fan Profile down button
GPIO.add_event_detect(PINAIRPRO, GPIO.FALLING, callback=airprofile_handler, bouncetime=200)	# Handle Fan Profile down button

####################################
####################################
## MAIN LOOP
####################################
####################################

print('Starting Main Loop, press Ctrl-C to quit...')

# Main loop.
while True:
    # Read the digitizer, calculate temperatures and set the stovetemp and pipetemp variables
    [stovetemp,pipetemp,thirdtemp,forthtemp] = read_adc()

    # Get roomtemp from owserver 1-wire temperature sensor every so often
    if (x % 30) == 0:
        roomtemp = get_owserver_tempf(owhost,owoid,owcommunity,roomtemp)

    # Calculate stovemax 
    stovemax = calc_stovemax()

    # Calculate pipeair (Maximum air setting according to pipetemp versus pipemax thru pipemin)
    pipeair = airsteps - (airsteps * (pipetemp - pipemin) / (pipemax - pipemin))
    pipeair = max(min(airsteps,pipeair),0)	# Limit: airsteps >= pipeair >= 0

    # Calculate stoveair (Maximum air setting according to stovetemp versus stovemax thru stovemin)
    stoveair = airsteps - (airsteps * (stovetemp - stovemin) / (stovemax - stovemin))
    stoveair = max(min(airsteps,stoveair),0)	# Limit: airsteps >= stoveair >= 0

    # Calculate stove state
    state = calc_stove_state()

    # Print variables. + concatination and str() to gets rid of extra spaces after = symbols
    print "stovetemp="+str(stovetemp)+" pipetemp="+str(pipetemp)+" roomtemp="+str(roomtemp)+" air="+str(air)+" stoveair="+str(stoveair)+" pipeair="+str(pipeair)+" stovemax="+str(stovemax)+str(airchar)+" state="+str(state)+" fanspeed="+str(fanspeed)+" fanpro="+str(fanpro)

    # Write text to the LED displays
    set_display_text()

    # Automatically control fan speed
    control_fan()

    # Calculate ideal air position based on lowest of stoveair and pipeair, but do not set position every iteration.
    calcair = min(stoveair,pipeair)

    # We want to batch stepper motor operations together to minimize distracting noise.
    # Set air control lever:
    #   if air control on the move
    #     OR
    #   air out of whack by 5% or more
    #     OR
    #   its been a minute or more since control_air has been called
    if airmoved or abs(calcair - air) * 100 / airsteps >= 5 or airage >= 60:
        airmoved = control_air(calcair)
        airage = 0
    else:
        airage += 1

    # Increment count variable
    x += 1

    # Logic to sleep between iterations
    if airmoved:
        time.sleep(0.1)		# Short sleep because moving air lever already takes about a second
    else:
        time.sleep(sleeptime)

# End of script
