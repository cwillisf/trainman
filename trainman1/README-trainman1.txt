# Trainman1: Read stove and pipe temperatures using thermocouple amplifiers and an analog digitizer.  

PHASE DESCRIPTION:

In this starting phase the Raspberry Pi is configured and the trainman hardware board is soldered together.  A PermaProto HAT Mini Kit is used to wire together the thermocouple amplifiers to the analog digitizer.  This HAT is then mounted onto the Rasapberry Pi allowing it to talk to the digitizer.   The main loop of the trainman1.py script reads the analog digitizer, formats the output and writes it to a file.   Sounds simple right?  Well there are a few tricks to getting it all up and running on the stove as you will see.

HARDWARE REQUIRED:

- Raspberry Pi 3 - Model B   https://www.adafruit.com/product/3055  Do you have to buy this from Adafruit?  No.  Will a Pi2 work?  Probably, but I like the built in WiFi of the Pi3.

- Micro SD Card - https://www.adafruit.com/product/2767  Recommend at least 8GB.  I actually like Sandisk Ultra 32GB Micro SD Cards.

- 5V 2.4A Powersupply MicroUSB - https://www.adafruit.com/product/1995

- Adafruit P2310 Perma-Proto HAT for Pi Mini Kit  https://www.adafruit.com/product/2310  Get the one with No EEPROM if you can.

- Adafruit P1778 Analog Output K-Type Thermocouple Amplifier AD8495 Breakout.  https://www.adafruit.com/product/1778  Qty 3, Recommend you get at least 2 so you can digitize both stove temperature and chimney pipe temperature (2 separate thermocouples).  Trainman will handle up to 3.  The last one can maybe be used for a chimney pipe probe or a room temperature sensor.  Maybe you have smoker or BBQ that needs monitoring as well.  Its always a good idea to have extras for debugging, spares and future projects.

- Adafruit P1085 ADS1115 16-Bit ADC - 4 Channel with Programmable Gain Amplifier.  https://www.adafruit.com/product/1085  Qty 1.  Trainman uses up to 3 of the 4 channels leaving one left over for futher experimentation and mischief. 

- Adafruit 598 36-pin 0.1" Female header - pack of 5  https://www.adafruit.com/product/598  The headers are soldered onto the HAT and then the thermocouple amplifiers and ADC plug into them.  Makes for a nice modular install

- Adafruit 3174 Hook-up Wire Set 22AWG Solid - https://www.adafruit.com/product/3174  Using different colors for Neg,+5VDC,Control,Data,etc organizes the wiring on the board.

- K type Thermocouple, Washer Probe  https://www.auberins.com/index.php?main_page=product_info&cPath=20_3&products_id=307  Recommend Qty 2 so you can read both the stove top and the chimney pipe.   For options I selected 6 foot with mini connector.  I really like the mini connector they make it easy to disconnect and swap around thermocouples.   

- Female Panel mount connector for K thermocouple (Round)  https://www.auberins.com/index.php?main_page=product_info&cPath=61_62&products_id=426  Qty 2  These are what the thermocouples plug into.

- K type Thermocouple extension wire  https://www.auberins.com/index.php?main_page=product_info&cPath=20_3&products_id=179  Connects the above connectors to the thermocouple amplifiers.  A couple feet (aka Qty 2) ought to be enough.

NOTE: Auber Instruments also sells a K type thermocouple probe but I have not tried it out.  The chimney pipe thermocouple gives me a good enough of a reading on the outsdie of the pipe without having to drill the stack.  Auber also sells all kinds of Temperature Controllers if you are looking for a more canned solution than what is involved with this builder project.

- Eclipse Magnetics Ltd 826 Shallow Pot Magnet.  Qty 1 or 2.   Try ebay or amazon.   I use this small magnet on the top of my stove to hold the thermocouple in place.  The grate on top is shallow so this magnet is perfect.  The pipe thermocouple is held in place using one of the chimney section screws.  No magnet required.  There are lots of options for magnets.  Remember to always use Alnico magnets so they will withstand the high temperatures (about 500C) when used on a wood stove.  My stove top magnet turned from red to brown to white but so far its holding on just fine.

- Eclipse Magnetics Ltd E821 Alnico Button Magnet 1.5 lb.  Try ebay or amazon.  Qty 2.  I use a couple of these magnets to hold the thermocouple wire in place on the back side of the stove.  


OPERATING SYSTEM:

1) Download the latest Raspian Jessie Lite OS from http://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2017-07-05/2017-07-05-raspbian-jessie-lite.zip and save it to disk.  Will the latest Stretch version work?  Haven't tried it so I don't know.

2) Unzip and install the .img on your MicroSD flash card.  This step is operating system dependant.  I use linux so just insert the flash into the card reader and it's just a quick couple of commands to find the target device and dd the .img file to it.

Example:

# Find the MicroSD device name
sudo fdisk -l 	

** For me the 32 GB micro SD is recognized as /dev/sdc **

