# Trainman3: Adding Automatic Fan Speed control based on stove top tempeture.

***WARNING DANGER!!!: Attempting this will void your blower fan warranty, obliterate its UL listing and is electrically dangerous because it involves modifications to wires that carry 120 Volts AC.   If you don't know how safely deal with 120VAC just don't do it.  Remember to unplug the blower fan and keep it unplugged while messing around with an open blower fan.  Using GFI outlet while messing around with it is a very good idea.

PHASE DESCRIPTION:

Being able to have the system automatically turn on and vary the blower fan has been really great.  I don't have to stop what I am doing and turn on the fan when the stove gets up to temperature.    If it gets really hot the the blower will go on full speed and let me know that the air control might need to be quenched off a bit.    When the burn is done, the speed is slowed down and then turned off.  I'm not wasting power running a fan that has been forgotten about.   I'm not blowing air off a cold stove creating a draft in the room.  Minimal power, Minimal noise, Minimal fuss.

This phase requires soldering on a 6 port terminal block onto the Pi-Hat board and wiring those to 5Volts, GND and 4 of the GPIO pins.


HARDWARE REQUIRED:

- A working TRAINMAN2 Board and Raspberry Pi3 from Phase2.  Please NOTE I have reworked the board so that the ADC terminal is at the opposite ends.   This allows shorter I2C wires and better placement of all the GPIO wires for the fan control and future button control.

- More AWG22 Wire (Red, Black, Brown, Orange, Yellow, White) from Phase2.

- 6-pin 0.1" terminal block for the fan controller.

- 7-pin 0.1" terminal block.for future buttons.

- Speed Control Model KBMS-13BV if you have a 120 Volt AC fan up to 2.5 amps load current

- SainSmart multi-channel 5volt opto-isoloated active-high solid state relay module.  
https://www.sainsmart.com/products/4-channel-5v-solid-state-relay-module

- A variety of resistors to acheive the fan speed for your blower fan, mostly in the 1 to 100K Ohm range.

- Set of 6 Jumper wires to connect the Fan Controller to the PiHat.  I use a set of Male-Male and Female-Male 6 wire ribbon cable to create a long harness that can be easily plugged/unplugged.

- Three-Way rocker switch On/Off/On with 6 terminals on the back to replace the simple 2-Way rocker On/Off switch.  The one that worked with my blower is KCD1 6A 250VAC/10A 125VAC On/Off/On Rectangular Rocker Switch 3 pin SPDT snap in type switch.
https://www.aliexpress.com/item/10-Pcs-x-AC-6A-250-V-10A-125-V-3-Broches-SPDT-ON-OFF-ON/32770263931.html
https://wholesaler.alibaba.com/product-detail/switch-rocker-dpdt-16a-250v-kcd1_60333960418.html 


PROBLEM DESCRIPTION AND INVENTED SOLUTION:

My stove is a Pacific Energy Classic.  The blower is nice and quiet on moderate speed, they cost about 300$.    There is a simple On/Off switch on the side with the speed control potentiometer and the stove comes with a snap switch that doesn't do what I want when I want.    Im not a EE so I haven't studied anything remotely close to a variable speed AC fan controller so when I busted open the blower in the back I was surprised to find this ...

Speed Control KB Electronics Model KBMS-13BV
http://www.kb-controls.com/product.sc?productId=158

Inside the plastic box is a small circuit board which has a bunch of compoenents soldered onto it as well as the and the large speed control potentiomter with a small trim speed potentiometer.  

At first I thought I was done ... there is no easy way to automatically vary the fan speed.   After a bit of reasearch I discovered that the circuit board is a DIAC/TRIAC (Thyristor) circuit and they have been around for quite some time.   Instead of the potentiometer reducing the voltage to the fan motor, browning it out (which would be bad), the Thyristor chops the AC waveform so peak voltages are maintained but the time that the motor sees voltage is reduced.

Basically, the fan speed is controlled by the triggering of the TRIAC.   The potentiometer varies the resistance that controls the triggering.   Higher resistance slows the fan.   Lower resistance speeds up the fan.

Awesome!  Wanting to do more experimentation but not wanting to wreck what I have, I bought a replacement speed control and using a soldering iron and solder vacumm I removed both the big potentiometer and the small blue trim pot and in thier place attached red+orange lead wires.   I could then (with a great deal of care) play around with various resistors and vary the speed of the fan.  

That's great but how does one automatically vary the resistance via a Raspberry Pi?    It might be possible to integrate a digital potentiometer into the circuit but I would still have to deal with turning the fan on/off, so instead I chose a 4 channel solid state relay board for this purpose.

https://www.sainsmart.com/products/4-channel-5v-solid-state-relay-module

This board is nice because it is optically isolated 5Volt active high which is perfect for integrating 120VAC with the Pi.  Also the current capacity of the solid state relay (0.1 to 2 AMP) will handle the limited amperage of the blower fan.   So I used one relay to turn the fan on/off and the other 3 to vary the resistances to the speed controller.

Which resistances to use? 

