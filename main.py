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

validPulseCode = {
    'gb': 0x2F,
    'rb': 0x2E,
    'rg': 0x2D,
    'white': 0x2C,
    'purple': 0x2B,
    'cyan': 0x2A,
    'yellow': 0x29,
    'blue': 0x28,
    'green': 0x27,
    'red': 0x26,
    'rgb': 0x61,
    'all': 0x25
}

validFlashCode = {
    'rgb': 0x62,
    'all': 0x38,
    'white': 0x37,
    'purple': 0x36,
    'cyan': 0x35,
    'yellow': 0x34,
    'blue': 0x33,
    'green': 0x32,
    'red': 0x31,
    'eyesore': 0x30
}


def isValidHex(dataList):
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

def isValidFlash(dataList):
    if ((len(dataList)==3 or len(dataList)==2) and dataList[0] in ['f','flash']):
        if (dataList[1] in validFlashCode.keys()):
            return True
    return False

def isValidPulse(dataList):
    if ((len(dataList)==3 or len(dataList)==2) and dataList[0] in ['p','pulse']):
        if (dataList[1] in validPulseCode.keys()):
            return True
    return False
    
def setInterval(dataList):
    if (len(dataList)==3):
        if (dataList[2].isnumeric()):
            var = int(dataList[2])
            if var>10:
                var = 0x00
            elif var<1:
                var = 0x10
            else:
                var = 10 - var
                var = 0x0 << 4 | var
            return var
        else:
            return 0x00
    else:
        return 0x00

async def send_data(address, char_uuid):
    async with BleakClient(address) as client:
        while True:
            user_input = input("Enter Command:\n")
            base = user_input.lower()
            if base in ['exit','quit']:
                break
            
            try:
                if (base=='on'):   
                    await client.write_gatt_char(char_uuid, bytearray([0xcc,0x23,0x33]))
                elif (base=='off'):
                    await client.write_gatt_char(char_uuid, bytearray([0xcc,0x24,0x33]))
                else:
                    if (isValidPulse(base.split())):
                        data_packet = bytearray([0xbb, validPulseCode[base.split()[1]], setInterval(base.split()), 0x44])
                        await client.write_gatt_char(char_uuid, data_packet)
                    elif (isValidFlash(base.split())):
                        data_packet = bytearray([0xbb, validFlashCode[base.split()[1]], setInterval(base.split()), 0x44])
                        await client.write_gatt_char(char_uuid, data_packet)
                    else:
                        r, g, b = 0, 0, 0
                        if (base in validColours.keys()):
                            r, g, b = map(int, validColours[base])
                        else:
                            if (isValidHex(base.split())):
                                r, g, b = map(int, base.split())
                            else:
                                print("Invalid Command. Try Again!")
                                continue
                        data_packet = bytearray([0x56, r, g, b, 0x00, 0xf0, 0xaa])
                        #RGB from second byte
                        await client.write_gatt_char(char_uuid, data_packet)
            except:
                print("Something went wrong. Please restart the program.")
                break

asyncio.run(send_data(bd_addr, uuid))
