import asyncio, os, time
from bleak import BleakClient

bd_addr = "32:06:C2:00:0A:9E"
uuid = "FFD9"
manual = True
step = 0

def isPlayerValid(dataList):
    if ((len(dataList)==1) and dataList[0] in ['s','start']):
        return True
    return False

def extractCmd(line):
    global prevTime,step
    line = line.split()
    if len(line)==0:
        return "red",0
    else:
        delay = float(line[0])
        del line[0]
        cmd = ""
        for i in line:
            if cmd == "":
                cmd = cmd+i
            else:
                cmd = cmd+" "+i
        return cmd, delay

def getCmd():
    file_path = os.path.join(os.pardir,"music.mp3")
    try:
        os.startfile(file_path)
        fobj = open(os.path.join(os.pardir,"music.txt"),"r")
        cmd = fobj.readlines()
        time.sleep(0.8)
        return True,len(cmd),cmd
    except:
        print("Error Opening Files")
        return False,None,None
    
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
    global manual,step
    async with BleakClient(address) as client:
        while True:
            if manual:
                user_input = input("Enter Command:\n")
                base = user_input.lower()
                if base in ['exit','quit']:
                    break
            else:
                if (step!=stepmax):
                    base, delay = extractCmd(cmds[step]) # type: ignore
                    time.sleep(delay)
                else:
                    step = 0
                    manual = True
                    continue
            
            if (base=='on'):   
                await client.write_gatt_char(char_uuid, bytearray([0xcc,0x23,0x33]))
            elif (base=='off'):
                await client.write_gatt_char(char_uuid, bytearray([0xcc,0x24,0x33]))
            else:
                if (isPlayerValid(base.split())):
                    valid, stepmax, cmds = getCmd()
                    if valid:
                        manual = False
                    continue
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
            if manual==False:
                step=step+1

asyncio.run(send_data(bd_addr, uuid))
