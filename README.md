# WeatherStation
A weather station that uses a Raspberry Pi and an Arduino 101. This project uses the Bluetooth Low Energy (BLE) protocol to transmit data. 
The Arduino 101 has a BME280 sensor which allows it to record the pressure, temperature, and humidity of its surroundings. 
The Arduino 101 also has a built-in BLE dongle, allowing it to transmit and receive data. 
The Arduino 101 acts as a Peripheral device, allowing it to send data to a Central device.
The Raspberry Pi acts as a Central device, receiving data from the Peripheral (Arduino 101) and notifying it that it has received the data. 

The project demonstrates the ability to use Bluetooth Low Energy as a way to send and receive data, convert that data into something usable, log it into a graph, and make a decision based off that data. 

How the project (currently) works: A BME280 sensor sends 0s and 1s (turns some wires on and off) via a protocol called I2C. The Arduino interprets this as data and is then decoded into three floating point values. They are then masqueraded by three BLE characteristics. To access the data, one would need to access the characteristic, and to access the characteristic, one would need to access the service. The data is sent from the peripheral device and is out in the open. A central device connects to the peripheral, grabs the data, which it grabs as a dbus.Array full of dbus.Bytes data types. This is then converted into hex values, which is then stripped of all its 0x values and squashed into one big hex value. An endianness swap occurs, then the data is turned into a floating point value! 
