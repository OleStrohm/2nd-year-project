
int IUD = A1;
int ILR = A0;

int UDRAW = 0;
int LRRAW = 0;
int UD = 0;
int LR = 0;
int UDMID = 0;
int LRMID = 0;
byte payload[3];

void setup() {
  joystick_setup();
}

void loop() {
  joystick_loop();
  delay(500);
}

void joystick_setup(){
  Serial.begin(9600);
  UDMID = analogRead(IUD);
  LRMID = analogRead(ILR); 
}

void joystick_loop(){
  
  UDRAW = analogRead(IUD);
  LRRAW = analogRead(ILR);
  UD = UDRAW - UDMID; // 
  LR = LRRAW - LRMID;
  LR = LR * 4;
  byte UD1 = highByte(UD);
  byte UD0 = lowByte(UD);
  byte LR1 = highByte(LR);
  byte LR0 = lowByte(LR);

  payload[0] = UD0; // first 8 bits of UD
  payload[1] = (UD1 & 0x2) + LR0; // first 6 bits of LR and last 2 bits of UD
  payload[2] = 0xA0 + (0xF & LR1); // hex A (1010) to represent joystick data and last 4 bits of LR

  // to decode :
  // UD = payload[0] + ((payload[1] & 0x2) << 8)
  // LR = (payload[1] & 0xFC) + ((payload[2] & 0xF) << 8)
  // Identifier = ((payload[2] >> 4) & 0xA)) this should give you 0xA
  
  Serial.print("UD: ");
  Serial.print(UD);
  Serial.print(" LR: ");
  Serial.println(LR/4);
  Serial.println(" Bytes: ");
  Serial.println(payload[2]);
  Serial.println(payload[1]);
  Serial.println(payload[0]);

  Serial.write(payload, 3);
  
}
