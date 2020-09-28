//     _____  _____  ______  _____ _____     _____ ____  _   _ _______ _____   ____  _          _______     _______ _______ ______ __  __
//    |  __ \|  __ \|  ____|/ ____/ ____|   / ____/ __ \| \ | |__   __|  __ \ / __ \| |        / ____\ \   / / ____|__   __|  ____|  \/  |
//    | |__) | |__) | |__  | (___| (___    | |   | |  | |  \| |  | |  | |__) | |  | | |       | (___  \ \_/ / (___    | |  | |__  | \  / |
//    |  ___/|  _  /|  __|  \___ \\___ \   | |   | |  | | . ` |  | |  |  _  /| |  | | |        \___ \  \   / \___ \   | |  |  __| | |\/| |
//    | |    | | \ \| |____ ____) |___) |  | |___| |__| | |\  |  | |  | | \ \| |__| | |____    ____) |  | |  ____) |  | |  | |____| |  | |
//    |_|    |_|  \_\______|_____/_____/    \_____\____/|_| \_|  |_|  |_|  \_\\____/|______|  |_____/   |_| |_____/   |_|  |______|_|  |_|


#include <REL6CH.h>
#include <INP12CH.h>

#define relay_module_number 8                                                                                                           // number of relay modules
REL6CH relay[relay_module_number] = { REL6CH(0), REL6CH(20), REL6CH(11),
                                      REL6CH(12), REL6CH(13), REL6CH(14),
                                      REL6CH(15), REL6CH(16) };                                                                                     // declarate relay module with his adress
int relay_value[relay_module_number];                                                                                                   // current relay module output value
int relay_value_to_set[relay_module_number];                                                                                            // relay module output value to set in next refresh
byte relay_write_attemps = 0;                                                                                                           // if relay module don't communicate it's number of repated trials

#define input_module_number 6                                                                                                           // number of input modules
INP12CH input[input_module_number] = { INP12CH(1), INP12CH(2), INP12CH(3),
                                       INP12CH(4), INP12CH(5), INP12CH{6} };                                                            // declarate input module with his adress

typedef enum { NONE, PRESS_1, PRESS_2, PRESS_3,
               PRESS_4, PRESS_5, PRESS_6, SWITCHING } states_switchgear;                                                                // states of hydraulic switchgear
typedef enum { ZERO, UP, DOWN, HOLD, STARTING } states_pump;                                                                            // states of hydraulic pump
states_switchgear switchgear_state                      = NONE;
states_switchgear switchgear_state_to_set               = NONE;
states_switchgear switchgear_state_on_change            = NONE;
states_pump pump_state                                  = ZERO;
states_pump pump_state_to_set                           = ZERO;
states_pump pump_state_on_change                        = ZERO;
int pump_relay_value_on_change                          = 0;

byte tick_switchgear                                    = 0;                                                                            // value to measure time for hydraulic switchgear
byte tick_pump                                          = 0;                                                                            // value to measure time for hydraulic pump
byte tick_pump_zero                                     = 0;
unsigned long tick_auto_zero                            = 0;
byte ready_to_switch                                    = 0;

int in[8];                                                                                                                              // temporary value where INP12CH read is hold
int button[9];                                                                                                                          // current values for button reads. Stores values in binary array (for one type of button - it means in variable are all states for same button from diffrent control panels). Indexes: 0 - UP, 1 - DOWN, 2 - PNEUMATIC UP, 3 - PNEUMATIC DOWN, 4 - PNEUMATIC CONSTANT, 5 - HEATER UP, 6 - HEATER DOWN, 7 - OPEN PRESS SWITCH LIMIT
int button_to_set[9];                                                                                                                   // temporary values for button
int hydraulic_up;                                                                                                                       // each byte is actual status of buttons for hydraulic up (when system is auto)
int hydraulic_down;                                                                                                                     // each byte is actual status of buttons for hydraulic down (when system is auto)
int limit_switch;                                                                                                                       // each byte is actual status of buttons for limit switch
int press_on_switch;                                                                                                                    // each byte is actual status of buttons for press on switch

