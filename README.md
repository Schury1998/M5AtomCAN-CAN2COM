# CAN-Analyse-M5AtomCAN

## INFO: The last tests weren't made yet but in testing condition everything worked

## Hardware to get CAN Messages - M5AtomCAN
Tool to analyse CAN Messages with different baudrates.

**Serial Interface**\
ESP32

**LED & Button Features:**\
The led from the M5Atom lights green if a correct CAN-Messages is recieved.\
The led from the M5Atom lights yellow if more than 1s no CAN-Messages is recieved.\
The led from the M5Atom lights blue if no valid Message has recived yet.

**Possible Baudrates:**
1. 100
2. 125
3. 200
4. 250
5. 500
6. 800
7. 1000

**Other Information:**\
The ESP32 always acknowledge the other bus components.\
Maybe you ned a termination resistor (120Ohm).

**Example of the serial Output**\
CAN MSG: 0x200 [7] <1F:C0:00:10:00:03:01> \
CAN MSG: 0x710 [8] <02:10:03:00:00:00:00:00>

**Possible serial Inputs:**\
100, 125, 200, 250, 500. 800 , 1000 \
The numbers to change the Baudrate.

## GUI
GUI in Python using CustomTkinter

**Imports for Python**\
serial, time, datetime customtkinter, threading/
pip install threaded customtkinter pyserial DateTime

**Use the GUI**
- Log and see incoming Messages (main use)
- Send one Message
- Dev window for change the baudrate oder debugging etc.
