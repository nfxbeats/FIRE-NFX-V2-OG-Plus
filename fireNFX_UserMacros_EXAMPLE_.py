# This is a sample user macro file that will allow you set some custom macros.
#
# To use this file, it must be renamed to exactly: "fireNFX_UserMacros.py"
# and exist in the same folder as the other scripts.
#
# Be sure to only edit the part below where marked "OK TO EDIT..."
# 
# DO NOT CHANGE THESE LINES:
from midi import *
import device
import channels
import patterns
import utils
import time
import ui 
import transport 
import mixer 
import general
import plugins 
import playlist
import arrangement
from fireNFX_Classes import TnfxMacro
from fireNFX_Colors import *
from fireNFX_DefaultSettings import Settings
from fireNFX_Utils import getShade, shDark, shDim, shLight, shNorm, NavigateFLMenu
from fireNFX_PadDefs import pdMacroNav, pdMacros, pdAllPads
MyMacros = {}



# OK to edit after this line

# macro functions are written in this section and assigned and called
# in the next section.
#
# define all macro function with a prefix of "um" for example umCloseAll or umRename
#
def umCloseAll():
    transport.globalTransport(FPT_F12, 1)  # close all...

def umTempoUp():
    transport.globalTransport(FPT_TempoJog, 10) # jogs in 0.1 bpm increments, so 10 = 1 BPM
    ui.setHintMsg("Tempo: " + str(mixer.getCurrentTempo()/1000))
    
def umTempoDown():
    transport.globalTransport(FPT_TempoJog, -10) # jogs in 0.1 bpm increments, so 10 = 1 BPM
    ui.setHintMsg("Tempo: " + str(mixer.getCurrentTempo()/1000))

def umRename():
    transport.globalTransport(FPT_F2, 1)

# macro and pad assignment:
#
# the number in the [] is the pad number from 0 to 63. 0 is top left, 63 is lower right 
#
# The basic syntax is: 
#
#       MyMacros[<pad number>] = TnfxMacro("<name>", <color>, <function>)
#
MyMacros[0]  = TnfxMacro("Close All", 0x33DFE0, umCloseAll)
MyMacros[7]  = TnfxMacro("Tempo Up", getShade(cGreen, shNorm), umTempoUp)
MyMacros[8]  = TnfxMacro("Tempo Down", getShade(cGreen, shLight), umTempoDown)
MyMacros[63] = TnfxMacro("Rename", cOrange, umRename)

