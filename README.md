# LightCraft
Software to control Bluetooth LED Strips like QHM-0A9E

<img width=600px src="https://github.com/user-attachments/assets/2b842b30-9303-430c-9ac6-cfd6d8ca6d31">

## Features
- Auto Connect
- Single Colour Control
- Dark Mode

## Under Development
Some of these features are available and ready to use in the CLI Version. Run the `main.py` file.
- Hex Colour Control (CLI)
- Pulsing with Timing Control (CLI)
- Flashing with Timing Control (CLI)
- Music Beats Sync (CLI)
- User Friendly GUI and Settings
- Multi-Language Support (Planned)

## Installation
There are no available release as of now but you may choose to run the source code yourself, Run the `lightcraft.py` file. Here are the requirements:

- Python [Get it here](https://www.python.org/downloads/release/)
- customtkinter [Get it here](https://github.com/TomSchimansky/CustomTkinter)
- bleak [Get it here](https://github.com/hbldh/bleak)
- pillow
  
Install via the `requirements.txt`
```
pip install -r requirements.txt
```
or simply paste the following in terminal
```
pip install customtkinter, bleak, pillow
```
Clone this Repository by
```
git clone https://akashcraft/LED-Controller.git
```

## Important Notes
LightCraft CLI version will not be developed further. Use it for a light weight option if you just want to send custom commands to your LED Strips.
LightCraft stores its configuration data in the `Settings.txt` which must be located in the same project folder. If this is not possible, LightCraft will attempt to re-create the files during the pre-GUI checks. Resources folder contains all the GUI elements and this folder **must not** be deleted. LightCraft will not load the GUI in that case.

## User Manual
Will be available after first stable release.

## Who can use this?
You are free to download and edit the source code files however you like. But, LightCraft is not to be resold for any commercial purpose(s).
Should you wish to publish this in your project or socials, please provide appropriate credits.

You can add this as your references (or description) if you like:

Source Code: https://github.com/akashcraft/LED-Controller<br>
Website: [akashcraft.ca](https://akashcraft.ca)

Thanks!
