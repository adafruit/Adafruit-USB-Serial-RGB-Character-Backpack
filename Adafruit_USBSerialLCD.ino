/***********************************
Matrix-orbitalish compatible LCD driver with USB and Serial 
For use with Teensy 1.0 core on AT90USB162 chips

---> http://www.adafruit.com/category/63_96

Adafruit invests time and resources providing this open source code, 
please support Adafruit and open-source hardware by purchasing 
products from Adafruit!

Written by Limor Fried/Ladyada  for Adafruit Industries.  
BSD license, check license.txt for more information
All text above must be included in any redistribution
****************************************/


#include <LiquidCrystal.h>
#include <EEPROM.h>
#include <util/delay.h>

// uncomment below to have the display buffer echo'd to USB serial (handy!)
//#define USBLCDDEBUG 1

// this will echo a 'buffer' showing what the display thinks is showing
//#define USBECHOBUFFER 1

// this will echo incoming chars
//#define USBECHOCHARS 1

#define D4  1  // PD1
#define D5  4  // PD4
#define D6  5  // PD5
#define D7  6  // PD6
#define RS  12 // PB4
#define RW  13 // PB5
#define EN  14 // PB6

LiquidCrystal lcd(RS, RW, EN, D4, D5, D6, D7);

// This line defines a "Uart" object to access the serial port
HardwareSerial Uart = HardwareSerial();

// connect these to the analog output (PWM) pins!
#define REDLITE 0              // D0
#define GREENLITE 18           // C5
#define BLUELITE 17            // C6
#define CONTRASTPIN 15         // B7

#define GPO_1  8 // PB0
#define GPO_2  20 // PC2
#define GPO_3  19 //PC4
#define GPO_4  16 //PC7
uint8_t GPO[] = {GPO_1, GPO_2, GPO_3, GPO_4};

// see a list of matrix orbital commands here (we dont support -all-)
//http://www.matrixorbital.ca/manuals/LCDVFD_Series/LCD2041/LCD2041.pdf

/******** Communication commands */
//#define MATRIX_I2CADDR 0x33      // not supported
#define MATRIX_BAUDRATE 0x39       // 1 arg
//#define MATRIX_BAUDRATE2 0xA4      // not supported

/******** text commands */
#define MATRIX_AUTOSCROLL_ON 0x51
#define MATRIX_AUTOSCROLL_OFF 0x52
#define MATRIX_CLEAR 0x58
#define MATRIX_CHANGESPLASH 0x40  // COL * ROW chars!
#define MATRIX_AUTOWRAPLINE_ON 0x43
#define MATRIX_AUTOWRAPLINE_OFF 0x44
#define MATRIX_SETCURSOR_POSITION 0x47    // 2 args: col, row
#define MATRIX_HOME 0x48
#define MATRIX_MOVECURSOR_BACK 0x4C
#define MATRIX_MOVECURSOR_FORWARD 0x4D
#define MATRIX_UNDERLINECURSOR_ON 0x4A
#define MATRIX_UNDERLINECURSOR_OFF 0x4B
#define MATRIX_BLOCKCURSOR_ON 0x53
#define MATRIX_BLOCKCURSOR_OFF 0x54

/****** special chars */
#define MATRIX_CUSTOM_CHARACTER 0x4E  // 9 args: char #, 8 bytes data
#define MATRIX_SAVECUSTOMCHARBANK 0xC1  // 9 args: char #, 8 bytes data
#define MATRIX_LOADCUSTOMCHARBANK 0xC0  // 9 args: char #, 8 bytes data
/***** Numbers & Bargraphs */
// not supported until we know what these look like
//#define MATRIX_PLACEMEDIUMDIGIT 0x6F
/***** display func */
#define MATRIX_DISPLAY_ON  0x42    // backlight. 1 argument afterwards, in minutes
#define MATRIX_DISPLAY_OFF  0x46
#define MATRIX_SET_BRIGHTNESS 0x99 // 1 arg: scale
#define MATRIX_SETSAVE_BRIGHTNESS 0x98 // 1 arg: scale
#define MATRIX_SET_CONTRAST 0x50 // 1 arg
#define MATRIX_SETSAVE_CONTRAST 0x91 // 1 arg
/***** GPO commands */
#define MATRIX_GPO_OFF 0x56
#define MATRIX_GPO_ON 0x57
#define MATRIX_GPO_START_ONOFF 0xC3