Simple answer. 
- Figure out the resitance of the slowest desired fan speed (For me it was about 90K Ohms).
- Select 3 available resistors that add up to this resistance that are roughly multiples of 1x,2x,4x (For me these ended up being 12K,27K,47K).  When wired in series the resistances are additive: 12K + 27K + 47K = 86KOhms

Once that is figured out, 3 sainsmart relays are used to individually short out these 3 separate resistors.  When a resistor is shorted its resitance is removed from the series.  Using various combinations of On/Off for the relays allows for 8 different resistance and 8 different fan speeds when the on/off relay is triggered on.    Its easier to figure this out looking at the following table.   The first relay simply turns the 120 VAC power to the motor on/off.   Remember! don't stick your fingers in it when plugged in.  ZAP!

FanSpeed Relay    Resistances     Total  Speed
=====================================================
  0      0,0,0,0  Blower Motor Off              Off
  1      1,0,0,0  12K + 27K + 47K  = 86K  Slowest
  2      1,1,0,0   0K + 27K + 47K  = 74K    ^
  3      1,0,1,0  12K +  0K + 47K  = 59K    |
  4      1,1,1,0   0K +  0K + 47K  = 47K     |
  5      1,0,0,1  12K + 27K +  0K  = 39K    |
  6      1,1,0,1   0K + 27K +  0K  = 27K     |
  7      1,0,1,1  12K +  0K +  0K  = 12K    V
  8      1,1,1,1   0  +  0K +  0K  =  0K    Maximum

I was kind of stunned to see it actually work in the end.  I cleaned up the install by replacing the 2 way On/Of switch with a 3 way switch that turns the fan Manual/Off/Auto.  
The wiring is basically:   120VAC Hot/BlackWire ---> 3-Way-Rocker-Switch ---> On/Off Relay ---> Speed Control ---> Fan Motor ----> 120VAC Neutral/WhiteWire.  
The Manual versus Auto setting selects which speed control is active.  (Manual for the original Speed Controller, Auto goes to the Sainsmart+Hacked Speed Controller).

4 GPIO pins on the Pi control the SainSmart relayboard.  I feed it 5VDC as well as GND so it uses a 6 wire harness to connect to a 6 pin terminal block on the trainman perma proto board.  


HARDWARE BUILD:

1) *ON THE PI-HAT BOARD*. Solder anothe 6 pin terminal block next to the ADC 10-pin black female header.  This will be used for the wiring harness that connects the PiHat to the Fan Speed Controller.  Make sure the holes are pointing away from the female header so you can wire to the block later.  There should also be room to solider on a 7 pin terminal block right next to that.  This will be used for future buttons.  Its useful to place and solder both terminal blocks at this time rather than later because it might not fit later on.

2) From Left to right solder on the 6 pin Fan Controller part of the board:
* Red    5VDC - powers the solid state relay module
* Black  GND  - ground
* Brown  #17  - relay to turn 120VAC fan on/off
* Orange #27  - lowest resistor short
* Yellow #22  - middle resistor short
* Green  #23  - highest resistor short

3) While you are at it you might as well solder on the wires for the 7 pin Button Box part of the board
* Red    #18  - 3.3VDC PWM for dimmable power to illuminated momentary buttons
* Black  GND  - ground
* Brown  #24  - button1
* Orange #25  - button2
* Yellow #5   - button3
* Green  #6   - button4
* White  #12  - button5

4) Modify the speed control by removing both the big speed conrol potentiometer and the small blue trim potentiomter.  Wire in leads in the spots shown in  the picture.

4) Unplug the fan controller and rewire it with the 3-way rocker switch, 1st Relay of the Solid State Relay Module, Speed Controller before going to the motor.

The wiring is basically:   120VAC Hot/BlackWire ---> 3-Way-Rocker-Switch ---> On/Off-Relay ---> Speed Control ---> Fan Motor ----> 120VAC Neutral/WhiteWire.  

5) Add resistors and jumper wire to the relays 2, 3 and 4 of the Solid State Relay Module.  The relays will short out these 3 resistors individually.  Wire in the speed control so it sees the various resistances presented by the series circuit of the resistors and relays.

6) Wire the controller blocks on the Solid State Relay module to the Fan Controller Block on the PiHat.  See picture for wiring example.


INSTALLATION:

1) Copy the trainman3.py script to the Pi and run it.  Remember to 'pkill trainman2.py' first in case you have that auto started from phase 2 of this project. 

2) If you want to modify the 8 speeds enabled by this setup be sure to unplug the 120 VAC fan controller frrom the wall before touching it.  You can the try various resistors, higher resistance will slow the fan, lower will speed it up.

3) Once its working the way you want, mount the Solid State Relay Module in a small metal box using some standoffs.  I used velcro to keep the module and the speed controller in place.  Reassemble the blower fan with the wiring hardness hanging out and remount it on the wood stove.  Connect the fan harness to the PiHat fan terminal block and test. 

4) If it works you can update your /etc/rc.local file to run the new version on boot

pi@trainman:~ sudo vi /etc/rc.local


THE CODE:

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




