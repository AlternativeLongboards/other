#ifndef INP12CH_h
#define INP12CH_h

#include <Arduino.h>

class INP12CH {

  public:
    INP12CH(byte adress);
    short read();
    boolean check_module();
    byte change_adress(byte adr);
  private:
    void processLastState();
    void IncomingByte(byte c);
    void ask_data();  
    int to_Ascii(byte j);
    void say_hello();
    void new_adress(byte n);
    void calculate_adress_parts(byte to_calculate);
    short readValue;
    byte flag;
    unsigned long last_time;
    byte readAdress;
    byte readHandshake;
    typedef enum {  NONE, GOT_A, GOT_R} states;
    states state = NONE;
    short currentValue;
    byte _adress;
    byte transmEnd;
    byte adressPart1;
    byte adressPart2;
   
};

#endif