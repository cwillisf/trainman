# Trainman4: Adding accurate room temperature to the DISPLAY LEDs.

PHASE DESCRIPTION:

Having accurate and easy to read room temperature is a great idea when heating with a wood stove.  Sometimes you might feel cold and the room is actually quite warm.  Or the room is warm but you feel cold.   The latter is problematic because it is too easy to just load up the stove and go for another burn and make the room way too hot.  Glancing at the room temperature allows for more control and comfort.   
I run my wood stove in batch mode and let the front room cool down overnight which saves wood and makes it easier to sleep.  A quick look at the time and room temperature is all I need to do to know if I should load up more wood and if so approximatly how much wood.

Of course, room temperature display is only the start.  It is possible to add in burn rate control based on temperature of the room by adjusting fan speed, air control or stove thermostat if your stove has one.

Please note that there are a vast multitude of ways to add this capability.  I just happen to have an OWServer already setup for my other automation project which sensors in many rooms as well as on the upper and lower elements of the electric water heater.   Feel free to modify the code and adapt it to whatever method you desire.


HARDWARE REQUIRED:

- A working TRAINMAN3 Board and Raspberry Pi3 from Phase3.  

- Embedded Data Systems OW-SERVER 1-Wire to Ethernet Server
https://www.embeddeddatasystems.com/OW-SERVER-1-Wire-to-Ethernet-Server-Revision-2_p_152.html 

- Embedded Data Systems OW-ENV-T DS18B20 Wall Mount Temperature Sensor
https://www.embeddeddatasystems.com/OW-ENV-T--DS18B20-Wall-Mount-Temperature-Sensor-_p_193.html

PROBLEM DESCRIPTION:

Trainman1 allows for up to three thermocouples to be measured.   The third thermocouple can be used to measure the temperature of the air next to the stove.  Right next to the stove is not a great place to measure temperature and the thermocouple is not accurate down to 0.1 degrees F like a 1-wire temperature sensor is.  In Phase 4 the code is modified to replace the 3rd thermocouple read with a read from the OW-Sserver.   With the temperature sensor physically separated from the trainman Raspberry Pi the sensor can now be placed with out any restrictions.   There is even a WiFi version of the OW-SERVER available now in the case you don't have ethernet cabling wired to the Pi.

Temperature sensor placement is a tricky thing.  I started out putting room sensors 1 foot from the floor but they read too cold.  I placed one sensor on the celing but it reads too hot.  After a lot of thought I think the best location is a temperature sensor that is as close as possible to where you spend most of the time in the room.  For the the front rooms with the wood stove that location is right next to the recliners for watching TV.   Why?  When you aren't moving around a lot is when you will notice being cold.   If you feel cold then is it because the room is cold?  If so, how cold is it?  A temperature sensor right next to your sedentary location will give you those answers.

HARDWARE BUILD:

There are no modifications to the Pi-Hat board, display or fan controller with the phase.   Instead there is the owserver and sensor setup which is documented by the owserver.   Configuration involves setting the IP address, OID and SNMP community of the temperature sensor.

INSTALLATION:

1) Setup the OWServer and Wire up the 1-Wire temperature sensor as per the manual.

2) Install the PYSNMP module on the Pi.  
sudo pip install pysnmp 

3) Install SNMP on the Pi if you need snmpwalk command
sudo apt-get install snmp

4) Do and SNMP Walk on the OWServer and determine the OID of the sensor.  Replace 192.168.1.17 with the IP address of the OWServer.  If you have changed the community from the default of 'public' to something else modify that as well in the following line.

snmpwalk -v2c -c public 192.168.1.17 iso.3.6.1.4.1.31440.10.5.1.1

example output:
iso.3.6.1.4.1.31440.10.5.1.1.0 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.1 = STRING: "24.0000"
iso.3.6.1.4.1.31440.10.5.1.1.2 = STRING: "15.8125"
iso.3.6.1.4.1.31440.10.5.1.1.3 = STRING: "50.0000"
iso.3.6.1.4.1.31440.10.5.1.1.4 = STRING: "44.1875"
iso.3.6.1.4.1.31440.10.5.1.1.5 = STRING: "23.1250"
iso.3.6.1.4.1.31440.10.5.1.1.6 = STRING: "21.1875"
iso.3.6.1.4.1.31440.10.5.1.1.7 = STRING: "22.4375"
iso.3.6.1.4.1.31440.10.5.1.1.8 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.9 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.10 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.11 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.12 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.13 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.14 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.15 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.16 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.17 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.18 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.19 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.20 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.21 = Hex-STRING: 00 
iso.3.6.1.4.1.31440.10.5.1.1.22 = Hex-STRING: 00 

I have a bunch of sensors on my OWServer so this command creates a lot of output.   The reading are in degrees Centegrade.  The two highest are the water heater upper and lower elements (50.000 and 44.1876).  The next highest (24.0000) is the room with the wood stove.   So my OID for the sensor is iso.3.6.1.4.1.31440.10.5.1.1.1.   

5) Copy trainman4.py to your Pi and modify the config for the OWServer IP Address, OID and Community.  Remember to 'pkill trainman3.py' first in case you have that auto started from phase 3 of this project. 

6) If it works you can update your /etc/rc.local file to run the new version on boot

pi@trainman:~ sudo vi /etc/rc.local


THE CODE:

# OWS One Wire Server Configuration: In this phase of project adds a One-Wire temperature server and sensor.  
# There are many ways to accomplish the acquistion of room temperature.  I just happen to have this One-Wire server
# setup for other projects so might as well just use the existing temperature sensor and server.
# This code supports a single temperature sensor but is easily adaptable for more if required.
# Currently the room temperature is just displayed on the first Green LED display.  It could be used for thermostat control.
owhost      = "192.168.1.17"                    # IP address of the OWServer
owoid       = "iso.3.6.1.4.1.31440.10.5.1.1.1"  # Use snmp walk to figure this out
owcommunity = "public"                          # Default is typically public

# Get the temperature in farenheit from an OWServer given the OID and the Community name
# Returns value in F rounded to 1 decimal place
def get_owserver_tempf(owhost,oid,community):
    print "Getting OWServer",owhost,oid

    errorIndication, errorStatus, errorIndex, varBinds = next(
        SNMP.getCmd(SNMP.SnmpEngine(), SNMP.CommunityData(community, mpModel=1),
        SNMP.UdpTransportTarget((owhost, 161)), SNMP.ContextData(),
        SNMP.ObjectType(SNMP.ObjectIdentity(oid)))
    )
    if errorIndication:
        print(errorIndication)
    elif (errorStatus):
        print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        tempc = float(varBinds[0][1])
        tempf = round(tempc * 1.8 + 32,1)
        return tempf

# Get roomtemp from owserver 1-wire temperature sensor every so often
if (x % 30) == 0:
    roomtemp = get_owserver_tempf(owhost,owoid,owcommunity)


