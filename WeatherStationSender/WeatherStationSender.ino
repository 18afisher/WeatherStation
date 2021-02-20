/* 
Weather Station project, Version 2.
Written by Aidan Fisher, 2018. 
*/
#include <Wire.h>
#include <CurieBLE.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

// Define Bluetooth Stuff
BLEService stationService("70f6ff21-8dc8-4234-9dd1-4688aaebedbb");
BLEFloatCharacteristic temperatureCharacteristic("89384f53-e826-4802-adb0-f5b8cb2b1ec4", BLERead | BLENotify);
BLEFloatCharacteristic pressureCharacteristic("4d228b66-afb7-415e-bfab-6414ace872c4", BLERead | BLENotify);
BLEFloatCharacteristic humidityCharacteristic("0319bc08-264f-4e39-90b3-d1ab22117e0f", BLERead | BLENotify);

// Define variables and objects
Adafruit_BME280 bmeSensor; // BME280 sensor
long timeStarted;
float temperature;
float pressure;
float humidity;

// Run the setup, which will run once
void setup()
{
   bmeSensor.begin(0x76);
   BLE.begin();
   // Set up Bluetooth
   BLE.setLocalName("WeatherStationSender");
   BLE.setAdvertisedService(stationService);

   // Add Characteristics, which are used for holding the values which are transmitted through Bluetooth Low Energy
   stationService.addCharacteristic(temperatureCharacteristic);
   stationService.addCharacteristic(pressureCharacteristic);
   stationService.addCharacteristic(humidityCharacteristic);

   BLE.addService(stationService); // Add the service

   temperatureCharacteristic.setValue(bmeSensor.readTemperature());
   pressureCharacteristic.setValue(bmeSensor.readPressure() / 100.0F);
   humidityCharacteristic.setValue(bmeSensor.readHumidity()); 

   BLE.advertise(); // Allow the Arduino 101 to be seen by other BLE devices. 
}

void loop()
{
   BLE.poll();
   BLEDevice raspberryPi = BLE.central();
   temperature = bmeSensor.readTemperature();
   if (raspberryPi)
   {
     temperatureCharacteristic.setValue(temperature);
     pressureCharacteristic.setValue(bmeSensor.readPressure() / 100.0F);
     humidityCharacteristic.setValue(bmeSensor.readHumidity());
     delay(1000);
   }

}
