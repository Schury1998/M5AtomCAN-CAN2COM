#include <Arduino.h>

void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.print("CAN MSG: 0x200 [7] <1F:C0:00:10:00:03:01>");
  Serial.println();
  delay(80);
  Serial.print("CAN MSG: 0x710 [8] <02:10:03:00:00:00:00:00>");
  Serial.println();
  delay(2000);
}
