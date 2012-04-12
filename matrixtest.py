'''
Test python sketch for Adafruit USB+Serial LCD backpack
---> http://www.adafruit.com/category/63_96

Adafruit invests time and resources providing this open source code, 
please support Adafruit and open-source hardware by purchasing 
products from Adafruit!

Written by Limor Fried/Ladyada  for Adafruit Industries.  
BSD license, check license.txt for more information
All text above must be included in any redistribution
'''


import serial
import sys
import time

# 20x4 LCD
#ROWS = 4
#COLS = 20

# 16x2 LCD:
ROWS = 2
COLS = 16

def matrixwritecommand(commandlist):
    commandlist.insert(0, 0xFE)
    #ser.write(bytearray([0xFE]))
    #time.sleep(0.1);
    for i in range(0, len(commandlist)):
         #print chr(commandlist[i]),
         ser.write(chr(commandlist[i]))
    #ser.write(bytearray(commandlist))

# 1. get serial port
if len(sys.argv) != 2:
    print "Usage: python test.py <serialport>"
    exit(0)

'''
# baudrate fix
ser = serial.Serial(sys.argv[1], 2400, timeout=1)
matrixwritecommand([0x39, 0x67])
time.sleep(2);
ser = serial.Serial(sys.argv[1], 4800, timeout=1)
matrixwritecommand([0x39, 0x67])
time.sleep(2);
ser = serial.Serial(sys.argv[1], 19200, timeout=1)
matrixwritecommand([0x39, 0x67])
time.sleep(2);
ser = serial.Serial(sys.argv[1], 28800, timeout=1)
matrixwritecommand([0x39, 0x67])
time.sleep(2);
ser = serial.Serial(sys.argv[1], 38400, timeout=1)
matrixwritecommand([0x39, 0x67])
time.sleep(2);
ser = serial.Serial(sys.argv[1], 57600, timeout=1)
matrixwritecommand([0x39, 0x67])
time.sleep(2);
'''

ser = serial.Serial(sys.argv[1], 9600, timeout=1)
matrixwritecommand([0x58]) 

# set size
matrixwritecommand([0xD1, COLS, ROWS]);
matrixwritecommand([0x58]) 

# turn on display
ser.write("Display on");
matrixwritecommand([0x42, 0]) 
time.sleep(0.3);

# contrast loop
for i in range(0, 256):
    matrixwritecommand([0x50, i]) 
#time.sleep(0.1);

matrixwritecommand([0x50, 220])


# turn GPIO's on
matrixwritecommand([0x57, 1])
time.sleep(0.1)
matrixwritecommand([0x57, 2])
time.sleep(0.1)
matrixwritecommand([0x57, 3])
time.sleep(0.1)
matrixwritecommand([0x57, 4])
time.sleep(0.1)
# turn GPIO's off
matrixwritecommand([0x56, 1])
time.sleep(0.1)
matrixwritecommand([0x56, 2])
time.sleep(0.1)
matrixwritecommand([0x56, 3])
time.sleep(0.1)
matrixwritecommand([0x56, 4])
time.sleep(0.1)

# turn off display
ser.write("off");
matrixwritecommand([0x46]) 
time.sleep(0.3);

# turn on display
ser.write("on");
matrixwritecommand([0x42, 0]) 
time.sleep(0.3);

# create custom char
matrixwritecommand([0x4E, 0, 0, 0xA, 0x15, 0x11, 0x11, 0xA, 0x4, 0]) 
ser.write(chr(0))
time.sleep(0.5)

# color loop
matrixwritecommand([0x99, 255]) 
for r in range(0, 256):
    matrixwritecommand([0xD0, r, 0, 0]) 
    time.sleep(0.005);
for g in range(0, 256):
    matrixwritecommand([0xD0, 255-g, g, 0]) 
    time.sleep(0.005);
for b in range(0, 256):
    matrixwritecommand([0xD0, 0, 255-b, b]) 
    time.sleep(0.005);
for r in range(0, 256):
    matrixwritecommand([0xD0, r, 0, 255-r]) 
    time.sleep(0.005);
for r in range(255, 0):
    matrixwritecommand([0xD0, r, 0, 0]) 
    time.sleep(0.005);

matrixwritecommand([0x99, 0]) 
matrixwritecommand([0xD0, 255, 255, 255]) 
# brightness loop
for i in range(0, 256):
    matrixwritecommand([0x99, i]) 
    time.sleep(0.01);