unsigned long pressing_time[10];                                                                                                        // pressing times for each press (index 0 - first press etc...)
int is_pressing[10];                                                                                                                    // value tells is press is close and press boards (index 0 - first press etc...)
int gui_state[10];                                                                                                                      // state of each press - for GUI communication purpose ( 0 - steady, 1 - closing, 2 - opening, 3 - pressing, 4 - open )

unsigned long minimum_time                              = 0;                                                                            // value to measire time for counting used during delay of reading INP12CH modules
unsigned long read_delay_time                           = 50;                                                                           // how long to wait between INP12CH reads
int automatic_close_time                                = 30;                                                                            // automatic switchgear closing variable. It means that switchear gonna restart if this amount of sec will pass
byte tick                                               = 0;                                                                            // tick - used to speed up code. Each tick measure time for other process
byte tick_counter                                       = 0;                                                                            // counter for ticks

byte active_input_module_count                          = B00000000;                                                                    // binary arrray to store information about INP12CH health
byte active_relay_module_count                          = B00000000;                                                                    // binary array to store information about REL6CH health
boolean system_status;                                                                                                                  // variable store system health - if all modules response this is true
//byte active_press                                       = 0;                                                                            // do usuniecia
int system_mode = 0;                                                                                                                    // 1 - automatic, 0 - manual
int magic_variable = 0;

String message                                          = "";                                                                           // variable to store read message

int abc = 0;                                                                                                                            // variable that every two system_tick update pressing times for each press

int job_done[10];

int limit_switch_flag                                   = 0;

unsigned long minimum_time_tick = 0;
unsigned long read_delay_time_tick = 500;

boolean system_tick() {                                                                                                                 // FUNCTION TO ITERATE SYSTEM TICK
  if (minimum_time_tick == 0) {
    minimum_time_tick = millis();
  }
  if ((unsigned long)(millis() - minimum_time_tick) > read_delay_time_tick){
    minimum_time_tick = 0;
    return true;
  } else {
    return false;
  }
}

void time_measure() {                                                                                                                   // FUNCTION TO ITERATE TICKS FOR DIFFRENT PROCESSES

  if (system_tick() == true) {

    if (switchgear_state == SWITCHING) {
      tick_switchgear ++;
    } else {
      tick_switchgear = 0;
    }

    if (pump_state == STARTING) {
      tick_pump ++;
    } else {
      tick_pump = 0;
    }

    if (ready_to_switch == 1) {
      tick_pump_zero ++;
    } else {
      tick_pump_zero = 0;
    }

    if (hydraulic_down == 0 && hydraulic_up == 0) {
       if (tick_auto_zero < automatic_close_time * 2) {
       tick_auto_zero ++;
       }
    } else {
       tick_auto_zero = 0;
    }

    if (limit_switch_flag > 0) {
      limit_switch_flag ++;
    } else {
      limit_switch_flag = 0;
    }

    abc ++;
    if (abc == 2) {
      for (int a = 0; a < 10; a++) {
        if (is_pressing[a] == 1) {
          pressing_time[a] ++;
        } else {
          pressing_time[a] = 0;
        }
      }

      abc = 0;

    }
    for (int a = 0; a < 10; a++) {
      if (is_pressing[a] == 0) {
        pressing_time[a] = 0;
      }
    }
  }

}

