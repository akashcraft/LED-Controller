#LightCraft Source Code
#Made by Akash Samanta

import asyncio, threading, os, time
from bleak import BleakClient
from customtkinter import *
import tkinter as tk

root = CTk()
address = "32:06:C2:00:0A:9E"
char_uuid = "FFD9"

class BluetoothController:
    def __init__(self, address, char_uuid):
        self.address = address
        self.char_uuid = char_uuid
        self.client = None
        self.loop = asyncio.new_event_loop()
        self.connected = False
        asyncio.set_event_loop(self.loop)

    async def connect(self):
        self.client = BleakClient(self.address)
        try:
            await self.client.connect()
            self.connected = True
        except:
            self.connected = False

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            self.client = None

    async def sendCmd(self, data):
        if self.client:
            await self.client.write_gatt_char(self.char_uuid, data)

    def run_coroutine(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

def main():
    def connect():
        future = controller.run_coroutine(controller.connect())
        connect_button.configure(text="Connecting", state="disabled",fg_color=("#3b8ed0","#1f6aa5"),hover_color=("#36719f","#144870"))
        root.after(20, lambda: check_connection(future))

    def check_connection(future):
        if future.done():
            if controller.connected:
                connect_button.configure(text="Connected", fg_color="green", hover_color="#00AA00", state="disabled")
            else:
                connect_button.configure(text="Reconnect", fg_color="red", hover_color="#AA0000", state="normal")
                tk.messagebox.showerror("Connection Failure", "LightCraft failed to connect with your LED Strips. Please make sure that your Bluetooth is turned on and that your LED Strips are not bonded with another device. Verify the MAC Address in Settings.")
        else:
            root.after(20, lambda: check_connection(future))

    def disconnect():
        controller.run_coroutine(controller.disconnect())

    def sendCmd(colour):
        if colour=='red':
            data = bytearray([0x56, 0xff, 0x00, 0x00, 0x00, 0xf0, 0xaa])
        elif colour=='green':
            data = bytearray([0x56, 0x00, 0xff, 0x00, 0x00, 0xf0, 0xaa])
        else:
            data = bytearray([0x56, 0x00, 0x00, 0xff, 0x00, 0xf0, 0xaa])

        controller.run_coroutine(controller.sendCmd(data))
    
    def destroyer(relaunch=False):
        global root
        if relaunch==False:
            ans = tk.messagebox.askyesno("Close LightCraft","Are you sure you want to close LightCraft?") #Confirm Quit
        else:
            ans = True
        if ans:        
            if relaunch:
                root.destroy()
                root = CTk()
                main()
            else:
                root.destroy()
        controller.loop.call_soon_threadsafe(controller.loop.stop)
        loop_thread.join()

    #Start Controller
    controller = BluetoothController(address, char_uuid)
    loop_thread = threading.Thread(target=controller.loop.run_forever)
    loop_thread.start()

    #Making the Application
    root.title("LightCraft")
    root.protocol("WM_DELETE_WINDOW", destroyer)
    root.iconbitmap(r".\Resources\logo.ico")
    #applysettings()
    userwinx = root.winfo_screenwidth()
    userwiny = root.winfo_screenheight()
    x = (userwinx)//2
    y = (userwiny)//2
    root.geometry(f"250x300+{x}+{y}")

    #Frames
    basicframe=CTkFrame(root)

    #Button Scaling
    bsize=16
    bheight=35
    bwidth=150

    #Basic Elements
    heading1 = CTkLabel(root, text="LightCraft", font=CTkFont(size=30)) #LightCraft
    heading2 = CTkLabel(root, text="Beta Build", font=CTkFont(size=15)) #Version
    connect_button = CTkButton(basicframe, text="Connect", font=CTkFont(size=bsize), width=bwidth, height=bheight, command=connect)
    red_button = CTkButton(basicframe, text="Red", fg_color="red", hover_color="#AA0000", font=CTkFont(size=bsize), width=bwidth, height=bheight, command=lambda: sendCmd('red'))
    green_button = CTkButton(basicframe, text="Green", fg_color="green", hover_color="#00AA00", font=CTkFont(size=bsize), width=bwidth, height=bheight, command=lambda: sendCmd('green'))
    blue_button = CTkButton(basicframe, text="Blue", fg_color="blue", hover_color="#0000AA", font=CTkFont(size=bsize), width=bwidth, height=bheight, command=lambda: sendCmd('blue'))

    heading1.pack(fill=X,expand=True,side=tk.TOP,pady=(10,2))
    heading2.pack(fill=Y,expand=True,side=tk.TOP,pady=0)
    basicframe.pack(fill=BOTH, expand=True,pady=10,padx=10)
    basicframe.grid_columnconfigure(0,weight=1)
    connect_button.grid(row=1,column=0,padx=20,pady=(10,5))
    red_button.grid(row=2,column=0,padx=20,pady=5)
    green_button.grid(row=3,column=0,padx=20,pady=5)
    blue_button.grid(row=4,column=0,padx=20,pady=(5,10))

    root.after(20,connect)
    root.mainloop()

if __name__ == "__main__":
    main()

