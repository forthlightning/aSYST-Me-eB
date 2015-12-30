#include <SoftwareSerial.h>
#include <SD.h>
#include <SPI.h>
SoftwareSerial mySerial(5, 6);
File listerine;

String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
int previous = 0;
int next = 2;

// LED pins
int green = 9;
int yellow = 8;
int red = 7;
int white = 4;

// distance, energy, and error
int D = 0;
int Ene = 0;
int error = 1.1;

float planVals[9];

void setup() {

  // choose pins for output
  pinMode (4, OUTPUT);
  pinMode (7, OUTPUT);
  pinMode (8, OUTPUT);
  pinMode (9, OUTPUT);

  //initialize serial
  Serial.begin(9600);
  mySerial.begin(9600);
  Serial.println("Serial Open.");

  // begin sd, check to make sure it started
  Serial.print("Initializing SD card...");
  if(!SD.begin(10))
  {
    Serial.println("initialization failed!");
    return;
  }
  Serial.println("initialized.");
  
  // check for plan.txt
  if (SD.exists("plan.txt"))
  {
    listerine = SD.open("plan.txt", FILE_READ);
    parsePlanToArray();
    Serial.println("done parsed ");
    listerine.close();  
  }
  else
  {
    Serial.print("something broke"); 
  }
  digitalWrite(red, HIGH);
  digitalWrite(yellow, HIGH);
  digitalWrite(green, HIGH);
  digitalWrite(white, HIGH);
  delay(1000);
  digitalWrite(red, LOW);
  digitalWrite(yellow, LOW);
  digitalWrite(green, LOW);
  digitalWrite(white, LOW); 
}

void loop() {
  serialEvent();
  if (stringComplete)
  {
    readStr();
  }
  actuate();
}

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

void parsePlanToArray()
// fills array planVals, odds are distance, evens are energy
{
  // buf holds single point of plan
  String buf = "" ; 
  int idx = 0;
  // read all of plan.txt
  while (listerine.available())
  {
    char newchar = listerine.read();
    buf += newchar;

    // check for comma
    if (newchar == ',')
    {
      float DisVal = buf.toFloat();
      planVals[idx] = DisVal;
      buf = "";
      idx++;
    }
    // check for colon
    else if (newchar == ':')
    {
      float EneVal = buf.toFloat();
      planVals[idx] = EneVal;
      buf = "";
      idx++;
    }
  }
}

void actuate()
{
  digitalWrite(red, LOW);
  digitalWrite(yellow, LOW);
  digitalWrite(green, LOW);
      
  if ((D < planVals[next]) && (D > planVals[previous])) 
  {
    if ((Ene/error) < planVals[previous+1])
    {
      digitalWrite(red, HIGH);
    }
    else if ((Ene*error) > planVals[previous+1])
    {
      digitalWrite(green, HIGH);
    }
    else 
    {
      digitalWrite(yellow, HIGH);
    }
  }
  else
  {
    next += 2;
    previous += 2;
  }
}

void readStr()
{
      // get distance string from cycle analyst, convert to float
    String distString = inputString.substring(23,29);
    float dist = distString.toFloat();

    // get AmpHr, get V
    String AmpHrString = inputString.substring(0,5);
    float AmpHr = AmpHrString.toFloat();

    String VString = inputString.substring(8,12);
    float V = VString.toFloat();

    // convert to energy
    float Ene = V * AmpHr;

    // get distance
    String DString = inputString.substring(26,31);
    float D = DString.toFloat();
    
    //reset inputstring and boolean for serial event
    inputString = "";
    stringComplete = false;
}

void blinkLED(led) 
{
  for i
  analogWrite(led,HIGH)
}



