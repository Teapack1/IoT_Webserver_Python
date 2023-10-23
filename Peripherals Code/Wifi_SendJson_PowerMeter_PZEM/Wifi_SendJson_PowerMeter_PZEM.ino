#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <PZEM004Tv30.h>
#include <SoftwareSerial.h>

#define DEVICE_ID "e1";

#define SERVER_IP "10.0.0.237:5000" // PC address with emulation on host
#define STASSID "Major"
#define STAPSK  "12345ABCDE"

/* Use software serial for the pzem_1
 * Pin D6, 8, 7 Rx (Connects to the Tx pin on the pzem_1)
 * Pin D7, 11, 6 Tx (Connects to the Rx pin on the pzem_1)
*/
SoftwareSerial pzem_1SWSerial_1(D6, D7);
SoftwareSerial pzem_1SWSerial_2(8, 11);
SoftwareSerial pzem_1SWSerial_3(7, 6);
PZEM004Tv30 pzem_1;

void setup() {
  Serial.begin(115200);
  WiFi.begin(STASSID, STAPSK);

  pzem_1 = PZEM004Tv30(pzem_1SWSerial_1);   

   
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
    Serial.print("Custom Address:");
    Serial.println(pzem_1.readAddress(), HEX);

    // Read the data from the sensor
    float voltage = pzem_1.voltage();
    float current = pzem_1.current();
    float power = pzem_1.power();
    float energy = pzem_1.energy();
    float frequency = pzem_1.frequency();
    float pf = pzem_1.pf();

    // Check if the data is valid
    if(isnan(voltage)){
        Serial.println("Error reading voltage");
    } else if (isnan(current)) {
        Serial.println("Error reading current");
    } else if (isnan(power)) {
        Serial.println("Error reading power");
    } else if (isnan(energy)) {
        Serial.println("Error reading energy");
    } else if (isnan(frequency)) {
        Serial.println("Error reading frequency");
    } else if (isnan(pf)) {
        Serial.println("Error reading power factor");
    } else {

        // Print the values to the Serial console
        Serial.print("Voltage: ");      Serial.print(voltage);      Serial.println("V");
        Serial.print("Current: ");      Serial.print(current);      Serial.println("A");
        Serial.print("Power: ");        Serial.print(power);        Serial.println("W");
        Serial.print("Energy: ");       Serial.print(energy,3);     Serial.println("kWh");
        Serial.print("Frequency: ");    Serial.print(frequency, 1); Serial.println("Hz");
        Serial.print("PF: ");           Serial.println(pf);

    }
    Serial.println();
if ((WiFi.status() == WL_CONNECTED)) {
    WiFiClient client;
    HTTPClient http;

StaticJsonDocument<384> doc;

doc["id"] = DEVICE_ID;

JsonArray values = doc.createNestedArray("values");
values.add(voltage);
values.add(current);
values.add(power);
values.add(energy);
values.add(frequency);
values.add(pf);

JsonArray units = doc.createNestedArray("units");
units.add("V");
units.add("A");
units.add("W");
units.add("kWh");
units.add("Hz");
units.add("PF");

String json;
serializeJson(doc, json);

http.begin(client, "http://" SERVER_IP "/postplain/");
http.addHeader("Content-Type", "application/json");
int httpCode = http.POST(json);

    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK) {
        const String& payload = http.getString();
        Serial.println("received payload:\n<<");
        Serial.println(payload);
        Serial.println(">>");
        Serial.println(httpCode);
      }
    } else {
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
  } else {
    Serial.println("WiFi disconnected. Attempting reconnection...");
    WiFi.begin(STASSID, STAPSK);
      while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
  }

  delay(30000);
}
