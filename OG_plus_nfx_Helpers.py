import utils 
import device
import midi
import channels
import plugins

pdBankA = [48, 49, 50, 51,
          32, 33, 34, 35, 
          16, 17, 18, 19,
           0,  1,  2,  3]

pdBankB = [52, 53, 54, 55,
          36, 37, 38, 39,
          20, 21, 22, 23,
           4,  5,  6,  7]

pdBankC = [56, 57, 58, 59,
          40, 41, 42, 43,
          24, 25, 26, 27,
          8,  9, 10, 11]

pdBankD = [60, 61, 62, 63, 
           44, 45, 46, 47,
           28, 29, 30, 31,
           12, 13, 14, 15 ]

PAD_Semitone =	1	#Retrieve semitone for pad specified by padIndex
PAD_Color =	2	#Retrieve color for pad specified by padIndex    

def isFPCChannel(chanIdx):
    if(channels.getChannelType(chanIdx) in [midi.CT_GenPlug]):
        pluginName = plugins.getPluginName(chanIdx, -1, 0)      
        return (pluginName == 'FPC') 

def getFPCPads(mode, isAlt = False):
    pads = []
    if(not isAlt): # FPC Pads
        if mode:
            pads.extend(pdBankA)
            pads.extend(pdBankB)
        else:
            pads.extend(pdBankB)
            pads.extend(pdBankC)

    return pads 

def FLColorToPadColor(FLColor, div = 2):
    
    padcolor = FLColor & 0xFFFFFF # take out any alpha channel
    r = (padcolor >> 16) & 0xFF
    g = (padcolor >> 8)  & 0xFF
    b = (padcolor) & 0xFF

    return utils.RGBToColor(r, g, b)

def AdjustedFirePadColor(color):
    r, g, b = utils.ColorToRGB(color)
    reduceRed = 1
    reduceBlue = 1
    if(b > r) :
        reduceRed  = r / b
    if(g > b):
        reduceBlue = b / g
    if(g > r) and (reduceRed == 1):
        reduceRed  = r / g
    if reduceRed < 1:
        r = int(r * reduceRed)  # red adjust
    if(reduceBlue < 1):
        b = int(b * reduceBlue)  # blue adjust
    # reduce by half to support 0..127 range
    r = r//2
    g = g//2
    b = b//2
    return utils.RGBToColor(r, g, b), r, g, b   

def SendMessageToDevice(ID, l, data): # Fire specific
    ManufacturerIDConst = 0x47
    DeviceIDBroadCastConst = 0x7F
    ProductIDConst = 0x43

    if not device.isAssigned():
        return
    
    msg = bytearray(7 + l + 1)
    lsb = l & 0x7F
    msb = (l & (~ 0x7F)) >> 7

    msg[0] = midi.MIDI_BEGINSYSEX
    msg[1] = ManufacturerIDConst
    msg[2] = DeviceIDBroadCastConst
    msg[3] = ProductIDConst
    msg[4] = ID
    msg[5] = msb
    msg[6] = lsb
    if (l > 63):
        for n in range(0, len(data)):
            msg[7 + n] = data[n]
    else:
        for n in range(0, l):
            msg[7 + n] = data[n]
    msg[len(msg) - 1] = midi.MIDI_ENDSYSEX
    device.midiOutSysex(bytes(msg))

def SetPadRGB(idx, r, g, b):  
    MsgIDSetRGBPadLedState = 0x65
    dataOut = bytearray(4)
    i = 0
    dataOut[i] = idx
    dataOut[i + 1] = r
    dataOut[i + 2] = g
    dataOut[i + 3] = b
    SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)


def SetPadColor(idx, col, dimFactor, dimMult = 2.5):
    if(idx < 0) or (idx > 63):
        return

    col = FLColorToPadColor(col, 1)

    newCol, r, g, b = AdjustedFirePadColor(col)

    # reduce brightness by half times dimFactor
    if(dimFactor > 0):
        for i in range(dimFactor):
            r = int(r / dimMult)
            g = int(g / dimMult)
            b = int(b / dimMult)

    SetPadRGB(idx, r, g, b)
