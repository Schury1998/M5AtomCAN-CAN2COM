#include <M5Atom.h>
#include <ESP32CAN.h>
#include <Preferences.h>

//EEPROM
Preferences preferences;

//CAN RX & TX
CAN_device_t CAN_cfg;                // CAN Config.
unsigned long previousMillis = 0;    // will store last time a CAN Message was send.
int interval;                        // interval at which send CAN Messages (milliseconds).
unsigned long previousMillis_r = 0;  // will store last time a CAN Message was recieved.
const int interval_r = 1000;         // interval at which send CAN Messages musst be recieved
const int rx_queue_size = 10;        // Receive Queue size.
int waitCANData = 0;
uint8_t msgcnt = 0;
long mscount_rx = 0;
bool output_message_on = false;

unsigned long currentMillis = 0;  //Aktuelle Systemzeit

void setup() {
  M5.begin(true, false, true);
  preferences.begin("EEPROM1_NSP", false);

  unsigned int canspeed_int = preferences.getUInt("canspeed", 500);
  interval = preferences.getInt("interval", 300);
  Serial.print("CAN Speed: ");
  Serial.print(canspeed_int);
  Serial.println();
  switch (canspeed_int) {
    case 100:
      CAN_cfg.speed = CAN_SPEED_100KBPS;
      break;
    case 125:
      CAN_cfg.speed = CAN_SPEED_125KBPS;
      break;
    case 200:
      CAN_cfg.speed = CAN_SPEED_200KBPS;
      break;
    case 250:
      CAN_cfg.speed = CAN_SPEED_250KBPS;
      break;
    case 500:
      CAN_cfg.speed = CAN_SPEED_500KBPS;
      break;
    case 1000:
      CAN_cfg.speed = CAN_SPEED_1000KBPS;
      break;
    default:
      CAN_cfg.speed = CAN_SPEED_500KBPS;
  }

  CAN_cfg.tx_pin_id = GPIO_NUM_22;
  CAN_cfg.rx_pin_id = GPIO_NUM_19;
  CAN_cfg.rx_queue = xQueueCreate(rx_queue_size, sizeof(CAN_frame_t));
  ESP32Can.CANInit();

  M5.dis.drawpix(0, 0x0000ff);
}

void change_speed(unsigned int canspeed_lok) {
  Serial.println();
  preferences.putUInt("canspeed", canspeed_lok);
  Serial.print("ESP RESET! - CAN SPEED = ");
  Serial.print(canspeed_lok);
  Serial.println();

  ESP32Can.CANStop();
  esp_restart();
}

void output_message(CAN_frame_t& tx_frame) 
{
  char str[80];
  previousMillis = currentMillis;

  tx_frame.FIR.B.FF = CAN_frame_std;

  Serial.printf("TXs from 0x%08X, DLC %d, Data 0x", tx_frame.MsgID,
                tx_frame.FIR.B.DLC);
  for (int i = 0; i < tx_frame.FIR.B.DLC; i++) {
    Serial.printf("%02X", tx_frame.data.u8[i]);
  }
  Serial.printf("\n");
  msgcnt++;
  if (msgcnt > 29) {
    msgcnt = 0;
  }
}

int* process_serialInput() 
{
  String d = "";
   if (Serial.available() > 0) 
   {
    d = Serial.readString();
   }

    //Options for configuration 
    if      (d == "100" && preferences.getUInt("canspeed", 500) != 100 ) change_speed(100);
    else if (d == "125" && preferences.getUInt("canspeed", 500) != 125) change_speed(125);
    else if (d == "200" && preferences.getUInt("canspeed", 500) != 200) change_speed(200);
    else if (d == "250" && preferences.getUInt("canspeed", 500) != 250) change_speed(250);
    else if (d == "500" && preferences.getUInt("canspeed", 500) != 500) change_speed(500);
    else if (d == "800" && preferences.getUInt("canspeed", 500) != 800) change_speed(800);
    else if (d == "1000" && preferences.getUInt("canspeed", 500) != 1000) change_speed(1000);
    else if (d == "Help") outputHelp();

    //User bedient ueber GUI
    int last_index_of_I = d.lastIndexOf('-'); //Wenn Zeichen nicht enthalten return von -1
    int str_len = d.length() + 1;
    static int can_message[10]; // ID + DLC + 8 Byte Payload Max
    if(last_index_of_I >= 0) 
    { 
      char char_array[str_len];
      d.toCharArray(char_array, str_len);
      char *teil;
    
      teil = strtok(char_array, "-"); 
      int i = 0;
      while (teil != NULL) 
      {
        can_message[i] = atoi(teil);
        teil = strtok(NULL, "-");
        ++i;
      }
    }
    else
    {
      can_message[0] = 0; //ID
      can_message[1] = 0; //DLC
      can_message[2] = 0; //Payload
      can_message[3] = 0; //Payload
      can_message[4] = 0; //Payload
      can_message[5] = 0; //Payload
      can_message[6] = 0; //Payload
      can_message[7] = 0; //Payload
      can_message[8] = 0; //Payload
      can_message[9] = 0; //Payload
    }
    return can_message;
}