# home
matrixwritecommand([0x48]) 
ser.write("home");
time.sleep(0.5);

#clear
matrixwritecommand([0x58]) 
ser.write("clear");
time.sleep(0.5);

matrixwritecommand([0x58]) 
# create horizontal bars in custom chars bank #1
matrixwritecommand([0xC1, 1, 0, 0x10,0x10,0x10,0x10,0x10,0x10,0x10,0x10]) 
matrixwritecommand([0xC1, 1, 1, 0x18,0x18,0x18,0x18,0x18,0x18,0x18,0x18])
matrixwritecommand([0xC1, 1, 2, 0x1C,0x1C,0x1C,0x1C,0x1C,0x1C,0x1C,0x1C])
matrixwritecommand([0xC1, 1, 3, 0x1E,0x1E,0x1E,0x1E,0x1E,0x1E,0x1E,0x1E]) 
matrixwritecommand([0xC1, 1, 4, 0xF,0xF,0xF,0xF,0xF,0xF,0xF,0xF]) 
matrixwritecommand([0xC1, 1, 5, 0x7,0x7,0x7,0x7,0x7,0x7,0x7,0x7]) 
matrixwritecommand([0xC1, 1, 6, 0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3]) 
matrixwritecommand([0xC1, 1, 7, 0x1,0x1,0x1,0x1,0x1,0x1,0x1,0x1]) 
matrixwritecommand([0xC0, 1])  # load bank 1
ser.write(chr(0))
ser.write(chr(1))
ser.write(chr(2))
ser.write(chr(3))
ser.write(chr(4))
ser.write(chr(5))
ser.write(chr(6))
ser.write(chr(7))
time.sleep(1)

matrixwritecommand([0x58]) 
# create vertical bars in custom chars bank #2
matrixwritecommand([0xC1, 2, 0, 0,0,0,0,0,0,0,0x1F])
matrixwritecommand([0xC1, 2, 1, 0,0,0,0,0,0,0x1F,0x1F])
matrixwritecommand([0xC1, 2, 2, 0,0,0,0,0,0x1F,0x1F,0x1F])
matrixwritecommand([0xC1, 2, 3, 0,0,0,0,0x1F,0x1F,0x1F,0x1F])
matrixwritecommand([0xC1, 2, 4, 0,0,0,0x1F,0x1F,0x1F,0x1F,0x1F])
matrixwritecommand([0xC1, 2, 5, 0,0,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F])
matrixwritecommand([0xC1, 2, 6, 0,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F])
matrixwritecommand([0xC1, 2, 7, 0x1F,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F])
matrixwritecommand([0xC0, 2])
ser.write(chr(0))
ser.write(chr(1))
ser.write(chr(2))
ser.write(chr(3))
ser.write(chr(4))
ser.write(chr(5))
ser.write(chr(6))
ser.write(chr(7))
time.sleep(1)


matrixwritecommand([0x58]) 
# create medium numbers in bank #3
matrixwritecommand([0xC1, 3, 0, 0x1f,0x1f,0x03,0x03,0x03,0x03,0x03,0x03])
matrixwritecommand([0xC1, 3, 1, 0x1f,0x1f,0x18,0x18,0x18,0x18,0x18,0x18])
matrixwritecommand([0xC1, 3, 2, 0x03,0x03,0x03,0x03,0x03,0x03,0x1F,0x1F])
matrixwritecommand([0xC1, 3, 3, 0x18,0x18,0x18,0x18,0x18,0x18,0x1F,0x1F])
matrixwritecommand([0xC1, 3, 4, 0x00,0x00,0x00,0x00,0x00,0x00,0x1F,0x1F])
matrixwritecommand([0xC1, 3, 5, 0x1F,0x1F,0x00,0x00,0x00,0x00,0x00,0x00])
matrixwritecommand([0xC1, 3, 6, 0x1F,0x1F,0x03,0x03,0x03,0x03,0x1F,0x1F])

matrixwritecommand([0xC1, 3, 7, 0x1F,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F])
matrixwritecommand([0xC0, 3])
ser.write(chr(0))
ser.write(chr(1))
ser.write(chr(2))
ser.write(chr(3))
ser.write(chr(4))
ser.write(chr(5))
ser.write(chr(6))
ser.write(chr(7))
time.sleep(1)

matrixwritecommand([0x58])
# write medium num #0
matrixwritecommand([0x6F, 0, 0, 0])
matrixwritecommand([0x6F, 2, 0, 1])
matrixwritecommand([0x6F, 4, 0, 2])
matrixwritecommand([0x6F, 6, 0, 3])
time.sleep(1)

