import serial
import itertools
from collections import defaultdict
from enum import Enum

# Special signals for the controller
SIG_COMMAND = 0xfe
CMD_CLEAR = 0x58
CMD_BACKLIGHT_ON = 0x42
CMD_BACKLIGHT_OFF = 0x46
CMD_SIZE = 0xd1
CMD_SPLASH_TEXT = 0x40
CMD_BRIGHTNESS = 0x98
CMD_CONTRAST = 0x91
CMD_COLOR = 0xd0
CMD_AUTOSCROLL_ON = 0x51
CMD_AUTOSCROLL_OFF = 0x52
CMD_UNDERLINE_CURSOR_ON = 0x4a
CMD_UNDERLINE_CURSOR_OFF = 0x4b
CMD_BLOCK_CURSOR_ON = 0x53
CMD_BLOCK_CURSOR_OFF = 0x54
CMD_CURSOR_HOME = 0x48
CMD_CURSOR_POS = 0x47
CMD_CURSOR_FWD = 0x4d
CMD_CURSOR_BACK = 0x4c
CMD_CREATE_CHAR = 0x4e
CMD_SAVE_CUSTOM_CHAR = 0xc1
CMD_LOAD_CHAR_BANK = 0xc0

BAUD_RATE = 9600


class CursorMode(Enum):
    off = 1
    underline = 2
    block = 3


def format_bytes(data):
    return ' '.join('{:02x}'.format(b) for b in data)


def diff_text(lines1, lines2):
    """
    @brief      Diffs the given lists of strings, producing a dict of (x,y):str tuples of the text
                from lines2 where they differed. Adjacent differing characters are included
                together in the same string. If one list is longer then the other, the shorter list
                is padded with empty strings. If one line is longer than its counterpart, the
                shorter string is padded with spaces. See unit tests for examples.

    @param      lines1  The first list of strings
    @param      lines2  The second list of strings (this one takes priority)

    @return     A dict of (x,y):str tuples representing changes from lines1 to lines2
    """
    diff = defaultdict(lambda: [])  # List of chars is more efficient for building up
    for y, (line1, line2) in enumerate(itertools.zip_longest(lines1, lines2, fillvalue='')):
        pos = None
        for x, (c1, c2) in enumerate(itertools.zip_longest(line1, line2, fillvalue=' ')):
            if c1 != c2:
                if pos is None:
                    pos = (x, y)
                diff[pos].append(c2)
            else:
                pos = None
    return {k: ''.join(v) for k, v in diff.items()}


