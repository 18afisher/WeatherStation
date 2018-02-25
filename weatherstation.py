""" Weather Station project, Version 2.
This new version uses a Raspberry Pi 3 to create an advanced prediction
through a neural network. 
Written by Aidan Fisher, 2018. """

# Import the libraries needed for this project 
import Adafruit_BluefruitLE
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
import datetime
import uuid
import binascii
import array
import struct
from time import sleep

# Set the UUIDs from the sender module (Arduino 101) so the base module (Raspberry Pi 3)
# can grab characteristics from these UUIDs. 
receiverUUID = uuid.UUID("70f6ff21-8dc8-4234-9dd1-4688aaebedbb")
temperatureUUID = uuid.UUID("89384f53-e826-4802-adb0-f5b8cb2b1ec4")
pressureUUID = uuid.UUID("4d228b66-afb7-415e-bfab-6414ace872c4")
humidityUUID = uuid.UUID("0319bc08-264f-4e39-90b3-d1ab22117e0f")

# Set how long you want to wait until you want to receive new data
waitingTime = 10

# Initialize our temperature, pressure, and humidity values as 0.
# These are placeholder values. 
temperature = pressure = humidity = float(0)

ble = Adafruit_BluefruitLE.get_provider()

def main():
	# Clearing cache data ensures no issues with bluez, which is used by the
	# Adafruit library. 
	ble.clear_cached_data()

	# Get the BLE network adapter and power it on, then begin scanning
	adapter = ble.get_default_adapter()
	adapter.power_on()

	# Make sure to disconnect before you connect to the Arduino, because
	# it may create an error in the process 
	ble.disconnect_devices([receiverUUID])

	# Find devices, and make sure it is the Arduino 101 as the Weather Station Sender
	# If the Arduino is not found, a runtime error will be raised. 
	try: 
		adapter.start_scan()
		stationSender = ble.find_device(service_uuids = [receiverUUID])
		if stationSender is None: 
			raise RuntimeError("Could not find the sender module, please check the wiring or check if the Arduino 101 is plugged in")

	finally: 
		# Stop scanning if the Arduino has been found
		adapter.stop_scan()

	# Connect to the device. 
	stationSender.connect() 

	# Discover the UUIDs from the sender. This is needed in order to copy the characteristics.
	stationSender.discover([receiverUUID], [temperatureUUID, pressureUUID, humidityUUID])
		
	# We will need to use the service in order to grab the hex values from the characteristics
	base = stationSender.find_service(receiverUUID)

	# Find the characteristics
	# This will be used in order to grab their values. 
	temperatureChar = base.find_characteristic(temperatureUUID)
	pressureChar = base.find_characteristic(pressureUUID)
	humidityChar = base.find_characteristic(humidityUUID)

	# Grab the values in the characteristics. 
	# These values are dbus.Array values, so we will need to convert them later. 
	temperatureRaw = temperatureChar.read_value()
	pressureRaw = pressureChar.read_value()
	humidityRaw = humidityChar.read_value()
	
	# Convert the dbus.Array values into swapped float values that can be read
	temperatureSwapped = dbusArrayToSwappedFloat(temperatureRaw)
	pressureSwapped = dbusArrayToSwappedFloat(pressureRaw)
	humiditySwapped = dbusArrayToSwappedFloat(humidityRaw)

	# Convert temperature from Celcius to Fahrenheit, because we don't use French Units
	temperatureFahrenheit = ((temperatureSwapped * (9/5)) + 32)
	
	# Log the time
	currentTime = str(datetime.time())
	
	# Print the data
	print("Local time: %s, Temperature: %f°F, Pressure: %f kPa, Humidity (in percent): %f" % (currentTime, temperatureFahrenheit, pressureSwapped, humiditySwapped))
	
	# Disconnect the device, allowing it to be reconnected.
	# Also, I hate Adafruit for forcing me to use their loop. 
	stationSender.disconnect()

	# Wait some time 
	sleep(waitingTime)

# This function is used to change a dbus.Byte array into a float value
def dbusArrayToSwappedFloat(rawValue):
	hexValue = ' '.join([hex(x) for x in rawValue]) # This is formatted with 0x hex 0x hex 0x hex
	hexValueConverted = hexValue.replace('0x', ' ') # Convert to 0x and then a huge hex value

	# There are some values with 3 characters in a hex value. Removing 0x will make it one. 
	# This is catastrophic–one of these values can stop the whole program, while two can change the whole value. 
	# This code snippet makes sure a 0 is added before that 1 character hex value, allowing it to be a 2 character (4 with 0x)
	# hex value. 
	hexValueArray = hexValueConverted.split() # Create an array in order to 
	for index, value in enumerate(hexValueArray): 
		if len(value) == 1: 
			hexValueCharArray = list(value)
			hexValueCharArray.insert(0, '0')
			u = ''.join(str(h) for h in hexValueCharArray)
			hexValueArray.remove(value)
			hexValueArray.insert(index, u)
	fixedHexValue = ''.join([str(w) for w in hexValueArray])
	bytesConvertedHex = binascii.unhexlify(fixedHexValue)
	hexToFloatArrayArray = array.array('f', bytesConvertedHex)  # Convert to a weird array whose only purpose is for endianness swapping
	hexToFloatArrayArray.byteswap() # Prepare for swapping
	swap = struct.Struct('>f') # Swap endianness
	unpacked = swap.unpack_from(hexToFloatArrayArray)[0] # Make it a normal value
	return float(unpacked) # Turn it into a float and return it 

# TODO: Tell the Arduino 101 that the data has been received, and to update it with new data
# TODO: Calculate the first and second derivatives after each hour
# We want to find the first and second derivatives of each data point over an hour,
# So we can just use the average rate of change for each data point

# Initialize the BLE module and begin to scan for the receiver module (Arduino 101)
ble.initialize()

ble.run_mainloop_with(main)

# TODO: Neural Network
