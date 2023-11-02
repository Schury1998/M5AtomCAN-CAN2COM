import serial 
import serial.tools.list_ports
import time
from datetime import date
import customtkinter

#---------------------------------------------------------------------------------------------------------------------------------------------------------
#CLASSES------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------

class GUI:
    def __init__(self, root):
        #setting window size, title and so on
        width=1100
        height=400
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.title('SUSF-CAN-Explorer v1.0.0.0')
        customtkinter.set_appearance_mode('dark')
        customtkinter.set_default_color_theme('blue')
        root.iconbitmap('GUI/ICON.ico')

        # Konfigurieren Grid-System
        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(0, weight=1)
        #empty fields for Grid
        empty_grid1 = customtkinter.CTkLabel(root, text='') 
        empty_grid1.grid(row=0, column=0)
        empty_grid2 = customtkinter.CTkLabel(root, text='')
        empty_grid2.grid(row=1, column=0) 
        
        #start Trace Button
        self.trace_active = customtkinter.IntVar()
        connect_button = customtkinter.CTkCheckBox(root, text='LOGGING', variable=self.trace_active, onvalue=1, offvalue=0)
        connect_button.place(x=10, y=15)
        
        #select Serialport
        self.port_var = customtkinter.StringVar(root)
        self.ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_menu = customtkinter.CTkOptionMenu(root, variable=self.port_var, values=self.ports)
        self.port_menu.place(x=120, y=15)
        self.frist_run_choose_serial = True

        #Textbox for the Logging 
        self.T = customtkinter.CTkTextbox(root, activate_scrollbars=True)
        self.S = customtkinter.CTkScrollbar(root,  command=self.T.yview)
        self.T.grid(row=2, column=0, sticky='nsew')
        self.S.configure(command=self.T.yview)
        self.T.configure(yscrollcommand=self.S.set)

        #Send Option
        label_id = customtkinter.CTkLabel(root, text="ID:")
        label_id.place(x=350, y=15)
        self.entry_id = customtkinter.CTkEntry(root, width = 80)
        self.entry_id.place(x=370, y=15)
        self.entry_id.insert(0, '0x')

        label_message = customtkinter.CTkLabel(root, text="Message:")
        label_message.place(x=460, y=15)
        self.entry_message = customtkinter.CTkEntry(root)
        self.entry_message.place(x=525, y=15)
        self.entry_message.insert(0, '0x')

        self.button_send = customtkinter.CTkButton(root, text="SEND", command=self.button_event)
        self.button_send.place(x=680, y=15)
        self.button_clicked = False

        self.light = customtkinter.CTkLabel(root, text="💡", font=("Arial", 24))
        self.light.place(x=820, y=15)


        
    def button_event(self): #Methode die aufgerufen wird wenn SEND gedrueckt wird
        self.button_clicked = True

    def button_send_clicked(self): #Methode um den pressed Zustand des SEND Buttons auch extern zu erhalten
        return_string = ''
        try: 
            id = int(self.entry_id.get(), 16)
            message = int(self.entry_message.get(), 16)
            dlc = len(self.entry_message.get()) - 2
        except:
            id = 0
            message = 0
            dlc = 0
            pass

        if self.button_clicked and id != 0:
            self.button_clicked = False
            return_string = str(id) + 'I' + str(dlc) + 'I' + str(message)
            self.light.configure(text_color="yellow")
            return True, return_string
        else:
            self.light.configure(text_color="black")
            return False, return_string

    

    def coose_SERIAL(self): #Methode die verfuegbare Ports anzeigt und den gewaehlten Port zurueckgibt
        self.ports = [port.device for port in serial.tools.list_ports.comports()]
        #choose inital Port 
        if  (self.frist_run_choose_serial is True and len(self.ports) >= 1): 
            self.port_var.set(self.ports[0])
            self.frist_run_choose_serial = False
        #insert 'NULL' if no serial device
        if(len(self.ports) < 1): 
            self.port_var.set('NULL')
            self.port_menu.configure()
        #update available ports
        else:
            self.port_menu.configure(values = self.ports)
        #return choosen port
        return self.port_var.get()


    def output_CAN(self, string): #Methode zur wiedergabe eines Strings in der Texbox
        self.T.configure(state='normal')
        self.T.insert('end', string)
        self.T.configure(state='disabled')
        self.T.see('end')


    def acitve_trace_box(self): #Status des Trace Buttons abfrage
        return self.trace_active.get()


