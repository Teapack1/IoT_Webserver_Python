#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "DHT.h"
#include <ArduinoJson.h>

#define DEVICE_ID "t1"
//#define DEVICE_NAME "teploměr_kůlna"

#define DHTPIN 2
#define DHTTYPE DHT11
#define SERVER_IP "10.0.0.178:5000" // PC address with emulation on host
#define STASSID "Major"
#define STAPSK  "12345ABCDE"

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  WiFi.begin(STASSID, STAPSK);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Reading DHT sensor
  float value_1 = dht.readHumidity();
  float value_2 = dht.readTemperature();

  if (isnan(value_1) || isnan(value_2)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  float hic = dht.computeHeatIndex(value_1, value_2, false);

  if ((WiFi.status() == WL_CONNECTED)) {
    WiFiClient client;
    HTTPClient http;

    http.begin(client, "http://" SERVER_IP "/postplain/");
    http.addHeader("Content-Type", "application/json");

    DynamicJsonDocument doc(1024);
    doc["id"] = DEVICE_ID;
    //doc["name"] = DEVICE_NAME;
    JsonArray values = doc.createNestedArray("values");
    values.add(value_1);
    values.add(value_2);
    
    JsonArray units = doc.createNestedArray("units");
    units.add("C");
    units.add("%");
    
    String json;
    serializeJson(doc, json);

    int httpCode = http.POST(json);

    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK) {
        const String& payload = http.getString();
        Serial.println("received payload:\n<<");
        Serial.println(payload);
        Serial.println(">>");
      }
    } else {
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
  }

  delay(3000);
}
