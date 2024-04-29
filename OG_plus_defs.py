from OG_plus_harmonicScales import * 

#globals  
FLFireDeviceName = 'Akai FL Studio Fire'
PadsW = 16
PadsH = 4
PadsStride = 16
ManufacturerIDConst = 0x47
DeviceIDBroadCastConst = 0x7F
ProductIDConst = 0x43

#system messages
SM_SetAsSlave = 0x01
SM_MasterDeviceChanRackOfs = 0x02
SM_MasterDeviceChanStartPos = 0x03
SM_MasterDeviceSetOfs = 0x04
SM_SlaveDeviceSetOfs = 0x05
SM_SlaveDeviceStartPos = 0x06
SM_SlaveDeviceRackOfs = 0x07
SM_SlaveDeviceModeLayout = 0x08
SM_UpdateLiveMode = 0x09
SM_SlaveUpdateDisplayZone = 0x0A
SM_SetAsSingle = 0x0B

StartingNote = 36 # top/left pad
TextTimerInterval = 60 # number of idle calls before hiding a timed text
BlinkSpeed = 10 # number of idle calls before blinking a button/pad (full cycle = double of that)
HeldButtonRetriggerTime = 10 # default number of idle calls before a held buttons retrigger it's def (can reduce over time)
# modes
ModeStepSeq = 0
ModeNotes = 1
ModeDrum = 2
ModePerf = 3
ModeAnalyzerNone = 5
ModeAnalyzerMono = 6
ModeAnalyzerLeft = 7
ModeAnalyzerRight = 8
ModePadVisFirst = ModeAnalyzerMono
ModePadVisLast = ModeAnalyzerRight
ModeNamesT =('Step seq mode', 'Note mode', 'Drum mode', 'Performance mode', 'Analyzer - Left', 'Analyzer - Right', 'Analyzer - Mono')
ModeVisNamesT = ('Visualizer off', 'Spectrogram', 'Peaks Left', 'Peaks Right')
ScreenModeNamesT = ('Visualizer off', 'Peak Level')

# screen vis modes
ScreenModeNone = 0
ScreenModePeak = 1
ScreenModeScope = 2
ScreenModeFirst = ScreenModePeak
ScreenModeLast = ScreenModePeak

# knobs modes
KnobsModeChannelRack = 0
KnobsModeMixer = 1
KnobsModeUser1 = 2
KnobsModeUser2 = 3
KnobsModeVis = KnobsModeUser1
KnobsModesNamesT = ('Channel rack', 'Mixer', 'User 1', 'User 2')
# notes modes
NoteModeDualKeyb = 0
NoteModeLast = HARMONICSCALE_LAST + 1

# drum modes
DrumModeFPC = 0
DrumModeFPCCenter = 1
DrumModeSlicex = 2
DrumModeOmni = 3

DrumModeLast = 3
DrumModesNamesT = ('FPC Left', 'FPC Center', 'Slicex', 'Omni channel')

# Message IDs (from PC to device)
MsgIDGetAllButtonStates = 0x40
MsgIDGetPowerOnButtonStates = 0x41
MsgIDSetRGBPadLedState = 0x65
MsgIDSetManufacturingData = 0x79
MsgIDDrawScreenText = 0x08
MsgIDDrawBarControl = 0x09
MsgIDFillOLEDDiplay = 0x0D
MsgIDSendPackedOLEDData = 0x0E
MsgIDSendUnpackedOLEDData = 0x0F

# Note/CC values for controls
IDKnobMode = 0x1B # shouldn't it be 0x1A ? (doc says 0x1B for outbound & 0x1A for inbound...)
IDJogWheel = 0x76
IDJogWheelDown = 0x19
IDPatternUp = 0x1F
IDPatternDown = 0x20
IDBrowser = 0x21
IDBankL = 0x22
IDBankR = 0x23
IDMute1 = 0x24
IDMute2 = 0x25
IDMute3 = 0x26
IDMute4 = 0x27
IDTrackSel1 = 0x28
IDTrackSel2 = 0x29
IDTrackSel3 = 0x2A
IDTrackSel4 = 0x2B
IDStepSeq = 0x2C
IDNote = 0x2D
IDDrum = 0x2E
IDPerform = 0x2F
IDShift = 0x30
IDAlt = 0x31
IDPatternSong = 0x32
IDPlay = 0x33
IDStop = 0x34
IDRec = 0x35
IDKnob1 = 0x10
IDKnob2 = 0x11
IDKnob3 = 0x12
IDKnob4 = 0x13

IdxStepSeq = 14
IdxNote = 15
IdxDrum = 16
IdxPerform = 17
IdxShift = 18
IdxAlt = 19
IdxPatternSong = 20
IdxPlay = 21
IdxStop = 22
IdxRec = 23
IdxButtonLast = 23

# Pads
PadFirst = 0x36
PadLast = 0x75

# Colors
DualColorOff = 0x00
DualColorHalfBright1 = 0x01
DualColorHalfBright2 = 0x02
DualColorFull1 = 0x03
DualColorFull2 = 0x04

SingleColorOff = 0x00
SingleColorHalfBright = 0x01
SingleColorFull = 0x02

# Text settings
Font6x8 = 0
Font6x16 = 1
Font10x16 = 2
Font12x32 = 3
JustifyLeft = 0
JustifyCenter = 1
JustifyRight = 2
ScreenDisplayDelay = 2 # delay (in ms) required to access the screen (seems slow)

EKRes = 1 / 64 # endless knobs resolution

# Multi devices modes
MultiDev_Single = 0 # single device mode
MultiDev_Master = 1
MultiDev_Slave = 2

# slaved device layouts (relative to the master's device position)
SlaveModeLayout_Right = 0
SlaveModeLayout_Bottom = 1
SlaveModeLayout_BottomRight = 2

SlaveModeLayout_Last = 2
SlaveModeLayoutNamesT = ('Right', 'Bottom', 'Bottom right')
SlaveModeLayoutXShift = (16, 0, 16)
SlaveModeLayoutYShift = (0, 4, 4)

AnalyzerBars = 0
AnalyzerPeakVol = 1

TextScrollPause = 10
TextScrollSpeed = 2
TextDisplayTime = 4000

TimedTextRow = 1
FPSRow = 3
FireFontSize = 16
TextOffset = -4
TextRowHeight = 20

Idle_Interval = 100
Idle_Interval_Max = 8

ScreenActiveTimeout = 30 # seconds to keep screen active (screen has its own timeout which will kick in after this)
ScreenAutoTimeout = 10

tlNone = 1
tlText = 1 << 1
tlBar = 1 << 2
tlMeter = 1 << 3

QF_Left = 0
QF_Right = 1
QF_Center = 2
QF_HMask = 3
QF_Top = 0
QF_Default = QF_Left | QF_Top
QF_PixelSnap = 1 << 22

RoundAsFloorS = -0.499999970197677612

