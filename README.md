# LightCraft
Software to control Bluetooth LED Strips like [QHM-0A9E](https://a.co/d/eOTiWzj)

<img width=600px src="https://github.com/user-attachments/assets/99a503c9-712a-48a3-841e-683dd15f06a1">

## Features
- Connect Button and Power Toggle
- Single Colour Control
- Hex Colour Control and Saves
- Pulsing and Flashing Control
- Interval Timing Control
- Alert SOS (Sounds from Hitman 3)
- Keyboard Shortcuts
- Settings
- Dark Mode

## Under Development
Some of these features are available and ready to use in the CLI Version. Run the `lightcraft_cli.py` file.
- Music Beats Sync (CLI)
- Custom Operation Codes
- Multi-Language Support (Planned)

## Installation
There is no available release as of now but you may choose to run the source code yourself, Run the `lightcraft.py` file. Please read important notes below. Here are the requirements:

- Python [Get it here](https://www.python.org/downloads/release/)
- customtkinter [Get it here](https://github.com/TomSchimansky/CustomTkinter)
- CTkColorPicker [Get it here](https://github.com/Akascape/CTkColorPicker)
- bleak [Get it here](https://github.com/hbldh/bleak)
- pillow
- pygame
- keyboard
  
Install via the `requirements.txt`. I highly recommend you create a virtual environment (like conda).
```
pip install -r requirements.txt
```
or simply paste the following in terminal
```
pip install customtkinter, CTkColorPicker, bleak, pillow, pygame, keyboard
```
Clone this Repository by
```
git clone https://akashcraft/LED-Controller.git
```

## Important Notes
### LightCraft CLI
This version will not be developed further. Use it for a light weight option if you just want to send custom commands to your LED Strips.

### LightCraft GUI
If you plan to run the project locally, you will need to modify the `CTkColorPicker` and `CTkRadioButton` package as the stock package is modified to add functionality to LightCraft. Find the files in the repository and overwrite with the stock file. Failure to do this will result in Runtime Errors.

LightCraft stores its configuration data in the `Settings.txt` which must be located in the same project folder. If this is not possible, LightCraft will attempt to re-create the files during the pre-GUI checks. Resources folder contains all the GUI elements and this folder **must not** be deleted. LightCraft will not load the GUI in that case.

## Screenshots
### Alert SOS
<img width=600px src="https://github.com/user-attachments/assets/bc0a3e24-5a77-42b3-8de7-948accdf8f22">

### Settings
<img width=600px src="https://github.com/user-attachments/assets/b360ae5b-77eb-42d3-ae64-fe243b3637ed">


## User Manual
Will be available after first stable release.

## Who can use this?
You are free to download and edit the source code files however you like. But, LightCraft is not to be resold for any commercial purpose(s).
Should you wish to publish this in your project or socials, please provide appropriate credits.

You can add this as your references (or description) if you like:

Source Code: https://github.com/akashcraft/LED-Controller<br>
Website: [akashcraft.ca](https://akashcraft.ca)

Thanks!