String to_string(int value) {                                                                                                           // FUNCTION TO CONVERT SERIAL READ INTO ASCII CHARTS

  switch (value) {

    case 48:
      return "0";
    break;
    case 49:
      return "1";
    break;
    case 50:
      return "2";
    break;
    case 51:
      return "3";
    break;
    case 52:
      return "4";
    break;
    case 53:
      return "5";
    break;
    case 54:
      return "6";
    break;
    case 55:
      return "7";
    break;
    case 56:
      return "8";
    break;
    case 57:
      return "9";
    break;
    case 65:
      return "A";
    break;
    case 66:
      return "B";
    break;
    case 67:
      return "C";
    break;
    case 68:
      return "D";
    break;
    case 69:
      return "E";
    break;
    case 70:
      return "F";
    break;
    case 71:
      return "G";
    break;
    case 72:
      return "H";
    break;
    case 73:
      return "I";
    break;
    case 74:
      return "J";
    break;
    case 75:
      return "K";
    break;
    case 76:
      return "L";
    break;
    case 77:
      return "M";
    break;
    case 78:
      return "N";
    break;
    case 79:
      return "O";
    break;
    case 80:
      return "P";
    break;
    case 81:
      return "Q";
    break;
    case 82:
      return "R";
    break;
    case 83:
      return "S";
    break;
    case 84:
      return "T";
    break;
    case 85:
      return "U";
    break;
    case 86:
      return "V";
    break;
    case 87:
      return "W";
    break;
    case 88:
      return "X";
    break;
    case 89:
      return "Y";
    break;
    case 90:
      return "Z";
    break;
    case 95:
      return "_";
    break;
    default:
      return "";
    break;
  }

}

