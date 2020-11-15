# Trainman1: Read stove and pipe temperatures using thermocouple amplifiers and an analog digitizer.  

PHASE DESCRIPTION:

Accurate temperature monitoring is the key to automating any kind of process that involves heat.  In this starting phase the Raspberry Pi is configured and the trainman hardware board is soldered together.  A PermaProto HAT Mini Kit is used to wire together the thermocouple amplifiers to the analog digitizer.  This HAT is then mounted onto the Raspberry Pi allowing it to talk to the digitizer.   The main loop of the trainman1.py script reads the analog digitizer, formats the output and writes it to a log file.   Sounds simple right?  Well there are a few tricks to getting it all up and running on the stove as you will see.  This project can be easily modified to monitor an oven, smoker or barbeque.

HARDWARE REQUIRED:

- Raspberry Pi 3 - Model B   https://www.adafruit.com/product/3055  Do you have to buy this from Adafruit?  No.  Will a Pi2 work?  Probably, but I like the built in WiFi of the Pi3.

- Micro SD Card - https://www.adafruit.com/product/2767  Recommend at least 8GB.  I actually like Sandisk Ultra 32GB Micro SD Cards.

- 5V 2.4A Powersupply MicroUSB - https://www.adafruit.com/product/1995

- Adafruit P2310 Perma-Proto HAT for Pi Mini Kit  https://www.adafruit.com/product/2310  Get the one with No EEPROM if you can.

- Adafruit P1778 Analog Output K-Type Thermocouple Amplifier AD8495 Breakout.  https://www.adafruit.com/product/1778  Qty 3, Recommend you get at least 2 so you can digitize both stove temperature and chimney pipe temperature (2 separate thermocouples).  Trainman will handle up to 3.  The last one can maybe be used for a chimney pipe probe or a room temperature sensor.  It is always a good idea to have extras for debugging, spares and future projects.

- Adafruit P1085 ADS1115 16-Bit ADC - 4 Channel with Programmable Gain Amplifier.  https://www.adafruit.com/product/1085  Qty 1.  Trainman uses up to 3 of the 4 channels leaving one left over for further experimentation and mischief. 

- Adafruit 598 36-pin 0.1" Female header - pack of 5  https://www.adafruit.com/product/598  The headers are soldered onto the HAT and then the thermocouple amplifiers and ADC plug into them.  Makes for a nice modular install

- Adafruit 3174 Hook-up Wire Set 22AWG Solid - https://www.adafruit.com/product/3174  Using different colors for Neg,+5VDC,Control,Data,etc organizes the wiring on the board.

- Adafruit 1008 Small Alligator Clip Test Leads - https://www.adafruit.com/product/1008  You need to ground the Pi to the Stove.  I found the easiest way to do this is to take an alligator clip and put one end on the USB port and the other end on the metal braid sheath that surrounds one of the thermocouples.

- K type Thermocouple, Washer Probe  https://www.auberins.com/index.php?main_page=product_info&cPath=20_3&products_id=307  Recommend Qty 2 so you can read both the stove top and the chimney pipe.   For options I selected 6 foot with mini connector.  I really like the mini connector they make it easy to disconnect and swap around thermocouples.   

- Female Panel mount connector for K thermocouple (Round)  https://www.auberins.com/index.php?main_page=product_info&cPath=61_62&products_id=426  Qty 2  These are what the thermocouples plug into.

- K type Thermocouple extension wire  https://www.auberins.com/index.php?main_page=product_info&cPath=20_3&products_id=179  Connects the above connectors to the thermocouple amplifiers.  A couple feet (aka Qty 2) ought to be enough.

NOTE: Auber Instruments also sells a K type thermocouple probe but I have not tried it out.  The chimney pipe thermocouple gives me a good enough of a reading on the outside of the pipe without having to drill the stack.  Auber also sells all kinds of Temperature Controllers if you are looking for a more canned solution than what is involved with this builder project.

- Eclipse Magnetics Ltd 826 Shallow Pot Magnet.  Qty 1 or 2.   Try ebay or amazon.   I use this small magnet on the top of my stove to hold the thermocouple in place.  The grate on top is shallow so this magnet is perfect.  The pipe thermocouple is held in place using one of the chimney section screws.  No magnet required.  There are lots of options for magnets.  Remember to always use Alnico magnets so they will withstand the high temperatures (about 500C) when used on a wood stove.  My stove top magnet turned from red to brown to white but so far its holding on just fine.

- Eclipse Magnetics Ltd E821 Alnico Button Magnet 1.5 lb.  Try ebay or amazon.  Qty 2.  I use a couple of these magnets to hold the thermocouple wire in place on the back side of the stove.  


OPERATING SYSTEM:

1) Download the latest Raspian Jessie Lite OS from http://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2017-07-05/2017-07-05-raspbian-jessie-lite.zip and save it to disk.  Will the latest Stretch version work?  Haven't tried it so I don't know.

