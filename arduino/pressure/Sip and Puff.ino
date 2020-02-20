int sensorPin = A3;
double sensorValue = 0;
byte samplePeriod = 10;
int numSamples = 15;
int samples[15];
unsigned long previousMillis = 0;
byte samplecounter = 0;

void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:

  unsigned long currentMillis = millis();

  if((currentMillis - previousMillis) >= samplePeriod){
    samplePressure();
    previousMillis = currentMillis;
  }

  if(samplecounter < numSamples){
    sensorValue = sampleAverage();
    samplecounter = 0;
  }

}

void samplePressure(){
  samples[samplecounter] = analogRead(sensorPin);
  samplecounter++;
}

double sampleAverage(){
  double average;
  for(byte i = 0; i < numSamples; i++){
    average += samples[i];
  }
  average = average/numSamples;
  return average;
}
