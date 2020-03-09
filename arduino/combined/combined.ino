int IUD_pin = A4; // UD pin assignment
int ILR_pin = A3; // LR pin assignment
int pressure_sensor_pin = A5; // pressure sensor pin assignment
int baud_rate = 19200; // serial baud rate *MUST MATCH IN PYTHON*

int sensorValue = 0; // pressure sensor data
int UD = 0; // UD data
int LR = 0; // LR data
unsigned long currentMillis; // current time
unsigned long previousMillis = 0; // previous time
int samplePeriod = 10;
const int numSamples = 10;
int samples[numSamples]; // array to store samples
int samplecounter = 0;
byte sL, sH, UD0, UD1, LR0, LR1; // bytes for encoding
byte snp_payload[2]; // pressure payload
byte joystick_payload[3]; // joystick payload

void setup() {
  Serial.begin(baud_rate);
}

void loop() {

  currentMillis = millis();

  if((currentMillis - previousMillis) >= samplePeriod){
   samplePressure();
   previousMillis = currentMillis;
  }

  if(samplecounter == numSamples){ // total 'delay' will be samplePeriod * numSamples
   sensorValue = sampleAverage();
   sL = lowByte(sensorValue);
   sH = highByte(sensorValue);
   snp_payload[0] = 0xB0 + sH;
   snp_payload[1] = sL;
   Serial.write(snp_payload,2);
   joystick_loop();
   samplecounter = 0;
  }
}

void joystick_loop(){

  UD = analogRead(IUD_pin);
  LR = analogRead(ILR_pin);
  LR = LR * 4; // purely for byte packing purposes (left shift by 2)

  // turns out int is 2 bytes in Arduino so below works well
  UD1 = highByte(UD); // MSB of UD
  UD0 = lowByte(UD); // LSB of UD
  LR1 = highByte(LR); // MSB of LR
  LR0 = lowByte(LR); // LSB of LR
  joystick_payload[0] = 0xA0 + (0xF & LR1); // hex A (1010) to represent joystick data and last 4 bits of LR
  joystick_payload[1] = LR0 + (UD1 & 0x3); // first 6 bits of LR and last 2 bits of UD
  joystick_payload[2] = UD0; // low byte of UD

  Serial.write(joystick_payload, 3);

}

void samplePressure(){
  samples[samplecounter] = analogRead(pressure_sensor_pin);
  samplecounter++;
}

int sampleAverage(){
  int average = 0;
  for(int i = 0; i < numSamples; i++){
    average += samples[i];
  }
  average = average/numSamples;
  return average;
}
