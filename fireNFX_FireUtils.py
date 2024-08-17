# Fire device specific functions.

import colorsys
import device 
import midi
import utils 
import math 
import time
import fireNFX_Utils as nfxutils
import fireNFX_Colors as colors

# Class representing a color map for a pad, including its index, color, and dimming factor
class TnfxColorMap:
    def __init__(self, padIndex, color, dimFactor):
        self.PadIndex = padIndex
        self.PadColor = color
        self.DimFactor = dimFactor
        self.R = 0
        self.G = 0
        self.B = 0

# Initialize color map with 64 pads
ColorMap = [TnfxColorMap(p, 0, 0) for p in range(64)]
NoteColorMap = [TnfxColorMap(p, 0, 0) for p in range(64)]

# Retrieve the current color of a specific pad by its index
def getPadColor(padIdx):
    return ColorMap[padIdx].PadColor

def getNotePadColor(padIdx):
    return  NoteColorMap[padIdx].PadColor


# Set the color of a pad in the buffer, with optional dimming and saving to the color map
def SetPadColorBuffer(idx, col, dimFactor, flushBuffer=False, bSave=True):
    if col == -1:
        col = ColorMap[idx].PadColor
        dimFactor = ColorMap[idx].DimFactor

    col = nfxutils.getShade(col, colors.dimShades[dimFactor])

    newCol, r, g, b = AdjustedFirePadColor(FLColorToPadColor(col))

    # if dimFactor > 0:
    #     for _ in range(dimFactor):
    #         r >>= 1
    #         g >>= 1
    #         b >>= 1

    if bSave:
        ColorMap[idx].PadColor = newCol 
        ColorMap[idx].DimFactor = dimFactor
        ColorMap[idx].R = r
        ColorMap[idx].G = g
        ColorMap[idx].B = b
    
    if flushBuffer:
        FlushColorMap()

# Send the current color map to the device, updating all pad colors
def FlushColorMap():
    MsgIDSetRGBPadLedState = 0x65
    dataOut = bytearray(4 * 64)
    bufOffs = 0
    for cMap in ColorMap:
        dataOut[bufOffs] = cMap.PadIndex
        dataOut[bufOffs + 1] = cMap.R
        dataOut[bufOffs + 2] = cMap.G
        dataOut[bufOffs + 3] = cMap.B
        bufOffs += 4
    SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)

# Retrieve the entire color map
def getColorMap():
    return ColorMap

# Set the color of a pad, either directly or using the buffer

# import inspect
# pdNav = [ 44, 45, 46, 47,
#           60, 61, 62, 63]


def SetPadColor(idx, col, dimFactor, bSaveColor=True, bUseBuffer=False, dimMult=2.5):

    # Get the caller's information from the stack
    # if(idx in pdNav):
    #     caller_info = inspect.stack()[1]
    #     caller_function = caller_info.function
    #     print(f"setcolor() was called by {caller_function}")

    if bUseBuffer:
        SetPadColorBuffer(idx, col, dimFactor, False)
    else:
        SetPadColorDirect(idx, col, dimFactor, bSaveColor, dimMult)

def scaleColorForFire(color, maxValue=127):
    """
    Scales RGB values to ensure the maximum value does not exceed 127.
    
    """
    r, g, b = nfxutils.ColorToRGB(color)
    max_rgb = max(r, g, b)
    
    if max_rgb > maxValue:
        # scale_factor = maxValue / max_rgb
        scale_factor = 127 / 255
        r = int(r * scale_factor)
        g = int(g * scale_factor)
        b = int(b * scale_factor)
    
    return nfxutils.RGBToColor(r, g, b), r, g, b

def scaleColor(color, maxValue=127):
    color, r, g, b = scaleColorForFire(color, maxValue)
    return color

def scaleRGB(r, g, b, maxValue=127):
    color = nfxutils.RGBToColor(r, g, b)
    newcolor, r, g, b = scaleColorForFire(color, maxValue)
    return r, g, b

# Adjust the color for the pad, ensuring it fits within the desired range and constraints
def AdjustedFirePadColor(color):
    return scaleColorForFire(color)
    # r, g, b = utils.ColorToRGB(color)    
    # reduceRed = min(1, r / max(b, 1))
    # reduceBlue = min(1, b / max(g, 1))
    # reduceRed = min(reduceRed, r / max(g, 1))
    # r = int(r * reduceRed) if reduceRed < 1 else r
    # b = int(b * reduceBlue) if reduceBlue < 1 else b
    # r //= 2
    # g //= 2
    # b //= 2
    # return utils.RGBToColor(r, g, b), r, g, b

