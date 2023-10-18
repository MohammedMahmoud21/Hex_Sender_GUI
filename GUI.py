from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import serial
import time
import functools
import os.path
import pathlib
import struct
import serial.tools.list_ports


ports = serial.tools.list_ports.comports()
ESP = serial.Serial()

def initComPorts(index):
    Baud_Rates = Baud_Rate.get()
    ComPortVar = str(Com.get().split(' ')[0])
    print(ComPortVar)
    
    ESP.baudrate =Baud_Rates
    ESP.port =ComPortVar 
    ESP.parity = serial.PARITY_NONE
    ESP.stopbits = serial.STOPBITS_ONE
    ESP.bytesize = serial.EIGHTBITS
    try:
        ESP.open()
        messagebox.showinfo("Correct","Done connecting")
    except(serial.SerialException,UnicodeDecodeError):
        messagebox.showerror("Error","Check Baudrate and COM")

def Send_Hex(Path):

    with open(pathlib.Path(My_Path.get()), "r") as Path:
        My_File = open(My_Path.get())
    ESP.reset_output_buffer()
    ESP.reset_input_buffer()
    for Line in My_File:
        Data = b''
        for c in Line:
            if(':' != c and  ('\n' != c)):
                Data += struct.pack('!B',int(c,16))
        
        Line = Line.strip('\n' or '\t')
        Label(main_frame,text=Line,font=('calibr','10'),bg='white').pack()
        #Send line and EOF
        ESP.write(Data)
        value = b''
        value += struct.pack('!B',0xFF)
        ESP.write(value)
        #Read Buffer
        ESP_Data = ESP.readline().decode('utf-8')
        while (ESP_Data != "OK\n" and ESP_Data != "NOK\n"):
            ESP_Data = ESP.readline().decode('utf-8')
        
        if(ESP_Data != "OK\n"):
            break

        Label(main_frame,text=ESP_Data,font=('calibr','10'),bg='white').pack()
        ESP.reset_output_buffer()
        ESP.reset_input_buffer()
        print(Line)
    if(ESP_Data != "OK\n"):
        Label(main_frame,text="Failed NOK was received",font=('calibr','10'),bg='white').pack()
    else:
        Label(main_frame,text="Done Sending, Write 0xFF to Send Finish state",font=('calibr','10'),bg='white').pack()
    My_File.close()


def SendCommand():
    Label(main_frame,text=User_Command.get(),font=('calibr','10'),bg='white').pack()
    Number = 0
    Hex_Command = b''
    Command_N = str(User_Command.get())
    for chr in Command_N:
        if(' ' == chr):
            print(Number)
            Hex_Command += struct.pack('!B',Number)
            Number=0
        else:
            Number = Number*16 + int(chr,16)
    Hex_Command += struct.pack('!B',Number)

    ESP.write(Hex_Command)
    ESP_Data = ESP.readline().decode('utf-8').rstrip('\n')
    while (0 != ESP.in_waiting):
        ESP_Data = ESP.readline().decode('utf-8').rstrip('\n')
    
    Label(main_frame,text=ESP_Data,font=('calibr','10'),bg='white').pack()

# Title
################################
My_Screen = Tk()

wrapper1 = LabelFrame(My_Screen,border=5,bg='white')
wrapper2 = LabelFrame(My_Screen,border=5)

DataCanvas = Canvas(wrapper2,bg='white',scrollregion=(0,0,100000000,10000000))
DataCanvas.pack()

Scrol = Scrollbar(wrapper2,orient='vertical',command=DataCanvas.yview)
Scrol.pack(side=RIGHT,fill="y")

DataCanvas.config(yscrollcommand=Scrol.set)



main_frame = Frame(DataCanvas,bg='white',relief=SOLID)

DataCanvas.create_window((0,0),window=main_frame,anchor='nw')
DataCanvas.place(x=0,y=0)



My_Screen.geometry('600x600')

My_Screen.title("Mohammed Elsayaad")

# Labels
##########################################
label_0 = Label(My_Screen, text="Send Hex USART", relief="solid", bg="yellow", width=20,
                font=("arial", 15, "bold"))
label_0.pack(fill=BOTH, pady=2, padx=2)

# Path and Com labels
#########################
# Vars

My_Path = StringVar()
My_Com = StringVar()

###################

label_1 = Label(wrapper1, text="Hex Path",  fg="black", width=10,
                font=("arial", 10, "bold"))
label_1.place(x=10, y=10)

entry_1 = Entry(wrapper1, textvariable=My_Path,width=19)
entry_1.place(x=50, y=10)


###############################

# Transfer_Button
###############################
Button_0 = Button(wrapper1, text="Send File", relief="groove", bg="red", width=10, command=functools.partial(Send_Hex, My_Path.get()),
                  font=("arial", 15, "bold"))
Button_0.place(x=30, y=180)
# Baud_Rate List
###############################
Baud_Rate = StringVar()

BaudRates_List = [9600, 115200]
Drop_list = OptionMenu(wrapper1, Baud_Rate, *BaudRates_List)
Baud_Rate.set("Select BaudRate")
Drop_list.config(width=30)
Drop_list.place(x=20, y=50)
# Ports
###############################
ComList = ["NONE"]
Com = StringVar()
for comPort in ports:
    ComList.append(comPort)
ComDrop_List = OptionMenu(wrapper1,Com,*ComList,command=(initComPorts))
Com.set("Com Ports")
ComDrop_List.config(width=30)
ComDrop_List.place(x=20,y=90)
# Send Command button
###############################

Button_1 = Button(wrapper1, text="Send Command", relief="groove", bg="blue", width=16,command=functools.partial(SendCommand),
                  font=("arial", 13, "bold"))
Button_1.place(x=300, y=180)
# Command Text input
###############################

User_Command=StringVar()

label_2 = Label(wrapper1, text="Write Command",  fg="black",
                font=("arial", 10, "bold"))
label_2.place(x=320, y=20)

entry_2 = Entry(wrapper1, textvariable=User_Command,width=60)
entry_2.place(x=320, y=50)


wrapper1.pack(fill=BOTH,expand=1,padx=2,pady=2)
wrapper2.pack(fill=BOTH,expand=1,padx=10,pady=10)
# Main
###########################
while True:
    My_Screen.update()