/***** Extra Adafruit commands */
#define EXTENDED_RGBBACKLIGHT 0xD0  // 3 args - R G B
#define EXTENDED_SETSIZE 0xD1  // 2 args - Cols & Rows
#define EXTENDED_TESTBAUD 0xD2  // zero args, prints baud rate to uart


#define MATRIX_STARTL_COMMAND 0xFE
//#define MATRIX_END_COMMAND 0x9A

// storage of the current backlight state
#define COLS_ADDR 0
#define ROWS_ADDR 1
#define SPLASH_ADDR 2
#define BACKLIGHT_R_ADDR 100
#define BACKLIGHT_G_ADDR 101
#define BACKLIGHT_B_ADDR 102
#define BACKLIGHT_STATE_ADDR 103
#define BACKLIGHT_BRIGHTNESS_ADDR 104
#define AUTOSCROLL_ADDR 105
#define BAUDRATE_ADDR 106  // and 107, 108
#define CONTRAST_ADDR 109
#define CUSTOMCHARBANKS_ADDR 110  
// 110 thru 430 !
#define GPO_1_START_ONOFF_ADDR 431
#define GPO_2_START_ONOFF_ADDR 432
#define GPO_3_START_ONOFF_ADDR 434
#define GPO_4_START_ONOFF_ADDR 435
#define LAST_ADDR 436
#define EEPROM_END 511

uint8_t COLS = EEPROM.read(COLS_ADDR);
uint8_t ROWS = EEPROM.read(ROWS_ADDR);
uint8_t x, y;

extern unsigned int __bss_end;
extern unsigned int __heap_start;
extern void *__brkval;
int freeMemory() {
  int free_memory;

  if ((int)__brkval == 0)
     free_memory = ((int)&free_memory) - ((int)&__bss_end);
  else
    free_memory = ((int)&free_memory) - ((int)__brkval);

  return free_memory;
}

void setup() {
  if (getBaud() > 115200) {
    setBaud(9600); 
  } else {
    setBaud(getBaud());
  }
  if (COLS > 20) COLS = 20;
  if (ROWS > 4) ROWS = 4;
  
  pinMode(CONTRASTPIN, OUTPUT);
  pinMode(REDLITE, OUTPUT);
  pinMode(GREENLITE, OUTPUT);
  pinMode(BLUELITE, OUTPUT);

/*** test ****
  setBrightness(255);
  setBacklight(255, 0, 0);
  _delay_ms(250);
  setBacklight(0, 255, 0);
  _delay_ms(250);
  setBacklight(0, 0, 255);
  _delay_ms(250);  
  setBacklight(255, 255, 255);      // set backlight full on
  setContrast(200);                 // default contrast
  setSize(16, 2);                   // default is 16x2
  EEPROM.write(SPLASH_ADDR, 0xFF);  // use default splashscreen
  setBaud(9600);                    // default baud rate
  //for(uint8_t i=0; i<4; i++)        // set all GPO to 'LOW' default
  // EEPROM.write(GPO_1_START_ONOFF_ADDR+i, O);
/*** test ****/

  for(uint8_t i=0; i<4; i++) {       // set all GPO to 'LOW' default
   if (EEPROM.read(GPO_1_START_ONOFF_ADDR+i)) 
     digitalWrite(GPO[i], HIGH);
   else
     digitalWrite(GPO[i], LOW);
   pinMode(GPO[i], OUTPUT);
  }
  // for the initial 'blink' we want to use default settings:
  lcd.begin(16, 2);
  analogWrite(CONTRASTPIN, 50);  // test contrast
  analogWrite(REDLITE, 255);
  analogWrite(GREENLITE, 255);
  analogWrite(BLUELITE, 255);

  lcd.clear();
  lcd.home();
  lcd.print(getBaud());
  lcd.print(F(" baud "));
  lcd.print(COLS); lcd.print('x'); lcd.print(ROWS);
  lcd.setCursor(0,1);
  lcd.print(F("Constrast = ")); lcd.print(getContrast());

  Uart.print(getBaud());
  Uart.print(F(" baud "));
  Uart.print(COLS); Uart.print('x'); Uart.print(ROWS);
  Uart.print(F(" constrast = ")); Uart.print(getContrast());

  Serial.print(getBaud());
  Serial.print(F(" baud "));
  Serial.print(COLS); Serial.print('x'); Serial.print(ROWS);
  Serial.print(F(" constrast = ")); Serial.print(getContrast());
  
  _delay_ms(250);

  // now setup the way we expect
  lcd.begin(COLS, ROWS);
  setContrast(getContrast());
  displayOn();
  
#ifdef USBLCDDEBUG
  // print to USB only
  Serial.print(F("free mem = ")); Serial.println(freeMemory());
#endif

  
  // do splash screen
  if (EEPROM.read(SPLASH_ADDR) == 0xFF) { 
    lcd.clear();
    lcd.home();
    lcd.print(F("USB/Serial LCD"));
    lcd.setCursor(0,1);
    lcd.print(F("Adafruit.com"));
  } else {
     for (uint8_t i=0; i < ROWS; i++) {
       lcd.setCursor(0,i);
       for (uint8_t j=0; j<COLS; j++) {
          lcd.write(EEPROM.read(SPLASH_ADDR + j * 40 + i));   
       }
     }
  }
  _delay_ms(250);
  _delay_ms(250);
  _delay_ms(250);
  _delay_ms(250);
  
  lcd.clear();
  x = 0; y = 0;
  clearbuffer();
  lcd.home();
}

