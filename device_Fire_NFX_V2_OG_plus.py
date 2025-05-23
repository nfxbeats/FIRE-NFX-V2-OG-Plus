# name=FIRE-NFX-V2-OG+
# supportedDevices=FL STUDIO FIRE
#
# author: Nelson F. Fernandez Jr. <nfxbeats@gmail.com>
#
# import sys 
VERSION = "2.2025.0109"
print('FIRE_NFX_V2_OG+.VERSION ' + VERSION)   

from fireNFX_Persist import *
from fireNFX_Defs import IDShift, IDAlt, IDRec
from FIRE_NFX_OG_plus import TFire
from FIRE_NFX_V2 import TFireNFX
from fireNFX_DefaultSettings import Settings

FIREMODE = 0
SHIFTHELD = False
ALTHELD = False

FireOG = TFire()        # the OG+ version
FireNFX = TFireNFX()    # the NFX version
Fire = FireNFX          # set the default 

if Settings.STARTINOG:
    Fire = FireOG


def CallEx(func, *args, **kwargs):
    try:
        # Execute the provided function with arguments
        return func(*args, **kwargs)
    except Exception as e:
        # Get the traceback object from the exception
        tb = e.__traceback__
        
        # Traverse the traceback to find the last frame
        while tb.tb_next:
            tb = tb.tb_next
        
        # Extract details from the traceback frame
        filename = tb.tb_frame.f_code.co_filename
        line_number = tb.tb_lineno
        func_name = tb.tb_frame.f_code.co_name
        
        # Print the exception details
        print("======================================================")
        print(f"An error occurred: {e}")
        print(f"Exception type: {type(e).__name__}")
        print(f"File: {filename}")
        print(f"Line number: {line_number}")
        print(f"Function name: {func_name}")
        print("======================================================")


def ToggleFireMode():
    global FIREMODE
    global Fire 

    if(FIREMODE == 0):
        print('changing to FIRE-OG+ mode')
        Fire = FireOG
        FIREMODE = 1
    else:
        print('changing to FIRE-NFX=V2 mode')
        Fire = FireNFX
        FIREMODE = 0 

def OnInit():
    CallEx(Fire.OnInit)

def OnDeInit():
    Fire.OnDeInit()

def OnDisplayZone():
    Fire.OnDisplayZone()

def OnIdle():
    Fire.OnIdle()

def OnMidiIn(event):
    global SHIFTHELD
    global ALTHELD

    ctrlID = event.data1


    # isModalWindowOpen = (event.pmeFlags & PME_System_Safe == 0)
    # isPMESafe = (event.pmeFlags & PME_System != 0)
    # if(not isPMESafe):
    # print('MidiIn PME Flags:', event.pmeFlags, '      PME Safe:', isPMESafe, '         Modal Window:', isModalWindowOpen)
    #     event.handled = True
    #     return 


    if(ctrlID == IDShift):
        SHIFTHELD = (event.data2 > 0)
    elif(ctrlID == IDAlt):
        ALTHELD = (event.data2 > 0)

    if(ALTHELD) and (IDRec == ctrlID and event.data2 == 0): # on release
        event.handled = True
        OnDeInit()
        ToggleFireMode()
        OnInit()
    else:
        Fire.OnMidiIn(event)

def OnMidiMsg(event):
    # isModalWindowOpen = (event.pmeFlags & PME_System_Safe == 0)
    # isPMESafe = (event.pmeFlags & PME_System != 0)
    # # if(not isPMESafe):
    # print('MidiMsg PME Flags:', event.pmeFlags, '      PME Safe:', isPMESafe, '         Modal Window:', isModalWindowOpen)
    Fire.OnMidiMsg(event)

def OnRefresh(Flags):
    CallEx(Fire.OnRefresh, Flags) #Fire.OnRefresh(Flags)

def OnUpdateLiveMode(LastTrackNum):
    Fire.OnUpdateLiveMode(1, LastTrackNum)

def OnUpdateBeatIndicator(Value):
    Fire.OnUpdateBeatIndicator(Value)

def OnProjectLoad(status):
    print('Project Loading...', status)
    Fire.OnProjectLoad(status)

def OnDoFullRefresh():
    Fire.OnDoFullRefresh()

def OnDirtyChannel(chan, flags):
    Fire.OnDirtyChannel(chan, flags)

def OnSendTempMsg(msg, duration):
    Fire.OnSendTempMsg(msg, duration)    

def OnNoteOn(event):
    Fire.OnNoteOn(event)

def OnNoteOff(event):
    Fire.OnNoteOff(event)

def OnSysEx(event):
    Fire.OnSysEx(event)

def OnControlChange(event):
    Fire.OnControlChange(event)

def OnProgramChange(event):
    Fire.OnProgramChange(event)

def OnPitchBend(event):
    Fire.OnPitchBend(event)

def OnKeyPressure(event):
    Fire.OnKeyPressure(event)

def OnChannelPressure(event):
    Fire.OnChannelPressure(event)

def OnMidiOutMsg(event):
    Fire.OnMidiOutMsg(event)

def OnDirtyMixerTrack(track):
    Fire.OnDirtyMixerTrack(track)

def OnFirstConnect():
    Fire.OnFirstConnect()

def OnWaitingForInput():
    Fire.OnWaitingForInput() 