int commands_handling() {                                                                                                               // FUNCTION READ MESSAGE AND HANDLE COMMANDS

  int message_arrive = 0;

  while (Serial.available() > 0) {
    message = message + to_string(Serial.read());
    message_arrive = 1;
  }

  if (message_arrive == 1) {

    if (message == "AE") {
      Serial.print("S");  Serial.print(switchgear_state);
      Serial.print("A");  Serial.print(gui_state[0]); Serial.print("Z"); Serial.print(pressing_time[0]);
      Serial.print("B");  Serial.print(gui_state[1]); Serial.print("Y"); Serial.print(pressing_time[1]);
      Serial.print("C");  Serial.print(gui_state[2]); Serial.print("X"); Serial.print(pressing_time[2]);
      Serial.print("D");  Serial.print(gui_state[3]); Serial.print("W"); Serial.print(pressing_time[3]);
      Serial.print("E");  Serial.print(gui_state[4]); Serial.print("V"); Serial.print(pressing_time[4]);
      Serial.print("F");  Serial.print(gui_state[5]); Serial.print("U"); Serial.print(pressing_time[5]); Serial.println("L");
      Serial.flush();
      goto command_end;
    }

    if (message == "ST") {
      Serial.print("I"); Serial.print(active_input_module_count); Serial.print("R"); Serial.print(active_relay_module_count); Serial.println("L");
      Serial.flush();
      goto command_end;
    }

    if (message == "A01") {                                                                                                             // open press 01
      Serial.print("A"); Serial.print("0"); Serial.print("1");
      Serial.flush();
      magic_variable = 1;
      hydraulic_down = 1;
      goto command_end;
    }
    if (message == "A02") {                                                                                                             // open press 02
      Serial.print("A"); Serial.print("0"); Serial.print("2");
      Serial.flush();
      magic_variable = 2;
      hydraulic_down = 1;
      goto command_end;
    }
    if (message == "A03") {                                                                                                             // open press 03
      Serial.print("A"); Serial.print("0"); Serial.print("3");
      Serial.flush();
      magic_variable = 4;
      hydraulic_down = 1;
      goto command_end;
    }
    if (message == "A04") {                                                                                                             // open press 04
      Serial.print("A"); Serial.print("0"); Serial.print("4");
      Serial.flush();
      magic_variable = 8;
      hydraulic_down = 1;
      goto command_end;
    }
    if (message == "A05") {                                                                                                             // open press 05
      Serial.print("A"); Serial.print("0"); Serial.print("5");
      Serial.flush();
      magic_variable = 16;
      hydraulic_down = 1;
      goto command_end;
    }
    if (message == "A06") {                                                                                                             // open press 06
      Serial.print("A"); Serial.print("0"); Serial.print("6");
      Serial.flush();
      magic_variable = 32;
      hydraulic_down = 1;
      goto command_end;
    }
    if (message == "Z00") {                                                                                                             // send system status
      Serial.println(system_status);
      goto command_end;
    }
    if (message == "Z01") {                                                                                                             // send system status
      Serial.print("Z"); Serial.print("0"); Serial.print("1");
      Serial.flush();
      system_mode = 0;
      goto command_end;
    }
    if (message == "Z02") {                                                                                                             // send system status
      Serial.print("Z"); Serial.print("0"); Serial.print("2");
      Serial.flush();
      system_mode = 1;
      goto command_end;
    }
    if (message == "C00") {
      Serial.print("C"); Serial.print("0"); Serial.print("0");
      Serial.flush();
      switchgear_state_to_set = NONE;
      goto command_end;
    }
    if (message == "C01") {
      Serial.print("C"); Serial.print("0"); Serial.print("1");
      Serial.flush();
      switchgear_state_to_set = PRESS_1;
      goto command_end;
    }
    if (message == "C02") {
      Serial.print("C"); Serial.print("0"); Serial.print("2");
      Serial.flush();
      switchgear_state_to_set = PRESS_2;
      goto command_end;
    }
    if (message == "C03") {
      Serial.print("C"); Serial.print("0"); Serial.print("3");
      Serial.flush();
      switchgear_state_to_set = PRESS_3;
      goto command_end;
    }
    if (message == "C04") {
      Serial.print("C"); Serial.print("0"); Serial.print("4");
      Serial.flush();
      switchgear_state_to_set = PRESS_4;
      goto command_end;
    }
    if (message == "C05") {
      Serial.print("C"); Serial.print("0"); Serial.print("5");
      Serial.flush();
      switchgear_state_to_set = PRESS_5;
      goto command_end;
    }
     if (message == "C06") {
      Serial.print("C"); Serial.print("0"); Serial.print("6");
      Serial.flush();
      switchgear_state_to_set = PRESS_6;
      goto command_end;
    }
    if (message == "B00") {
      Serial.print("B"); Serial.print("0"); Serial.print("0");
      Serial.flush();
      pump_state_to_set = ZERO;
      goto command_end;
    }
    if (message == "B01") {
      Serial.print("B"); Serial.print("0"); Serial.print("1");
      Serial.flush();
      pump_state_to_set = UP;
      goto command_end;
    }
    if (message == "B02") {
      Serial.print("B"); Serial.print("0"); Serial.print("2");
      Serial.flush();
      pump_state_to_set = DOWN;
      goto command_end;
    }
    if (message == "R02") {
     if (system_mode == 1) {
      relay_value_to_set[3] = 14;
      Serial.print("R"); Serial.print("0"); Serial.print("2");
      Serial.flush();
     }
     goto command_end;
    }
   if (message == "R03") {
    if (system_mode == 1) {
     relay_value_to_set[4] = 14;
     Serial.print("R"); Serial.print("0"); Serial.print("3");
     Serial.flush();
    }
   }
   if (message == "R04") {
    if (system_mode == 1) {
     relay_value_to_set[5] = 14;
     Serial.print("R"); Serial.print("0"); Serial.print("4");
     Serial.flush();
    }
   }
   if (message == "R05") {
    if (system_mode == 1) {
     relay_value_to_set[6] = 14;
     Serial.print("R"); Serial.print("0"); Serial.print("5");
     Serial.flush();
    }
   }
   if (message == "R06") {
    if (system_mode == 1) {
     relay_value_to_set[7] = 14;
     Serial.print("R"); Serial.print("0"); Serial.print("6");
     Serial.flush();
    }
   }
  }
command_end:

  message_arrive = 0;
  message = "";
  return 0;

}

void check_modules() {                                                                                                                  // FUNCTION CHECK MODULES STATUS

  while (Serial1.available()) {
    Serial1.read();
  }

  for (int a = 0; a < relay_module_number; a++) {
    if (relay[a].check_module() == true) {
      bitWrite(active_relay_module_count, a, 1);
    } else {
      bitWrite(active_relay_module_count, a, 0);
    }
  }

  for (int a =0; a < input_module_number; a++) {
    if (input[a].check_module() == true) {
      bitWrite(active_input_module_count, a, 1);
    } else {
      bitWrite(active_input_module_count, a, 0);
    }
  }

  if ( (active_input_module_count == (int(pow(2,input_module_number)) - 1)) && (active_relay_module_count == (int(pow(2,relay_module_number)) - 1)) ) {
    system_status = true;
  } else {
    system_status = false;
  }

}