def init_SERIAL():
    if (GUI.coose_SERIAL() != 'NULL'):
        s = serial.Serial(port=GUI.coose_SERIAL(), baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
    return s

#---------------------------------------------------------------------------------------------------------------------------------------------------------
#FUNCTIONS------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------

def init_LOGGING_FILE():
    aktuellesDatum = str(date.today())
    tiemstamp = str(time.asctime())
    timestamp_list = tiemstamp.split()

    fiele_name = aktuellesDatum + '_' + timestamp_list[3].replace(':','-') +  '_log' +  '.txt'
    f = open('GUI/log.trc', 'w')

    starttime_list = timestamp_list[3].split(':')
    starttime = int(starttime_list[0]) * 60 * 60 #h in s
    starttime = starttime + int(starttime_list[1]) * 60 #min in s
    starttime_string = str(starttime) + '.' + starttime_list[2]

    ausgabe_string = (';$FILEVERSION=1.0'
                    + '\n'
                    + ';$STARTTIME=' + starttime_string
                    + '\n'
                    + ';'
                    + '\n'
                    + ';   Start time: ' +  aktuellesDatum + ' ' +  timestamp_list[3] 
                    + '\n'
                    + ';   Generated by SUSF-CAN-Explorer v1.0.0.0'
                    + '\n'
                    + ';-------------------------------------------------------------------------------'
                    + '\n'
                    + ';   Bus  Connection   Net Connection     Protocol  Bit rate'
                    + '\n'
                    + ';   1    Verbindung1  M5Atom             CAN       Controller Setup'
                    + '\n'
                    + ';-------------------------------------------------------------------------------'
                    + '\n'
                    + ';   Message   Time    Bus  Type   ID    Reserved'
                    + '\n'
                    + ';   Number    Offset  |    |      [hex] |   Data Length Code'
                    + '\n'
                    + ';   |         [ms]    |    |      |     |   |    Data [hex] ...'
                    + '\n'
                    + ';   |         |       |    |      |     |   |    |'
                    + '\n'
                    + ';---+-- ------+------ +- --+-- ---+---- +- -+-- -+ -- -- -- -- -- -- --'
                    + '\n')
    
    f.write(ausgabe_string)
    GUI.output_CAN(ausgabe_string)
    f.close()
    return fiele_name


def read_sym_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    id_datenbank = []
    for i in range(1, len(lines)):
        if 'ID=' in lines[i]:
            id_str = lines[i].split('ID=')[1].strip()
            id_str = id_str.replace('h', '')  
            id_int = int(id_str) 
            id_datenbank.append(lines[i-1].strip())
            id_datenbank.append(id_int)
    return id_datenbank

#---------------------------------------------------------------------------------------------------------------------------------------------------------
#MAIN-----------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    root = customtkinter.CTk()
    GUI = GUI(root)
    message_number = 0
    inititialisierung = False
    port_after_init = ''

    id_datenbank = read_sym_file('GUI/CAN.sym')
    print(id_datenbank)
    print('Serieller Port: ' + GUI.coose_SERIAL())

    while 1:
        root.update()

        if ((GUI.coose_SERIAL() != 'NULL') and inititialisierung is False):
            s= init_SERIAL()
            fiele_name = init_LOGGING_FILE()
            init_time = time.time_ns()
            inititialisierung = True
            port_after_init = GUI.coose_SERIAL()
        elif (port_after_init != GUI.coose_SERIAL() and inititialisierung is True ):
            s.close()
            s= init_SERIAL()
            inititialisierung = True
            port_after_init = GUI.coose_SERIAL()
        elif (GUI.coose_SERIAL() != 'NULL' and inititialisierung is True):
            #to ignore incoming messages when the checkBox is not acitve
            if(GUI.acitve_trace_box() !=  1):
                s.read_all() 

            bool_send, serial_output_string = GUI.button_send_clicked()
            if (bool_send is True and inititialisierung is True):
                bytes_data = serial_output_string.encode('utf-8')
                s.write(bytes_data) #EXAMPLE: 16I2I3 -> ID:0x10 DTL:2 Pyload:0x03

            # Wait until there is data waiting in the serial buffer
            if s.in_waiting > 0 and GUI.acitve_trace_box() ==  1:

                # Read data out of the buffer until a carraige return / new line is found
                serialString = s.readline()

                # Print the contents of the serial data
                try:
                    list = serialString.decode('Ascii').split()
                    del list[0]
                    del list[0]
                    timestamp = int((time.time_ns() - init_time) / 1000) #for ms 
                    timestamp_string = str(timestamp) 
                    timestamp_string_len = len(timestamp_string)

                    if (timestamp_string_len <= 3):
                        timestamp_string = 0 + '.' + timestamp_string[timestamp_string_len-3:]
                    else:
                        timestamp_string = timestamp_string[:timestamp_string_len-3] + '.' + timestamp_string[timestamp_string_len-3:]

                    list.insert(0, timestamp_string)
                    list[1] = list[1].replace('0x','')
                    list[2] = list[2].replace('[','')
                    list[2] = list[2].replace(']','')
                    list[3] = list[3].replace('<','')
                    list[3] = list[3].replace('>','')
                    list[3] = list[3].replace('>','')
                    list[3] = list[3].replace(':',' ')
                    
                    # Insert missing Parameters
                    message_number = message_number + 1
                    message_number_string = str(message_number) + ')'
                    list.insert(0, message_number_string)
                    list.insert(2, '1') #Bus = 1
                    list.insert(3, 'Rx') #Type = Rx
                    list.insert(5, '-') #Reserved

                    #example list: ['1)', '.0', 1, 'Rx', '710', '-', '8', '02 10 03 00 00 00 00 00']
                    print(list)
                    f = open('GUI/log.trc', 'a')
                    ausgabe_string = ' ' + list[0] + ' ' + list[1] + ' ' + list[2] + ' ' + list[3] + ' ' + list[4] + ' ' + list[5] + ' ' + list[6] + ' ' + list[7] + '\n'
                    f.write(ausgabe_string)
                    f.close()

                    if int(list[4]) in id_datenbank:
                        index_id_datenbank = id_datenbank.index(int(list[4]))
                        list[4] = list[4] + ' -> ' + id_datenbank[index_id_datenbank - 1]

                    ausgabe_string = '' + list[0] + '\t' + list[1] + '\t\t' + list[2] + ' ' + list[3] + '\t' + list[4] + '\t\t\t\t\t' + list[5] + ' ' + list[6] + '\t' + list[7] + '\n'
                    GUI.output_CAN(ausgabe_string)
                except:
                    pass
        


