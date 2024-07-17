#LightCraft Source Code
#Made by Akash Samanta

import asyncio, threading, os, time, webbrowser
from bleak import BleakClient
from PIL import Image
from customtkinter import *
import tkinter as tk
from CTkColorPicker import *
from functools import wraps

root = CTk()
address = "32:06:C2:00:0A:9E"
char_uuid = "FFD9"
isConnected = False
isOn = False

validColours = {
    'red': [255, 0, 0],
    'orange': [204, 51, 0],
    'yellow': [153, 102, 0],
    'brown': [153, 153, 0],
    'gold': [204, 204, 0],
    'green': [0, 255, 0],
    'olive': [75, 128, 0],
    'lime': [0, 128, 75],    
    'coral': [0, 128, 128],
    'cyan': [0, 238, 238],
    'blue': [0, 0, 255],
    'teal': [0, 75, 128],
    'indigo': [75, 0, 128],
    'purple': [128, 0, 128],
    'violet': [238, 0, 238],
    'magenta': [255, 0, 255],
    'black': [0, 0, 0],
    'white': [255, 255, 255],
    'pink': [255, 0, 40],
    'navy': [255, 0, 128],
    'maroon': [255, 0, 204],
}

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
    def debounce(wait):
        def decorator(fn):
            last_call = [0]

            @wraps(fn)
            def debounced(*args, **kwargs):
                now = time.time()
                if now - last_call[0] >= wait:
                    last_call[0] = now
                    return fn(*args, **kwargs)
            return debounced
        return decorator
    
    def connect():
        global isConnected
        if isConnected:
            isConnected = False
            connect_button.configure(text="Connect", state="normal",fg_color=("#3b8ed0","#1f6aa5"),hover_color=("#36719f","#144870"))
            disconnect()
        else:
            future = controller.run_coroutine(controller.connect())
            connect_button.configure(text="Connecting", state="disabled",fg_color=("#3b8ed0","#1f6aa5"),hover_color=("#36719f","#144870"))
            root.after(20, lambda: check_connection(future))

    def check_connection(future):
        global isConnected
        if future.done():
            if controller.connected:
                isConnected = True
                connect_button.configure(text="Connected", fg_color="green", hover_color="#00AA00", state="normal")
            else:
                connect_button.configure(text="Reconnect", fg_color="red", hover_color="#AA0000", state="normal")
                tk.messagebox.showerror("Connection Failure", "LightCraft failed to connect with your LED Strips. Please make sure that your Bluetooth is turned on and that your LED Strips are not bonded with another device. Verify the MAC Address in Settings.")
        else:
            root.after(20, lambda: check_connection(future))

    def disconnect():
        controller.run_coroutine(controller.disconnect())

    def togglePower():
        global isOn
        if not isOn:
            isOn = True
            power_button.configure(image=imgtk2)
            data = bytearray([0xcc,0x23,0x33])
        else:
            isOn = False
            power_button.configure(image=imgtk3)
            data = bytearray([0xcc,0x24,0x33])
        controller.run_coroutine(controller.sendCmd(data))

    def setBrightness(isUp):
        curr_value = colorpicker.slider.get()
        if isUp:
            new_value = curr_value + 10
            if new_value > 255:
                new_value = 255
        else:
            new_value = curr_value - 10
            if new_value < 0:
                new_value = 0
        colorpicker.slider.set(new_value)
        colorpicker.update_colors()
        sendHex(colorpicker.label.cget("text"))

    @debounce(0.1)
    def sendHex(data):
        data = data[1:]
        data = bytearray([0x56, int(data[0:2], 16), int(data[2:4], 16), int(data[4:6], 16), 0x00, 0xf0, 0xaa])
        controller.run_coroutine(controller.sendCmd(data))

    def sendColour(r,g,b):
        colorpicker.update_colors(r,g,b)
        data = bytearray([0x56, r, g, b, 0x00, 0xf0, 0xaa])
        controller.run_coroutine(controller.sendCmd(data))
    
    def sgButton(frame,row,col,colour):
        r, g, b = map(int, validColours[colour])
        return CTkButton(frame,text="", fg_color="#{:02x}{:02x}{:02x}".format(r, g, b), hover=False, font=CTkFont(size=bsize), width=sgwidth, corner_radius=sgradius, height=sgheight, command=lambda: sendColour(r,g,b)).grid(row=row,column=col,padx=(10,0),pady=(10,0))

    def destroyer(relaunch=False):
        global root
        #TO DO Settings Ask for Confirmation
        #if relaunch==False:
        #    ans = tk.messagebox.askyesno("Close LightCraft","Are you sure you want to close LightCraft?") #Confirm Quit
        #else:
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

    #TO DO Settings
    #applysettings()
    userwinx = root.winfo_screenwidth()
    userwiny = root.winfo_screenheight()
    x = (userwinx)//3
    y = (userwiny)//3
    root.geometry(f"700x410+{x}+{y}")
    root.resizable(False,False)

    #Frames
    mainframe=CTkTabview(root)
    mainframe.add("Control")
    mainframe.add("Music")
    mainframe.add("Settings")
    sgframe=CTkFrame(mainframe.tab("Control"), fg_color="transparent")

    #Button Scaling
    bsize=16
    bheight=35
    bwidth=150
    sgwidth=35
    sgheight=35
    sgradius=40

    #Images
    try:
        image1 = Image.open(r".\Resources\logo.png")
        image2 = Image.open(r".\Resources\onButton.png")
        image3 = Image.open(r".\Resources\offButton.png")
    except:
        tk.messagebox.showerror("Missing Resources","LightCraft could not find critical resources. The Resources folder may have been corrupted or deleted. Please re-install LightCraft from official sources.") #Missing Resources
        quit()
    imgtk1 = CTkImage(light_image=image1,size=(60,60))
    imgtk2 = CTkImage(light_image=image2,size=(25,25))
    imgtk3 = CTkImage(light_image=image3,size=(25,25))

    #Basic Elements
    headinglogo = CTkButton(root, text="", width=80, image=imgtk1,command=lambda :webbrowser.open("https://github.com/akashcraft/LED-Controller"),hover=False, fg_color="transparent")
    heading1 = CTkLabel(root, text="LightCraft", font=CTkFont(size=30)) #LightCraft
    heading2 = CTkLabel(root, text="Version 1.0.2 (Beta)", font=CTkFont(size=13)) #Version
    connect_button = CTkButton(root, text="Connect", font=CTkFont(size=bsize), width=bwidth, height=bheight, command=connect)
    power_button = CTkButton(root, text="", fg_color="#333333", image=imgtk3, hover=False, font=CTkFont(size=bsize), width=sgwidth, corner_radius=10, height=bheight, command=togglePower)
    colorpicker = CTkColorPicker(mainframe.tab("Control"), width=250, orientation=HORIZONTAL, command=lambda e: sendHex(e))

    root.grid_columnconfigure(1,weight=1)
    root.grid_rowconfigure(2,weight=1)
    headinglogo.grid(row=0,column=0,rowspan=2,pady=10, sticky='w')
    heading1.grid(row=0,column=1,pady=0, sticky='sw')
    heading2.grid(row=1,column=1,pady=0, sticky='nw')
    connect_button.grid(row=0,column=2,rowspan=2,padx=0, sticky='e')
    power_button.grid(row=0,column=3,rowspan=2,padx=10, sticky='e')
    mainframe.grid(row=2,column=0,columnspan=4,padx=10, pady=(0,10), sticky='nsew')
    mainframe.tab("Control").grid_columnconfigure(2,weight=1)
    sgframe.grid(row=0,column=0,padx=10,pady=10, sticky='n')
    sgButton(sgframe, 0, 0, "red")
    sgButton(sgframe, 0, 1, "green")
    sgButton(sgframe, 0, 2, "blue")
    sgButton(sgframe, 0, 3, "maroon")
    sgButton(sgframe, 1, 0, "orange")
    sgButton(sgframe, 1, 1, "olive")
    sgButton(sgframe, 1, 2, "teal")
    sgButton(sgframe, 1, 3, "navy")
    sgButton(sgframe, 2, 0, "yellow")
    sgButton(sgframe, 2, 1, "lime")
    sgButton(sgframe, 2, 2, "indigo")
    sgButton(sgframe, 2, 3, "pink")
    sgButton(sgframe, 3, 0, "brown")
    sgButton(sgframe, 3, 1, "coral")
    sgButton(sgframe, 3, 2, "purple")
    sgButton(sgframe, 3, 3, "black")
    sgButton(sgframe, 4, 0, "gold")
    sgButton(sgframe, 4, 1, "cyan")
    sgButton(sgframe, 4, 2, "violet")
    sgButton(sgframe, 4, 3, "white")
    colorpicker.grid(row=0,column=1,padx=42,pady=10,sticky='n')

    #Key Binds
    root.bind("<KeyRelease-r>",lambda e:sendColour(255,0,0))
    root.bind("<KeyRelease-g>",lambda e:sendColour(0,255,0))
    root.bind("<KeyRelease-b>",lambda e:sendColour(0,0,255))
    root.bind("<KeyRelease-w>",lambda e:sendColour(255,255,255))
    root.bind("<KeyRelease-p>",lambda e:sendColour(255,0,40))
    root.bind("<KeyRelease-c>",lambda e:connect())
    root.bind("<space>",lambda e:togglePower())
    root.bind("<Up>",lambda e:setBrightness(True))
    root.bind("<Down>",lambda e:setBrightness(False))

    #TO DO Settings Auto Reconnect
    #root.after(20,connect)
    root.mainloop()

if __name__ == "__main__":
    main()