# Set the color of a pad directly, with optional dimming and saving to the color map
def SetPadColorDirect(idx, col, dimFactor, bSaveColor=True, dimMult=2.5):
    if idx < 0 or idx > 63:
        return

    if col == -1:
        col = ColorMap[idx].PadColor
        dimFactor = ColorMap[idx].DimFactor

    col = nfxutils.getShade(col, colors.dimShades[dimFactor])

    # col = FLColorToPadColor(col, 1)

    if bSaveColor:
        ColorMap[idx].PadColor = col 
        ColorMap[idx].DimFactor = dimFactor
    
    newCol, r, g, b = AdjustedFirePadColor(col)

    # if dimFactor > 0:
    #     for _ in range(dimFactor):
    #         r = int(r / dimMult)
    #         g = int(g / dimMult)
    #         b = int(b / dimMult)

    SetPadRGB(idx, r, g, b)

# Set the RGB color of a specific pad by sending a MIDI message
def SetPadRGB(idx, r, g, b):
    MsgIDSetRGBPadLedState = 0x65
    dataOut = bytearray(4)
    dataOut[0] = idx
    dataOut[1] = r
    dataOut[2] = g
    dataOut[3] = b
    SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)

# Send a SysEx message to the MIDI device
def SendMessageToDevice(ID, dataLength, data):
    ManufacturerIDConst = 0x47
    DeviceIDBroadCastConst = 0x7F
    ProductIDConst = 0x43

    if not device.isAssigned():
        return
    
    msg = bytearray(7 + dataLength + 1)
    lsb = dataLength & 0x7F
    msb = (dataLength & (~0x7F)) >> 7

    msg[0] = midi.MIDI_BEGINSYSEX
    msg[1] = ManufacturerIDConst
    msg[2] = DeviceIDBroadCastConst
    msg[3] = ProductIDConst
    msg[4] = ID
    msg[5] = msb
    msg[6] = lsb
    msg[7:7+dataLength] = data[:dataLength]
    msg[7+dataLength] = midi.MIDI_ENDSYSEX
    device.midiOutSysex(bytes(msg))

_FixChannelColors = True

def PadColorToFLColor(padcolor):
    r, g, b, a = nfxutils.ColorToRGBA(padcolor)
    scaleby = 255/127 
    r = min(255, int(r * scaleby))
    g = min(255, int(g * scaleby))
    b = min(255, int(b * scaleby))
    a = min(255, a)
    return nfxutils.RGBAToColor(r, g, b, a)


# Convert an FL color to a pad-compatible color, with optional division for brightness adjustment
def FLColorToPadColor(FLColor, div=2):

    if FLColor == None:
        return 0

    color, r, g, b = scaleColorForFire(FLColor)
    return color 

    # padcolor = FLColor & 0xFFFFFF
    # r = (padcolor >> 16) & 0xFF
    # g = (padcolor >> 8) & 0xFF
    # b = padcolor & 0xFF

    # # if _FixChannelColors:
    # #     r, g, b = [0 if x == 20 else x for x in (r, g, b)]

    # return nfxutils.RGBToColor(r, g, b)

# Transition the color of a pad from a start color to an end color over a specified duration
def TransitionPadColor(idx, start_col, end_col, duration=1.0, steps=10):
    start_r, start_g, start_b = nfxutils.ColorToRGB(start_col)
    end_r, end_g, end_b = nfxutils.ColorToRGB(end_col)

    delta_r = (end_r - start_r) / steps
    delta_g = (end_g - start_g) / steps
    delta_b = (end_b - start_b) / steps

    for step in range(steps + 1):
        r = int(start_r + delta_r * step)
        g = int(start_g + delta_g * step)
        b = int(start_b + delta_b * step)
        col = nfxutils.RGBToColor(r, g, b)
        SetPadColor(idx, col, 0)
        time.sleep(duration / steps)


def TestColorMap():
    for i in range(64):
        flushNow = False # (i == 63)
        SetPadColorBuffer(i, colors.cRed, 0, flushNow, True)
        FlushColorMap()
    time.sleep(5.0)
    for i in range(64):
        flushNow = (i == 63)
        SetPadColorBuffer(i, colors.cGreen, 0, flushNow, True)
    time.sleep(5.0)
    for i in range(64):
        flushNow = (i == 63)
        SetPadColorBuffer(i, colors.cBlue, 0, flushNow, True)