2) Unzip and install the .img on your MicroSD flash card.  This step is operating system dependent.  I use Linux so just insert the flash into the card reader and it's just a quick couple of commands to find the target device and dd the .img file to it.

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

7) Connect the 5VDC power supply.  You should see the red and green LEDs on the Pi flash as the OS boots

8) Login via SSH using userid pi and password raspberry

example: ssh pi@192.168.1.199 (replace 192.168.1.199 with whatever IP address your router assigned).

9) Configure Raspian using raspi-config

pi@trainman:~ $ sudo raspi-config

At the very least do the following:

 * Change User Password
 * Change Hostname to 'trainman'
 * Interfacing Options SSH Enable
 * Interfacing Options I2C Enable
 * Localization Options > Change Wi-Fi Country
 * Advanced Options > Expand Filesystem
 * Internationalization > Set Wi-Fi Country

Select reboot now when exiting.

10) SSH back on to confirm you can still talk to it.

HARDWARE BUILD:

11) Solder the 2X20 pin header that comes with the kit onto the the Pi Hat board

12) Solder the 1x10 pin header onto the ADC board.

13) Solder the 1x4 pin headers onto the Thermocouple Amplifier boards.

14) Grab one of the 0.1" Female Headers from your 5-pack and snip off one 10 section and three 4 pin sections.  Wear glasses when do this.  Stuff goes flying.  You will lose a pin slot for every cut you make.  These 4 paces will use up about one stick.   

15) HOLE NUMBERING: Look at the top side of your Perma-Proto Pi HAT.  Along the top row are 25 holes that give you access to most of the 2x20 pins on the Pi.  They are individually labeled so I use that label when referring how to wire them.

Not so with the holes below this row.  There is just a grid of unlabeled holes.  For convention I will call the upper left hole A1 (it's next to the SCL and TXD hole), The upper right hole I refer to as W1 (next to the #21 hole).  The line of holes below them are A2 through W2. You can probably figure out the numbering scheme from there.  There are a total of 14 rows.

16) HOLE INTERCONNECTIONS: If you look closely at the back side of the Perma-Proto Pi Hat board you should notice:

 - All the holes from A1 to W1 are interconnected +3VDC.  
 - All the holes from A2 to W2 are interconnected GND.
 - All the holes from C13 to O13 are interconnected +5VDC.
 - All the holes from C14 to O14 are interconnected GND.
 - A3 through A7 are interconnected, same goes for B3 through B7 and so on across the grid
 - A8 through A12 are interconnected, same goes for B8 through B12 and so on across the grid
 - P8 through P12 are missing instead there is a slot for the camera ribbon cable that you wont likely be using.  Awwww.

17) SOLDER FEMALE HEADERS TO THE BOARD

 - Solder the 1x10 Female Header to holes N7:W7
 - Solder the 1x4 Female Headers to holes C8:F8, J8:M8, Q8:T8

18) SOLDER JUMPER WIRES

POWER WIRES: All wire is Solid AWG22 of specified color.  Both the ADC and the AMPs use 5VDC for power.  I standardize the color of the wire when possible to reduce confusion.  Black is GND and Red is +5VDC.  There is leeway in which holes can be used but would recommend staying away from rows 6 and 9.  It is very easy to melt the female headers with a soldering iron.

 - GND For ADC and AMPS: Black D11-D14, K11-K14, R11-O14
 - +5VDC For ADC and AMPS: Red C10-C13, J10-J13, Q10-O13

SIGNAL WIRES:  These wires carry the analog voltage level representing the temperature detected by the thermocouple to the correct channel on the ADC.  Higher temperature means higher voltage.  The ADC reads the voltages and digitizes the signal voltage versus ground and makes these values available to be read by a call to the I2C bus.   I use whatever colors are leftover for miscellaneous things like signal wires and GPIO pins.  

 - Analog Level from AMP0 to ChannelA0: Brown  E10-T4
 - Analog Level from AMP1 to ChannelA1: Orange L10-U4
 - Analog Level from AMP2 to ChannelA2: Yellow S10-V4

I2C WIRES AND POWER FOR THE ADC:  These are used by the Pi to talk to the digitizer module.  I use Blue for Clock and Purple for the Data.  Note: Ignore the solder points in the picture if you are planning to go to the next phase.  There needs to be a terminal block soldered on row 5 so these are all soldered on row 3

 - GND for ADC: O3-N14
 - +5VDC for ADC: N3-M13
 - SDA for ADC: Purple SDA-Q3
 - SCL for ADC: Blue SCL-P3

19) Pi Hat INSTALLATION

#Shutdown the Pi
pi@trainman:~ $ sudo halt

# Power off the Pi

# Mount the Pi Hat onto the Pi3

# Power up the Pi, wait for boot

# SSH back on
ssh pi@192.168.1.199


FINAL INSTALLATION

20) INSTALL SOFTWARE TO READ THE ADC

Read the how-to page: https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/ads1015-slash-ads1115

