import serial 
import serial.tools.list_ports
import time
from datetime import date
import customtkinter
import threading

#---------------------------------------------------------------------------------------------------------------------------------------------------------
#CLASSES------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------

class GUI:
    def __init__(self, root):

        #Initialisierung Variablen
        self.message_number = 0
        self.inititialisierung = False
        self.port_after_init = ''
        self.id_datenbank = self.read_sym_file('GUI/CAN.sym')
        print(self.id_datenbank)

        #setting window size, title and so on
        width=1100
        height=700
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
        self.connect_button = customtkinter.CTkCheckBox(root, text='LOGGING', variable=self.trace_active, onvalue=1, offvalue=0)
        self.connect_button.place(x=10, y=15)
        
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
        self.button_send.bind('<ButtonRelease-1>', self.on_release)
        self.button_send.place(x=680, y=15)

        self.light = customtkinter.CTkLabel(root, text="Out", font=("Arial", 12))
        self.light.place(x=825, y=15)

        #DEV option to change baud rate etc.
        self.button_send = customtkinter.CTkButton(root, text="DEV", width=35, height=10, command= lambda: self.dev_window(root), fg_color = "grey")
        self.button_send.place(x=1060, y=0)

        #Start Lese-Thread
        threading.Thread(target=self.read_data).start()

        print('Serieller Port: ' + self.coose_SERIAL())

        
    def dev_window(self, root): #Methode die aufgerufen wird wenn DEV gedruckt wird
        self.connect_button.deselect()

        #def buttonCLOSEclick():
            #tkFensterDEV.quit()
            #tkFensterDEV.destroy()
            #self.dev_thread.join()

        def send_data_raw():
            data = entry.get()
            if (self.coose_SERIAL() != 'NULL' and self.inititialisierung is True):
                self.s.write(data.encode('utf-8'))
        
        def read_data_raw():
            while True:
                data = self.s.readline().decode('utf-8').strip()
                text.insert(customtkinter.END, data + '\n')
                text.see("end")

        # Neues Fenster öffnen
        tkFensterDEV = customtkinter.CTkToplevel(root)
        tkFensterDEV.resizable(False, False)
        tkFensterDEV.after(250, lambda: tkFensterDEV.iconbitmap('GUI/ICON.ico'))
        tkFensterDEV.title('DEV')
        #Eingabe Serial
        entry = customtkinter.CTkEntry(tkFensterDEV)
        entry.pack(pady=10)
        #Senden Button
        button = customtkinter.CTkButton(tkFensterDEV, text="send_raw", command=send_data_raw)
        button.pack(pady=10)
        #Read Serial - Ausgabe
        text = customtkinter.CTkTextbox(tkFensterDEV, activate_scrollbars=True)
        text.pack(pady=10)

        # Start DEV Read Thread
        self.dev_thread = threading.Thread(target=read_data_raw)
        self.dev_thread.start()
        #Close Window
        #button_close = customtkinter.CTkButton(tkFensterDEV, text='close_DEV', command=buttonCLOSEclick)
        #button_close.pack(pady=10)
        

    def button_event(self): #Methode die aufgerufen wird wenn SEND gedrueckt wird
        self.connect_button.deselect()
        self.timestamp = int((time.time_ns() - self.init_time) / 1000) #for ms 
        id = self.entry_id.get().replace('0x', '')
        entry_message_loc = self.entry_message.get()
        len_message = len(entry_message_loc)
        entry_message_loc = entry_message_loc.replace('0x', '')
        entry_message_byte = [entry_message_loc[i:i+2] for i in range(0, len(entry_message_loc), 2)]  #String in 2er-Bloecke 
        entry_message_byte = 'I'.join(entry_message_byte)
        dlc = int((len(self.entry_message.get()) - 2) / 2)

        return_string = ''
        if (id != '' or dlc != 0) and (len_message % 2 == 0):
            return_string = str(id) + 'I' + str(dlc) + 'I' + entry_message_byte
            print('CAN Message out: ' + return_string)
            self.light.configure(text_color="green")
            if (self.inititialisierung is True):
                bytes_data = return_string.encode('Ascii')
                self.s.write(bytes_data) #EXAMPLE: 16I2I33I55 -> ID:0x10 DTL:2 Pyload:0x21 0x37
        else:
            self.light.configure(text_color="red")


    def on_release(self, event):
        self.light.configure(text_color="white")


    def coose_SERIAL(self): #Methode die verfuegbare Ports anzeigt und den gewaehlten Port zurueckgibt
        self.ports = [port.device for port in serial.tools.list_ports.comports()]
        #choose inital Port 
        if  (self.frist_run_choose_serial is True and len(self.ports) >= 1): 
            self.port_var.set(self.ports[0])
            self.frist_run_choose_serial = False
            self.actual_ports = self.ports
        #insert 'NULL' if no serial device
        if(len(self.ports) < 1): 
            self.port_var.set('NULL')
            self.port_menu.configure()
        #update available ports
        elif (self.ports != self.actual_ports):
            self.port_menu.configure(values = self.ports)
            self.actual_ports = self.ports
        #return choosen port
        return self.port_var.get()
    

    def output_CAN(self, string): #Methode zur wiedergabe eines Strings in der Texbox
        self.T.configure(state='normal')
        self.T.insert('end', string)
        self.T.configure(state='disabled')
        self.T.see('end')


    def acitve_trace_box(self): #Status des Trace Buttons abfrage
        return self.trace_active.get()


    def init_SERIAL(self):
        if (self.coose_SERIAL() != 'NULL'):
            ser = serial.Serial(port=self.coose_SERIAL(), baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE) #115200 #1500000
        return ser


    def close(self, s):
        self.s.close()  # Dann die Verbindung schliessen
        print('Serial Port closed')


    def read_data(self):
        while True:
            if ((self.coose_SERIAL() != 'NULL') and self.inititialisierung is False):
                self.s = self.init_SERIAL()
                fiele_name = self.init_LOGGING_FILE()
                self.init_time = time.time_ns()
                self.inititialisierung = True
                self.port_after_init = self.coose_SERIAL()
            elif (self.port_after_init != self.coose_SERIAL() and self.inititialisierung is True ):
                self.s.close()
                self.s= self.init_SERIAL()
                self.inititialisierung = True
                self.port_after_init = self.coose_SERIAL()
            elif (self.coose_SERIAL() != 'NULL' and self.inititialisierung is True):
                #to ignore incoming messages when the checkBox is not acitve
                if(self.acitve_trace_box() !=  1):
                    self.s.read_all() 

                # Wait until there is data waiting in the serial buffer
                if self.s.in_waiting > 0 and self.acitve_trace_box() ==  1:

                    # Read data out of the buffer until a carraige return / new line is found
                    serialString = self.s.readline()

                    # Print the contents of the serial data
                    try:
                        list = serialString.decode('Ascii').split()
                        del list[0]
                        del list[0]
                        timestamp = int((time.time_ns() - self.init_time) / 1000) #for ms 
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
                        self.message_number = self.message_number + 1
                        message_number_string = str(self.message_number) + ')'
                        list.insert(0, message_number_string)
                        list.insert(2, '1') #Bus = 1
                        list.insert(3, 'Rx') #Type = Rx
                        list.insert(5, '-') #Reserved

                        #example list: ['1)', '.0', 1, 'Rx', '710', '-', '8', '02 10 03 00 00 00 00 00']
                        print(list)
                        f = open('GUI/log.trc', 'a') #fiele_name
                        ausgabe_string = ' ' + list[0] + ' ' + list[1] + ' ' + list[2] + ' ' + list[3] + ' ' + list[4] + ' ' + list[5] + ' ' + list[6] + ' ' + list[7] + '\n'
                        f.write(ausgabe_string)
                        f.close()

                        if int(list[4]) in self.id_datenbank:
                            index_id_datenbank = self.id_datenbank.index(int(list[4]))
                            list[4] = list[4] + ' -> ' + self.id_datenbank[index_id_datenbank - 1]

                        ausgabe_string = '' + list[0] + '\t' + list[1] + '\t\t' + list[2] + ' ' + list[3] + '\t' + list[4] + '\t\t\t\t\t' + list[5] + ' ' + list[6] + '\t' + list[7] + '\n'
                        self.output_CAN(ausgabe_string)
                    except:
                        pass


    #Methode wird nur zu Beginn genutzt
    def init_LOGGING_FILE(self):
        aktuellesDatum = str(date.today())
        tiemstamp = str(time.asctime())
        timestamp_list = tiemstamp.split()

        fiele_name = aktuellesDatum + '_' + timestamp_list[3].replace(':','-') +  '_log' +  '.txt'
        f = open('GUI/log.trc', 'w') #fiele_name

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
        self.output_CAN(ausgabe_string)
        f.close()
        return fiele_name


    #Methode wird nur zu Beginn genutzt
    def read_sym_file(self, file_path):
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
    root.mainloop()
        

