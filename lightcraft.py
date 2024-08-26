#LightCraft Source Code
#Made by Akash Samanta

import asyncio, threading, os, time, webbrowser, re, subprocess, keyboard
from bleak import BleakClient
from PIL import Image
from customtkinter import * # type: ignore
import tkinter as tk
from tkinter import messagebox
from CTkColorPicker import * # type: ignore
from functools import wraps
import pygame
from lightcraft_cli import repeat, enableRepeat, disableRepeat

root = CTk()
address = "32:06:C2:00:0A:9E"
char_uuid = "FFD9"
isConnected = False
isOn = False
interval = 5
isFlashing = False
isPulsing = True
linkColour = "white"
isPlaying = False
isLinked = False
isLoaded = False
isUpdatingSlider = False
seekAmount = 0.5
isHidden = False

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
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.connected = False

    def stop(self):
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

        def close_loop():
            if not self.loop.is_running():
                self.loop.close()

        self.loop.call_soon_threadsafe(close_loop)

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
    global controller, loop_thread
    pygame.mixer.init()
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
    
    #Connection Functions
    def connect():
        global isConnected
        if isConnected:
            isConnected = False
            connect_button.configure(text="Connect", state="normal",fg_color=("#3b8ed0","#1f6aa5"),hover_color=("#36719f","#144870"))
            radio_button_1.configure(state="disabled")
            radio_button_2.configure(state="disabled")
            radio_button_3.configure(state="disabled")
            radio_button_4.configure(state="disabled")
            alertButton.configure(state="disabled")
            alertText.configure(text="Please connect your LED Strips first")
            macInput.configure(state="normal")
            macInputButton.configure(state="normal")
            uuidInput.configure(state="normal")
            uuidInputButton.configure(state="normal")
            resetButton.configure(state="normal")
            disconnect()
        else:
            future = controller.run_coroutine(controller.connect())
            connect_button.configure(text="Connecting", state="disabled",fg_color=("#3b8ed0","#1f6aa5"),hover_color=("#36719f","#144870"))
            macInput.configure(state="disabled")
            macInputButton.configure(state="disabled")
            uuidInput.configure(state="disabled")
            uuidInputButton.configure(state="disabled")
            resetButton.configure(state="disabled")
            root.after(20, lambda: check_connection(future))

    def check_connection(future):
        global isConnected
        if future.done():
            if controller.connected:
                isConnected = True
                connect_button.configure(text="Connected", fg_color="green", hover_color="#00AA00", state="normal")
                radio_button_1.configure(state="normal")
                radio_button_2.configure(state="normal")
                radio_button_3.configure(state="normal")
                radio_button_4.configure(state="normal")
                alertButton.configure(state="normal")
                alertText.configure(text="This feature mimics real-life sounds. Use at your own risk.")
                macInput.configure(state="disabled")
                macInputButton.configure(state="disabled")
                uuidInput.configure(state="disabled")
                uuidInputButton.configure(state="disabled")
                resetButton.configure(state="disabled")
            else:
                connect_button.configure(text="Reconnect", fg_color="#AA0000", hover_color="#880000", state="normal")
                messagebox.showerror("Connection Failure", "LightCraft failed to connect with your LED Strips. Please make sure that your Bluetooth is turned on and that your LED Strips are not bonded with another device. Verify the MAC Address in Settings.")
                macInput.configure(state="normal")
                macInputButton.configure(state="normal")
                uuidInput.configure(state="normal")
                uuidInputButton.configure(state="normal")
                resetButton.configure(state="normal")
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

    #Commands
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
    def sendColourCB(button,index):
        global settings
        if keyboard.is_pressed("shift"):
            button.configure(fg_color="#FFFFFF")
            colorpicker.slider.configure(progress_color="#FFFFFF")
            colorpicker.label.configure(text="#FFFFFF",fg_color="#FFFFFF")
            sendHex("#FFFFFF")
            settings[index] = "#FFFFFF\n"
            writesettings()
        else:
            if colorpicker.dragging == True:
                colorpicker.dragging = False
                button.configure(fg_color=colorpicker.label.cget("text"))
                sendHex(colorpicker.label.cget("text"))
                settings[index] = colorpicker.label.cget("text") + "\n"
                writesettings()
            else:
                colorpicker.slider.configure(progress_color=settings[index][:-1])
                colorpicker.label.configure(text=settings[index][:-1],fg_color=settings[index][:-1])
                sendHex(settings[index][:-1])
    
    @debounce(0.1)
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

    @debounce(0.1)
    def updateInterval():
        global interval
        interval = 10 - intervalSlider.get()
        if isPulsing:
            sendPulse(linkColour!="unset")
        if isFlashing:
            sendFlash(linkColour!="unset")
    
    def sgButton(frame,row,col,colour):
        global customColour1, customColour2, customColour3, customColour4, customColour5
        r, g, b = map(int, validColours[colour])
        if col == 4:
            match row:
                case 0:
                    customColour1 = CTkButton(frame,text="", fg_color=settings[7][:-1], hover=False, font=CTkFont(size=bsize), width=sgwidth, corner_radius=sgradius, height=sgheight, command=lambda: sendColourCB(customColour1,7))
                    customColour1.grid(row=row,column=col,padx=(10,0),pady=(10,0))
                case 1:
                    customColour2 = CTkButton(frame,text="", fg_color=settings[8][:-1], hover=False, font=CTkFont(size=bsize), width=sgwidth, corner_radius=sgradius, height=sgheight, command=lambda: sendColourCB(customColour2,8))
                    customColour2.grid(row=row,column=col,padx=(10,0),pady=(10,0))
                case 2:
                    customColour3 = CTkButton(frame,text="", fg_color=settings[9][:-1], hover=False, font=CTkFont(size=bsize), width=sgwidth, corner_radius=sgradius, height=sgheight, command=lambda: sendColourCB(customColour3,9))
                    customColour3.grid(row=row,column=col,padx=(10,0),pady=(10,0))
                case 3:
                    customColour4 = CTkButton(frame,text="", fg_color=settings[10][:-1], hover=False, font=CTkFont(size=bsize), width=sgwidth, corner_radius=sgradius, height=sgheight, command=lambda: sendColourCB(customColour4,10))
                    customColour4.grid(row=row,column=col,padx=(10,0),pady=(10,0))
                case 4:
                    customColour5 = CTkButton(frame,text="", fg_color=settings[11][:-1], hover=False, font=CTkFont(size=bsize), width=sgwidth, corner_radius=sgradius, height=sgheight, command=lambda: sendColourCB(customColour5,11))
                    customColour5.grid(row=row,column=col,padx=(10,0),pady=(10,0))
        else:
            CTkButton(frame,text="", fg_color="#{:02x}{:02x}{:02x}".format(r, g, b), hover=False, font=CTkFont(size=bsize), width=sgwidth, corner_radius=sgradius, height=sgheight, command=lambda: sendColourWB(r,g,b)).grid(row=row,column=col,padx=(10,0),pady=(10,0))

    #Settings Functions
    def macInputSave():
        global settings, address
        address = macInputVar.get()
        if validate_mac_address(macInputVar.get()):
            settings[2] = macInputVar.get() + "\n"
            writesettings()
            recreate_controller()
            macInputButton.configure(state="disabled", text="Saved", fg_color="green")
            macInputButton.after(1000, lambda: macInputButton.configure(state="normal", text="Save", fg_color="#1f6aa5"))
        else:
            messagebox.showerror("Invalid MAC Address", "Please enter a valid MAC address.")

    def validate_mac_address(mac_address):
        # MAC address format: XX:XX:XX:XX:XX:XX
        mac_regex = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        if re.match(mac_regex, mac_address):
            return True
        else:
            return False

    def uuidInputSave():
        global settings, char_uuid
        char_uuid = uuidInputVar.get()
        if len(uuidInputVar.get()) == 4:
            settings[3] = uuidInputVar.get() + "\n"
            writesettings()
            recreate_controller()
            uuidInputButton.configure(state="disabled", text="Saved", fg_color="green")
            uuidInputButton.after(1000, lambda: uuidInputButton.configure(state="normal", text="Save", fg_color="#1f6aa5"))
        else:
            messagebox.showerror("Invalid UUID", "Please enter a UUID with exactly 4 characters.")

    def start_event_loop(controller):
        asyncio.set_event_loop(controller.loop)
        controller.loop.run_forever()

    def recreate_controller():
        global controller, loop_thread,address, char_uuid
        # Stop the previous controller and thread, if they exist
        if 'controller' in globals() and controller is not None:
            controller.stop()
            if loop_thread.is_alive():
                loop_thread.join()
        # Start the new controller
        controller = BluetoothController(address, char_uuid)
        loop_thread = threading.Thread(target=start_event_loop, args=(controller,))
        loop_thread.start()

    def toggleAutoCS():
        global settings
        settings[4] = str(autoCSVar.get()) + "\n"
        writesettings()

    def toggleKeyBind():
        global settings
        settings[5] = str(keyBindVar.get()) + "\n"
        if keyBindVar.get()==0:
            unbindAll()
        else:
            updateTab()
        writesettings()

    def toggleLoaded():
        global settings
        if loadedVar.get()==0:
            clearload()
        settings[6] = str(loadedVar.get()) + "\n"
        writesettings()

    def toggleTheme():
        global settings
        settings[14] = str(darkModeVar.get()) + "\n"
        messagebox.showinfo("Theme Change","The theme will change after you restart LightCraft.")
        writesettings()

    def toggleHidden():
        global settings, isHidden
        if hiddenVar.get()==0:
            isHidden = False
        else:
            isHidden = True
        settings[15] = str(hiddenVar.get()) + "\n"
        writesettings()
    
    def openManual():
        webbrowser.open(r"www.github.com/akashcraft/LED-Controller")
    
    def openSettings():
        if os.path.exists("Settings.txt"):
            subprocess.Popen(["Settings.txt"], shell=True)
        else:
            messagebox.showerror("Unable to Load Configuration","The settings file seems to be missing. LightCraft will attempt to restore default settings.")  

    #Alert Functions
    def playAlert():
        global interval
        if not isOn:
            togglePower()
        enableRepeat()
        alert = alert_var.get()
        pulseflash_var.set("red_pulse")
        match alert:
            case 0:
                pygame.mixer.music.load(r".\Resources\italyAlert.mp3")
                loop_thread1 = threading.Thread(target=lambda: asyncio.run(repeat(controller.client, char_uuid, '["0.3 red","0.3 pink"]', 100)))
                loop_thread1.start()
            case 1:
                pygame.mixer.music.load(r".\Resources\japanAlert.mp3")
                interval = 0
                sendPulse()
            case 2:
                pygame.mixer.music.load(r".\Resources\franceAlert.mp3")
                interval = 1
                sendPulse()
            case 3:
                pygame.mixer.music.load(r".\Resources\usaAlert.mp3")
                interval = 6
                sendPulse()
        intervalSlider.set(10-interval)
        pygame.mixer.music.play()
        alertButton.configure(text="Stop Alert", fg_color="#AA0000", hover_color="#880000", command=stopAlert)

    def stopAlert():
        pygame.mixer.music.stop()
        disableRepeat()
        sendColourWB(255,0,0)
        alertButton.configure(text="Play Alert",fg_color=("#3b8ed0","#1f6aa5"),hover_color=("#36719f","#144870"), command=playAlert)

    #Music Functions
    def clearload():
        load_button.configure(text="Load",fg_color=("#3b8ed0","#1f6aa5"),hover_color=("#36719f","#144870"))
        pygame.mixer.music.unload()
        heading3.configure(text="No Music Loaded")
        play_button.configure(state="disabled")
        link_button.configure(state="disabled")
        add_button.configure(state="disabled")
        seek_button.configure(state="disabled", text="Seek")
        stop_button.configure(state="disabled")
        musicframechild.grid_forget()

    def load(autoload=False):
        global isLoaded, music_length, position
        if not autoload:
            music = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
            if music == "":
                clearload()
                isLoaded = False
                if isPlaying:
                    stop()
                return
            else:
                if settings[6][:-1] == "1":
                    settings[12] = music + "\n"
                    writesettings()
        else:
            music = settings[12][:-1]
        fobj = open(music.split(".")[0]+" LightCraft.txt","a+")
        if isHidden:
            os.system(f'attrib +h "{music.split(".")[0]} LightCraft.txt"')
        fobj.close()
        isLoaded = True
        musicframechild.grid(row=0,column=0,padx=0,pady=0, sticky='nsew')
        music_length = pygame.mixer.Sound(music).get_length()
        load_button.configure(text="Loaded", fg_color="green", hover_color="#00AA00")
        heading3.configure(text=music.split("/")[-1].split(".")[0])
        play_button.configure(state="normal")
        link_button.configure(state="normal")
        add_button.configure(state="normal")
        seek_button.configure(state="normal", text=str(seekAmount).rstrip('0').rstrip('.') + "s")
        stop_button.configure(state="normal")
        total_time.configure(text=time.strftime("%M:%S", time.gmtime(music_length))+".0")
        pygame.mixer.music.load(music)
        pygame.mixer.music.play()
        pygame.mixer.music.pause()
        position = 0

    def update_music_slider():
        global isPlaying, isUpdatingSlider, position
        if isPlaying and not isUpdatingSlider:
            slider_value = (position / music_length / 1000) * 100
            music_slider.set(slider_value)
            actual_time.configure(text=time.strftime("%M:%S", time.gmtime(position//1000))+"."+format_ms(position%1000))
            position += 100
            if position >= music_length * 1000:
                stop()
            root.after(100, update_music_slider)

    def set_music_slider(offset=0):
        global isUpdatingSlider, position
        isUpdatingSlider = True
        new_pos = (music_slider.get() / 100) * music_length
        if new_pos + offset < 0:
            new_pos = 0
        elif new_pos + offset > music_length:
            new_pos = music_length
        else:
            new_pos += offset
        pygame.mixer.music.set_pos(new_pos)
        position = new_pos * 1000
        if not isPlaying:
            slider_value = (position / music_length / 1000) * 100
            music_slider.set(slider_value)
            actual_time.configure(text=time.strftime("%M:%S", time.gmtime(position/1000))+"."+format_ms(position%1000))
        isUpdatingSlider = False

    def format_ms(ms):
        if ms < 100:
            return "0"
        else:
            return str(ms)[:1]

    def play():
        global isPlaying
        if not isPlaying:
            isPlaying = True
            play_button.configure(text="Pause")
            pygame.mixer.music.unpause()
            update_music_slider()
        else:
            isPlaying = False
            play_button.configure(text="Play")
            pygame.mixer.music.pause()

    def stop():
        global isPlaying, position
        position = 0
        actual_time.configure(text="00:00.0")
        music_slider.set(0)
        isPlaying = False
        play_button.configure(text="Play")
        pygame.mixer.music.stop()
        pygame.mixer.music.play()
        pygame.mixer.music.pause()
        
    def link():
        global isLinked
        if not isLinked:
            isLinked = True
            link_button.configure(text="Unlink")
        else:
            isLinked = False
            link_button.configure(text="Link")

    def seekBack():
        set_music_slider(-seekAmount) # type: ignore
    
    def seekForward():
        set_music_slider(seekAmount) # type: ignore

    def seekAdjust(manual=False, invert=False):
        global seekAmount
        seeks = [0.1, 0.5, 1, 2, 5, 10]
        index = seeks.index(seekAmount)
        if invert:
            index -= 1
            if index == -1:
                index = 0
        else:
            index += 1
            if index == 6:
                if manual:
                    index = 0
                else:
                    index = 5
        seekAmount = seeks[index]
        settings[13] = str(seekAmount) + "\n"
        writesettings()
        seek_button.configure(text=str(seekAmount) + "s")

    #Page Functions
    def unbindAll():
        root.unbind("<KeyRelease-o>")
        root.unbind("<KeyRelease-s>")
        root.unbind("<KeyRelease-l>")
        root.unbind("<KeyRelease-a>")
        root.unbind("<KeyRelease-r>")
        root.unbind("<KeyRelease-g>")
        root.unbind("<KeyRelease-b>")
        root.unbind("<KeyRelease-w>")
        root.unbind("<KeyRelease-p>")
        root.unbind("<KeyRelease-c>")
        root.unbind("<space>")
        root.unbind("<Right>")
        root.unbind("<Left>")
        root.unbind("<Up>")
        root.unbind("<Down>")
        root.unbind("<KeyRelease-1>")
        root.unbind("<KeyRelease-2>")
        root.unbind("<KeyRelease-3>")
        root.unbind("<KeyRelease-4>")
        root.unbind("<KeyRelease-5>")
        root.unbind("<KeyRelease-6>")
        root.unbind("<KeyRelease-7>")
        root.unbind("<KeyRelease-8>")
        root.unbind("<KeyRelease-9>")
        root.unbind("<KeyRelease-0>")
        root.unbind("<KeyRelease-`>")
        root.bind("<Tab>")
    
    def bindBasic():
        unbindAll()
        root.bind("<KeyRelease-r>",lambda e:sendColourWB(255,0,0))
        root.bind("<KeyRelease-g>",lambda e:sendColourWB(0,255,0))
        root.bind("<KeyRelease-b>",lambda e:sendColourWB(0,0,255))
        root.bind("<KeyRelease-w>",lambda e:sendColourWB(255,255,255))
        root.bind("<KeyRelease-p>",lambda e:sendColourWB(255,0,40))
        root.bind("<KeyRelease-c>",lambda e:connect())
        root.bind("<KeyRelease-`>",lambda e:swapPulseFlash())
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
        root.bind("<Tab>",lambda e:nextTab())

    def bindAlert():
        unbindAll()
        root.bind("<KeyRelease-c>",lambda e:connect())
        root.bind("<KeyRelease-1>",lambda e:radio_button_1.invoke())
        root.bind("<KeyRelease-2>",lambda e:radio_button_2.invoke())
        root.bind("<KeyRelease-3>",lambda e:radio_button_3.invoke())
        root.bind("<KeyRelease-4>",lambda e:radio_button_4.invoke())
        root.bind("<Tab>",lambda e:nextTab())
        root.bind("<space>",lambda e: alertButton.invoke())

    def bindMusic():
        unbindAll()
        root.bind("<KeyRelease-c>",lambda e:connect())
        root.bind("<KeyRelease-o>",lambda e:load_button.invoke())
        root.bind("<KeyRelease-s>",lambda e:stop_button.invoke())
        root.bind("<KeyRelease-l>",lambda e:link_button.invoke())
        root.bind("<KeyRelease-a>",lambda e:add_button.invoke())
        root.bind("<Tab>",lambda e:nextTab())
        root.bind("<space>",lambda e: play_button.invoke())
        root.bind("<Left>",lambda e:seekBack())
        root.bind("<Right>",lambda e:seekForward())
        root.bind("<Up>",lambda e:seekAdjust())
        root.bind("<Down>",lambda e:seekAdjust(invert=True))

    def bindSettings():
        unbindAll()
        root.bind("<KeyRelease-c>",lambda e:connect())
        root.bind("<Tab>",lambda e:nextTab())

    def nextTab():
        if settings[5][:-1]=="1":
            tab = mainframe.get()
            if tab=="Basic":
                mainframe.set("Alert")
            elif tab=="Alert":
                mainframe.set("Music")
            elif tab=="Music":
                mainframe.set("Settings")
            else:
                mainframe.set("Basic")
            updateTab()

    def updateTab():
        stopAlert()
        if isPlaying:
            stop()
        tab = mainframe.get()
        macInput.configure(state="disabled")
        uuidInput.configure(state="disabled")
        if tab=="Basic":
            bindBasic()
        elif tab=="Alert":
            bindAlert()
        elif tab=="Music":
            bindMusic()
            connect_button.grid_forget()
            power_button.grid_forget()
            headinglogo.grid_forget()
            heading1.grid_forget()
            heading2.grid_forget()
            if isLoaded:
                pygame.mixer.music.load(settings[12][:-1])
                pygame.mixer.music.play()
                pygame.mixer.music.pause()
            else:
                clearload()
            mcontrolframe.grid(row=0,column=0,rowspan=2,columnspan=4,padx=10,pady=(5,0),sticky='nsew')
        else:
            if not isConnected:
                macInput.configure(state="normal")
                uuidInput.configure(state="normal")
            bindSettings()
        if tab!="Music":
            connect_button.grid(row=0,column=2,rowspan=2,padx=0, sticky='e')
            power_button.grid(row=0,column=3,rowspan=2,padx=10, sticky='e')
            headinglogo.grid(row=0,column=0,rowspan=2,pady=10, sticky='w')
            heading1.grid(row=0,column=1,pady=0, sticky='sw')
            heading2.grid(row=1,column=1,pady=0, sticky='nw')
            mcontrolframe.grid_forget()
            
    #Settings Validation and Reset
    def createsettings():
        try:
            f=open("Settings.txt","w")
        except PermissionError:
            messagebox.showerror("Administrator Privileges Needed","Because of the nature of this LightCraft install, you will need to launch as administrator. To prevent this behaviour, please install LightCraft again on a user directory.")
            quit()
        f.write("LightCraft Settings - Any corruption may lead to configuration loss\nMade by Akash Samanta\n32:06:C2:00:0A:9E\nFFD9\n0\n1\n1\n#FFFFFF\n#FFFFFF\n#FFFFFF\n#FFFFFF\n#FFFFFF\nSave\n0.5\n1\n1\n")
        f.close()

    #Quit or Relaunch Application
    def destroyer():
        global root, isPlaying
        if isPlaying:
            stop()
        disconnect()
        root.destroy()
        controller.loop.call_soon_threadsafe(controller.loop.stop)
        loop_thread.join()

    #For other functions to write Settings
    def writesettings():
        global settings
        f=open("Settings.txt","w")
        f.writelines(settings)
        f.close()

    #Normal Reset from Application
    def resetsettings():
        ans=messagebox.askyesno("Clear Application Data","You will also lose any custom operation code configurations. Are you sure you want to clear application data?")
        if ans:
            autoCSwitch.deselect()
            keyBindSwitch.select()
            loadedSwitch.select()
            macInputVar.set("32:06:C2:00:0A:9E")
            uuidInputVar.set("FFD9")
            customColour1.configure(fg_color="#FFFFFF")
            customColour2.configure(fg_color="#FFFFFF")
            customColour3.configure(fg_color="#FFFFFF")
            customColour4.configure(fg_color="#FFFFFF")
            customColour5.configure(fg_color="#FFFFFF")
            macInputSave()
            uuidInputSave()
            updateTab()
            createsettings()
            applysettings()

    #Settings Corruption Reset
    def resetsettings2():
        messagebox.showerror("Unable to Load Settings","The settings file seems corrupted, possibly due to file tampering. LightCraft will attempt to restore default settings.")
        createsettings()
        applysettings()

    #Boot and apply settings
    def applysettings():
        global settings, address, char_uuid, seekAmount, isHidden
        f=open("Settings.txt","a+")
        f.seek(0)
        settings=f.readlines()
        check=[['LightCraft Settings - Any corruption may lead to configuration loss'],['Made by Akash Samanta'],[],[],['0','1'],['0','1'],['0','1'],['Hex'],['Hex'],['Hex'],['Hex'],['Hex'],[],['0.1','0.5','1','2','5','10'],['0','1'],['0','1']]
        #print(len(settings),len(check)) #For Debug Only
        #print(settings) #For Debug Only
        for i in range(len(check)):
            try:
                if check[i]!=[]:
                    if check[i]==['Hex']:
                        #print(settings[i],check[i]) #For Debug Only
                        if settings[i][:-1][0]!="#" or len(settings[i][:-1])!=7:
                            resetsettings2()
                    elif settings[i][:-1] not in check[i]:
                        #print(settings[i][:-1],"and",check[i]) #For Debug Only
                        resetsettings2()
            except:
                #print("FAIL") #For Debug Only
                resetsettings2()
        address=settings[2][:-1]
        char_uuid=settings[3][:-1]
        seekAmount=float(settings[13][:-1])
        if settings[14][:-1]=="1":
            set_appearance_mode("dark")
        else:
            set_appearance_mode("light")
        if settings[15][:-1]=="1":
            isHidden = True
        else:
            isHidden = False
        f.close()

    #Getting settings
    if not os.path.exists("Settings.txt"):
        createsettings()

    #Making the Application
    root.title("LightCraft")
    root.protocol("WM_DELETE_WINDOW", destroyer)
    root.iconbitmap(r".\Resources\logo.ico")
    applysettings()
    userwinx = root.winfo_screenwidth()
    userwiny = root.winfo_screenheight()
    x = (userwinx)//3
    y = (userwiny)//3
    root.geometry(f"750x420+{x}+{y}")
    root.resizable(False,False)

    #Start Controller
    controller = BluetoothController(address, char_uuid)
    loop_thread = threading.Thread(target=start_event_loop, args=(controller,))
    loop_thread.start()

    #Frames
    mainframe=CTkTabview(root, command=updateTab)
    mainframe.add("Basic")
    mainframe.add("Alert")
    mainframe.add("Music")
    mainframe.add("Settings")
    settingschild=CTkScrollableFrame(mainframe.tab("Settings"), fg_color="transparent")
    sgframe=CTkFrame(mainframe.tab("Basic"), fg_color="transparent")
    mgframe=CTkFrame(mainframe.tab("Basic"), fg_color="transparent")
    alertframe=CTkFrame(mainframe.tab("Alert"))
    mcontrolframe=CTkFrame(root, fg_color="transparent", height=70)

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
        image6 = Image.open(r".\Resources\italy.png")
        image7 = Image.open(r".\Resources\japan.png")
        image8 = Image.open(r".\Resources\france.png")
        image9 = Image.open(r".\Resources\usa.png")
    except:
        tk.messagebox.showerror("Missing Resources","LightCraft could not find critical resources. The Resources folder may have been corrupted or deleted. Please re-install LightCraft from official sources.") # type: ignore #Missing Resources
        quit()
    imgtk1 = CTkImage(light_image=image1,size=(60,60))
    imgtk10 = CTkImage(light_image=image1,size=(20,20))
    imgtk2 = CTkImage(light_image=image2,size=(25,25))
    imgtk3 = CTkImage(light_image=image3,size=(25,25))
    imgtk4 = CTkImage(light_image=image4,size=(25,25))
    imgtk5 = CTkImage(light_image=image5,size=(25,25))
    imgtk6 = CTkImage(light_image=image6,size=(160,90))
    imgtk7 = CTkImage(light_image=image7,size=(160,90))
    imgtk8 = CTkImage(light_image=image8,size=(160,90))
    imgtk9 = CTkImage(light_image=image9,size=(160,90))

    #Basic Elements
    headinglogo = CTkButton(root, text="", width=80, image=imgtk1,command=lambda :webbrowser.open("https://github.com/akashcraft/LED-Controller"), hover=False, fg_color="transparent")
    heading1 = CTkLabel(root, text="LightCraft", font=CTkFont(size=30)) #LightCraft
    heading2 = CTkLabel(root, text="Version 1.7.3 (Beta)", font=CTkFont(size=13)) #Version
    connect_button = CTkButton(root, text="Connect", font=CTkFont(size=bsize), width=bwidth, height=bheight, command=connect)
    power_button = CTkButton(root, text="", fg_color="#333333", image=imgtk3, hover=False, font=CTkFont(size=bsize), width=sgwidth, corner_radius=10, height=bheight, command=togglePower)
    colorpicker = CTkColorPicker(mainframe.tab("Basic"), width=257, orientation=HORIZONTAL, command=lambda e: sendHex(e))
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
    mainframe.tab("Basic").grid_columnconfigure(1,weight=1)
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
    mainframe.tab("Settings").grid_columnconfigure(0,weight=1)
    mainframe.tab("Settings").grid_rowconfigure(0,weight=1)
    settingschild.grid(row=0,column=0,padx=0,pady=0, sticky='nsew')
    settingschild.grid_columnconfigure(1,weight=1)
    CTkLabel(settingschild, text="LED MAC Address").grid(row=0,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(settingschild, text="Characteristic UUID").grid(row=1,column=0,padx=5,pady=(4,0), sticky='w')
    darkModeLabel = CTkLabel(settingschild, text="Dark Mode")
    darkModeLabel.grid(row=2,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(settingschild, text="Auto Connect").grid(row=3,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(settingschild, text="Enable Keyboard Shortcuts").grid(row=4,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(settingschild, text="Remember Loaded Files").grid(row=5,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(settingschild, text="Make Hidden Configurations").grid(row=6,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(settingschild, text="Edit Operation Codes (Advanced)").grid(row=8,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(settingschild, text="Clear Application Data").grid(row=9,column=0,padx=5,pady=(4,0), sticky='w')
    CTkLabel(settingschild, text="User Manual").grid(row=7,column=0,padx=5,pady=(4,0), sticky='w')
    macInputVar = tk.StringVar(value=settings[2][:-1])
    macInput = CTkEntry(settingschild, placeholder_text="32:06:C2:00:0A:9E", textvariable=macInputVar, height=5, corner_radius=5, justify='right')
    macInput.grid(row=0,column=1,padx=5,pady=(4,0), sticky='e')
    macInputButton= CTkButton(settingschild, text="Save", width=60, height=15, corner_radius=5, command=macInputSave)
    macInputButton.grid(row=0,column=2,padx=8,pady=(4,0), sticky='e')
    uuidInputVar = tk.StringVar(value=settings[3][:-1])
    uuidInput = CTkEntry(settingschild, placeholder_text="FFD9", textvariable=uuidInputVar, height=5, corner_radius=5, justify='right')
    uuidInputButton = CTkButton(settingschild, text="Save", width=60, height=15, corner_radius=5, command=uuidInputSave)
    uuidInputButton.grid(row=1,column=2,padx=8,pady=(4,0), sticky='e')
    uuidInput.grid(row=1,column=1,padx=5,pady=(4,0), sticky='e')
    darkModeVar = tk.IntVar(value=int(settings[14][:-1]))
    darkModeSwitch = CTkCheckBox(settingschild, text="", variable=darkModeVar, checkbox_height=15, checkbox_width=15, border_width=1, corner_radius=5, width=0, command=toggleTheme)
    darkModeSwitch.grid(row=2,column=2,padx=(5,0),pady=(4,0), sticky='e')
    autoCSVar = tk.IntVar(value=int(settings[4][:-1]))
    autoCSwitch = CTkCheckBox(settingschild, text="", variable=autoCSVar, checkbox_height=15, checkbox_width=15, border_width=1, corner_radius=5, width=0, command=toggleAutoCS)
    autoCSwitch.grid(row=3,column=2,padx=(5,0),pady=(4,0), sticky='e')
    keyBindVar = tk.IntVar(value=int(settings[5][:-1]))
    keyBindSwitch = CTkCheckBox(settingschild, text="", variable=keyBindVar, checkbox_height=15, checkbox_width=15, border_width=1, corner_radius=5, width=0, command=toggleKeyBind)
    keyBindSwitch.grid(row=4,column=2,padx=(5,0),pady=(4,0), sticky='e')
    loadedVar = tk.IntVar(value=int(settings[6][:-1]))
    loadedSwitch = CTkCheckBox(settingschild, text="", variable=loadedVar, checkbox_height=15, checkbox_width=15, border_width=1, corner_radius=5, width=0, command=toggleLoaded)
    loadedSwitch.grid(row=5,column=2,padx=(5,0),pady=(4,0), sticky='e')
    hiddenVar = tk.IntVar(value=int(settings[15][:-1]))
    hiddenSwitch = CTkCheckBox(settingschild, text="", variable=hiddenVar, checkbox_height=15, checkbox_width=15, border_width=1, corner_radius=5, width=0, command=toggleHidden)
    hiddenSwitch.grid(row=6,column=2,padx=(5,0),pady=(4,0), sticky='e')
    editOpButton = CTkButton(settingschild, text="Edit", width=60, height=15, corner_radius=5, command=openSettings).grid(row=8,column=2,padx=8,pady=(4,0), sticky='e')
    resetButton = CTkButton(settingschild, text="Clear", width=60, height=15, corner_radius=5, command=resetsettings)
    resetButton.grid(row=9,column=2,padx=8,pady=(4,0), sticky='e')
    useManButton = CTkButton(settingschild, text="Open", width=60, height=15, corner_radius=5, command=openManual).grid(row=7,column=2,padx=8,pady=(4,0), sticky='e')

    #Alert
    mainframe.tab("Alert").grid_columnconfigure(0,weight=1)
    CTkLabel(alertframe,text='',image=imgtk6).grid(row=0,column=0,padx=(10,0),pady=(10,0), sticky='nw')
    CTkLabel(alertframe,text='',image=imgtk7).grid(row=0,column=1,padx=(10,0),pady=(10,0), sticky='nw')
    CTkLabel(alertframe,text='',image=imgtk8).grid(row=0,column=2,padx=(10,0),pady=(10,0), sticky='nw')
    CTkLabel(alertframe,text='',image=imgtk9).grid(row=0,column=3,padx=(10,0),pady=(10,0), sticky='nw')
    alertText = CTkLabel(mainframe.tab("Alert"), text="Please connect your LED Strips first", font=CTkFont(size=12), text_color=("red","yellow"))
    alertText.grid(row=0,column=0,padx=10,pady=(4,0), sticky='nsew')
    alert_var = tk.IntVar(value=0)
    radio_button_1 = CTkRadioButton(alertframe, text="Sapienza, Italy", variable=alert_var, value=0, state="disabled", command=stopAlert)
    radio_button_1.grid(row=1,column=0,padx=10,pady=10, sticky='w')
    radio_button_2 = CTkRadioButton(alertframe, text="Hokkaido, Japan", variable=alert_var, value=1, state="disabled", command=stopAlert)
    radio_button_2.grid(row=1,column=1,padx=10,pady=10, sticky='w')
    radio_button_3 = CTkRadioButton(alertframe, text="Paris, France", variable=alert_var, value=2, state="disabled", command=stopAlert)
    radio_button_3.grid(row=1,column=2,padx=10,pady=10, sticky='w')
    radio_button_4 = CTkRadioButton(alertframe, text="Colorado, US", variable=alert_var, value=3, state="disabled")
    radio_button_4.grid(row=1,column=3,padx=10,pady=10, sticky='w')
    alertframe.grid(row=1,column=0,padx=10,pady=5, sticky='n')
    alertButton = CTkButton(mainframe.tab("Alert"), text="Play Alert", font=CTkFont(size=bsize), width=bwidth, height=bheight, corner_radius=5, command=playAlert, state="disabled")
    alertButton.grid(row=2,column=0,padx=0,pady=(10,0))

    #Music
    mainframe.tab("Music").grid_columnconfigure(0,weight=1)
    mcontrolframe.grid_columnconfigure(1,weight=1)
    heading3 = CTkLabel(mcontrolframe, text="No Music Loaded", font=CTkFont(size=15))
    heading3.grid(row=0,column=0,padx=10,sticky='nw')
    mcontrolsframe = CTkFrame(mcontrolframe, fg_color="transparent")
    mcontrolsframe.grid(row=0,column=1,columnspan=2,padx=5,pady=(0,5),sticky='e')
    musicframe = CTkScrollableFrame(mainframe.tab("Music"), bg_color="transparent", fg_color="transparent")
    musicframe.grid(row=0,column=0,padx=0,pady=0, sticky='nsew')
    load_button = CTkButton(mcontrolsframe, text="Load", width=60, height=15, corner_radius=5, command=load)
    load_button.grid(row=0,column=0,padx=5,pady=5)
    link_button = CTkButton(mcontrolsframe, text="Link", width=60, height=15, corner_radius=5, command=link, state="disabled")
    link_button.grid(row=0,column=1,padx=5,pady=5)
    add_button = CTkButton(mcontrolsframe, text="Add", width=60, height=15, corner_radius=5, state="disabled")
    add_button.grid(row=0,column=2,padx=5,pady=5)
    seek_button = CTkButton(mcontrolsframe, text="Seek", width=60, height=15, corner_radius=5, command=lambda: seekAdjust(manual=True), state="disabled")
    seek_button.grid(row=0,column=3,padx=5,pady=5)
    stop_button = CTkButton(mcontrolsframe, text="Stop", width=60, height=15, corner_radius=5, command=stop, state="disabled")
    stop_button.grid(row=0,column=4,padx=5,pady=5)
    play_button = CTkButton(mcontrolsframe, text="Play", width=60, height=15, corner_radius=5, command=play, state="disabled")
    play_button.grid(row=0,column=5,padx=5,pady=5)
    music_slider = CTkSlider(mcontrolframe, from_=0, to=100, orientation="horizontal", progress_color="white", border_width=3, height=12, command=lambda e: set_music_slider())
    music_slider.grid(row=1,column=0,columnspan=8,padx=8,pady=(5,3),sticky='ew')
    music_slider.set(0)
    actual_time = CTkLabel(mcontrolframe, text="00:00:00", font=CTkFont(size=12))
    actual_time.grid(row=2,column=0,padx=10,pady=0, sticky='w')
    total_time = CTkLabel(mcontrolframe, text="00:00:00", font=CTkFont(size=12))
    total_time.grid(row=2,column=2,padx=10,pady=0, sticky='e')
    musicframechild = CTkFrame(musicframe, fg_color="transparent")
    musicframechild.grid_columnconfigure(0,weight=1)

    if settings[4][:-1]=="1":
        root.after(20,connect)
    if settings[5][:-1]=="1":
        bindBasic()
    if settings[6][:-1]=="1" and os.path.exists(settings[12][:-1]):
        load(True)
    else:
        clearload()
    root.mainloop()


if __name__ == "__main__":
    main()

