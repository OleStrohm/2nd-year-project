int sensorPin = A3;
int sensorValue = 0;
int samplePeriod = 10;
int numSamples = 15;
int samples[15];
unsigned long previousMillis = 0;
int samplecounter = 0;
byte payload_snp[2];
byte sL;
byte sH;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  snploop()
}

void snploop(){
   unsigned long currentMillis = millis();

  if((currentMillis - previousMillis) >= samplePeriod){
    samplePressure();
    previousMillis = currentMillis;
  }

  if(samplecounter == numSamples){
    sensorValue = sampleAverage();
    sL = lowByte(sensorValue);
    sH = highByte(sensorValue);
    payload_snp[0] = 0xB0 + sH;
    payload_snp[1] = sL;
    Serial.write(payload_snp,2);
    samplecounter = 0;
  }
}

void samplePressure(){
  samples[samplecounter] = analogRead(sensorPin);
  samplecounter++;
}

int sampleAverage(){
  int average=0;
  for(int i = 0; i < numSamples; i++){
    average += samples[i];
  }
  average = average/numSamples;
  return average;
}
