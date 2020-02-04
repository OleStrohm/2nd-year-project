int IUD = A1;
int ILR = A0;

int UDRAW = 0;
int LRRAW = 0;
int UD = 0;
int LR = 0;
int UDMID = 0;
int LRMID = 0;

void setup() {
  Serial.begin(9600);
  UDMID = analogRead(IUD);
  LRMID = analogRead(ILR); 

}

void loop() {
  UDRAW = analogRead(IUD);
  LRRAW = analogRead(ILR);
  UD = UDRAW - UDMID;
  LR = LRRAW - LRMID;
  Serial.print("UD: ");
  Serial.print(UD);
  Serial.print("\tLR: ");
  Serial.println(LR);
  delay(100);
}