// max 20x4
char displaybuff[20][4];

void loop() {
  byte a, b, c;
  //parse command loop 
  
  if (serialAvailable()) {
    c = serialBlockingRead();
    
    if (c != MATRIX_STARTL_COMMAND) {
      // not a command, just print the text!

      if (c == 0x0D) {
        // special exception for new lines
        while (x <= COLS-1) {
          lcd.print(' '); // fill with spaces
          displaybuff[x][y] = ' ';
          x++;
        }   
      } else if (c == 0x0A) {
       // do nothing 
       return;
      } else if (c == 0x08) {
       if (x > 0) x--;
         else {
           x = COLS - 1;
          if (y > 0) y--;
          else y = ROWS - 1; 
         }
         lcd.setCursor(x, y);
         displaybuff[x][y] = ' ';
         lcd.print(' ');
         lcd.setCursor(x, y);
         return;
      }
      else {
        lcd.print((char)c);
        displaybuff[x][y] = c;
      } 
      
      // wrap the cursor
      x++;
      if (x >= COLS) {
        // go to the next row
        x = 0;
        y++;
        if (y >= ROWS) {
          // ran out of display space!
          if (! getAutoScroll()) {
            // go to the top left
            y = 0;
          } else {
            // shift all data up by one line!
            for (int8_t i=0; i < ROWS; i++) {
              for (uint8_t j=0; j<COLS; j++) {
                if (i == ROWS-1) {
                  //Serial.print("spaces");
                  displaybuff[j][ROWS-1] = ' ';
                } else {
                  displaybuff[j][i] = displaybuff[j][i+1];                  
                }
              }
            }
            for (int8_t i=0; i < ROWS; i++) {
              lcd.setCursor(0, i);
              for (uint8_t j=0; j<COLS; j++) {
                lcd.write(displaybuff[j][i]);
              }
            }
            // set the x & y
            x = 0;
            y = ROWS-1;
            printbuffer();
          }
        }
        lcd.setCursor(x, y);
      }
       printbuffer();
      return;
    }
    //Serial.print(F("\ncommand: "));
    // it is a command! get the command byte
    c = serialBlockingRead();
    //Serial.println(c, HEX);
    switch (c) {
      case MATRIX_DISPLAY_ON:
        displayOn();
        c = serialBlockingRead();   // todo - add timeout!
        break;
      case MATRIX_DISPLAY_OFF:
        displayOff();
        break;
      case MATRIX_SET_BRIGHTNESS:
      case MATRIX_SETSAVE_BRIGHTNESS:
        c = serialBlockingRead();
        setBrightness(c);
        break;
      case MATRIX_SET_CONTRAST:
      case MATRIX_SETSAVE_CONTRAST:
        c = serialBlockingRead();
        setContrast(c);
        break;
      case MATRIX_HOME:
        lcd.home();
        x = 0; y = 0;
        break;
      case MATRIX_CLEAR:
        lcd.clear();
        clearbuffer();
        x = 0; y = 0;
        break;
      case MATRIX_AUTOSCROLL_OFF:
        setAutoScroll(0);
        break;
      case MATRIX_AUTOSCROLL_ON:
        setAutoScroll(1);
        break;
      case MATRIX_AUTOWRAPLINE_OFF:
      case MATRIX_AUTOWRAPLINE_ON:
         // not implemented
         break;
      case MATRIX_SETCURSOR_POSITION:
         x = serialBlockingRead();
         y = serialBlockingRead();
         x--; y--;// matrix orbital starts at (1,1) not (0,0)
         if (x >= COLS) { y += x / COLS; x %= COLS; }
         y %= ROWS;
         lcd.setCursor(x, y);  
         //Serial.print(F("\nMoving to (")); Serial.print(x, DEC); 
         //Serial.print(','); Serial.print(y, DEC); Serial.println(')');
         break;
       case MATRIX_MOVECURSOR_BACK:
         if (x > 0) x--;
         else {
           x = COLS - 1;
          if (y > 0) y--;
          else y = ROWS - 1; 
         }
         lcd.setCursor(x, y);
         break;
       case MATRIX_MOVECURSOR_FORWARD:
         if (x < COLS - 1) x++;
         else {
           x = 0;
          if (y < ROWS - 1) y++;
          else y = 0; 
         }
         lcd.setCursor(x, y);
         break;
       case MATRIX_UNDERLINECURSOR_ON:
         lcd.cursor();
         break;
       case MATRIX_BLOCKCURSOR_OFF:
       case MATRIX_UNDERLINECURSOR_OFF:
         lcd.noCursor();
         lcd.noBlink();
         break;
       case MATRIX_BLOCKCURSOR_ON:
         lcd.blink();
         break;
       case MATRIX_CHANGESPLASH:
         for (uint8_t i=0; i < ROWS; i++) {
            for (uint8_t j=0; j<COLS; j++) {
              c = serialBlockingRead();
              EEPROM.write(SPLASH_ADDR + j * 40 + i, c); 
            }
          }
         break; 
       case MATRIX_BAUDRATE:
         c = serialBlockingRead();
         switch (c) {
           case 0x53: setBaud(1200); break;
           case 0x29: setBaud(2400); break;
           case 0xCf: setBaud(4800); break;
           case 0x67: setBaud(9600); break;
           case 0x33: setBaud(19200); break;
           case 0x22: setBaud(28800); break;
           case 0x19: setBaud(38400); break;
           case 0x10: setBaud(57600); break;
           case 0x08: setBaud(115200); break;
         }
         break;
       case MATRIX_CUSTOM_CHARACTER:
         c = serialBlockingRead();
         readCustom(c, 255);
         break;
       case MATRIX_LOADCUSTOMCHARBANK:
         c = serialBlockingRead();
         loadCustom(c);
         break;
       case MATRIX_SAVECUSTOMCHARBANK:
         //Serial.println(F("Custom char")); 
         b = serialBlockingRead();
         c = serialBlockingRead();
         readCustom(c, b);
         break;
        case MATRIX_GPO_OFF:
          a = serialBlockingRead();
          a--;
          if (a >= 4) return;
          digitalWrite(GPO[a], LOW);
          break;
        case MATRIX_GPO_ON:
          a = serialBlockingRead();
          a--;
          if (a >= 4) return;
          digitalWrite(GPO[a], HIGH);
          break;
        case MATRIX_GPO_START_ONOFF:
          a = serialBlockingRead();
          b = serialBlockingRead();
          a--;
          if (a >= 4) return;
          EEPROM.write(GPO_1_START_ONOFF_ADDR+a, b);
          break;
         /*  hmm this didnt work out, try again later? 
       case MATRIX_PLACEMEDIUMDIGIT:
         a = serialBlockingRead();
         b = serialBlockingRead();
         c = serialBlockingRead();
         // MEME: load the medium chars into RAM
         uint8_t tl, tr, bl, br;
         if (c == 0) {
             tl = 1; tr = 0; bl = 3; br = 2;
         } else if (c == 1) {
             tl = 0; tr = ' '; bl = 2; br = 4;
         } else if (c == 2) {
             tl = 5; tr = 6; bl = 3; br = 4;
         } else if (c == 3) {
             tl = 5; tr = 6; bl = 4; br = 2;
         } else if (c == 4) {
             tl = 3; tr = 2; bl = ' '; br = ' ';
         } else if (c == 5) {
             tl = 3; tr = 2; bl = ' '; br = ' ';
         }
         lcd.setCursor(a, b);
         lcd.write(tl);        
         lcd.setCursor(a+1, b);
         lcd.write(tr);        
         lcd.setCursor(a, b+1);
         lcd.write(bl);        
         lcd.setCursor(a+1, b+1);
         lcd.write(br);        
         break;
         */
       case EXTENDED_RGBBACKLIGHT:
         a = serialBlockingRead();
         b = serialBlockingRead();
         c = serialBlockingRead();
         setBacklight(a, b, c);
         break;
         
       case EXTENDED_SETSIZE:
         a = serialBlockingRead();
         b = serialBlockingRead();
         setSize(a, b);
         break;
       case EXTENDED_TESTBAUD:
         Uart.print(getBaud());
         break;
     }
  }
}