# autoscroll on
matrixwritecommand([0x58]) 
matrixwritecommand([0x51])
if (ROWS == 4):
    ser.write("Here is a long long long line of text   ");
    time.sleep(1)
    ser.write("Adding more text... ");
    time.sleep(1)
    ser.write("even more text now!");
    time.sleep(1)
    ser.write(" which will scroll");
if (ROWS == 2):
    ser.write("Here's some text");
    time.sleep(1)
    ser.write("Add some more..");
    time.sleep(1)
    ser.write(" which'll scroll");
time.sleep(1)

# autoscroll off
matrixwritecommand([0x58]) 
matrixwritecommand([0x52]) 
ser.write("long long long text that ends @ top left    ");
time.sleep(1);

# cursor test
matrixwritecommand([0x58]) 
matrixwritecommand([0x47,1,1]) 
ser.write('1');
matrixwritecommand([0x47,COLS,1]) 
ser.write('2');
matrixwritecommand([0x47,1,ROWS]) 
ser.write('3');
matrixwritecommand([0x47,COLS,ROWS]) 
ser.write('4');

#underline cursor on
matrixwritecommand([0x4A])
# move cursor left
matrixwritecommand([0x4C])
time.sleep(2);
# cursor off
matrixwritecommand([0x4B])
time.sleep(0.5);

# block cursor
matrixwritecommand([0x53])
# move cursor right
matrixwritecommand([0x4D])
time.sleep(2);
matrixwritecommand([0x54])
time.sleep(0.5);

# baudrate change
matrixwritecommand([0x39, 0x29])
time.sleep(1);
ser.close();
ser = serial.Serial(sys.argv[1], 2400, timeout=1)
matrixwritecommand([0x58]) 
ser.write("2400")

matrixwritecommand([0x39, 0xCF])
time.sleep(1);
ser.close();
ser = serial.Serial(sys.argv[1], 4800, timeout=1)
matrixwritecommand([0x58]) 
ser.write("4800")

matrixwritecommand([0x39, 0x67])
time.sleep(1);
ser.close();
ser.close();
ser = serial.Serial(sys.argv[1], 9600, timeout=1)
matrixwritecommand([0x58]) 
ser.write("9600")

matrixwritecommand([0x39, 0x33])
time.sleep(1);
ser.close();
ser = serial.Serial(sys.argv[1], 19200, timeout=1)
matrixwritecommand([0x58]) 
ser.write("19200")

matrixwritecommand([0x39, 0x22])
time.sleep(1);
ser.close();
ser = serial.Serial(sys.argv[1], 28800, timeout=1)
matrixwritecommand([0x58]) 
ser.write("28800")

matrixwritecommand([0x39, 0x19])
time.sleep(1);
ser.close();
ser = serial.Serial(sys.argv[1], 38400, timeout=1)
matrixwritecommand([0x58]) 
ser.write("38400")

matrixwritecommand([0x39, 0x10])
time.sleep(1);
ser.close();
ser = serial.Serial(sys.argv[1], 57600, timeout=1)
matrixwritecommand([0x58]) 
ser.write("57600")

# Revert back to 9600 baud
matrixwritecommand([0x39, 0x67])
time.sleep(1);
ser.close();
ser = serial.Serial(sys.argv[1], 9600, timeout=1)

# Splashscreen change
matrixwritecommand([0x40, ord('H'),ord('e'),ord('l'),ord('l'),ord('o'),ord(' '),ord('W'),ord('o'),ord('r'),ord('l'),ord('d'),ord('!'),ord(' '),ord(' '),ord(' '),ord(' '),ord('T'),ord('e'),ord('s'),ord('t'),ord('i'),ord('n'),ord('g'),ord(' '),ord('1'),ord('6'),ord('x'),ord('2'),ord(' '),ord('L'),ord('C'),ord('D')])

#matrixwritecommand([0x40, ord(' '),ord(' '),ord('A'),ord('d'),ord('a'),ord('f'),ord('r'),ord('u'),ord('i'),ord('t'),ord('.'),ord('c'),ord('o'),ord('m'),ord(' '),ord(' '),ord('1'),ord('6'),ord('x'),ord('2'),ord(' '),ord('U'),ord('S'),ord('B'),ord('+'),ord('S'),ord('e'),ord('r'),ord(' '),ord('L'),ord('C'),ord('D')]) 
exit()