#Build and Install the ADC Library from Source so you get the example code
pi@trainman:~ $ sudo apt-get update
pi@trainman:~ $ sudo apt-get install build-essential python-dev python-smbus git
pi@trainman:~ $ cd ~
pi@trainman:~ $ git clone https://github.com/adafruit/Adafruit_Python_ADS1x15.git
pi@trainman:~ $ cd Adafruit_Python_ADS1x15
pi@trainman:~/Adafruit_Python_ADS1x15 $ sudo python setup.py install

# Confirm that the ADC is readable by the Pi by running example code simpletest.py
pi@trainman:~/Adafruit_Python_ADS1x15 $ cd ~/Adafruit_Python_ADS1x15/examples
pi@trainman:~/Adafruit_Python_ADS1x15 $ python simpletest.py

example output:
Reading ADS1x15 values, press Ctrl-C to quit...
|      0 |      1 |      2 |      3 |
-------------------------------------
|  32767 |  32767 |   4603 |   4607 |
|  32767 |  32767 |   4508 |   4542 |
|  32767 |  32767 |   4510 |   4541 |

Notice that channels 0 and 1 output 32767 which is digitizing the output from two thermocouple amps. Channels 2 and 3 are floating with respect to GND so they produce a changing value.

21) CONNECT THERMOCOUPLES TO AMPS

- Cut 6 inch pieces of the Thermocouple extension wire for each thermocouple

- Strip then ends and wire the thermocouple amp to the Female Panel mount connector.  Use the RED wire for NEG- and YELLOW for POS+. 

- Plug the K type Thermocouple into the Female Panel mount connector.

- If you run the simpletest.py script again you should see the value for the channel change if you warm up the thermocouple end with your hand.

22) COPY TRAINMAN1 PYTHON SCRIPT TO PI AND RUN IT

# Copy the trainman1.py Python script to the Pi3
cd trainman1   (or wherever you downloaded the trainman1 package)
sftp pi@192.168.1.199
> put trainman1.py

# SSH to the Pi3 and run the trainman1.py script
ssh pi@192.168.1.199

pi@trainman:~ $ ./trainman1.py 

Starting Main Loop, press Ctrl-C to quit...
stovetemp=69 pipetemp=68 roomtemp=1057
stovetemp=69 pipetemp=68 roomtemp=1057
stovetemp=70 pipetemp=69 roomtemp=1057
stovetemp=70 pipetemp=72 roomtemp=1057
stovetemp=70 pipetemp=75 roomtemp=1057
stovetemp=70 pipetemp=77 roomtemp=1057
stovetemp=70 pipetemp=79 roomtemp=1057
stovetemp=70 pipetemp=81 roomtemp=1057

# Pinching the end of one of the thermocouples with your warm fingers will make one of the temperatures go up.   Letting go you will see the temperature come down.

23) UNDERSTAND THE SCRIPT

Take a look at the code.  There are inline comments for most of it.  The main loop just reads the ADC, converts and scales the channel data and prints it to standard out.

24) CREATE RC.LOCAL FILE TO AUTOMATICALLY RUN SCRIPT ON BOOT UP

# Commands in /etc/rc.local are run on boot up as userid root.  This script will run /home/pi/trainman1.py and output both standard out and error to the /var/tmp/trainman log file.   You can look at the log any time using the command 'tail -100f /var/tmp/trainman'

pi@trainman:~ $ sudo vi /etc/rc.local

#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

sleep 5
su pi -c '/home/pi/trainman1.py >> /var/tmp/trainman 2>&1 &'

exit 0

25) MOUNT /var/tmp onto tmpfs (aka RAM) TO KEEP THE MICROSD CARD FROM BURNING OUT 

There is a problem with flash memory in that it will burn out quickly (sometimes in a matter of a few months) if a program keeps writing to it.  To prevent this mount the log file filesystem /var/tmp onto tmpfs.  You will lose the logs on reboot but you will keep the flash from burning out with one write per second.

pi@trainman:~ $ sudo vi /etc/fstab

proc            /proc           proc    defaults          0       0
PARTUUID=a5271f5c-01  /boot           vfat    defaults          0       2
PARTUUID=a5271f5c-02  /               ext4    defaults,noatime  0       1
# a swapfile is not a swap partition, no line here
#   use  dphys-swapfile swap[on|off]  for that
#
# Mount /var/tmp on RAM for trainman log file so SD card does not get burned out.
tmpfs /var/tmp tmpfs defaults,noatime,nosuid,size=100m  0      0

pi@trainman:~ $ sudo reboot

26) INSTALL ON STOVE

Power down the Pi and move it to a safe place near the wood stove

Attach the stove thermocouple to the top of the stove using the Agnico button magnet

Attach the pipe thermocouple to the chimney pipe using existing pipe screw if available or another magnet if not.

Dress the thermocouple wires using the Agnico pot magnets on the back and side of the stove.

Ground the Pi to the stove using an alligator clip from the Pi to a thermocouple metal braid.  Forgetting this step may cause irregular temperature readings.

Power up the Pi and start testing.






   