void loadCustom(uint8_t bank) {
  uint8_t newChar[8];
  
  if (bank > 4) return;
  
  int16_t addr = bank;
    addr *= 64;
    addr += CUSTOMCHARBANKS_ADDR;
    
  for (uint8_t loc = 0; loc < 8; loc++) {
    for (uint8_t i=0; i<8; i++) {
     newChar[i] = EEPROM.read(addr);
     //Serial.print(F("Loaded ")); Serial.print(newChar[i], HEX); Serial.print(F(" from $"));
     //Serial.println(addr);
     addr++;
    }
    lcd.createChar(loc, newChar);
    //lcd.write(loc);
  }
  lcd.setCursor(x, y);
}

void readCustom(uint8_t loc, uint8_t bank) {
/*
  Serial.print(F("Saving char to bank #")); Serial.print(bank, DEC);
  Serial.print(F(" : "));
  Serial.println(loc, DEC);
  */
  
  uint8_t newChar[8];
  for (uint8_t i=0; i<8; i++) {
     newChar[i] = serialBlockingRead();
  }
  if (bank > 4) {
    // instant display
    lcd.createChar(loc, newChar);
    lcd.setCursor(x, y);
  } else {
    // save it to EEPROM
    int16_t addr = bank;
    addr *= 64;
    addr += loc * 8;
    addr += CUSTOMCHARBANKS_ADDR;
    
    for (uint8_t i=0; i<8; i++) {
      EEPROM.write(addr + (int16_t)i, newChar[i]);
    }
  }
} 

