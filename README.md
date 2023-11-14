# CAN-Analyse-M5AtomCAN

## Description
Tool to analyse CAN Messages with different baudrates.

**SerialInterface**\
The ESP32 uses an baudrate from 115200.

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
