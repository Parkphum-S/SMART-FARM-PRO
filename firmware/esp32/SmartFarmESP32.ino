
#include <WiFi.h>
#include <time.h>
#include <DHT.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "secrets.h"

// ===== SMART FARM PRO CONFIG =====
#define DEVICE_ID   "esp32_001"
#define FARM_ID     "farm_001"
#define ZONE_ID     "zone_01"

#define DHT_PIN     4
#define DHT_TYPE    DHT22
#define SOIL_PIN    35

#define RELAY_ACTIVE_LOW true

const uint8_t relayPins[] = {18, 19, 22, 23};

const char* actuatorIds[] = {
  "relay_01", "relay_02", "relay_03", "relay_04"
};

const int RELAY_COUNT = 4;

const char* STATUS_TOPIC =
  "farm/farm_001/esp32/esp32_001/status";

const char* SENSOR_TOPIC =
  "farm/farm_001/zone/zone_01/sensor/am2305b_001/reading";

const char* COMMAND_FILTER =
  "farm/farm_001/zone/zone_01/actuator/+/command";

// ===== SOIL CALIBRATION =====
const int SOIL_DRY_RAW = 3100;
const int SOIL_WET_RAW = 1350;

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
DHT dht(DHT_PIN, DHT_TYPE);

unsigned long lastSensorPublish = 0;
const unsigned long SENSOR_INTERVAL_MS = 30000;

bool relayState[RELAY_COUNT] = {false, false, false, false};

// ===== UTC TIMESTAMP =====
String timestampUTC() {
  struct tm t;

  if (!getLocalTime(&t, 1000) || t.tm_year < 124) {
    return "1970-01-01T00:00:00Z";
  }

  char buffer[25];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &t);

  return String(buffer);
}

// ===== RELAY CONTROL =====
void setRelay(int index, bool on) {
  if (index < 0 || index >= RELAY_COUNT) return;

  relayState[index] = on;

  uint8_t level;

  if (RELAY_ACTIVE_LOW) {
    level = on ? LOW : HIGH;
  } else {
    level = on ? HIGH : LOW;
  }

  digitalWrite(relayPins[index], level);
}

// ===== PUBLISH RELAY STATE =====
void publishRelayState(int index) {
  if (index < 0 || index >= RELAY_COUNT || !mqtt.connected()) {
    return;
  }

  char topic[160];

  snprintf(
    topic,
    sizeof(topic),
    "farm/farm_001/zone/zone_01/actuator/%s/state",
    actuatorIds[index]
  );

  JsonDocument doc;

  doc["actuator_id"] = actuatorIds[index];
  doc["state"] = relayState[index] ? "on" : "off";
  doc["timestamp"] = timestampUTC();

  char payload[256];

  serializeJson(doc, payload, sizeof(payload));

  mqtt.publish(topic, payload);
}

// ===== MQTT COMMAND HANDLER =====
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  JsonDocument doc;

  DeserializationError err = deserializeJson(doc, payload, length);

  if (err) {
    Serial.println("Invalid actuator command JSON");
    return;
  }

  const char* actuatorId = doc["actuator_id"] | "";
  const char* command = doc["command"] | "";
  const char* requestId = doc["request_id"] | "";

  String topicString(topic);
  String prefix = "farm/farm_001/zone/zone_01/actuator/";

  if (!topicString.startsWith(prefix)) return;

  String remaining = topicString.substring(prefix.length());

  int slash = remaining.indexOf('/');

  if (slash < 0) return;

  String topicActuatorId = remaining.substring(0, slash);

  // Topic actuator ID and JSON actuator_id must match.
  if (topicActuatorId != String(actuatorId)) {
    Serial.println("Rejected: actuator ID mismatch");
    return;
  }

  int index = -1;

  for (int i = 0; i < RELAY_COUNT; i++) {
    if (topicActuatorId == actuatorIds[i]) {
      index = i;
      break;
    }
  }

  bool accepted = false;

  if (index >= 0 && requestId[0] != '\0') {
    if (strcmp(command, "on") == 0) {
      setRelay(index, true);
      accepted = true;
    } else if (strcmp(command, "off") == 0) {
      setRelay(index, false);
      accepted = true;
    }
  }

  if (index >= 0 && accepted) {
    publishRelayState(index);
  }

  char ackTopic[160];

  snprintf(
    ackTopic,
    sizeof(ackTopic),
    "farm/farm_001/zone/zone_01/actuator/%s/ack",
    topicActuatorId.c_str()
  );

  JsonDocument ack;

  ack["actuator_id"] = topicActuatorId;
  ack["request_id"] = requestId;
  ack["result"] = accepted ? "accepted" : "rejected";
  ack["timestamp"] = timestampUTC();

  char ackPayload[256];

  serializeJson(ack, ackPayload, sizeof(ackPayload));

  mqtt.publish(ackTopic, ackPayload);

  Serial.printf(
    "Actuator %s command %s: %s\n",
    topicActuatorId.c_str(),
    command,
    accepted ? "accepted" : "rejected"
  );
}