uint8_t getContrast() {
  EEPROM.read(CONTRAST_ADDR);
}

void setContrast(uint8_t c) {
  if (c != getContrast()) {
    EEPROM.write(CONTRAST_ADDR, c);
  }
  analogWrite(CONTRASTPIN, 255-c);      // contrast is inverted
}

uint32_t getBaud() {
  uint32_t b;
  
  b = EEPROM.read(BAUDRATE_ADDR);
  b <<= 8;
  b |= EEPROM.read(BAUDRATE_ADDR+1);
  b <<= 8;
  b |= EEPROM.read(BAUDRATE_ADDR+2);

  return b;
}

int serialAvailable() {
  return max(Serial.available(), Uart.available());
}

char serialBlockingRead() {
   while (!serialAvailable());
   char c = 0;

   if (Serial.available()) {
#ifdef USBECHOCHARS
     Serial.print(F("Read USB char: "));
#endif
     c = Serial.read();
   } else if (Uart.available()) {
#ifdef USBECHOCHARS
     Serial.print(F("Read UART char: "));
#endif
     c = Uart.read();
   }
#ifdef USBECHOCHARS
   Serial.write(c);
   Serial.print(F(" (0x"));
   Serial.print(c, HEX);
   Serial.print(')');
#endif
  return c;
}

void setBaud(uint32_t baudrate) {
  if (getBaud() != baudrate) {
    EEPROM.write(BAUDRATE_ADDR, baudrate >> 16);
    EEPROM.write(BAUDRATE_ADDR+1, baudrate >> 8);
    EEPROM.write(BAUDRATE_ADDR+2, baudrate & 0xFF);
  }
  
  Serial.begin(baudrate); 
  Uart.begin(baudrate);
  // the Uart is a little noisy without a pullup, so we'll use the internal one on PD2
  digitalWrite(PD2, HIGH);
}