void zero_REL6CH_modules() {                                                                                                            // FUNCTION SETS ALL REL MODULES INTO ZERO STATE

  for (int a = 0; a < relay_module_number; a++) {
    relay[a].set(0);
  }

}

void read_inputs() {                                                                                                                    // FUNCTION READ INP12CH VALUES

  if (minimum_time  == 0) {

    for (int a = 0; a < input_module_number; a++) {
      in[a] = input[a].read();
      if (in[a] < 0) {                                                                                                                  // NOWE
        in[a] = 0;                                                                                                                      // NOWE
      }                                                                                                                                 // NOWE
      for (int b = 0; b < 9; b ++ ) {
        bitWrite(button_to_set[b],a,bitRead(in[a],b));
      }
    }
    minimum_time = millis();
  }

  if ((unsigned long)(millis() - minimum_time) > read_delay_time) {
    for (int a = 0; a < 9; a ++) {
      if (button[a] != button_to_set[a]) {
        button[a] = button_to_set[a];
      }
    }
    minimum_time = 0;
   // tick = 1;
  }

}

void calculate_buttons() {                                                                                                              // FUNCTION CALCULATE STATE BASED ON BUTTONS

  if (system_mode == 0) {
    for (int a = 0; a < 9; a ++) {
      bitWrite(hydraulic_down,a,bitRead(button[1],a));
      bitWrite(hydraulic_up,a,bitRead(button[0],a));
    }
    magic_variable = (hydraulic_up ^ hydraulic_down) & press_on_switch;

    if (tick_auto_zero >=   automatic_close_time * 2) {
      pump_state_to_set = ZERO;
      switchgear_state_to_set = NONE;
    }
  }


  switch (magic_variable) {

    case 0:
      if (system_mode == 0) {
        if (switchgear_state == NONE) {
          pump_state_to_set = ZERO;
        } else {
          if (switchgear_state != SWITCHING) {
            if (bitRead(press_on_switch,switchgear_state - 1) == 0) {
              pump_state_to_set = ZERO;
              switchgear_state_to_set = NONE;
            } else {
              if (switchgear_state == switchgear_state_to_set) {
                pump_state_to_set = HOLD;
              }
            }
          } else {
            switchgear_state_to_set = NONE;
            pump_state_to_set = ZERO;
          }
        }
      }
    break;
    case 1:
      switchgear_state_to_set = PRESS_1;
      if (switchgear_state != switchgear_state_to_set) {
        if (pump_state != ZERO) {
          pump_state_to_set = ZERO;
        }
      } else {
        if (hydraulic_up > 0) {
          pump_state_to_set = UP;
        }
        if (hydraulic_down > 0) {
          pump_state_to_set = DOWN;
        }
      }
    break;
    case 2:
      switchgear_state_to_set = PRESS_2;
        if (switchgear_state != switchgear_state_to_set) {
          if (pump_state != ZERO) {
            pump_state_to_set = ZERO;
          }
        } else {
          if (hydraulic_up > 0) {
            pump_state_to_set = UP;
          }
          if (hydraulic_down > 0) {
            pump_state_to_set = DOWN;
          }
        }
    break;
    case 4:
      switchgear_state_to_set = PRESS_3;
      if (switchgear_state != switchgear_state_to_set) {
        if (pump_state != ZERO) {
          pump_state_to_set = ZERO;
        }
      } else {
        if (hydraulic_up > 0) {
          pump_state_to_set = UP;
        }
        if (hydraulic_down > 0) {
          pump_state_to_set = DOWN;
        }
      }
    break;
    case 8:
      switchgear_state_to_set = PRESS_4;
      if (switchgear_state != switchgear_state_to_set) {
        if (pump_state != ZERO) {
          pump_state_to_set = ZERO;
        }
      } else {
        if (hydraulic_up > 0) {
          pump_state_to_set = UP;
        }
        if (hydraulic_down > 0) {
          pump_state_to_set = DOWN;
        }
      }
    break;
    case 16:
      switchgear_state_to_set = PRESS_5;
      if (switchgear_state != switchgear_state_to_set) {
        if (pump_state != ZERO) {
          pump_state_to_set = ZERO;
        }
      } else {
        if (hydraulic_up > 0) {
          pump_state_to_set = UP;
        }
        if (hydraulic_down > 0) {
          pump_state_to_set = DOWN;
        }
      }
    break;
    case 32:
      switchgear_state_to_set = PRESS_6;
      if (switchgear_state != switchgear_state_to_set) {
        if (pump_state != ZERO) {
          pump_state_to_set = ZERO;
        }
      } else {
        if (hydraulic_up > 0) {
          pump_state_to_set = UP;
        }
        if (hydraulic_down > 0) {
          pump_state_to_set = DOWN;
        }
      }
    break;
    default:
      pump_state_to_set = ZERO;
    break;
  }

  for (int a = 0; a < 9; a ++) {
    if ( bitRead(button[4],a) == 0 && bitRead(press_on_switch,a) == 0) {
      if (relay_value[a+2] > 0) {																	// NOWE
        relay_value_to_set[a+2] = 0;
      }																									// NOWE
    }
    if ( bitRead(button[7],a) == 1 && bitRead(limit_switch,a) == 0) {
      if (is_pressing[a] == 1) {
        is_pressing[a] = 0;
        job_done[a] = 1;
      }
    }																																	// NOWE
    bitWrite(limit_switch,a,bitRead(button[7],a));
    if (bitRead(button[4],a) > 0) {
      bitWrite(press_on_switch,a,0);
      if ( job_done[a] == 0 ) {
        is_pressing[a] = 1;
      }
    } else {
      bitWrite(press_on_switch,a,1);
      is_pressing[a] = 0;
      job_done[a] = 0;
    }
  }

}

