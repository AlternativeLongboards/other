#include <Arduino.h>
#include <REL6CH.h>

REL6CH::REL6CH(byte adress) {
  
  pinMode(50, OUTPUT);
  pinMode(52, OUTPUT);
  digitalWrite(50, LOW);
  digitalWrite(52, HIGH);
  Serial1.begin(1000000);
  _adress       = adress;
  readValue     = 0;
  readHandshake = 0;
  transmEnd     = 0;
  flag          = 0;
  sendPart1     = 0;
  sendPart2     = 0;
  calculate_adress_parts(_adress);

}


void REL6CH::calculate_adress_parts(byte to_calculate) {

  switch (to_calculate) {
    case 0 ... 9:
      adressPart1 = 48;
      adressPart2 = to_Ascii(to_calculate);
      break;
    case 10 ... 70:
      adressPart1 = to_Ascii(to_calculate / 10);
      adressPart2 = to_Ascii(to_calculate - (10 * (to_calculate / 10)));
      break;
  }
  
}

void REL6CH::processLastState() {

  switch (state) {
    case GOT_A:
      readAdress = currentValue;
      break;
    case GOT_U:
      readValue = currentValue;
      break;
  }
  currentValue = 0;

}

void REL6CH::IncomingByte(byte c) {
  if (isdigit(c)) {
    currentValue *= 10;
    currentValue += c- '0';
  } 
  else {
    processLastState();
    switch (c) {
      case 65:
        state = GOT_A;
        if (transmEnd == 1) {
          transmEnd = 0;
        }
      break;
      case 85:
        state = GOT_U;
      break;
      case 72:
        state = NONE;
        readHandshake = 1;
      break;
      case 69:
        state = NONE;
        transmEnd = 1;
      break;
      case 13:
      state = NONE;
      break;
      default:
        state = NONE;
      break;
    }
  }

}

void REL6CH::send_data(byte Set) {

  if (Set < 10) {
    sendPart1 = 48;
    sendPart2 = to_Ascii(Set);
  }
  if (Set > 9 && Set < 65) {
    sendPart1 = Set/10;
    sendPart2 = Set - sendPart1*10;
    sendPart1 = to_Ascii(sendPart1);
    sendPart2 = to_Ascii(sendPart2);
  }
  Serial1.write(65);
  Serial1.write(adressPart1);
  Serial1.write(adressPart2);
  Serial1.write(84);
  Serial1.write(sendPart1);
  Serial1.write(sendPart2);
  Serial1.write(69);
  Serial1.write(13);
  Serial1.write(10);

  Serial1.flush();
}

void REL6CH::say_hello() {

  Serial1.write(65);
  Serial1.write(adressPart1);
  Serial1.write(adressPart2);
  Serial1.write(67);
  Serial1.write(50);
  Serial1.write(69);
  Serial1.write(13);
  Serial1.write(10);

  Serial1.flush();
}

void REL6CH::new_adress( byte N) {
  
  Serial1.write(65);
  Serial1.write(adressPart1);
  Serial1.write(adressPart1);
  Serial1.write(78);
  
  _adress = N;
  calculate_adress_parts(_adress);

  Serial1.write(adressPart1);
  Serial1.write(adressPart2);
  Serial1.write(69);
  Serial1.write(13);
  Serial1.write(10);

  Serial1.flush();
}

int  REL6CH::to_Ascii(byte j) {                                                  // FUNCTION changing number into ASCII chart

  switch (j) {
    case 0:
      return 48;
      break;
    case 1:
      return 49;
      break;
    case 2:
      return 50;
      break;
    case 3:
      return 51;
      break;
    case 4:
      return 52;
      break;
    case 5:
      return 53;
      break;
    case 6:
      return 54;
      break;
    case 7:
      return 55;
      break;
    case 8:
      return 56;
      break;
    case 9:
      return 57;
      break;

  }

}

boolean REL6CH::set(byte value) {
  
  send_data(value);
  
  last_time = micros();
  while ((unsigned long)(micros() - last_time) < 200) { 
    if (Serial1.available() > 2) { 
      break; 
    } 
  }
  while (Serial1.available() > 0 ) {
    IncomingByte(Serial1.read());
  }
  if ((readAdress != _adress) || (readValue != value)) {
    return false;
  } 
  else {
    return true;
  }
  
}

boolean REL6CH::check_module() {
  
  readHandshake = 0;
  say_hello();
  last_time = micros();
  while ((unsigned long)(micros() - last_time) < 200) {
    if (Serial1.available() > 2) { 
      break; 
    } 
  }
  while (Serial1.available() > 0) {
    IncomingByte(Serial1.read());
  }
  if (readHandshake == 1 && readAdress == _adress) {
    return true;
  } else {
    return false;
  }
  
}