void setAutoScroll(uint8_t x) {
  EEPROM.write(AUTOSCROLL_ADDR, x);
}
uint8_t getAutoScroll() {
  return EEPROM.read(AUTOSCROLL_ADDR);
}

void displayOn() {
  setBrightness(EEPROM.read(BACKLIGHT_BRIGHTNESS_ADDR));
}

void displayOff() {
  analogWrite(REDLITE, 0);
  analogWrite(GREENLITE, 0);
  analogWrite(BLUELITE, 0);
}

void setBrightness(uint8_t brightness) {
    if (brightness != EEPROM.read(BACKLIGHT_BRIGHTNESS_ADDR))
      EEPROM.write(BACKLIGHT_BRIGHTNESS_ADDR, brightness);
    setBacklight(EEPROM.read(BACKLIGHT_R_ADDR), EEPROM.read(BACKLIGHT_G_ADDR), EEPROM.read(BACKLIGHT_B_ADDR));
}

void setSize(uint8_t c, uint8_t r) {
  if (r != EEPROM.read(ROWS_ADDR))
    EEPROM.write(ROWS_ADDR, r);
  if (c != EEPROM.read(COLS_ADDR))
    EEPROM.write(COLS_ADDR, c);

  COLS = c;
  ROWS = r;
}

void setBacklight(uint8_t r, uint8_t g, uint8_t b) {
  if (r != EEPROM.read(BACKLIGHT_R_ADDR))
    EEPROM.write(BACKLIGHT_R_ADDR, r);
  if (g != EEPROM.read(BACKLIGHT_G_ADDR))
    EEPROM.write(BACKLIGHT_G_ADDR, g);
  if (b != EEPROM.read(BACKLIGHT_B_ADDR))
    EEPROM.write(BACKLIGHT_B_ADDR, b);
    
  uint8_t brightness = EEPROM.read(BACKLIGHT_BRIGHTNESS_ADDR);
  // normalize the red LED
  r = map(r, 0, 255, 0, 100);
  b = map(b, 0, 255, 0, 190);

  r = map(r, 0, 255, 0, brightness);
  g = map(g, 0, 255, 0, brightness);
  b = map(b, 0, 255, 0, brightness);

  analogWrite(REDLITE, r);
  analogWrite(GREENLITE, g);
  analogWrite(BLUELITE, b);

  TCNT0 = 127;
  TCNT1 = 0;
  TCCR0B = 0x01;
  TCCR1B = 0x01;
  
   /*
  Serial.print(F("Brightness: ")); Serial.print(brightness, DEC);
  Serial.print(F(" R = ")); Serial.print(r, DEC);
  Serial.print(F(" G = ")); Serial.print(g, DEC);
  Serial.print(F(" B = ")); Serial.println(b, DEC);

  Serial.print(F("TCCR0A = ")); Serial.println(TCCR0A, HEX);
  Serial.print(F("TCCR0B = ")); Serial.println(TCCR0B, HEX);
  Serial.print(F("OCR0B = ")); Serial.println(OCR0B, HEX);

  Serial.print(F("TCCR1A = ")); Serial.println(TCCR1A, HEX);
  Serial.print(F("TCCR1B = ")); Serial.println(TCCR1B, HEX);
  Serial.print(F("OCR1A = ")); Serial.println(OCR1A, HEX);
  Serial.print(F("OCR1B = ")); Serial.println(OCR1B, HEX);
  */
}

void clearbuffer() {
    for (uint8_t i=0; i <ROWS; i++) {
       for (uint8_t j=0; j<COLS; j++) {
         displaybuff[j][i] = ' ';
       }
    }
}


void printbuffer() {
#ifdef USBECHOBUFFER
  Serial.println(F("\n\r------------------"));
  for (uint8_t i=0; i <ROWS; i++) {
    Serial.print('|');
    for (uint8_t j=0; j<COLS; j++) {
      Serial.print(displaybuff[j][i], BYTE);   
    }
    Serial.println('|');
   }
   Serial.println(F("------------------"));
#endif
}

