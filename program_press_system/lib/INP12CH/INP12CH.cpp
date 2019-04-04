#include <Arduino.h>
#include <INP12CH.h>


INP12CH::INP12CH(byte adress) {
  pinMode(50, OUTPUT);
  pinMode(52, OUTPUT);
  digitalWrite(50, LOW);
  digitalWrite(52, HIGH);
  Serial1.begin(1000000);
  _adress = adress;
  readValue = 0;
  readValue = 0;
  readHandshake = 0;
  transmEnd = 0;
  flag = 0;

  calculate_adress_parts(_adress);

}

void INP12CH::calculate_adress_parts(byte to_calculate) {

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

void INP12CH::processLastState() {

  switch (state) {
    case GOT_A:
      readAdress = currentValue;
      break;
    case GOT_R:
      readValue = currentValue;
      break;
  }
  currentValue = 0;

}

void INP12CH::IncomingByte(byte c) {
  if (c >= 48 && c <= 57) {
    currentValue *= 10;
    currentValue += c - '0';
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
      case 82:
        state = GOT_R;
        break;
      case 72:
        state = NONE;
        readHandshake = 1;
        break;
      case 69:
        state = NONE;
        transmEnd = 1;
        break;
      default:
        state = NONE;
        break;
    }
  }
}

void INP12CH::ask_data() {

  Serial1.write(65);
  Serial1.write(adressPart1);
  Serial1.write(adressPart2);
  Serial1.write(67);
  Serial1.write(49);
  Serial1.write(69);
  Serial1.write(13);
  Serial1.write(10);

  Serial1.flush();
}

void INP12CH::say_hello() {

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

void INP12CH::new_adress( byte N) {
  
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

int  INP12CH::to_Ascii(byte j) {                                                  // FUNCTION changing number into ASCII chart

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

short INP12CH::read() {

  ask_data();
  last_time = micros();
  while ((unsigned long)(micros() - last_time) < 300) { }
  while (Serial1.available() > 2) {
    IncomingByte(Serial1.read());
  }
  if (readAdress != _adress) {
    return ~B1;
  } else {
  return readValue;
  }
}

boolean INP12CH::check_module() {
  
  readHandshake = 0;
  say_hello();
  last_time = micros();
  while ((unsigned long)(micros() - last_time) < 300) {
    if (Serial1.available() > 2) {
      break;
    }
  }
  if (Serial1.available() > 2) {
    while (Serial1.available() > 0) {
      IncomingByte(Serial1.read());
    }
  }
  if (readHandshake == 1 && readAdress == _adress) {
    return true;
  } else {
    return false;
  }
}