void send_outputs() {                                                                                                                   // FUNCTION SEND TO REL6CH MODULES VALUES THAT SHOULD BE SET ON MODULES

  for (int a = 0; a < relay_module_number; a++ ) {

    relay_write_attemps = 0;
    if (relay_value_to_set[a] != relay_value[a]) {
      while (relay[a].set(relay_value_to_set[a]) == 0) {
        relay_write_attemps ++;
        if (relay_write_attemps > 2) {
          check_modules();
          system_status = false;
          bitWrite(active_relay_module_count,a,0);
          break;
        }
      }
      relay_value[a] = relay_value_to_set[a];
    }
  }

  for (int a = 0; a < 9; a++) {

    if (is_pressing[a] == 1) {
      gui_state[a] = 3;
    } else {
      gui_state[a] = 0;
    }
    
  }

  if (relay_value[1]  == 5) {
    switch(relay_value[0]) {
      case 1:
        gui_state[0] = 1;
      break;
      case 2:
        gui_state[1] = 1;
      break;
      case 4:
        gui_state[2] = 1;
      break;
      case 8:
        gui_state[3] = 1;
      break;
      case 16:
        gui_state[4] = 1;
      break;
      case 32:
        gui_state[5] = 1;
      break;
    }
  }

  if (relay_value[1]  == 6) {
    switch(relay_value[0]) {
      case 1:
        gui_state[0] = 2;
      break;
      case 2:
        gui_state[1] = 2;
      break;
      case 4:
        gui_state[2] = 2;
      break;
      case 8:
        gui_state[3] = 2;
      break;
      case 16:
        gui_state[4] = 2;
      break;
      case 32:
        gui_state[5] = 2;
      break;
    }
  }

  for (int a = 0; a < 9; a++)  {                                                                                                      // NOWE
    if (bitRead(limit_switch,a) == 1) {                                                                                               // NOWE
      gui_state[a] = 4;                                                                                                               // NOWE
    }                                                                                                                                 // NOWE
  }                                                                                                                                   // NOWE

}