class Lcd:

    def __init__(self, serial_port, width, height):
        self._ser = serial.Serial(serial_port,
                                  baudrate=BAUD_RATE,
                                  bytesize=serial.EIGHTBITS,
                                  parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE,
                                  writeTimeout=0)

        # Declare fields
        self._width, self._height = None, None
        self._color = None
        self._lines = None

        # Use the setters to initialize them
        self.set_size(width, height)
        self.set_color((0, 0, 0))

    def _write(self, data, flush=False):
        """
        @brief      Writes the given bytes to the serial stream. The given data must be a bytes-like
                    object.

        @param      data   The data (must be bytes-like)
        @param      flush  Whether or not to flush the serial buffer after writing the data

        @return     The number of bytes written
        """
        num_written = self._ser.write(data)
        if num_written != len(data):
            raise IOError("Expected to write {} bytes (), but only wrote {} bytes".format(
                len(data), format_bytes(data), num_written)
            )
        if flush:
            self.flush_serial()
        return num_written

    def _send_cmd(self, command, *args, flush=False):
        """
        @brief      Sends the given command to the LCD, with the given arguments.

        @param      command  The command to send
        @param      args     The arguments for the command (if any)
        """
        all_bytes = bytes([SIG_COMMAND, command]) + bytes(args)
        self._write(all_bytes, flush)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def color(self):
        return self._color

    @property
    def text(self):
        return '\n'.join(self._lines)

    def flush_serial(self):
        """
        @brief      Flushes the serial buffer, i.e. waits until everything in the buffer is sent.
        """
        self._ser.flush()

    def clear(self):
        """
        @brief      Clears all text on the screen.
        """
        self._send_cmd(CMD_CLEAR)

    def on(self):
        """
        @brief      Turns the display on, restoring saved brightness, contrast, text and color.
        """
        # The on command takes an arg for how long to stay on, but it's actually ignored.
        self._send_cmd(CMD_BACKLIGHT_ON, 0)

    def off(self):
        """
        @brief      Turns the display off. Brightness, contrast, text, and color are saved.
        """
        self._send_cmd(CMD_BACKLIGHT_OFF)

    def set_size(self, width, height):
        """
        @brief      Configures the size of the LCD. Only needs to be called once ever, and the LCD
                    will remember its size.

        @param      width   The width of the LCD (in characters)
        @param      height  The height of the LCD (in characters)
        """
        if self._width != width or self._height != height:
            self._width, self._height = width, height
            self._send_cmd(CMD_SIZE, width, height)
            self._lines = [''] * height  # Resize the text buffer

    def set_splash_text(self, splash_text):
        """
        @brief      Sets the splash text, which is displayed when the LCD boots.

        @param      splash_text  The splash text
        """
        self._send_cmd(CMD_SPLASH_TEXT, splash_text.encode())

    def set_brightness(self, brightness):
        """
        @brief      Sets the brightness of the LCD.

        @param      brightness  The brightness [0, 255]
        """
        self._send_cmd(CMD_BRIGHTNESS, brightness)

    def set_contrast(self, contrast):
        """
        @brief      Sets the contrast of the LCD

        @param      contrast  The contrast [0, 255]
        """
        self._send_cmd(CMD_CONTRAST, contrast)

    def set_color(self, color):
        """
        @brief      Sets the color of the LCD.

        @param      color    The color, as an RGB tuple ([0, 255], [0, 255], [0, 255])
        """
        if color != self._color:
            self._color = color
            self._send_cmd(CMD_COLOR, *color)

    def set_autoscroll(self, enabled):
        """
        @brief      Enables or disables autoscrolling. When autoscrolling is enabled, the LCD
                    automatically scrolls down when the text is too long to fit on one screen.

        @param      enabled  Whether or not to enable autoscroll [True or False]
        """
        if enabled:
            self._send_cmd(CMD_AUTOSCROLL_ON)
        else:
            self._send_cmd(CMD_AUTOSCROLL_OFF)

    def set_cursor_mode(self, cursor_mode):
        """
        @brief      Sets the cursor mode. Options (specified the CursorMode class) are off,
                    underline, and block.

        @param      cursor_mode  The cursor mode (see CursorMode class)
        """
        if cursor_mode == CursorMode.off:
            self._send_cmd(CMD_UNDERLINE_CURSOR_OFF)
            self._send_cmd(CMD_BLOCK_CURSOR_OFF)
        elif cursor_mode == CursorMode.underline:
            self._send_cmd(CMD_UNDERLINE_CURSOR_ON)
        elif cursor_mode == CursorMode.block:
            self._send_cmd(CMD_BLOCK_CURSOR_ON)

    def cursor_home(self):
        """
        @brief      Moves the cursor to the (1,1) position.
        """
        self._send_cmd(CMD_CURSOR_HOME)

    def set_cursor_pos(self, x, y):
        """
        @brief      Sets the position of the cursor. The top-left corner is (1,1). X increases going
                    right, y increases going down.

        @param      x     The x position of the cursor
        @param      y     The y position of the cursor
        """
        self._send_cmd(CMD_CURSOR_POS, x, y)

    def move_cursor_forward(self):
        """
        @brief      Moves the cursor forward one position. If it is at the end of the screen, it
                    will wrap to (1,1).
        """
        self._send_cmd(CMD_CURSOR_FWD)

    def move_cursor_back(self):
        """
        @brief      Moves the cursor back one position. If it is at (1,1), it will wrap to the end
                    of the screen.
        """
        self._send_cmd(CMD_CURSOR_BACK)

    def create_char(self, bank, code, char_bytes):
        """
        @brief      Creates a custom character in the given bank, with the given alias (code) and
                    given pattern.
        """
        self._send_cmd(CMD_SAVE_CUSTOM_CHAR, bank, code, *char_bytes)

    def load_char_bank(self, bank):
        """
        @brief      Loads the custom character bank with the given index.
        """
        self._send_cmd(CMD_LOAD_CHAR_BANK, bank)

    def set_text(self, text):
        """
        @brief      Sets the text on the LCD. Only the characters on the LCD that need to change
                    will be updated.

        @param      text  The text for the LCD, with lines separated by a newline character
        """

        def encode_str(s):
            # UTF-8 encodes 128+ as two bytes but we want just one byte for [0, 255]
            return bytes(ord(c) for c in s)

        lines = [line[:self._width] for line in text.splitlines()[:self._height]]
        diff = diff_text(self._lines, lines)
        for (x, y), s in diff.items():
            self.set_cursor_pos(x + 1, y + 1)  # Move to the cursor to the right spot
            self._write(encode_str(s), flush=True)
        self._lines = lines

    def stop(self):
        """
        @brief      Turns the LCD off and clears it, then flushes and closes the serial
                    connection with the LCD.
        """
        try:
            self.off()
            self.clear()
            self.flush_serial()
        finally:
            self._ser.close()
