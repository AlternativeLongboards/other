#ifndef REL6CH_h
#define REL6CH_h

#include <Arduino.h>

class REL6CH {

  public:
    REL6CH(byte adress);
    boolean set(byte toSet);
    boolean check_module();
  private:
    void processLastState();
    void IncomingByte(byte c);
    void send_data(byte Set);  
    int to_Ascii(byte j);
    void say_hello();
    void new_adress(byte n);
    void calculate_adress_parts(byte to_calculate);
    short readValue;
    byte flag;
    unsigned long last_time;
    byte readAdress;
    byte readHandshake;
    typedef enum {  NONE, GOT_A, GOT_U} states;
    states state = NONE;
    short currentValue;
    byte _adress;
    byte _toSet;
    byte transmEnd;
    byte adressPart1;
    byte adressPart2;
    byte sendPart1;
    byte sendPart2;

};

#endif