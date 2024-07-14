import asyncio
from bleak import BleakClient

bd_addr = "32:06:C2:00:0A:9E"
uuid = "FFD9"

validColours = {
    'red': [255, 0, 0],
    'green': [0, 255, 0],
    'blue': [0, 0, 255],
    'yellow': [255, 255, 0],
    'cyan': [0, 255, 255],
    'magenta': [255, 0, 255],
    'black': [0, 0, 0],
    'white': [255, 255, 255],
    'gray': [128, 128, 128],
    'orange': [255, 45, 0],
    'purple': [128, 0, 128],
    'pink': [255, 0, 40],
    'brown': [165, 42, 42],
    'lime': [0, 255, 0],
    'navy': [0, 0, 128],
    'gold': [255, 215, 0],
    'silver': [192, 192, 192],
    'teal': [0, 128, 128],
    'maroon': [128, 0, 0],
    'olive': [128, 128, 0],
    'skyblue': [135, 206, 235],
    'violet': [238, 130, 238],
    'indigo': [75, 0, 130],
    'coral': [255, 127, 80]
}

def isValidHex(data):
    dataList = data.split(" ")
    if len(dataList)==3:
        flag = True
    else:
        return False
    for i in dataList:
        if int(i)>=0 and int(i)<256:
            continue
        else:
            flag = False
            break
    return flag

async def send_data(address, char_uuid):
    async with BleakClient(address) as client:
        while True:
            # Get user input for RGB values
            user_input = input("Enter Command:\n")
            if user_input.lower() in ['exit','quit']:
                break
            
            try:
                if (user_input.lower()=='on'):   
                    await client.write_gatt_char(uuid, bytearray([0xcc,0x23,0x33]))
                elif (user_input.lower()=='off'):
                    await client.write_gatt_char(uuid, bytearray([0xcc,0x24,0x33]))
                else:
                    r, g, b = 0, 0, 0
                    if (user_input.lower() in validColours.keys()):
                        r, g, b = map(int, validColours[user_input.lower()])
                    else:
                        if (isValidHex(user_input)):
                            r, g, b = map(int, user_input.split())
                        else:
                            print("Invalid Command. Try Again!")
                            continue
                    data_packet = bytearray([0x56, r, g, b, 0x00, 0xf0, 0xaa])
                    #RGB from second byte
                    await client.write_gatt_char(uuid, data_packet)
            except:
                print("Something went wrong. Please restart the program.")
                break

asyncio.run(send_data(bd_addr, uuid))
