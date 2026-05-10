#include <Wire.h>
#include "MPU6050.h"
#include <Servo.h>

MPU6050 mpu;
Servo suspensionServo;

// Variables MPU
int16_t ax, ay, az;

// Servo
const int servoPin = 9;
int servoPos = 90;

void setup() {

  Serial.begin(115200);

  Wire.begin();

  mpu.initialize();

  suspensionServo.attach(servoPin);
  suspensionServo.write(servoPos);

  delay(1000);
}

void loop() {

  // Leer aceleración
  mpu.getAcceleration(&ax, &ay, &az);

  // Vibración respecto a gravedad
  int vibration = abs(az - 16384);

  // Regular servo según vibración
  servoPos = map(vibration, 0, 4000, 80, 120);

  servoPos = constrain(servoPos, 80, 120);

  suspensionServo.write(servoPos);

  // ==========================
  // ENVIAR DATOS A PYTHON
  // ==========================

  // Formato:
  // tiempo,az,servo

  Serial.print(millis());
  Serial.print(",");
  Serial.print(az);
  Serial.print(",");
  Serial.println(servoPos);

  delay(150);
}