# DD the image to the /dev/sdc disk.
** Be REALLY careful to replace /dev/sdc with the right device name **
sudo dd bs=4M if=2017-07-05-raspbian-jessie-lite.img of=/dev/sdc

# Flush the write before removing the disk from the reader.
sync

3) Remove the MicroSD card from the reader and PLUG IT BACK IN.  Linux should detect that the flash now has two partitions.  Mount the partitions.    

4) Create an empty file called 'ssh' on the 'boot' partition.  This will allow you to ssh to the Pi when you boot it up. https://learn.adafruit.com/adafruits-raspberry-pi-lesson-6-using-ssh/enabling-ssh.  You can also just boot the Pi with keyboard and monitor attached avoiding this step.

5) Unmount and remove the MicroSD card from the reader and plug it into the Pi

6) Connect the Ethernet to your local LAN.

7) Connect the 5VDC power supply.  You should see the red and green LEDs ont the Pi flash as the OS boots

8) Login via SSH using userid pi and password raspberry

example: ssh pi@192.168.1.199 (replace 192.168.1.199 with whatever ip address your router assigned).

9) Configure Raspian using raspi-config

sudo raspi-config

At the very least do the following:

1. Change User Password
2. Change Hostname to 'trainman'
3. Interfacing Options SSH Enable
4. Interfacing Options I2C Enable
5. Localisation Options > Change Wi-fi Country
6. Advanced Options > Expand Filesystem
7. Internationalization > Set Wifi Country

Select reboot now when exiting.

10) SSH back on to confirm you can still talk to it.


HARDWARE BUILD:

1) Solder the 2X20 pin header that comes with the kit onto the the Pi Hat board

2) Solder the 1x10 pin header onto the ADC board.

3) Solder the 1x4 pin headers onto the Thermocouple Amplifer boards.

4) Grab one of the 0.1" Female Headers from your 5-pack and snip off one 10 section and three 4 pin sections.  Wear glasses when do this.  Stuff goes flying.  You will lose a pin slot for every cut you make.  These 4 peices will use up about one stick.   

5) HOLE NUMBERING: Look at the top side of your Perma-Proto Pi HAT.  Along the top row are 25 holes that give you access to most of the 2x20 pins on the Pi.  They are individually labeled so I use that label when referring how to wire them.

Not so with the holes below this row.  There is just a grid of unlabeled holes.  For convention I will call the upper left hole A1 (it's next to the SCL and TXD hole), The upper right hole I refer to as W1 (next to the #21 hole).  The line of holes below them are A2 thru W2. You can probably figure out the numbering scheme from there.  There are a total of 14 rows.

6) HOLE INTERCONNECTIONS: If you look closely at the back side of the Perma-Proto Pi Hat board you should notice:

 - All the holes from A1 to W1 are interconnected +3VDC.  
 - All the holes from A2 to W2 are interconnected GND.
 - All the holes from C13 to O13 are interconnected +5VDC.
 - All the holes from C14 to O14 are interconnected GND.
 - A3 thru A7 are interconnected, same goes for B3 thru B7 and so on across the grid
 - A8 thru A12 are interconnected, same goes for B8 thru B12 and so on across the grid
 - P8 thru P12 are missing instead there is a slot for the camera ribbon cable that you wont likely be using.  Awwww.

7) SOLDER FEMALE HEADERS TO THE BOARD

 - Solder the 1x10 Female Header to holes N7:W7
 - Solder the 1x4 Female Headers to holes C8:F8, J8:M8, Q8:T8

8) SOLDER POWER WIRES: All wire is Solid AWG22 of specified color.  Both the ADC and the AMPs use 5VDC for power.  I standardize the color of the wire when possible to reduce confusion.  Black is GND and Red is +5VDC.  There is leeway in which holes can be used but would recommend staying away from rows 6 and 9.  It is very easy to melt the female headers with a soldering iron.

 - GND For ADC and AMPS: Black D11-D14, K11-K14, R11-O14, O5-N14
 - +5VDC For ADC and AMPS: Red C10-C13, J10-J13, Q10-O13, N5-M13

9) SOLDER THE I2C WIRES FOR THE ADC:  These are used by the Pi to talk to the digitizer module.  I use Blue for Clock and Purple for the Data.

 - SDA for ADC: Purple SDA-Q4
 - SCL for ADC: Blue SCL-P3

10) SOLDER THE ANALOG SIGNAL LEVEL WIRES BETWEEN THE ADC AND THE AMPs:  These wires carry the analog voltage level representing the tempeature detected by the thermocouple to the correct channel on the ADC.  Higher temperature means higher voltage.  The ADC reads the voltages and digitizes the signal voltage versus ground and makes these values available to be read by a call to the I2C bus.   I use whatever colors are leftover for miscellaneous things like signal wires and GPIO pins.  

 - Analog Level from AMP#1: Brown  E10-T4
 - Analog Level from AMP#2: Orange L10-U4
 - Analog Level from AMP#3: Yellow S10-V4

