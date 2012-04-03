import serial
import sys
import time

# matrix orbital example test


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


# turn on display
ser.write("Display on");
matrixwritecommand([0x42, 0]) 
time.sleep(0.3);

# contrast loop
#for i in range(0, 256):
    #matrixwritecommand([0x50, i]) 
#time.sleep(0.1);

matrixwritecommand([0x50, 80]) 

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

'''
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
'''

# autoscroll on
matrixwritecommand([0x58]) 
matrixwritecommand([0x51]) 
ser.write("long long long text that scrolls the display ");
time.sleep(1);

# autoscroll off
matrixwritecommand([0x58]) 
matrixwritecommand([0x52]) 
ser.write("long long long text that ends @ top left   ");
time.sleep(1);

# cursor test
matrixwritecommand([0x58]) 
matrixwritecommand([0x47,1,1]) 
ser.write('1');
matrixwritecommand([0x47,16,1]) 
ser.write('2');
matrixwritecommand([0x47,1,2]) 
ser.write('3');
matrixwritecommand([0x47,16,2]) 
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
#matrixwritecommand([0x40, 'H','e','l','l','o',' ','W','o','r','l','d','!',' ',' ',' ',' ','T','e','s','t','i','n','g',' ','1','6','x','2',' ','L','C','D'])

#matrixwritecommand([0x40, ' ',' ','A','d','a','f','r','u','i','t','.','c','o','m',' ',' ','1','6','x','2',' ','U','S','B','+','S','e','r',' ','L','C','D']) 
exit()

