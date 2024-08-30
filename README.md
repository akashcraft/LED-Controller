# LightCraft
Software to control Bluetooth LED Strips like [QHM-0A9E](https://a.co/d/eOTiWzj)

<img width=600px src="https://github.com/user-attachments/assets/cd95f957-19d0-464f-b410-fe24c6800e57">

## Features
- Dark Mode
- Connect Button and Power Toggle
- Single Colour Control
- Hex Colour Control
- Custom Colour Saves
- Pulsing and Flashing Control
- Frequency Control
- Alert SOS (Sounds from Hitman 3)
- Media Player with LED Sync
- Keyboard Shortcuts
- Settings with Custom Operation Codes

## User Manual
Please read the [Wiki](https://github.com/akashcraft/LED-Controller/wiki).

## Installation
LightCraft can be installed on Windows using the Installer file provided in the [Releases](https://github.com/akashcraft/LED-Controller/releases) section. You may also choose to run the source code yourself. Run the `lightcraft.py` file. Please read important notes below. Here are the requirements:

Install via the `requirements.txt`. I highly recommend you create a virtual environment (like conda).
```
pip install -r requirements.txt
```
or simply paste the following in terminal
```
pip install customtkinter, CTkColorPicker, bleak, pillow, pygame, keyboard, mutagen, opencv-python
```
Clone this Repository by
```
git clone https://akashcraft/LED-Controller.git
```

## Screenshots
### Alert SOS
<img width=600px src="https://github.com/user-attachments/assets/53214608-b8fd-4d42-bda1-e5cd4c47438c">

### Music Player
<img width=600px src="https://github.com/user-attachments/assets/bae4fb64-e2ea-4c79-ad48-da6e79a57d52">

### Settings
<img width=600px src="https://github.com/user-attachments/assets/62bd5397-1ac7-4868-ae7d-0e8fd53f7994">

## Important Notes
### LightCraft CLI
This version will not be developed further. Use it for a light weight option if you just want to send custom commands to your LED Strips. Please read the [Wiki](https://github.com/akashcraft/LED-Controller/wiki) for more information.

### LightCraft GUI
If you plan to run the project locally, you will need to modify the `CTkColorPicker` package as the stock package is modified to add functionality to LightCraft. Find the file in the repository and overwrite the stock file.

LightCraft stores its settings and custom operation codes data in the `Settings.txt` which must be located in the same project folder. If this is not possible, LightCraft will attempt to re-create the files during the pre-GUI checks. Resources folder contains all the GUI elements and this folder **must not** be deleted. LightCraft will not load the GUI in that case.

## Who can use this?
You are free to download and edit the source code files however you like. 
Should you wish to publish this in your project or socials, please provide appropriate credits.

You can add this as your references (or description) if you like:

Source Code: https://github.com/akashcraft/LED-Controller<br>
Website: [akashcraft.ca](https://akashcraft.ca)

Your help is appreciated!
