# LightCraft
Software to control Bluetooth LED Strips like [QHM-0A9E](https://a.co/d/eOTiWzj)

<img width=600px src="https://github.com/user-attachments/assets/9f66c3ec-44bc-48c8-bb99-abcd90124662">

## Features
- Connect Button and Power Toggle
- Single Colour Control
- Hex Colour Control
- Custom Colour Saves
- Pulsing and Flashing Control
- Interval Timing Control
- Alert SOS (Sounds from Hitman 3)
- Media Player with LED Sync
- Keyboard Shortcuts
- Settings
- Dark Mode

## Under Development
- Custom Operation Codes

## Installation
There is no available release as of now but you may choose to run the source code yourself, Run the `lightcraft.py` file. Please read important notes below. Here are the requirements:

- Python [Get it here](https://www.python.org/downloads/release/)
- customtkinter [Get it here](https://github.com/TomSchimansky/CustomTkinter)
- CTkColorPicker [Get it here](https://github.com/Akascape/CTkColorPicker)
- bleak [Get it here](https://github.com/hbldh/bleak)
- pillow
- python-vlc
- keyboard
  
Install via the `requirements.txt`. I highly recommend you create a virtual environment (like conda).
```
pip install -r requirements.txt
```
or simply paste the following in terminal
```
pip install customtkinter, CTkColorPicker, bleak, pillow, python-vlc, keyboard
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
<img width=600px src="https://github.com/user-attachments/assets/d70d88b3-f898-4f2b-9ef9-85f327614674">

### Music Player
<img width=600px src="https://github.com/user-attachments/assets/188b8216-53b5-4af2-ba98-a7115da286b9">

### Settings
<img width=600px src="https://github.com/user-attachments/assets/04b4b444-fd64-414d-b190-e473373aa1ea">


## User Manual
Will be available under Wiki after first stable release.

## Who can use this?
You are free to download and edit the source code files however you like. But, LightCraft is not to be resold for any commercial purpose(s).
Should you wish to publish this in your project or socials, please provide appropriate credits.

You can add this as your references (or description) if you like:

Source Code: https://github.com/akashcraft/LED-Controller<br>
Website: [akashcraft.ca](https://akashcraft.ca)

Thanks!
