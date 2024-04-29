# fireNFX_Globals
from fireNFX_DefaultSettings import * 
from fireNFX_Defs import * 
from fireNFX_Utils import * 
from fireNFX_Classes import * 

#region globals

dimDim = Settings.DIM_DIM
dimNormal = Settings.DIM_NORMAL
dimBright = Settings.DIM_BRIGHT
Settings.DEV_MODE = -1 

debugprint = Settings.SHOW_PRN
rectTime = Settings.DISPLAY_RECT_TIME_MS
ShiftHeld = False
FLChannelFX = False
AltHeld = False
PatternCount = 0
CurrentPattern = -1
PatternPage = 1
MixerPage = 1
PlaylistPage = 1
ChannelCount = 0
CurrentChannel = -1
# _PreviousChannel = -1
isAltMode = False
isShiftMode = False 
ChannelPage = 1
KnobMode = 0
Beat = 1
PadMap = list()
PatternMap = list()
PatternSelectedMap = list()
ChannelMap = list()
ChannelSelectedMap = list()
PlaylistMap = list()
PlaylistSelectedMap = list()
MarkerMap = list()
ProgressMapSong = list()
MixerMap = list()
OrigColor = 0x000000
NewColor = 0x000000
BlinkTimer = False
BlinkLast = 0.0
BlinkSeconds = 0.2
ToBlinkOrNotToBlink = False

showText = ['OFF', 'ON']

WalkerChanIdx = -1

#display menu
ShowMenu = 0
menuItems = []
chosenItem = 0
menuItemSelected = chosenItem
menuHistory = []
MAXLEVELS = 2
menuBackText = '<back>'
progressZoom = [0,1,2,4]
progressZoomIdx = 1

LOADED_PLUGINS = {}

DirtyChannelFlags = 0

HW_CustomEvent_ShiftAlt = 0x20000

lyBanks = 0
lyStrips = 1
Layouts = ['Banks', 'Strips']

#notes/scales
ScaleIdx = Settings.SCALE
ScaleDisplayText = ""
ScaleNotes = list()
lastNote =-1
NoteIdx = Settings.NOTE_NAMES.index(Settings.ROOT_NOTE)
NoteRepeat = False
NoteRepeatLengthIdx = BeatLengthsDefaultOffs
isRepeating = False

SnapIdx = InitialSnapIndex
OctaveIdx = OctavesList.index(Settings.OCTAVE)
ShowChords = False
ChordNum = -1
ChordInvert = 0 # 0 = none, 1 = 1st, 2 = 2nd
ChordTypes = ['Normal', '1st Inv', '2nd Inv']
Chord7th = False
VelocityMin = 100
VelocityMax = 126

#GS
AccentEnabled = Settings.ACCENT_ENABLED  #GS
AccentCurveShape = 0.4  #GS - The value should be in a range between 0.1 (very steep) and 1.0 (linear). 
AccentVelocityMin = 32   #GS - minimum velocity on the Fire is 32

DebugPrn = True
DebugMin = lvlD


# list of notes that are mapped to pads
NoteMap = list()
NoteMapDict = {}
#_FPCNotesDict = {}

SongPos = 0
SongLen  = -1
ScrollTo = True # used to determine when to scroll to the channel/pattern

lastHints = []
MAX_HINTS = 20
MONITOR_HINTS = False
SHOW_AUDIO = True 
IsOnIdleRefreshing = False
peakCheckTime = None 
pressCheckTime = None
PEAKTIME = 0.0
LONG_PRESS_DELAY = 0.125
LONG_PRESS_DETECT = 0.5
pressisRepeating = False

SHOW_PROGRESS = True
FollowChannelFX = True 
lastFocus = -1
lastWindowID = -1 # only tracks the basic windows with widXXXX values

windowIDNames = {
            widMixer: 'Mixer', 
            widChannelRack: 'Channel Rack', 
            widPlaylist: 'Playlist', 
            widPianoRoll: 'Piano Roll',
            widBrowser: 'Browser', 
            widPlugin: 'Plugin', 
            widPluginEffect: 'Plugin Effect', 
            widPluginGenerator: 'Plugin/Generator',
            -1: 'Unknown'
            }

tempMsg = ''
tempMsg2 = ''
prevCtrlID = 0
proctime = 0
DoubleTap = False
isPMESafe = True
isModalWindowOpen = False

resetAutoHide = False
prevNavSet = -1

menuAssign = TnfxMenuItems('Assign Knobs', 0)
menuAssign.addSubItem( TnfxMenuItems('Knob-1') )
menuAssign.addSubItem( TnfxMenuItems('Knob-2') )
menuAssign.addSubItem( TnfxMenuItems('Knob-3') )
menuAssign.addSubItem( TnfxMenuItems('Knob-4') )
menuParams = TnfxMenuItems('Browse Params', 0)
menus = []
menus.append(menuAssign)
menus.append(menuParams)

modePattern = TnfxPadMode('Pattern', MODE_PATTERNS, IDStepSeq, False)
modePatternAlt = TnfxPadMode('Pattern Alt', MODE_PATTERNS, IDStepSeq, True)
modeNote = TnfxPadMode('Note', MODE_NOTE, IDNote, False)
modeNoteAlt = TnfxPadMode('Note Alt', MODE_NOTE, IDNote, True)
modeDrum = TnfxPadMode('Drum', MODE_DRUM, IDDrum, False)
modeDrumAlt = TnfxPadMode('Drum Alt', MODE_DRUM, IDDrum, True)
modePerform = TnfxPadMode('Perform', MODE_PERFORM, IDPerform, False)
modePerformAlt = TnfxPadMode('Perform Alt', MODE_PERFORM, IDPerform, True)    
PadMode = modePattern 

arp1 = 1446
arp2= 1232
arp4 = 1024
arp8 = 820
arp16 = 648
arp32 = 502 # 450
arpTimes = {'Beat': arp1, 'Half-Beat':arp2, '4th-Beat':arp4, '8th-Beat':arp8, '16th-Beat':arp16, '32nd-Beat': arp32}

PerformanceBlockMap = []
PerformanceBlocks = {}
PerfTrackOffset = 0 

lastSlotIdx = -1
ParamPadMapDict = {}

UserKnobModes = [KM_USER0, KM_USER1, KM_USER2, KM_USER3]
UserModeLEDValues = [0, 4, 8, 12]
UserKnobModeIndex = 0

turnOffMetronomeOnNextPlay = False 

lastBrowserFolder = ''

ShiftLock = False 
AltLock = False 

lastKnobCtrlID = -1
shuttingDown = False

ChromaticOverlay = True        

FPCChannels = []

lastMixerTrack = -1

WalkerName = 'Walker'    

#endregion 
