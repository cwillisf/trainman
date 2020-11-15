# Trainman2: Display stove, pipe and room temperatures on alphanumeric LED displays

PHASE DESCRIPTION:

Remote monitoring of wood stove temperature is great but also very useful is being able to read those tempuratures while in the room.  The Adafruit quad alphanumeric displays are large, bright and easy to ready at least 20 feet away.  In this phase a full sized Perma-Proto board is used to mount up to six alphanumeric displays of various colors.  It is possible to use the half-size Perma-Proto if you only need 4 displays or even a quarter-size Perma-Proto for 2.  I have tried to make the wiring on the display board modular enough that it is easy to downsize it if desired. 

Quick note about LED colors: The Quad Alphanumeric Display with I2C Backpack comes in six different colors:  My favorites are Red, Yellow and Green.  I like the way they look together.   The other available colors: White, Blue, Yellow-Green will work but are less than ideal for this application.  White might be tiring to look at.  I can't read the Blue very well from across the room and Yellow-Green is rather dim.

Quick note about Voltages:  The Pi3 does not have very much current available on the 3.3VDC pin. You can run one or two of the LED backpacks directly off the 3.3VDC pin but the light output might flicker and it might cause OS stability issues.  It is much better to drive the displays with 5VDC and use an inexpensive Buck Converter to drop the 5VDC power supply down to 3.3VDC.  

This phase requires soldering on a 4 port terminal block onto the Pi-Hat board that shares the same pin rows as the +5V,GND,SDA,SCL pins of the ADC.    


HARDWARE REQUIRED:

- A working TRAINMAN1 Board and Raspberry Pi3 from Phase1.

- More AWG22 Wire (Red, Black, Blue, Purple) from Phase1.

- Another Female header 36-pin 0.1" from Phase1. 

- Adafruit 1606 Perma-Proto Full-sized Breadboard PCB - Single https://www.adafruit.com/product/1606

- Adafruit 1911 (Qty 2) Quad Alphanumeric Display Red with I2C Backpack. https://www.adafruit.com/product/1911

- Adafruit 2158 (Qty 2) Quad Alphanumeric Display Yellow with I2C Backpack. https://www.adafruit.com/product/2158

- Adafruit 2160 (Qty 2) Quad Alphanumeric Display Green with I2C Backpack. https://www.adafruit.com/product/2160

- Adafruit 2745 LM3671 3.3V Buck Converter Breakout 600mA. https://www.adafruit.com/product/2745

- Adafruit 2137 (Qty 2) Terminal Block 4-pin 0.1" Pitch. https://www.adafruit.com/product/2137

- Adafruit 760 Premium Male/Male Jumper Wires - 40 x 12". https://www.adafruit.com/product/760


HARDWARE BUILD:

1) *ON THE PI-HAT BOARD*. Solder anothe 4 port terminal block to the slot right in front of the ADC SDA,SCL,GND,5VDC pins.  The terminal block will be almost touching the 1x10 pin ADC female header.  Make sure the holes are pointing away from the female header so you can wire to the block later.

2) Solder together the six Quad Alphanumeric displays as per instructions on the Adafruit web site for the product.  Address the displays as follows: Red 000, Yellow 001, Green 010, Red 100, Yellow 101, Green 110.   This will translate into I2C addresses: 0x70,0x71,0x72,0x74,0x75,0x76.   For the demo code I made the last three displays: Blue 011=0x73, White 101=0x75, Yellow-Green 110=0x76.

3) Solder together the 3.3V Buck Converter board

4) Cut a stick of Female header into six pieces with 5 intact pins each.   These will be used to hold the Quad Alphanumeric Displays.

5) *ON THE DISPLAY BOARD* Solder on the six pieces into slots J8:J12, J28:J32, J48:J52, A8:A12, A28:A32, A48:A52.  Its helpful to just tack the end pins with a bit of solder to make sure they are well seated and straight with the pins centered in the holes.  Also, using the completed backpacks helps align these header slots before soldering all the pins.

6) Solder the Buck Converter directly to the display board E3:E6.   Mounting in a 1x4 female header would have been ideal but there is not enough vertical room for that.

7) Solder the second 4 port terminal block to the display board A23:A26.  Make sure the open holes are pointing downward.

8) Look at the pictures of the board to figure out the wiring.  I wired on the front of the board which is opposite of the board wired in phase1.  The black female header connectors are just too easy to melt with the soldering iron so it is better to solder on the backside.

9)  The 4 port terminal block pins are 5VDC,GND,SDA,SCL from left to right.  The 5VDC and GND are wired down to the bottom + rail using Red and Black wire.  

10) 5VDC goes to Vin on the Buck Converter using Red wire.  3V coming out of the Buck Converter is wired up to the upper + rail using Orange wire.  

11) The rest is easy but there are a lot of jumper wires and soldering to do for six displays.  Each 1x5 female header must be wired 5VDC,5VDC,GND,SDA,SCL from left to right using Orange,Orange,Black,Purple,Blue wire.


INSTALLATION:

1) Take your Male/Male Jumper Wire ribbon cable and strip off a set of 4 wires.  I like using the colors White,Grey,Purple,Blue for 5VDC,GND,SDA,SCL.  Mark the White wire with Red tape if desired. 

2) Wire the Pi-Hat display block to the Display Board.  The Pi-Hat goes Blue,Purple,Grey,White from left to right and the Display board is reverse order.

3) Mount all the Displays onto the display board.

4) COPY THE SCRIPT AND CHECK DISPLAYS

Log into the Pi and copy the trainman2.py script to the Pi

Run i2cdetect command to display bus addresses that are in use.

pi@trainman:~ i2cdetec -y 1
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: 70 71 72 -- 74 75 76 --   

These values should match up with your displayaddr variable in trainman2.py
e.g. displayaddr=[0x70,0x71,0x72,0x74,0x75,0x76]

5) INSTALL SOFTWARE TO DRIVE THE LEDS

pi@trainman:~ git clone https://github.com/adafruit/Adafruit_Python_LED_Backpack.git

pi@trainman:~ cd Adafruit_Python_LED_Backpack

pi@trainman:~ sudo python setup.py install

6) Kill the existing trainman1.py if running and run the new trainman2.py

pi@trainman:~ pkill trainman1.py

pi@trainman:~ ./trainman2.py
Starting Main Loop, press Ctrl-C to quit...
stovetemp=71 pipetemp=73 roomtemp=74 bright=3
stovetemp=70 pipetemp=73 roomtemp=74 bright=3
stovetemp=70 pipetemp=73 roomtemp=74 bright=3
stovetemp=70 pipetemp=73 roomtemp=74 bright=3
stovetemp=70 pipetemp=73 roomtemp=74 bright=3
stovetemp=70 pipetemp=73 roomtemp=74 bright=3
stovetemp=70 pipetemp=73 roomtemp=74 bright=3
stovetemp=70 pipetemp=73 roomtemp=74 bright=3
^CCaught Interrupt, running Deinitializing
Done, Exiting

7) If it works you can update your /etc/rc.local file to run the new version on boot

pi@trainman:~ sudo vi /etc/rc.local


THE CODE:

1) The displayaddr=[] array contains a list of I2C addresses for the displays.  This has to match up with the messages set in the set_display_text() function.

2) Brightness can be increased from 0 (off) to 5 (very bright).  New brightness profiles can be created and you can tweek individual brightness on a display basis to boost YellowGreen or tone down White or whatever.

3) There is an Interrupt Handler for catching Cntr-C and kills from the OS.  This way the display doesn't end up in a scrambled state.  It should blank out the LEDs when the program exits.



