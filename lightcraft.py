#LightCraft Source Code
#Made by Akash Samanta

import asyncio, threading, os, time, webbrowser
from bleak import BleakClient
from PIL import Image
from customtkinter import * # type: ignore
import tkinter as tk
from tkinter import messagebox
from CTkColorPicker import * # type: ignore
from functools import wraps

root = CTk()
address = "32:06:C2:00:0A:9E"
char_uuid = "FFD9"
isConnected = False
isOn = False
interval = 5
isFlashing = False
isPulsing = True
linkColour = "white"

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

validFlashCode = {
    'rgb_flash': 0x62,
    'all_flash': 0x38,
    'white_flash': 0x37,
    'purple_flash': 0x36,
    'cyan_flash': 0x35,
    'yellow_flash': 0x34,
    'blue_flash': 0x33,
    'green_flash': 0x32,
    'red_flash': 0x31,
    'eyesore_flash': 0x30
}

validPulseCode = {
    'gb_pulse': 0x2F,
    'rb_pulse': 0x2E,
    'rg_pulse': 0x2D,
    'white_pulse': 0x2C,
    'purple_pulse': 0x2B,
    'cyan_pulse': 0x2A,
    'yellow_pulse': 0x29,
    'blue_pulse': 0x28,
    'green_pulse': 0x27,
    'red_pulse': 0x26,
    'rgb_pulse': 0x61,
    'all_pulse': 0x25
}