void outputHelp() {
  Serial.println();
  Serial.print("Possible Serial Commands:  100, 125, 200, 250, 500, 800, 1000 - to modify the Baudrate.");
  Serial.println();
  Serial.print("Busabschluswiederstand verwenden falls nötig - 120Ohm?");
  Serial.println();
  unsigned int canspeed_int = preferences.getUInt("canspeed", 500);
  Serial.print("CAN Speed: ");
  Serial.print(canspeed_int);
  Serial.println();
}

void input_Message() 
{
  CAN_frame_t rx_frame;

  if (xQueueReceive(CAN_cfg.rx_queue, &rx_frame, 3 * portTICK_PERIOD_MS) == pdTRUE) {
    char str[80];
    ++mscount_rx;
    M5.dis.drawpix(0, 0x00ff00);
    previousMillis_r = currentMillis;

    if (rx_frame.FIR.B.RTR == CAN_RTR) 
    {
      Serial.printf("CAN MSG: 0x%X [%d] <>\n", rx_frame.MsgID, rx_frame.FIR.B.DLC);
    } 
    else 
    {
      Serial.printf("CAN MSG: 0x%X [%d] <", rx_frame.MsgID, rx_frame.FIR.B.DLC);
      for (int i = 0; i < rx_frame.FIR.B.DLC; i++) 
      {
        if(i!=0) Serial.printf(":");
        Serial.printf("%02X", rx_frame.data.u8[i]);
      }
      Serial.printf(">\n");
    }
  }
  if ((currentMillis - previousMillis_r >= interval_r) && mscount_rx > 0) M5.dis.drawpix(0, 0xffff00);  //Orange wenn keine Messages kommen
}

void loop() 
{
  static int* ptr_can_messages_array;

  ptr_can_messages_array = process_serialInput();

  currentMillis = millis();

  M5.update();

  if (M5.Btn.wasPressed()) outputHelp();

  if (!(ptr_can_messages_array[0] == 0 && ptr_can_messages_array[1] == 0 && ptr_can_messages_array[2] == 0 
                                       && ptr_can_messages_array[3] == 0 && ptr_can_messages_array[4] == 0 
                                       && ptr_can_messages_array[5] == 0 && ptr_can_messages_array[6] == 0 
                                       && ptr_can_messages_array[7] == 0 && ptr_can_messages_array[8] == 0
                                       && ptr_can_messages_array[9] == 0)) //Nur wenn alles == 0 wird keine Message gesendet
  {
    CAN_frame_t tx_frame;
    tx_frame.MsgID      = ptr_can_messages_array[0];
    tx_frame.FIR.B.DLC  = ptr_can_messages_array[1];
    tx_frame.data.u8[0] = ptr_can_messages_array[0];
    tx_frame.data.u8[1] = ptr_can_messages_array[1];
    tx_frame.data.u8[2] = ptr_can_messages_array[2];
    tx_frame.data.u8[3] = ptr_can_messages_array[3];
    tx_frame.data.u8[4] = ptr_can_messages_array[4];
    tx_frame.data.u8[5] = ptr_can_messages_array[5];
    tx_frame.data.u8[6] = ptr_can_messages_array[6];
    tx_frame.data.u8[7] = ptr_can_messages_array[7];

    output_message(tx_frame);
    ESP32Can.CANWriteFrame(&tx_frame);
  }

  input_Message();
}