int switchgear_handling() {                                                                                                            // FUNCTION HANDLES SWITCHGEAR SWITCHING

  if ( switchgear_state_to_set == switchgear_state) {
    return 0;
  } else {
    if ( switchgear_state_to_set == NONE ) {
      relay_value_to_set[0] = 0;
      switchgear_state = NONE;
    } else {
      if ( switchgear_state != SWITCHING ) {
        switchgear_state_on_change = switchgear_state;
        switchgear_state = SWITCHING;
      } else {
        if (relay_value[0] == 0 && tick_switchgear < 4 && switchgear_state_on_change == NONE) {
          tick_switchgear = 5;
          goto skip_this_shit;
        } else {
          if (relay_value_to_set[0] != 0 && tick_switchgear <= 4) {
            relay_value_to_set[0] = 0;

          }
        }
skip_this_shit:
        if (tick_switchgear > 4 && tick_switchgear < 8 ) {
          if (relay_value_to_set[0] == 0) {
            switch (switchgear_state_to_set) {
              case 0:
                relay_value_to_set[0] = 0;
              break;
              case 1:
                relay_value_to_set[0] = 1;
              break;
              case 2:
                relay_value_to_set[0] = 2;
              break;
              case 3:
                relay_value_to_set[0] = 4;
              break;
              case 4:
                relay_value_to_set[0] = 8;
              break;
              case 5:
                relay_value_to_set[0] = 16;
              break;
              case 6:
                relay_value_to_set[0] = 32;
              break;
            }
          }
        }
        if ( tick_switchgear >= 8 ) {
          switchgear_state = switchgear_state_to_set;
          switchgear_state_on_change = switchgear_state;
          tick_switchgear = 0;
        }
      }
      return 1;
    }
  }

}

int pump_handling() {                                                                                                                   // FUNCTION HANDLES HYDRAULIC PUMP

  if (bitRead(limit_switch, switchgear_state - 1) == 1 && pump_state_to_set == DOWN) {        // do poprawy
    if (limit_switch_flag == 0) {                                                             // NOWE
      limit_switch_flag = 1;                                                                  // NOWE
    }                                                                                         // NOWE
    if (limit_switch_flag > 3) {                                                              // NOWE
//      if (system_mode == 1) {
//        system_mode = 0;
//      }
      pump_state = HOLD;
      relay_value_to_set[1] = 4;
      limit_switch_flag = 0;
      return 1;
    }                                                                                         // NOWE
  } else {
    limit_switch_flag = 0;
    if (pump_state_to_set == pump_state) {
      return 0;
    } else {
      if (pump_state != STARTING) {
        pump_state_on_change = pump_state_to_set;
        pump_state = STARTING;
        pump_relay_value_on_change = relay_value[1];
      } else {
        if (pump_relay_value_on_change == 0) {
          if (relay_value_to_set[1] != 4 && tick_pump <= 2) {
            relay_value_to_set[1] = 4;
          }
          if (tick_pump >= 2) {
            if (relay_value_to_set[1] == 4) {
              fast_switching:
              switch (pump_state_to_set) {
                case 0:
                  relay_value_to_set[1] = 0;
                break;
                case 1:
                  relay_value_to_set[1] = 5;
                break;
                case 2:
                  relay_value_to_set[1] = 6;
                break;
                case 3:
                  relay_value_to_set[1] = 4;
              }
            }
          }
          if (tick_pump >= 3) {
            if (relay_value_to_set[1] == relay_value[1]) {
              pump_state = pump_state_on_change;
              tick_pump = 0;
            }
          }
        } else {
          goto fast_switching;
        }
      }
      return 1;
    }
  }

}

int press_system_handling() {                                                                                                           // FUNCTION HANDLES SYSTEM PRESS WORK (double check is hydraulic pump off)

  if (pump_handling() == 0) {
    if (pump_state == ZERO) {
      switchgear_handling();
    }
  }

}


void setup() {

  Serial.begin(115200);
  delay(1000);
  check_modules();
  zero_REL6CH_modules();

}

void loop() {

  commands_handling();

  time_measure();

  read_inputs();

  calculate_buttons();

  press_system_handling();

  send_outputs();

}
