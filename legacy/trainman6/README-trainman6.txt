# Trainman6: Automatic air control based on stove and pipe temperature, Burn states, User control over automatic air control

PHASE DESCRIPTION:

Controlling air based on soley pipe temperature works quite well but it would be nice to quench off the air in the latter part of the burn.   Non-catalytic stoves tend to work most efficiently when the air is quenched off enough for the smoke to burn in the firebox giving a lively secondary fire show.   If the air is open too much there are lively flames but little in the way of secondary burn with a lot of the heat going up the chimney.   If the air is closed down too much or too early the fire will smoulder, also not providing much in the way of secondary burn.   Modulating the air based on stove top temperature allows for the most efficient non-catalytic burn.

HARDWARE REQUIRED:

- A working TRAINMAN5 Board and Raspberry Pi3, Adafruit MotorHat, Stepper Motor and mini gantry and rail from Phase 5.

PROBLEM DESCRIPTION:

- A linear relationship for air control between pipemin (100% air) and pipemax (0% air) works quite well in the initial part of the burn.   We can use the same logic for stovemin (100% air) and stovemax (0% air) for controlling air in the latter part of the burn when stove top temperatures are more critical and give a better indication of what is going on.

- Also stovemax can be varied (between 500F and approx 750F) to allow macro control of the burn process.   Similar in the way that fan profile are used to allow macro control over the fan profile while the program micro manages the fan speed, air profiles can be defined to allow control over the stove max parameter.   

- Automatic stovemax profiles can be setup to automatically peel back the stove max temperature based on room temperature.  The logic being that when the room is cold we want the stove to give off a lot of heat and warm the room up quickly.  Once the room is warm we can have the stovemax reduced which will help to keep the room from over heating as well as provide extended burn times.

HARDWARE BUILD:

Nothing new in this phase

INSTALLATION:

Nothing new in this phase.  Just a new trainman6.py program.  Copy trainman6.py to your Pi and modify the config for the OWServer IP Address, OID and Community.  Remember to 'pkill trainman5.py' first in case you have that auto started from phase 5 of this project. 

If it works you can update your /etc/rc.local file to run the new version on boot


MAJOR CHANGES TO THE CODE:

# Using the airpro variable, the airprofiles array and the current roomtemp the stovemax parameter is calculated.
stovemax = calc_stovemax()

# Besides pipeair, also calculate stoveair (the number of steps left from 0% air) based on stovemin, stovemax and stovetemp.
stoveair = airsteps - (airsteps * (stovetemp - stovemin) / (stovemax - stovemin))
stoveair = max(min(airsteps,stoveair),0)	# Limit: airsteps >= stoveair >= 0

# The actual air values used to control the air supply is simply the minimum of stoveair and pipeair. 
calcair = min(stoveair,pipeair)

# For fun and ease of use I use the stovetemp, pipetemp and air setting variables to calculate and display the air percentage value of the current air position and if the program is regulating according to pipetemp or stovetemp.   If the stove is in 100% airstate display various informational states like: IGNT, BURN, HEAT, HOT, WARM and COOL.
state = calc_stove_state()

# Few tweeks to batch air control movements together and update air when temperatures are rapidly changing.  It would be distracting to have the air control moving all the time.

# Cleaned up a bunch of routines and moved stuff that was in the main loop into their own separate functions like read_adc() and control_fan()


NEXT UP:

1) Wall bracket for LED, PI, Motorhat and Thermocouple ports

2) Rotary Encoder or Switches to allow for better control over air and fan profiles.

3) Manual override/kill switch for stepper motor.

4) Limit switches for stepper motor operation.

