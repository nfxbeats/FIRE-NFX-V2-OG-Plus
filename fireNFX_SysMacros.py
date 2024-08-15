from midi import *
import transport
import ui
import general
import channels 
from fireNFX_Classes import TnfxMacro
from fireNFX_Colors import *
from fireNFX_DefaultSettings import Settings
from fireNFX_Utils import getShade, shDark, shDim, shLight, shNorm, NavigateFLMenu
from fireNFX_PadDefs import pdMacroNav, pdMacros

# code for macros
def Undo():
    if(Settings.UNDO_STYLE == 0):
        general.undoUp()
    else:
        general.undo()    

def ZoomSelection(zoomVal = Settings.DBL_TAP_ZOOM):
    zStr = 'DDDDDDDD'[0:zoomVal]
    NavigateFLMenu(',DRDDDDDR,DD,{}E'.format(zStr) )

def Articulate():
    NavigateFLMenu(',R,DR,DDDE,E')    

def TransposePROctaveUp():
    NavigateFLMenu(',RR,DDDDDDDDDDDE')    

def TransposePROctaveDown():
    NavigateFLMenu(',RR,DDDDDDDDDDDDE')    

def QuickQuantize():
    #NavigateFLMenu(',R,DR,DDDDE')    
    channels.quickQuantize(channels.channelNumber())

def QuickPRFix():
    QuickQuantize()
    Articulate()
    

def ShowScriptOutputWindow():
    ui.showWindow(widChannelRack)       # make CR the active window so it pulls up the main menu
    NavigateFLMenu(',LLLLDDDDDDDDDDE')  # series of keys to pass

def CloseAll():
    transport.globalTransport(FPT_F12, 1)  # close all...
    if(Settings.REOPEN_WINDOWS_AFTER_CLOSE_ALL):
        ui.showWindow(widPlaylist)
        ui.showWindow(widMixer)
        ui.showWindow(widBrowser)
        ui.showWindow(widChannelRack)

def Rename():
    transport.globalTransport(FPT_F2, 1)

# BUILT-IN MACROS DEFINED HERE
# 
macCloseAll = TnfxMacro("CloseAll", cOff, CloseAll) # special 
macTogChanRack = TnfxMacro("ChanRack", cCyan) # internal
macTogPlaylist = TnfxMacro("Playlist", cCyan) # internal 
macTogMixer = TnfxMacro("Mixer", cCyan) # internal
# 
macUndo = TnfxMacro("Undo", getShade(cYellow, shNorm), Undo )
macCopy = TnfxMacro("Copy", getShade(cBlue, shLight), ui.copy)
macCut = TnfxMacro("Cut", getShade(cMagenta, shNorm), ui.cut )
macPaste = TnfxMacro("Paste", getShade(cGreen, shLight), ui.paste)

# misc
macShowScriptWindow         = TnfxMacro("Script Window", cWhite, ShowScriptOutputWindow)
macZoom                     = TnfxMacro("Zoom", cWhite, ZoomSelection)
macRename                   = TnfxMacro("Rename", cPurple, Rename)

#Piano Roll
macQuickQuantize            = TnfxMacro("Quantize", getShade(cGreen, shLight), QuickQuantize)
macQuickPRFix               = TnfxMacro("Quant/Art", getShade(cGreen, shNorm), QuickPRFix)
macTransposePROctaveUp      = TnfxMacro("Oct Up", getShade(cBlue, shLight), TransposePROctaveUp)
macTransposePROctaveDown    = TnfxMacro("Oct Down", getShade(cBlue, shDark), TransposePROctaveDown)

PianoRollMacros = [macQuickQuantize, macQuickPRFix, macTransposePROctaveUp, macTransposePROctaveDown]

# master macro list
DefaultMacros = [macCloseAll,  macTogChanRack, macTogPlaylist, macTogMixer, 
                  macUndo,      macCopy,        macCut,         macPaste ]

MacroList = DefaultMacros
CustomMacros = []

if(len(Settings.DEFAULT_MACROS) > 0):
    MacroList.clear()
    for idx, pad in enumerate(pdMacros):
        if(idx < len(Settings.DEFAULT_MACROS)):
            MacroList.append(Settings.DEFAULT_MACROS[idx])
        elif(idx < len(DefaultMacros)):
            MacroList.append(DefaultMacros[idx])
        else:
            MacroList.append(TnfxMacro('', cOff, None)) # empty macro

if(len(Settings.CUSTOM_MACROS) == 0):
    for idx, pad in enumerate(pdMacroNav):
        if(idx < len(Settings.CUSTOM_MACROS)):
            CustomMacros.append(Settings.CUSTOM_MACROS[idx])
        else:
            CustomMacros.append(TnfxMacro('', cOff, None)) # empty macro


UserMacros = {}
try:
    from fireNFX_UserMacros import * 
    UserMacros = MyMacros 
    print('User macros loaded.')
except ImportError:
    print('User macros NOT found.')# Failed to import - assume they don't have custom macros 





