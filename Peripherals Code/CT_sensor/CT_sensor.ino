#include <SPI.h>
#include <Ethernet.h>

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED }; // MAC address for the Ethernet shield
IPAddress ip(192, 168, 1, 177); // IP address for the Arduino (ensure it's available in your network)

EthernetServer server(80); // Server on port 80

const int CT1_PIN = A1;
const int CT2_PIN = A2;
const int CT3_PIN = A3;

const float CALIBRATION_FACTOR = 0.098;
void setup() {
    Ethernet.begin(mac, ip);
  server.begin();
Serial.begin(9600);
}

void loop() {
  // Read the analog values from the CTs using the 16-bit ADC
  int rawValue1 = readADC(CT1_PIN);
  int rawValue2 = readADC(CT2_PIN);
  int rawValue3 = readADC(CT3_PIN);

  float current1 = rawValue1 * CALIBRATION_FACTOR;
  float current2 = rawValue2 * CALIBRATION_FACTOR;
  float current3 = rawValue3 * CALIBRATION_FACTOR;

  Serial.print("Current in CT1: ");
  Serial.print(current1);
  Serial.println(" A");

  Serial.print("Current in CT2: ");
  Serial.print(current2);
  Serial.println(" A");

  Serial.print("Current in CT3: ");
  Serial.print(current3);
  Serial.println(" A");

  delay(1000);
 
}

int readADC(int pin) {
return analogRead(pin);
}
