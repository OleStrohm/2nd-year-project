<<<<<<< Updated upstream
int IUD = A5; // UD pin assignment
int ILR = A4; // LR pin assignment

int UDRAW = 0; // raw UD data
int LRRAW = 0; // raw LR data
int UDMID = 0; // midpoint of UD (start pos)
int LRMID = 0; // midpoint of LR (start pos)
int UD = 0; // final UD data
int LR = 0; // final LR data
byte payload_j[3]; // payload of 3 bytes
int data_delay = 100; // delay (in ms) of joystick data sent to computer

void setup() {
  joystick_setup();
}

void loop() {
  joystick_loop();
  delay(data_delay);
}

void joystick_setup(){
  Serial.begin(9600);
}

void joystick_loop(){
  
  UDRAW = analogRead(IUD);
  LRRAW = analogRead(ILR);
//  UD = UDRAW - UDMID; // calculates UD displacement from centre
//  LR = LRRAW - LRMID; // calculates LR displacement from centre
  UD = UDRAW;
  LR = LRRAW;
  LR = LR * 4; // purely for byte packing purposes (left shift by 2)
  
  // turns out int is 2 bytes in Arduino so below works well
  byte UD1 = highByte(UD); // MSB of UD
  byte UD0 = lowByte(UD); // LSB of UD
  byte LR1 = highByte(LR); // MSB of LR
  byte LR0 = lowByte(LR); // LSB of LR

  payload_j[2] = UD0; // first 8 bits of UD
  payload_j[1] = (UD1 & 0x3) + LR0; // first 6 bits of LR and last 2 bits of UD
  payload_j[0] = 0xA0 + (0xF & LR1); // hex A (1010) to represent joystick data and last 4 bits of LR

  // to decode :
  // UD = payload[2] + ((payload[1] & 0x3) << 8)
  // LR = (payload[1] & 0xFC) + ((payload[0] & 0xF) << 8)
  // Identifier = ((payload[0] >> 4) & 0xA)) this should give you 0xA
  
//  Serial.print("UD: ");
//  Serial.print(UD);
//  Serial.print(" LR: ");
//  Serial.println(LR/4);
//  Serial.println(" Bytes: ");
//  Serial.println(payload[2]);
//  Serial.println(payload[1]);
//  Serial.println(payload[0]);

  Serial.write(payload_j, 3);
  
}
=======

int IUD = A1; //Input up down
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
  UDMID = analogRead(IUD); //sets up the midpoint for the joystick on startup
  LRMID = analogRead(ILR); 
}

void joystick_loop(){
  
  UDRAW = analogRead(IUD);
  LRRAW = analogRead(ILR);
  UD = UDRAW - UDMID; // 
  LR = LRRAW - LRMID;
  LR = LR * 4;
  byte UD1 = highByte(UD); //upper byte taken
  byte UD0 = lowByte(UD); //lower byte taken
  byte LR1 = highByte(LR);
  byte LR0 = lowByte(LR);

  payload[0] = 0xA0 + (0xF & LR1); // hex A (1010) to represent joystick data and last 4 bits of LR
  payload[1] = (UD1 & 0x3) + LR0; // first 6 bits of LR and last 2 bits of UD
  payload[2] = UD0; // first 8 bits of UD
  
  // to decode :
  // UD = payload[2] + ((payload[1] & 0x3) << 8)
  // LR = (payload[1] & 0xFC) + ((payload[0] & 0xF) << 8)
  // Identifier = ((payload[0] >> 4) & 0xA)) this should give you 0xA
  
  Serial.print("UD: ");
  Serial.print(UD);
  Serial.print(" LR: ");
  Serial.println(LR/4);
  Serial.println(" Bytes: ");
  Serial.println(payload[0]);
  Serial.println(payload[1]);
  Serial.println(payload[2]);

  Serial.write(payload, 3);
  
}
>>>>>>> Stashed changes