colourToRGB = {
    'red': (255,0,0),
    'green': (0,255,0),
    'blue': (0,0,255),
    'white': (255,255,255)
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
                    last_call[0] = now # type: ignore
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
                tk.messagebox.showerror("Connection Failure", "LightCraft failed to connect with your LED Strips. Please make sure that your Bluetooth is turned on and that your LED Strips are not bonded with another device. Verify the MAC Address in Settings.") # type: ignore
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

    def swapPulseFlash():
        global isPulsing, isFlashing
        if isPulsing:
            isPulsing = False
            isFlashing = True
            pulseflash_var.set(pulseflash_var.get().replace("pulse","flash"))
        else:
            isPulsing = True
            isFlashing = False
            pulseflash_var.set(pulseflash_var.get().replace("flash","pulse"))
    def sliderColourFun(sliderColour):
        if sliderColour in ["all","rgb"]:
            sliderColour = "white"
        intervalSlider.configure(progress_color=sliderColour)
        r,g,b = colourToRGB[sliderColour]
        colorpicker.update_colors(r,g,b)

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
    
    def setInterval(isUp):
        curr_value = intervalSlider.get()
        if isUp:
            new_value = curr_value + 1
            if new_value > 10:
                new_value = 10
        else:
            new_value = curr_value - 1
            if new_value < 0:
                new_value = 0
        intervalSlider.set(new_value)
        updateInterval()

    @debounce(0.1)
    def sendHex(data):
        intervalSlider.configure(progress_color=data)
        data = data[1:]
        data = bytearray([0x56, int(data[0:2], 16), int(data[2:4], 16), int(data[4:6], 16), 0x00, 0xf0, 0xaa])
        controller.run_coroutine(controller.sendCmd(data))

    @debounce(0.1)
    def sendColour(r,g,b):
        colorpicker.update_colors(r,g,b)
        data = bytearray([0x56, r, g, b, 0x00, 0xf0, 0xaa])
        controller.run_coroutine(controller.sendCmd(data))
    
    def sendColourWB(r,g,b):
        global linkColour
        if (r==255 and g==255 and b==255):
            linkColour = "white"
        elif (r==255 and g==0 and b==0):
            linkColour = "red"
        elif (r==0 and g==255 and b==0):    
            linkColour = "green"
        elif (r==0 and g==0 and b==255):
            linkColour = "blue"
        else:
            linkColour = "unset"
        if linkColour!="unset":
            if isPulsing:
                pulseflash_var.set(linkColour+"_pulse")
            if isFlashing:
                pulseflash_var.set(linkColour+"_flash")
        colorpicker.update_colors(r,g,b)
        sendHex(colorpicker.label.cget("text"))

    @debounce(0.1)
    def sendPulse(isSet=False):
        global isPulsing, isFlashing, linkColour
        isPulsing = True
        isFlashing = False
        if isSet==False:
            data = bytearray([0xbb,validPulseCode[pulseflash_var.get()],int(interval),0x44])
            linkColour = "unset"
            sliderColourFun(pulseflash_var.get().split("_")[0]) 
        else:
            data = bytearray([0xbb,validPulseCode[linkColour+"_pulse"],int(interval),0x44])
        controller.run_coroutine(controller.sendCmd(data))

    @debounce(0.1)
    def sendFlash(isSet=False):
        global isPulsing, isFlashing, linkColour
        isPulsing = False
        isFlashing = True
        if isSet==False:
            data = bytearray([0xbb,validFlashCode[pulseflash_var.get()],int(interval),0x44])
            linkColour = "unset"
            sliderColourFun(pulseflash_var.get().split("_")[0])
        else:
            data = bytearray([0xbb,validFlashCode[linkColour+"_flash"],int(interval),0x44])
        controller.run_coroutine(controller.sendCmd(data))
    
    def sgButton(frame,row,col,colour):
        r, g, b = map(int, validColours[colour])
        return CTkButton(frame,text="", fg_color="#{:02x}{:02x}{:02x}".format(r, g, b), hover=False, font=CTkFont(size=bsize), width=sgwidth, corner_radius=sgradius, height=sgheight, command=lambda: sendColourWB(r,g,b)).grid(row=row,column=col,padx=(10,0),pady=(10,0))

    @debounce(0.1)
    def updateInterval():
        global interval
        interval = 10 - intervalSlider.get()
        if isPulsing:
            sendPulse(linkColour!="unset")
        if isFlashing:
            sendFlash(linkColour!="unset")

    #Settings Functions
    def toggleTheme():
        print("Dummy Settings Function")

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
                disconnect()
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
    root.geometry(f"750x410+{x}+{y}")
    root.resizable(False,False)

    #Frames
    mainframe=CTkTabview(root)
    mainframe.add("Control")
    mainframe.add("Music")
    mainframe.add("Settings")
    sgframe=CTkFrame(mainframe.tab("Control"), fg_color="transparent")
    mgframe=CTkFrame(mainframe.tab("Control"), fg_color="transparent")

    #Button Scaling
    bsize=16
    bheight=35
    bwidth=150
    sgwidth=37
    sgheight=37
    sgradius=50

    #Images
    try:
        image1 = Image.open(r".\Resources\logo.png")
        image2 = Image.open(r".\Resources\onButton.png")
        image3 = Image.open(r".\Resources\offButton.png")
        image4 = Image.open(r".\Resources\pulseHint.png")
        image5 = Image.open(r".\Resources\flashHint.png")
    except:
        tk.messagebox.showerror("Missing Resources","LightCraft could not find critical resources. The Resources folder may have been corrupted or deleted. Please re-install LightCraft from official sources.") # type: ignore #Missing Resources
        quit()
    imgtk1 = CTkImage(light_image=image1,size=(60,60))
    imgtk2 = CTkImage(light_image=image2,size=(25,25))
    imgtk3 = CTkImage(light_image=image3,size=(25,25))
    imgtk4 = CTkImage(light_image=image4,size=(25,25))
    imgtk5 = CTkImage(light_image=image5,size=(25,25))

    #Basic Elements
    headinglogo = CTkButton(root, text="", width=80, image=imgtk1,command=lambda :webbrowser.open("https://github.com/akashcraft/LED-Controller"), hover=False, fg_color="transparent")
    heading1 = CTkLabel(root, text="LightCraft", font=CTkFont(size=30)) #LightCraft
    heading2 = CTkLabel(root, text="Version 1.5.0 (Beta)", font=CTkFont(size=13)) #Version
    connect_button = CTkButton(root, text="Connect", font=CTkFont(size=bsize), width=bwidth, height=bheight, command=connect)
    power_button = CTkButton(root, text="", fg_color="#333333", image=imgtk3, hover=False, font=CTkFont(size=bsize), width=sgwidth, corner_radius=10, height=bheight, command=togglePower)
    colorpicker = CTkColorPicker(mainframe.tab("Control"), width=257, orientation=HORIZONTAL, command=lambda e: sendHex(e))
    pulseflash_var = tk.StringVar(value='all_pulse')
    rainbowPulse = CTkRadioButton(mgframe, text="Rainbow", command=sendPulse, variable= pulseflash_var, value='all_pulse')
    rgbPulse = CTkRadioButton(mgframe, text="RGB", command=sendPulse, variable= pulseflash_var, value='rgb_pulse')
    redPulse = CTkRadioButton(mgframe, text="Red", command=sendPulse, variable= pulseflash_var, value='red_pulse')
    greenPulse = CTkRadioButton(mgframe, text="Green", command=sendPulse, variable= pulseflash_var, value='green_pulse')
    bluePulse = CTkRadioButton(mgframe, text="Blue", command=sendPulse, variable= pulseflash_var, value='blue_pulse')
    whitePulse = CTkRadioButton(mgframe, text="White", command=sendPulse, variable= pulseflash_var, value='white_pulse')
    rainbowFlash = CTkRadioButton(mgframe, text="Rainbow", command=sendFlash, variable= pulseflash_var, value='all_flash')
    rgbFlash = CTkRadioButton(mgframe, text="RGB", command=sendFlash, variable= pulseflash_var, value='rgb_flash')
    redFlash = CTkRadioButton(mgframe, text="Red", command=sendFlash, variable= pulseflash_var, value='red_flash')
    greenFlash = CTkRadioButton(mgframe, text="Green", command=sendFlash, variable= pulseflash_var, value='green_flash')
    blueFlash = CTkRadioButton(mgframe, text="Blue", command=sendFlash, variable= pulseflash_var, value='blue_flash')
    whiteFlash = CTkRadioButton(mgframe, text="White", command=sendFlash, variable= pulseflash_var, value='white_flash')
    pulseHint = CTkButton(mgframe, text="Pulse", width=20, compound="right", image=imgtk4, hover=False, fg_color="transparent")
    flashHint = CTkButton(mgframe, text="Flash", width=20, compound="right", image=imgtk5, hover=False, fg_color="transparent")
    intervalSlider = CTkSlider(mgframe, from_=0, to=10, orientation="vertical", height=185, width=20, progress_color="white", border_width=0, command=lambda e: updateInterval())

    root.grid_columnconfigure(1,weight=1)
    root.grid_rowconfigure(2,weight=1)
    headinglogo.grid(row=0,column=0,rowspan=2,pady=10, sticky='w')
    heading1.grid(row=0,column=1,pady=0, sticky='sw')
    heading2.grid(row=1,column=1,pady=0, sticky='nw')
    connect_button.grid(row=0,column=2,rowspan=2,padx=0, sticky='e')
    power_button.grid(row=0,column=3,rowspan=2,padx=10, sticky='e')
    mainframe.grid(row=2,column=0,columnspan=4,padx=10, pady=(0,10), sticky='nsew')
    mainframe.tab("Control").grid_columnconfigure(1,weight=1)
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
    sgButton(sgframe, 0, 4, "white")
    sgButton(sgframe, 1, 4, "white")
    sgButton(sgframe, 2, 4, "white")
    sgButton(sgframe, 3, 4, "white")
    sgButton(sgframe, 4, 4, "white")
    colorpicker.grid(row=0,column=1,pady=10,sticky='n')
    mgframe.grid(row=0,column=2,padx=(5,10),pady=10, sticky='n')
    pulseHint.grid(row=0,column=0,pady=(5,0), padx=0, ipadx=0, sticky='w')
    flashHint.grid(row=0,column=1,pady=(5,0), sticky='w')
    rainbowPulse.grid(row=1,column=0,pady=(8,0), padx=5, sticky='e')
    rgbPulse.grid(row=2,column=0,pady=(10,0), padx=5, sticky='e')
    redPulse.grid(row=3,column=0,pady=(10,0), padx=5, sticky='e')
    greenPulse.grid(row=4,column=0,pady=(10,0), padx=5, sticky='e')
    bluePulse.grid(row=5,column=0,pady=(10,0), padx=5, sticky='e')
    whitePulse.grid(row=6,column=0,pady=(10,0), padx=5, sticky='e')
    rainbowFlash.grid(row=1,column=1,pady=(10,0), padx=5, sticky='e')
    rgbFlash.grid(row=2,column=1,pady=(10,0), padx=5, sticky='e')
    redFlash.grid(row=3,column=1,pady=(10,0), padx=5, sticky='e')
    greenFlash.grid(row=4,column=1,pady=(10,0), padx=5, sticky='e')
    blueFlash.grid(row=5,column=1,pady=(10,0), padx=5, sticky='e')
    whiteFlash.grid(row=6,column=1,pady=(10,0), padx=5, sticky='e')
    intervalSlider.grid(row=1,column=2,rowspan=6, padx=0, sticky='se')

    #Settings
    mainframe.tab("Settings").grid_columnconfigure(1,weight=1)
    CTkLabel(mainframe.tab("Settings"), text="LED MAC Address").grid(row=0,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(mainframe.tab("Settings"), text="Characteristic UUID").grid(row=1,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(mainframe.tab("Settings"), text="Auto Connect").grid(row=2,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(mainframe.tab("Settings"), text="Enable Keyboard Shortcuts").grid(row=3,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(mainframe.tab("Settings"), text="Remember Loaded Files").grid(row=4,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(mainframe.tab("Settings"), text="Edit Operation Codes").grid(row=5,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(mainframe.tab("Settings"), text="Reset Settings").grid(row=6,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(mainframe.tab("Settings"), text="User Manual").grid(row=7,column=0,padx=5,pady=(4,0), sticky='w')
    macInput = CTkEntry(mainframe.tab("Settings"), placeholder_text="32:06:C2:00:0A:9E", height=5, corner_radius=5).grid(row=0,column=2,padx=5,pady=(4,0), sticky='e')
    uuidInput = CTkEntry(mainframe.tab("Settings"), placeholder_text="FFD9", height=5, corner_radius=5).grid(row=1,column=2,padx=5,pady=(4,0), sticky='e')
    autoCSwitch = CTkCheckBox(mainframe.tab("Settings"), text="", checkbox_height=15, checkbox_width=15, border_width=1, corner_radius=5, width=0, command=toggleTheme).grid(row=2,column=2,padx=(5,0),pady=(4,0), sticky='e')
    keyBindSwitch = CTkCheckBox(mainframe.tab("Settings"), text="", checkbox_height=15, checkbox_width=15, border_width=1, corner_radius=5, width=0, command=toggleTheme).grid(row=3,column=2,padx=(5,0),pady=(4,0), sticky='e')
    loadedSwitch = CTkCheckBox(mainframe.tab("Settings"), text="", checkbox_height=15, checkbox_width=15, border_width=1, corner_radius=5, width=0, command=toggleTheme).grid(row=4,column=2,padx=(5,0),pady=(4,0), sticky='e')
    editOpButton = CTkButton(mainframe.tab("Settings"), text="Edit", width=60, height=15, corner_radius=5, command=toggleTheme).grid(row=5,column=2,padx=8,pady=(4,0), sticky='e')
    resetButton = CTkButton(mainframe.tab("Settings"), text="Reset", width=60, height=15, corner_radius=5, command=toggleTheme).grid(row=6,column=2,padx=8,pady=(4,0), sticky='e')
    useManButton = CTkButton(mainframe.tab("Settings"), text="Open", width=60, height=15, corner_radius=5, command=toggleTheme).grid(row=7,column=2,padx=8,pady=(4,0), sticky='e')

    #Key Binds
    root.bind("<KeyRelease-r>",lambda e:sendColourWB(255,0,0))
    root.bind("<KeyRelease-g>",lambda e:sendColourWB(0,255,0))
    root.bind("<KeyRelease-b>",lambda e:sendColourWB(0,0,255))
    root.bind("<KeyRelease-w>",lambda e:sendColourWB(255,255,255))
    root.bind("<KeyRelease-p>",lambda e:sendColourWB(255,0,40))
    root.bind("<KeyRelease-c>",lambda e:connect())
    root.bind("<space>",lambda e:togglePower())
    root.bind("<Right>",lambda e:setBrightness(True))
    root.bind("<Left>",lambda e:setBrightness(False))
    root.bind("<Up>",lambda e:setInterval(True))
    root.bind("<Down>",lambda e:setInterval(False))
    root.bind("<KeyRelease-1>",lambda e:rainbowPulse.invoke())
    root.bind("<KeyRelease-2>",lambda e:rainbowFlash.invoke())
    root.bind("<KeyRelease-3>",lambda e:rgbPulse.invoke())
    root.bind("<KeyRelease-4>",lambda e:rgbFlash.invoke())
    root.bind("<KeyRelease-5>",lambda e:redPulse.invoke())
    root.bind("<KeyRelease-6>",lambda e:redFlash.invoke())
    root.bind("<KeyRelease-7>",lambda e:greenPulse.invoke())
    root.bind("<KeyRelease-8>",lambda e:greenFlash.invoke())
    root.bind("<KeyRelease-9>",lambda e:bluePulse.invoke())
    root.bind("<KeyRelease-0>",lambda e:blueFlash.invoke())
    root.bind("<Tab>",lambda e:swapPulseFlash())

    #TO DO Settings Auto Reconnect
    #root.after(20,connect)
    root.mainloop()

if __name__ == "__main__":
    main()

