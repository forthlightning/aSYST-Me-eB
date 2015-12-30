#include <SoftwareSerial.h>
#include <SD.h>
#include <SPI.h>
#include <Wire.h>
#include "RTClib.h"
SoftwareSerial mySerial(1,2);
File writer;
RTC_DS1307 RTC;

String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete

void setup() {
  // initialize serial:
  pinMode (10, OUTPUT);
  Serial.begin(9600);
  Wire.begin();
  RTC.begin();
  mySerial.begin(9600);

  Serial.print("Initializing SD card...");
  
  if(!SD.begin(10)) {
    Serial.println("initialization failed!");
    return;
  }
  Serial.println("initialization done.");

  if (! RTC.isrunning()) {
    Serial.println("RTC is NOT running!");
  }
 
  writer = SD.open("data.txt opened", FILE_WRITE);
  if (writer) {
    Serial.println("Writing to data.txt...");
    Serial.println("done.");
  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening data.txt");
  }

  DateTime initialTime = RTC.now();
  String month = String(initialTime.month());
  String day = String(initialTime.day());
  String hour = String(initialTime.hour());
  // time stamp ONLY ONCE at the beginning of the run
  writer.println("Date of run: " + month + '/' + day + " Hour of run: " + hour + '.');
  // close the file:
  writer.close();
}

void loop() {
  serialEvent(); //call the function
  // print the string when a newline arrives:
  if (stringComplete) {
    
    DateTime now = RTC.now();
    
    String nowMin = String(now.minute());
    String nowSec = String(now.second());
    String timeStamp = nowMin + ':' + nowSec;
    
    writer.println(timeStamp + '\t' + inputString);
//    SD.write(toFile);
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
}

/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent() {
  while (mySerial.available()) {
    // get the new byte:
    char inChar = (char)mySerial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
