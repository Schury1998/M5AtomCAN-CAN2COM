#include <Arduino.h>

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) //Send Messages
  {
    String incomingString = Serial.readString();
    int last_index_of_I = incomingString.lastIndexOf('I'); //Wenn Zeichen nicht enthalten return von -1
    if(last_index_of_I >= 0) 
    {
      int str_len = incomingString.length() + 1; 
      char char_array[str_len];
      incomingString.toCharArray(char_array, str_len);
      char *teil;
      int can_message[3];
      teil = strtok(char_array, "I"); 
      int i = 0;
      while (teil != NULL) 
      {
        can_message[i] = atoi(teil);
        teil = strtok(NULL, "I");
        ++i;
      }
      //Serial.println(can_message[0]); //ID
      //Serial.println(can_message[1]); //DLC
      //Serial.println(can_message[2]); //Payload
    }
  }
  
  Serial.print("CAN MSG: 0x200 [7] <1F:C0:00:10:00:03:01>"); //Recive Messages
  Serial.println();
  delay(80);
  Serial.print("CAN MSG: 0x710 [8] <02:10:03:00:00:00:00:00>");
  Serial.println();
  delay(2000);
}