// ===== DEVICE STATUS =====
void publishStatus(const char* status) {
  JsonDocument doc;

  doc["device_id"] = DEVICE_ID;
  doc["status"] = status;
  doc["timestamp"] = timestampUTC();

  char payload[256];

  serializeJson(doc, payload, sizeof(payload));

  mqtt.publish(STATUS_TOPIC, payload, true);
}

// ===== SENSOR READING =====
void publishSensorReading() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("DHT reading unavailable; skipping publish");
    return;
  }

  // Multi-sampling: average 10 ADC readings.
  int soilMin = 4095;
  int soilMax = 0;
  long soilSum = 0;

  const int SOIL_SAMPLES = 10;

  for (int i = 0; i < SOIL_SAMPLES; i++) {
    int soilRaw = analogRead(SOIL_PIN);

    if (soilRaw < soilMin) soilMin = soilRaw;
    if (soilRaw > soilMax) soilMax = soilRaw;

    soilSum += soilRaw;

    delay(10);
  }

  float soilAverage = (float)soilSum / SOIL_SAMPLES;

  // Keep ADC value inside calibrated dry/wet range.
  int constrainedRaw = (int)soilAverage;

  if (SOIL_DRY_RAW > SOIL_WET_RAW) {
    constrainedRaw = constrain(
      constrainedRaw,
      SOIL_WET_RAW,
      SOIL_DRY_RAW
    );
  } else {
    constrainedRaw = constrain(
      constrainedRaw,
      SOIL_DRY_RAW,
      SOIL_WET_RAW
    );
  }

  // ORIGINAL CALIBRATION DIRECTION:
  // dry ADC -> 0%, wet ADC -> 100%.
  int moisturePercent = map(
    constrainedRaw,
    SOIL_DRY_RAW,
    SOIL_WET_RAW,
    0,
    100
  );

  moisturePercent = constrain(moisturePercent, 0, 100);

  Serial.printf(
    "Soil ADC | Min: %d | Max: %d | Average: %.1f | Percent: %d%%\n",
    soilMin,
    soilMax,
    soilAverage,
    moisturePercent
  );

  // ===== SENSOR JSON: KEEP PROJECT CONTRACT =====
  JsonDocument doc;

  doc["sensor_id"] = "am2305b_001";
  doc["type"] = "temperature_humidity_soil";
  doc["temperature_c"] = temperature;
  doc["humidity_pct"] = humidity;
  doc["soil_moisture_pct"] = moisturePercent;
  doc["timestamp"] = timestampUTC();

  char payload[320];

  serializeJson(doc, payload, sizeof(payload));

  if (mqtt.publish(SENSOR_TOPIC, payload)) {
    Serial.printf(
      "Sensors published: %.1f C, %.1f %%, Soil: %d %%\n",
      temperature,
      humidity,
      moisturePercent
    );
  } else {
    Serial.println("Sensor publish failed");
  }
}

// ===== WIFI =====
void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.printf(
    "\nWiFi connected: %s\n",
    WiFi.localIP().toString().c_str()
  );

  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
}

// ===== MQTT =====
void connectMQTT() {
  while (!mqtt.connected()) {
    Serial.println("Connecting to MQTT...");

    JsonDocument willDoc;

    willDoc["device_id"] = DEVICE_ID;
    willDoc["status"] = "offline";
    willDoc["timestamp"] = "1970-01-01T00:00:00Z";

    char willPayload[160];

    serializeJson(willDoc, willPayload, sizeof(willPayload));

    bool connected = mqtt.connect(
      DEVICE_ID,
      MQTT_USERNAME,
      MQTT_PASSWORD,
      STATUS_TOPIC,
      1,
      true,
      willPayload
    );

    if (connected) {
      Serial.println("MQTT connected");

      mqtt.subscribe(COMMAND_FILTER);

      Serial.println("Actuator command subscription active");

      publishStatus("online");

      for (int i = 0; i < RELAY_COUNT; i++) {
        publishRelayState(i);
      }
    } else {
      Serial.printf(
        "MQTT connection failed, state=%d\n",
        mqtt.state()
      );

      delay(3000);
    }
  }
}

// ===== SETUP =====
void setup() {
  Serial.begin(115200);

  for (int i = 0; i < RELAY_COUNT; i++) {
    pinMode(relayPins[i], OUTPUT);
    setRelay(i, false);
  }

  analogReadResolution(12);
  analogSetPinAttenuation(SOIL_PIN, ADC_11db);

  dht.begin();

  connectWiFi();

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(mqttCallback);
  mqtt.setBufferSize(512);

  connectMQTT();
}

// ===== MAIN LOOP =====
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    delay(500);
    return;
  }

  if (!mqtt.connected()) {
    connectMQTT();
  }

  mqtt.loop();

  unsigned long now = millis();

  if (now - lastSensorPublish >= SENSOR_INTERVAL_MS) {
    lastSensorPublish = now;
    publishSensorReading();
  }
}
