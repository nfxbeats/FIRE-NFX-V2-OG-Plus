# name=AKAI FL Studio Fire OG+ v3
# url=https://forum.image-line.com/viewtopic.php?p=1496543#p1496543
# receiveFrom=AKAI FL Studio Fire

import patterns
import channels
import mixer
import device
import transport
import arrangement
import general
import launchMapPages
import playlist
import ui
import screen
import plugins

from midi import *
import utils
import time
import OG_plus_harmonicScales
import OG_plus_nfx_Helpers 
from fireNFX_Defs import * 
from OG_plus_defs import * 

class TAccentModeParams:
    def __init__(self, pitch, vel, pan, modx, mody):
        self.Pitch = pitch
        self.Vel = vel
        self.Pan = pan
        self.ModX = modx
        self.ModY = mody

class TiniKeyRecord:
    def __init__(self, name, prt):
        self.Name = name
        self.prt = prt

class TiniKeySection:
    def __init__(self, name, keys):
        self.Name = name
        self.keys = keys

class TMidiEvent:
    def __init__(self):
        self.handled = False
        self.timestamp = 0
        self.status = 0
        self.data1 = 0
        self.data2 = 0
        self.port = 0
        self.isIncrement = 0
        self.res = 0.0
        self.inEV = 0
        self.outEV = 0
        self.midiId = 0
        self.midiChan = 0
        self.midiChanEx = 0
        self.SenderId = 0
        self.pmeFlags = 0
        self.sysexLen = 0
        self.sysexData = 0

class TFire():

    def __init__(self):
        self.FPCNoteMap = {}
        self.ChanRackOfs = 0
        self.ChanRackStartPos = 0
        self.TrackOfs = 0
        self.ClipOfs = 0
        self.BtnT = bytearray(IdxButtonLast) # see buttons indexes above
        self.BtnLastClip = [0 for x in range(PadsH * PadsW)]
        for n in range(0, len(self.BtnLastClip)):
            self.BtnLastClip[n] = utils.TClipLauncherLastClip(MaxInt, MaxInt, MaxInt)
        self.BtnMap = [0] * 64
        self.PlayingNotes = bytearray(0)
        self.PlayingChannels = [] # for "omni" drum mode
        self.CurStep = 0 # current playing step when FL plays
        self.MuteBtnStates = [False] * 4 # to know if mute buttons are held
        self.DidTweakLooping = False
        self.CurrentNoteGrid = [[0 for x in range(PadsH)] for y in range(PadsW)]
        self.SlavedDevices = {}   # port -> mode layout
        self.MultiDeviceMode = MultiDev_Single
        self.SlaveModeLayout = 0 # see SlaveModeLayout_ constants
        
        self.SlaveLayoutSelectionMode = False # when True, shows a menu to select the slave layout
        self.AnalyzerMode = 0
        self.AnalyzerChannel = 0
        self.AnalyzerFlipX = False
        self.analyzerFlipY = False
        self.AnalyzerScrollX  = False
        self.AnalyzerScrollY = False
        self.CurrentMode = 0
        self.NonVisMode = 0
        self.OldMode = 0
        self.OldMode = 0 # see mode constants
        self.AccentMode = False # True when "accent" is enabled in step seq mode
        self.AccentParams = TAccentModeParams(0, 0, 0, 0, 0) # default param values of steps in accent mode
        self.OverviewMode = False # True when in "overview" in perf mode
        self.BrowserMode = False # True when "browser" is enabled
        self.BrowserShouldClose = False
        self.BrowserShouldAutoHide = False # to restore the state of the browser when exiting browser mode
        self.JogWheelPushed = False # True when holding down the jogwheel
        self.JogWheelHeldTime = 0.0 # time (number of idle calls) during which the Jog button was held
        self.GridBtnHeldTime = 0 # time (number of idle calls) during which the grid buttons were held
        self.GridBtnHeldTriggerTime = 0 # time before it retriggers the same action (reduces the more you hold)
        self.GridUpBtnHeld = False
        self.GridDownBtnHeld = False # True if either grid buttons are pressed
        self.PatBtnHeldTime = 0 # time (number of idle calls) during which the pattern up | down button was held
        self.PatUpBtnHeld = False
        self.PatDownBtnHeld = False # True if either (or both) pat up | pat down buttons are held
        self.PatBtnHeldTriggerTime = 0 # time before it retriggers the same action (reduces the more you hold)
        self.CurrentKnobsMode = 0 # active mode for knobs (CR, mixer, user1, user2)
        self.CurrentMixerTrack = 0 # mixer track being tweaked by the knobs
        self.CurrentNoteMode = 0
        self.OldNoteMode = 0 # for notes mode (dual keyboards | scales)
        self.CurrentDrumMode = 0 # for drum mode (FPC, Slicex, etc)
        self.TopText = '' # text at the top of the screen
        self.DisplayedText = '' # central text (bigger)
        self.KeyOffset = 36 # for notes mode
        self.TextTimer = 0 # to make the text disappear after a while
        self.TopTextTimer = 0.0
        self.DisplayZoneTimer = 0 # to make the self.Display zone disappearing after using the jog
        self.BlinkTimer = 0 # to make buttons blink
        self.TrackSelIdleValue = 0 # for the idle anim of the track selectors (when "receive notes from" is active)
        self.HeldPadsChanged = False # True when held pads were tweaked via knobs/jogwheel (to avoid switching their state after changing a param)
        self.ShiftHeld = False
        self.AltHeld = False # True when holding shift | alt buttons
        self.LayoutSelectionMode = False # True when selection the layout in notes mode
        self.MixerTrackSelectionMode = False # True when assigning a channel's mixer track
        self.TouchingKnob = False # Is the user currently handling a knob?
        self.KnobTouched = 0 # The knob the user is currently touching
        self.UHP = 0
        self.UHC = 0
        self.UHL = 0 # Stored history (undo) positions
        self.ChangeFlag = False # Set if the user changes a step parameter
        self.MasterDeviceChanRackOfs = 0
        self.MasterDeviceChanRackStartPos = 0
        self.MasterDeviceClipOfs = 0
        self.MasterTrackOfs = 0
        self.MasterClipOfs = 0

        self.bmpTimer = 0 #TDateTime
        self.NoteColorSet = 0
        self.LastRawData1 = 0
        self.LastRawData2 = 0

        self.LastIdleSec = 0
        self.IdleFPS = 0
        self.ScreenMode = ScreenModeNone
        self.KnobsV = [0] * 4
        self.HeldPads = bytearray(0)
        self.PlayingPads = []

        #todo def GetEventForPad(Device: TMIDIInDevice_Fire PadNum): pRecEvent
        #todo def GetTimeForPad(Device: TMIDIInDevice_Fire PadNum):
        self.KeyColorsDefault = [[0xFF4000, 0xFFFFFF, 0x0F0F0F, 0x7F7F7F, 0x9CFF00, 0x00FF00, 0x80FF00, 0xFFFF00, 0xFF4000, 0x000080, 0x0060FF, 0x000080],  [0x00FFFF, 0xFFFFFF, 0x0F0F0F, 0x7F7F7F, 0xFF4000, 0x00FFFF, 0x7FFFFF, 0xFFFFFF, 0xFF0000, 0x000080, 0x0060FF, 0x000080]]
        self.KeyColors = [[0 for x in range(7 + PadsH+ 1)] for y in range(2)]
        self.FLFirePadBrightness = 0
        self.FLFirePadSaturation = 0

        self.FLFireDeviceCount = 0
        self.IdleDeviceCount = 0
        self.AnalyzerHue = 0.0

    def LoadKeyColors(self):
        for n in range(0, 2):
            for i in range(0, 7 + PadsH+ 1):
                self.KeyColors[n][i] = self.KeyColorsDefault[n][i]

    def OnInit(self):
        self.FLFireDeviceCount += 1
        if self.FLFireDeviceCount == 1: # first (or only) FL Fire unit. Load the settings
            self.LoadKeyColors()
            self.FLFirePadBrightness = 96
            self.FLFirePadSaturation = 101
            self.FromToReg(False)

        self.ScreenMode = ScreenModeNone
        self.CurStep = -1
        self.ChanRackOfs = 0
        self.ChanRackStartPos = 0
        self.TrackOfs = 0
        self.ClipOfs = 0
        self.KeyOffset = 36
        self.CurrentMode = ModeStepSeq
        self.OldMode = 128 # make sure it's invalid not to miss the first update
        self.CurrentKnobsMode = KnobsModeChannelRack
        self.CurrentNoteMode =NoteModeDualKeyb
        self.OldNoteMode = -1
        self.CurrentDrumMode = DrumModeFPC #DrumModeFPCCenter
        self.TopText = 'FL Studio'
        self.DisplayedText = ''
        self.ShiftHeld = False
        self.AltHeld = False
        self.OverviewMode = False
        self.JogWheelPushed = False
        self.JogWheelHeldTime = 0
        self.BrowserMode = False
        self.BrowserShouldClose = False
        self.BrowserShouldAutoHide = False
        self.TextTimer = 0
        self.TopTextTimer = 0.0
        self.DisplayZoneTimer = 0
        self.BlinkTimer = 0
        self.HeldPadsChanged = False
        self.TrackSelIdleValue = 0
        self.CurrentMixerTrack = 0
        self.MultiDeviceMode = MultiDev_Single
        self.SlaveModeLayout = SlaveModeLayout_Right # to the right by default
        self.MasterDevice = 0
        self.SlavedDevices = {}
        self.TouchingKnob = False
        self.KnobTouched = 0
        self.PatBtnHeldTime = 0
        self.PatUpBtnHeld = False
        self.PatDownBtnHeld = False
        self.PatBtnHeldTriggerTime = HeldButtonRetriggerTime
        self.GridBtnHeldTime = 0
        self.GridUpBtnHeld = False
        self.GridDownBtnHeld = False
        self.GridBtnHeldTriggerTime = HeldButtonRetriggerTime // 2
        for n in range(0, 4):
            self.MuteBtnStates[n] = False
        self.DidTweakLooping = False
        self.AccentParams = TAccentModeParams(DotNote_Default, 100, 64, 127, 0)
        self.DisplayWidth = 128
        self.DisplayHeight = 64

        for n in range(0, len(self.BtnT)):
            self.BtnT[n] = 0
        self.ClearBtnMap()
        self.ClearAllButtons()
        launchMapPages.createOverlayMap(1, 8, PadsW, PadsH)
        for y in range(0, PadsH):
            for x in range(0, PadsW):
                launchMapPages.setMapItemTarget(-1, y * PadsW + x, y * PadsStride + x)

        screen.init(self.DisplayWidth, self.DisplayHeight, TextRowHeight, FireFontSize, 0xFFFFFF, 0)
        sysexHeader = int.from_bytes(bytes([MIDI_BEGINSYSEX, ManufacturerIDConst, DeviceIDBroadCastConst ,ProductIDConst, MsgIDSendPackedOLEDData]), byteorder='little')
        screen.setup(sysexHeader, ScreenActiveTimeout, ScreenAutoTimeout, TextScrollPause, TextScrollSpeed, TextDisplayTime)
        self.BgCol = 0x000000
        self.FgCol = 0xFFFFFF
        self.DiCol = 0xFFFFFF
        screen.fillRect(0, 0, self.DisplayWidth, self.DisplayHeight, 0)

        self.bmpTimer = time.time()
        self.Reset()
        self.SetOfs(self.TrackOfs, self.ClipOfs)
        self.ClearDisplay()

        # OG Pattern lights  
        # self.SendCC(IDPatternUp, SingleColorHalfBright)
        # self.SendCC(IDPatternDown, SingleColorOff)

        print("OG+")

    def OnProjectLoad(self,status):
        pass 

    def OnDoFullRefresh(self):
        pass

    def OnDirtyChannel(self,chan, flags):
        pass

    def OnNoteOn(self,event):
        pass

    def OnNoteOff(self,event):
        pass

    def OnSysEx(self, event):
        pass

    def OnSendTempMsg(self, msg, duration):
        pass

    def OnDirtyMixerTrack(self,track):
        pass


    def OnControlChange(self, event):
        pass

    def OnProgramChange(self, event):
        pass

    def OnPitchBend(self, event):
        pass

    def OnKeyPressure(self, event):
        pass

    def OnChannelPressure(self, event):
        pass

    def OnMidiOutMsg(self, event):
        pass

    def OnFirstConnect(self):
        pass

    def OnWaitingForInput(self):
        pass


    def OnDeInit(self):

        if self.FLFireDeviceCount == 1: # last (or only) FL Fire unit. Save the settings
            self.FromToReg(True)

        self.Reset()
        screen.deInit()
        self.FLFireDeviceCount -= 1

    def CutPlayingNotes(self):

        if (len(self.PlayingNotes) == 0) & (len(self.PlayingChannels) == 0):
            return
        #for n in range(0, len(self.PlayingChannels)):
        #    if utils.InterNoSwap(self.PlayingChannels[n], 0, channels.channelCount()):
        #        channels.midiNoteOn(self.PlayingChannels[n], DotNote_Default, -127)
        self.PlayingChannels = []
        chanNum = self.IsLockedByReceiveNotesFrom()
        if chanNum < 0:
            chanNum = channels.channelNumber()
        if chanNum < 0:
            return

        #for n in range(0, len(self.PlayingNotes)):
        #    channels.midiNoteOn(chanNum, self.PlayingNotes[n], -127) # negative vel for note off
        self.PlayingNotes = bytearray(0)

    def Reset(self):

        self.ClearAllPads()
        self.CurStep = -1
        self.ClearAllButtons()
        self.ClearDisplay()
        self.ClearBtnMap()
        self.ClearKnobsMode()
        self.PlayingNotes = bytearray(0)
        self.PlayingChannels = []

    def FromToReg(self, ToReg):
        return
        #todo IntegerFromToReg(['PadBrightness', 'PadSaturation'], [@self.FLFirePadBrightness, @self.FLFirePadSaturation], FIniFile, Ini_Devices + '\' + FLFireDeviceName, ToReg)

    def Sign(self, AValue):
      Result = 0
      if AValue < 0:
        Result = -1
      elif AValue > 0:
        Result = 1
      return Result

    def DisplayText(self, Font, Justification, PageTop, Text, CheckIfSame, DisplayTime = 0):

        screen.displayText(Font, Justification, PageTop, Text, CheckIfSame, DisplayTime)

    def DisplayBar(self, Text, Value, Bipolar):

        screen.displayBar(0, TextRowHeight * TimedTextRow, Text, Value, Bipolar)

    def DisplayTimedText(self, Text):

        screen.displayTimedText(Text, TimedTextRow)

    def OnDisplayZone(self):

        if self.MultiDeviceMode == MultiDev_Slave:
          self.DispatchMessageToDeviceScripts(SM_SlaveUpdateDisplayZone, 0, 0, 0)
        else:
          if playlist.getDisplayZone() != 0:
            R = self.GetGridRect(ModePerf)
            playlist.liveDisplayZone(R.Left, R.Top, R.Right, R.Bottom, 2000)
          else:
            playlist.liveDisplayZone(-1, -1, -1, -1, 2000)

    def GetChanRackOfs(self):

        if (self.MultiDeviceMode == MultiDev_Single) | (self.MultiDeviceMode == MultiDev_Master):
            if not channels.isHighLighted():
                self.ChanRackOfs = 0
            return self.ChanRackOfs
        else:
            return self.MasterDeviceChanRackOfs + SlaveModeLayoutYShift[self.SlaveModeLayout]

    def GetChanRackStartPos(self):

        if (self.MultiDeviceMode == MultiDev_Single) | (self.MultiDeviceMode == MultiDev_Master):
            if not channels.isHighLighted():
                self.ChanRackStartPos = 0
            return self.ChanRackStartPos
        else:
            return self.MasterDeviceChanRackStartPos + SlaveModeLayoutXShift[self.SlaveModeLayout]

    def GetClipOfs(self):

        if (self.MultiDeviceMode == MultiDev_Single) | (self.MultiDeviceMode == MultiDev_Master):
            return self.ClipOfs
        else:
            return self.MasterDeviceClipOfs + SlaveModeLayoutXShift[self.SlaveModeLayout]

    def GetGridRect(self, Mode):

        if Mode == ModeStepSeq:
            ofsX = self.GetChanRackStartPos()
            ofsY = self.GetChanRackOfs()

        elif Mode == ModePerf:
            ofsX = self.GetClipOfs()
            ofsY = self.GetTrackOfs() + 1
        else:
            ofsX = 0
            ofsY = 0
        r = utils.TRect(ofsX, ofsY, PadsW, PadsH)
        if Mode == ModePerf:
          r.Right  += ofsX
          r.Bottom  += ofsY

        Result = r

        if self.MultiDeviceMode == MultiDev_Single:
            Result = r
        elif self.MultiDeviceMode == MultiDev_Slave:
            Result = r  #Result = self.MasterDevice.GetGridRect(Mode)             #todo
            print('todo')
        else:  #is master
            for port, layout in self.SlavedDevices.items():
                if layout == SlaveModeLayout_Right:
                    r.Right += PadsW
                elif layout == SlaveModeLayout_Bottom:
                    r.Bottom += PadsH

            Result = r

        return Result

    def GetTrackOfs(self):

        if (self.MultiDeviceMode == MultiDev_Single) | (self.MultiDeviceMode == MultiDev_Master):
            return self.TrackOfs
        else:
            return self.MasterTrackOfs + SlaveModeLayoutYShift[self.SlaveModeLayout]

    def GetNoteModeName(self):

        if self.CurrentNoteMode == NoteModeDualKeyb:
            return 'Dual keyboard'
        else:
            scale = self.CurrentNoteMode - 1
            return OG_plus_harmonicScales.HarmonicScaleNamesT[scale]

    def GetOmniNoteValue(self, Data1):

        y = Data1 // PadsStride
        x = Data1 - y * PadsStride
        y = PadsH- 1 - y # invert y (we want bottom to top)
        return x + y * PadsStride # rebuild pad num

    def GetSlicexNoteValue(self, Data1):

        y = Data1 // PadsStride
        x = Data1 - y * PadsStride
        y = PadsH- 1 - y # invert y (we want bottom to top)
        Result = x + y * PadsStride # rebuild note num
        Result  += 5 * 12 # +5 octaves
        return Result

    def GetStepParam(self, Step, Param):

        return channels.getStepParam(Step, Param, self.GetChanRackOfs(), self.GetChanRackStartPos(), PadsStride)

    def GetCurStepParam(self, ChanIndex, Param):

        return channels.getCurrentStepParam(ChanIndex, self.CurStep, Param)

    def GetDualKeybWhiteNoteVal(self, x, y):
        conv = [0, 2, 4, 5, 7, 9, 11, 0 + 12, 2 + 12, 4 + 12, 5 + 12, 7 + 12,  9 + 12,  11 + 12, 0 + 24, 2 + 24]
        if x < 16:
            Result = conv[x]
        else:
            Result = -1

        if Result >= 0:
            Result += self.KeyOffset + (12 * int(y >= 2)) # two octaves up in keyb mode
        return max(0, min(Result, 127))

    
    
    def GetFPCNoteValue(self, Data1):
        result = -1
        if(Data1 in self.FPCNoteMap.keys()):
            result =self.FPCNoteMap[Data1]
        #print("FPCNoteMap  Pad:", Data1, '=', result)
        return result 
        # convert to FPC notes
        # if Data1 ==52:
        #     Result = 37 # C#3
        # elif Data1 ==53:
        #     Result = 36 # C3
        # elif Data1 ==54:
        #     Result = 42 # F#3
        # elif Data1 ==55:
        #     Result = 54 # F#4
        # elif Data1 ==56:
        #     Result = 60 # C5
        # elif Data1 ==57:
        #     Result = 61 # C#5
        # elif Data1 ==58:
        #     Result = 62 # D5
        # elif Data1 ==59:
        #     Result = 63 # D#5
        # elif Data1 ==36:
        #     Result = 40 # E3
        # elif Data1 ==37:
        #     Result = 38 # D3
        # elif Data1 ==38:
        #     Result = 46 # A#3
        # elif Data1 ==39:
        #     Result = 44 # G#3
        # elif Data1 ==40:
        #     Result = 64 # E5
        # elif Data1 ==41:
        #     Result = 65 # F5
        # elif Data1 ==42:
        #     Result = 66 # F#5
        # elif Data1 ==43:
        #     Result = 67 # G5
        # elif Data1 ==20:
        #     Result = 48 # C4
        # elif Data1 ==21:
        #     Result = 47 # B3
        # elif Data1 ==22:
        #     Result = 45 # A3
        # elif Data1 ==23:
        #     Result = 43 # G3
        # elif Data1 ==24:
        #     Result = 68 # G#5
        # elif Data1 ==25:
        #     Result = 69 # A5
        # elif Data1 ==26:
        #     Result = 70 # A#5
        # elif Data1 ==27:
        #     Result = 71 # B5
        # elif Data1 == 4:
        #     Result = 49 # C#4
        # elif Data1 == 5:
        #     Result = 55 # G4
        # elif Data1 == 6:
        #     Result = 51 # D#4
        # elif Data1 == 7:
        #     Result = 53 # F4
        # elif Data1 == 8:
        #     Result = 72 # C6
        # elif Data1 == 9:
        #     Result = 73 # C#6
        # elif Data1 == 10:
        #     Result = 74 # D6
        # elif Data1 == 11:
        #     Result = 75 # E6
        # else:
        #     Result = -1
        # return Result

    def GetDualKeybBlackNoteVal(self, x, y):

        conv = (-1, 1, 3, -1, 6, 8, 10, -1, 1 + 12, 3 + 12, -1, 6 + 12, 8 + 12, 10 + 12, -1, 1 + 24)
        if x < 16:
            Result = conv[x]
        else:
            Result = -1

        if Result >= 0:
            Result += self.KeyOffset + (12 * int(y >= 2)) # two octaves up in keyb mode
            return max(0, min(Result, 127))
        return Result

    def OnIdle(self):

        def BlinkBtn(b, id):

            if not device.isAssigned():
                return
            if b:
                if self.BlinkTimer < BlinkSpeed:
                    self.SendCC(id, DualColorFull2)
                else:
                    self.SendCC(id, DualColorOff)
            else:
                self.SendCC(id, DualColorOff)

        #************

        if self.IdleDeviceCount == 0:
            self.IdleDeviceCount = self.FLFireDeviceCount
            self.AnalyzerHue = self.AnalyzerHue + 10
            if self.AnalyzerHue >= 360:
                self.AnalyzerHue = self.AnalyzerHue - 360
        else:
            self.IdleDeviceCount -= 1

        TopLineJustify = JustifyLeft
        if self.SlaveLayoutSelectionMode: # this mode takes over the other ones (it's "blocking")
            self.TopText = 'Slave device layout'
            self.DisplayTimedText(SlaveModeLayoutNamesT[self.SlaveModeLayout])
            self.TopTextTimer = 0
        elif self.TopTextTimer > 0:
            TopLineJustify = JustifyCenter
            self.TopTextTimer = self.TopTextTimer - device.getIdleElapsed()
            if self.TopTextTimer < 0:
                self.TopTextTimer = 0
        else:
            s = patterns.getPatternName(patterns.patternNumber())
            if transport.getLoopMode() == SM_Pat:
                self.TopText = s
            else:
                self.TopText = 'Song (' + s + ')'
            if self.LayoutSelectionMode:
                self.TopText = 'Layout select'

        self.CurStep = mixer.getSongStepPos() # set current playing step
        self.DisplayText(Font6x16 , TopLineJustify, 0, self.TopText, True)

        #NFX - show ALT + options
        self.DisplayText(Font6x16, JustifyLeft, 1, '', True) # clear line
        self.DisplayText(Font6x16, JustifyLeft, 2, '', True) # clear line
        if(self.AltHeld):
            self.DisplayText(Font6x16, JustifyLeft, 0, 'Alt +', True)
            self.DisplayText(Font6x16, JustifyLeft, 1, 'DRUM = COPY', True)
            self.DisplayText(Font6x16, JustifyLeft, 2, 'PERF = PASTE', True)
        elif self.JogWheelPushed & self.AltHeld:
            self.JogWheelHeldTime = self.JogWheelHeldTime + device.getIdleElapsed()
            if self.JogWheelHeldTime >= 2000:
                self.JogWheelHeldTime = 0
                self.SetAsMasterDevice(not self.IsMasterDevice())
        else:
            self.JogWheelHeldTime = 0

        self.BlinkTimer += 1
        if self.BlinkTimer >= BlinkSpeed * 2:
            self.BlinkTimer = 0

        if (self.PatDownBtnHeld | self.PatUpBtnHeld) & (not self.AltHeld):
            self.PatBtnHeldTime  += 1
            if self.PatBtnHeldTime >= self.PatBtnHeldTriggerTime:
                self.PatBtnHeldTime = 0
                # resend pat up/down while button is held
                if self.PatBtnHeldTriggerTime > 2:
                    self.PatBtnHeldTriggerTime -= 1 # make it go faster & faster
                fakeMidi = TMidiEvent()
                fakeMidi.handled = 0
                fakeMidi.midiId = MIDI_NOTEON
                if self.PatDownBtnHeld:
                    fakeMidi.data1 = IDPatternDown
                else:
                    fakeMidi.data1 = IDPatternUp
                fakeMidi.data2 = 127
                self.OnMidiMsg(fakeMidi) # NFX
        else:
            self.PatBtnHeldTime = 0
            self.PatBtnHeldTriggerTime = HeldButtonRetriggerTime # reset to max time

        if (self.GridDownBtnHeld | self.GridUpBtnHeld) & (not self.BrowserMode):
            self.GridBtnHeldTime  +=   1
            if self.GridBtnHeldTime >= self.GridBtnHeldTriggerTime:
                self.GridBtnHeldTime = 0
                # resend Grid up/down while button is held
                if self.GridBtnHeldTriggerTime > 2:
                    self.GridBtnHeldTriggerTime -= 1 # make it go faster & faster
                fakeMidi = TMidiEvent()
                fakeMidi.handled = 0
                fakeMidi.midiId = MIDI_NOTEON
                if self.GridDownBtnHeld:
                    fakeMidi.data1 = IDBankR
                else:
                    fakeMidi.data1 = IDBankL
                fakeMidi.data2 = 127

                oldShift = self.ShiftHeld
                oldAlt = self.AltHeld
                self.ShiftHeld = False
                self.AltHeld = False
                self.OnMidiMsg(fakeMidi)
                self.ShiftHeld = oldShift
                self.AltHeld = oldAlt
        else:
            self.GridBtnHeldTime = 0
            self.GridBtnHeldTriggerTime = HeldButtonRetriggerTime # reset to max time

            

            if self.TextTimer > 0:
                self.TextTimer -= 1
                if self.TextTimer == 0:
                    self.DisplayTimedText(chr(13))

        if self.DisplayZoneTimer > 0:
            self.DisplayZoneTimer -= 1
            if self.DisplayZoneTimer == 0:
                playlist.lockDisplayZone(1 + self.GetTrackOfs(), False)

        self.UpdateCurrentKnobsMode()
        self.UpdateCurrentPadsMode()
        self.RefreshTransport()

        if self.ShiftHeld:
            # metronome status
            BlinkBtn(ui.isMetronomeEnabled(), IDPatternSong)
            # wait before rec
            BlinkBtn(ui.isStartOnInputEnabled(), IDPlay)
            # countdown
            BlinkBtn(ui.isPrecountEnabled(), IDStop)
            # looprec
            BlinkBtn(ui.isLoopRecEnabled(), IDRec)
            # snap
            BlinkBtn(ui.getSnapMode() != Snap_None, IDNote)
            # accent
            BlinkBtn(self.AccentMode, IDStepSeq)
            # overview
            BlinkBtn(self.OverviewMode, IDPerform)
        elif self.AltHeld: # NFX added copy/paste
            self.SendCC(IDStepSeq, SingleColorOff)
            self.SendCC(IDNote, SingleColorOff)
            self.SendCC(IDDrum, SingleColorHalfBright) # copy
            self.SendCC(IDPerform, SingleColorHalfBright) # paste
        else:
            self.UpdateCurrentModeBtns()


        res = screen.findTextLine(0, 20, 128, 20 + 44)
        if (res < 0) & (self.ScreenMode != ScreenModeNone):
            i = self.ScreenMode
            self.ScreenMode = ScreenModeNone
            self.SetScreenMode(i)

        screen.animateText(self.ScreenMode)
        t = time.time()

        if self.LastIdleSec == 0:
            self.LastIdleSec = t
            self.IdleFPS = 0
        else:
            if t < self.LastIdleSec:
                # i = Integer((Int64(t) + 0x100000000) - Int64(self.LastIdleSec)) # rewrote for syntax issues. python doesnt support Integer or Int64
                i = int((int(t) + 0x100000000) - int(self.LastIdleSec))
            else:
                i = (t - self.LastIdleSec)
            if i >= 1000:
                screenActiveCounter = screen.getScreenActiveCounter()
                if (screenActiveCounter > 0) & (not screen.isBlanked()):
                    screenActiveCounter -= 1
                    screen.setScreenActiveCounter(screenActiveCounter)
                    if screenActiveCounter > ScreenAutoTimeout:
                        screen.keepDisplayActive()
                    elif screenActiveCounter == 0:
                        screen.blank(True, self.ScreenMode)

                self.LastIdleSec = t
                R = utils.TRect(0, TextRowHeight * FPSRow, self.DisplayWidth, (TextRowHeight * FPSRow) + TextRowHeight)
                R2 = R
                utils.OffsetRect(R2, 0, TextOffset)
                screen.eraseRect(R2.Left, R2.Top, R2.Right, R2.Bottom)
                screen.drawText(0, 'FPS: ' + str(self.IdleFPS), R2.Left, R2.Top, R2.Right, R2.Bottom)
                self.IdleFPS = 0
            else:
                self.IdleFPS  += 1

        if screen.isUnBlank():
            screen.blank(False, self.ScreenMode)

        screen.update()
        screen.unBlank(False)

    def Init(self):

        self.Reset()
        self.SetOfs(self.TrackOfs, self.ClipOfs)
        self.ClearDisplay()

    def IsLockedByReceiveNotesFrom(self):

        for n in range(0, channels.channelCount()):
            if channels.getChannelMidiInPort(n) == device.getPortNumber():
                return(n)
        return -1

    def IsMasterDevice(self):

        return self.MultiDeviceMode == MultiDev_Master

    def TranslateNote(self, event):

        Data1 = event.data1
        Data2 = 0

        Result = True
        if (Data1 >= PadFirst) & (Data1 <= PadLast):
            Data1 -= PadFirst
            Data2 = event.data2
        if self.CurrentMode == ModeNotes:
            Data2 = self.AdaptVelocity(Data2)
            y = Data1 // PadsStride
            x = Data1 - y * PadsStride
            if self.CurrentNoteMode != NoteModeDualKeyb:
                Data1 = self.CurrentNoteGrid[x][ y]
                Data1 = max(0, min(Data1, 127))
            else:
                y = PadsH- 1 - y # invert y (we want bottom to top)
                if y % 2 == 0:
                    # white notes
                    Data1 = self.GetDualKeybWhiteNoteVal(x, y)
                    if Data1 < 0:
                        Result = False
                        return Result
                else:
                    # black notes
                    Data1 = self.GetDualKeybBlackNoteVal(x, y)
                    if Data1 < 0:
                        Result = False
                        return Result
        elif self.CurrentMode == ModeDrum:
            if self.CurrentDrumMode in [DrumModeFPC, DrumModeFPCCenter]:
                # if (self.CurrentDrumMode == DrumModeFPCCenter):
                #     Data1 += 4 # offset to match center layout
                Data1 = self.GetFPCNoteValue(Data1)
            elif self.CurrentDrumMode == DrumModeSlicex:
                Data1 = self.GetSlicexNoteValue(Data1)
            elif self.CurrentDrumMode == DrumModeOmni:
                Data1 = self.GetOmniNoteValue(Data1)
            if Data1 < 0:
                Result = False

        if Result:
            event.data1 = Data1
            event.data2 = Data2       
        return Result

    def OnMidiIn(self, event):

        if ((event.status == MIDI_NOTEON) | (event.status == MIDI_NOTEOFF)) & utils.InterNoSwap(event.data1, IDKnob1, IDKnob4) & self.ShiftHeld:
            print('Ignored note on/off')
            return
        else:
            self.LastRawData1 = event.data1
            self.LastRawData2 = event.data2
            if (event.status & 0xF0) in [MIDI_NOTEON, MIDI_NOTEOFF]:
                if not self.TranslateNote(event):
                    event.handled = False #todo
                    return
            if event.status == 0xF4:

                ID = event.sysex[4]
                data1 = event.sysex[7] + (event.sysex[8] << 7)
                data2 = event.sysex[9] + (event.sysex[10] << 7)
                data3 = event.sysex[11] + (event.sysex[12] << 7)
                
                if ID == SM_SetAsSlave:
                  self.SetAsSlaveDevice(data1)
                  self.DispatchMessageToDeviceScripts(SM_SlaveDeviceModeLayout, self.SlaveModeLayout, device.getPortNumber(), 0)
                elif ID == SM_SetAsSingle:
                  self.SetAsSingleDevice()
                elif ID == SM_MasterDeviceChanRackOfs:
                  if self.MultiDeviceMode == MultiDev_Slave:
                    self.MasterDeviceChanRackOfs = data1
                    self.SetChanRackOfs(0, False)
                elif ID == SM_MasterDeviceChanStartPos:
                  self.MasterDeviceChanRackStartPos = data1
                elif ID == SM_SlaveDeviceSetOfs:
                  if self.MultiDeviceMode == MultiDev_Master:
                    self.SetOfs(self.GetTrackOfs() + data1 - 128, self.GetClipOfs() + data2 - 128, False)
                    self.DispatchMessageToDeviceScripts(SM_MasterDeviceSetOfs, self.TrackOfs + 128, self.ClipOfs + 128, 0)
                elif ID == SM_MasterDeviceSetOfs:
                  if self.MultiDeviceMode == MultiDev_Slave:
                    self.MasterTrackOfs = data1 - 128
                    self.MasterClipOfs = data1 - 128
                    self.SetOfs(self.MasterTrackOfs, self.MasterClipOfs, False)
                elif ID == SM_SlaveDeviceStartPos:
                  if self.MultiDeviceMode == MultiDev_Master:
                    self.SetChanRackStartPos(self.GetChanRackStartPos() + data1 - 128, False)
                elif ID == SM_SlaveDeviceRackOfs:
                  if self.MultiDeviceMode == MultiDev_Master:
                    self.SetChanRackOfs(self.GetChanRackOfs() + data1 - 128, False)
                    self.DispatchMessageToDeviceScripts(SM_MasterDeviceChanRackOfs, self.ChanRackOfs, 0, 0)
                elif ID == SM_UpdateLiveMode:
                  if self.MultiDeviceMode == MultiDev_Slave:
                    self.OnUpdateLiveMode(1, playlist.trackCount())
                elif ID == SM_SlaveDeviceModeLayout:
                  if self.MultiDeviceMode == MultiDev_Master:
                    self.SlavedDevices[data2] = data1
                elif ID == SM_SlaveUpdateDisplayZone:
                  if self.MultiDeviceMode == MultiDev_Master:
                    self.OnDisplayZone()


                event.handled = True

    # def GetTimeForPad(self, Device, PadNum):
    #     Result = (self.GetChanRackStartPos() + PadNum - ((PadNum // PadsStride) * PadsStride)) * RecPPS
    #     return Result # added - NFX

    def GetChannelNumForPad(self, PadNum):

        Result = -1
        padRow = PadNum // PadsStride

        if self.CurrentMode == ModeStepSeq:
            if not utils.InterNoSwap(padRow + self.GetChanRackOfs(), 0, channels.channelCount() - 1):
                return
            Result = padRow + self.GetChanRackOfs()

        return Result

    # def GetEventForPad(self, PadNum):

    #     Result = -1
    #     #chNum = self.GetChannelNumForPad(Device, PadNum)
    #     chNum = self.GetChannelNumForPad(PadNum) # NFX fixed too many args
    #     if chNum > -1:
    #         cID = channels.getChannelIndex(chNum)
    #         Time = self.GetTimeForPad(Device, PadNum)
    #         if Assigned(PatInfoT[patterns.patternNumber()].NoteRecChan):
    #             for i in range(0, Count):
    #                 Event = pNoteEvent(GetEventAtPos(i))
    #                 if (Event.ChanID == cID) & (((Event.Time // RecPPS) * RecPPS) == Time):
    #                     Result = pRecEvent(Event)
    #                     return

    #     return Result

    def OnMidiMsg(self, event):

        tempHeldPads = bytearray()
        ParamNames = ('Step pitch', 'Velocity', 'Release', 'Fine pitch', 'Panning', 'Mod X', 'Mod Y', 'Shift')
        
        def SetStep(padNum, Force):

            Result = False
            padRow = padNum // PadsStride
            padCol = padNum - padRow * PadsStride
            general.saveUndo('Fire: Step seq edit', UF_PR, True)
            if self.CurrentMode == ModeStepSeq:
                if not utils.InterNoSwap(padRow + self.GetChanRackOfs(), 0, channels.channelCount() - 1):
                    return
                index = padRow + self.GetChanRackOfs()
                if channels.isGridBitAssigned(index):
                    if Force:
                        if channels.getGridBit(index, padCol + self.GetChanRackStartPos()) == 0:
                            channels.setGridBit(index, padCol + self.GetChanRackStartPos(), 1)
                        Result = True
                    else:
                        if channels.getGridBit(index, padCol + self.GetChanRackStartPos()) > 0:
                            channels.setGridBit(index, padCol + self.GetChanRackStartPos(), 0)
                        else:
                            channels.setGridBit(index, padCol + self.GetChanRackStartPos(), 1)
                            Result = True
            return Result

        def HandleStepSeqPad(id, padNum):

            # store pads being held
            if id == MIDI_NOTEON:
                self.HeldPads.append(padNum)
            else:
                for i in range(0, len(self.HeldPads)):
                    if self.HeldPads[i] != padNum:
                        tempHeldPads.append(self.HeldPads[i])

                self.HeldPads = bytearray(len(tempHeldPads))
                for i in range(0, len(tempHeldPads)):
                    self.HeldPads[i] = tempHeldPads[i]

            didSetStep = False
            if id == MIDI_NOTEOFF:
                didSetStep = SetStep(padNum, self.HeldPadsChanged) # if we tweaked a param, force the step on upon releasing

            if self.AccentMode & didSetStep:
                self.SetStepParam(padNum, pPitch, self.AccentParams.Pitch)
                self.SetStepParam(padNum, pVelocity, self.AccentParams.Vel)
                self.SetStepParam(padNum, pPan, self.AccentParams.Pan)
                self.SetStepParam(padNum, pModX, self.AccentParams.ModX)
                self.SetStepParam(padNum, pModY, self.AccentParams.ModY)
                channels.updateGraphEditor()

            if len(self.HeldPads) == 0:
                self.HeldPadsChanged = False
                channels.closeGraphEditor(True)

        def HandleKnob(ID, Data2, Name, Bipolar):

            mixer.automateEvent(ID, Data2, REC_MIDIController, 0, 1, EKRes)
            barVal = device.getLinkedValue(ID)
            self.DisplayBar(Name, barVal, Bipolar)

        def HandleHeldPadsParam(Data2, Param):

            ParamDefVal = (DotNote_Default, 100, 64, 120, 64, 128, 128, 0)
            ParamMax = (127, 127, 127, 240, 127, 255, 255, 255)
            ParamInc = (1, 2, 2, 2, 2, 2, 2, 1)
            RecPPS = mixer.getRecPPS()

            for m in range(0, len(self.HeldPads)):
                n = (self.HeldPads[m] // PadsStride) + self.GetChanRackOfs()
                if n >= channels.channelCount():
                    return

                bitPos = self.HeldPads[m] % PadsStride
                if (Param == pShift) & (channels.getGridBit(n, bitPos) == 0):
                    channels.setGridBit(n, bitPos, 1)

                val = self.GetStepParam(self.HeldPads[m], Param)
                oldVal = val

                if val == -1:
                    val = ParamDefVal[Param]

                if Data2 >= 0x7F // 2:
                    Data2 = -(0x80 - Data2)

                if Data2 > 0:
                    val += ParamInc[Param]
                else:
                    val -=  ParamInc[Param]

                if Param == pShift: # other parameters will be limited by graph editor
                    oldVal = (oldVal // RecPPS) * RecPPS
                    val = utils.Limited(val, oldVal, oldVal + RecPPS - 1)
                self.SetStepParam(self.HeldPads[m], Param, val)

                if Param != pShift:
                    val = utils.Limited(val, 0, ParamMax[Param])

                if m == 0:
                    if Param == pPitch:
                        self.DisplayTimedText(ParamNames[Param] + ': ' + utils.GetNoteName(val))
                    else:
                        if Param == pShift:
                            val = val % RecPPS
                            self.DisplayBar(ParamNames[Param] + ': ' + str(val), val / (RecPPS - 1), False)
                        else:
                            bipolar = (Param == pFinePitch) | (Param == pPan)
                            if bipolar:
                                showVal = val - ParamMax[Param] // 2
                            else:
                                showVal = val
                            self.DisplayBar(ParamNames[Param] + ': ' + str(showVal), val / ParamMax[Param], bipolar)

                channels.updateGraphEditor()

        def SetChanLoop(ChanIndex, LoopLength):

            loopName = patterns.setChannelLoop(ChanIndex, LoopLength)
            self.DisplayTimedText(channels.getChannelName(ChanIndex) + ' loop: ' + loopName)
            self.DidTweakLooping = True

        #************
        # treat self.SlaveLayoutSelectionMode in priority as it's a mode that should lock all others
        screen.unBlank(True)
        event.data1 = self.LastRawData1
        event.data2 = self.LastRawData2

        if (not event.handled):
            if self.SlaveLayoutSelectionMode:
                if (event.midiId == MIDI_CONTROLCHANGE) & (event.data1 == IDJogWheel):
                    if event.data2 == 1:
                        self.SlaveModeLayout  +=  1
                    else:
                        self.SlaveModeLayout -= 1
                    if self.SlaveModeLayout > SlaveModeLayout_Last:
                        self.SlaveModeLayout = 0
                    elif self.SlaveModeLayout < 0:
                        self.SlaveModeLayout = SlaveModeLayout_Last
                    self.DispatchMessageToDeviceScripts(SM_SlaveDeviceModeLayout, self.SlaveModeLayout, device.getPortNumber(), 0)
                    self.DisplayTimedText(SlaveModeLayoutNamesT[self.SlaveModeLayout])
                elif (event.midiId == MIDI_NOTEON) & (event.data1 == IDJogWheelDown):
                    self.SlaveLayoutSelectionMode = False
                    if self.CurrentMode == ModeStepSeq:
                        self.SetChanRackStartPos(self.GetChanRackStartPos())
                    elif self.CurrentMode == ModePerf:
                        self.SetOfs(self.TrackOfs, self.ClipOfs)
                    self.DisplayTimedText('')
                    self.ClearBtnMap()
                    self.UpdateCurrentPadsMode()
                    event.handled = True
                return

        if (not event.handled):
            # ALT+KNOB1 = BRIGHTNESS
            if (event.data1 == IDKnob1) & (event.data2 != 0) & self.AltHeld:    
                i = event.data2
                if (i >= 64) & (i <= 127):
                    i -= 128
                self.FLFirePadBrightness = utils.Limited(self.FLFirePadBrightness + i, 32, 128)
                self.DisplayBar('Pad brightness', (self.FLFirePadBrightness - 32) / 96, False)
                ui.setHintMsg(str(round(100 * ((self.FLFirePadBrightness - 32) / 96))) + '% Pad brightness')
                self.OnUpdateLiveMode(1, playlist.trackCount())
                event.handled = True
            
            # ALT+KNOB2 = SATURATION
            if (event.data1 == IDKnob2) & (event.data2 != 0) & self.AltHeld:    
                i = event.data2
                if (i >= 64) & (i <= 127):
                    i -= 128
                self.FLFirePadSaturation = utils.Limited(self.FLFirePadSaturation + i, 0, 128)
                self.DisplayBar('Pad saturation', (self.FLFirePadSaturation) / 96, False)
                ui.setHintMsg(str(round(100 * (self.FLFirePadSaturation / 128))) + '% Pad saturation')
                self.OnUpdateLiveMode(1, playlist.trackCount())
                event.handled = True

            # ALT+KNOB3 = VISUALIZATION
            if (event.data1 == IDKnob3) & (event.data2 != 0) & self.AltHeld:
                i = event.data2
                if (i >= 64) & (i <= 127):
                    i -= 128
                self.KnobsV[2]  += i
                if self.KnobsV[2] <= -32:
                    self.KnobsV[2]  += 32
                elif self.KnobsV[2] >= 32:
                    self.KnobsV[2] -= 32
                else:
                    i = 0
                if i != 0:
                    if (self.CurrentMode < ModePadVisFirst) | (self.CurrentMode > ModePadVisLast):
                        self.NonVisMode = self.CurrentMode
                        if self.Sign(i) > 0:
                            self.CurrentMode = ModePadVisFirst
                        else:
                            self.CurrentMode = ModePadVisLast
                    else:
                        self.CurrentMode = self.CurrentMode + self.Sign(i)
                        if (self.CurrentMode < ModePadVisFirst) | (self.CurrentMode > ModePadVisLast):
                            self.CurrentMode = ModeAnalyzerNone
                        print(self.CurrentMode)
                        self.TopText = ModeVisNamesT[0]

                    if self.CurrentMode == ModeAnalyzerNone:
                        self.CurrentMode = self.NonVisMode
                    else:
                        self.TopText = ModeVisNamesT[self.CurrentMode + 1 - ModePadVisFirst]
                        self.SetAnalyzerMode(self.CurrentMode)
                    self.TopTextTimer = TextDisplayTime
                event.handled = True

            # ALT+KNOB4 = SHOW PEAKS
            if (event.data1 == IDKnob4) & (event.data2 != 0) & self.AltHeld: 
                i = event.data2
                if (i >= 64) & (i <= 127):
                    i -= 128
                self.KnobsV[3]  += i
                if self.KnobsV[3] <= -32:
                    self.KnobsV[3]  += 32
                elif self.KnobsV[3] >= 32:
                    self.KnobsV[3] -= 32
                else:
                    i = 0
                if i != 0:
                    if (self.ScreenMode < ScreenModeFirst) | (self.ScreenMode > ScreenModeLast):
                        if self.Sign(i) > 0:
                            i = ScreenModeFirst
                        else:
                            i = ScreenModeLast
                    else:
                        i = self.ScreenMode + self.Sign(i)
                        if (i < ScreenModeFirst) | (i > ScreenModeLast):
                            i = ScreenModeNone
                        self.TopText = ScreenModeNamesT[0]

                    if i != ScreenModeNone:
                        self.TopText = ScreenModeNamesT[i + 1 - ScreenModeFirst]
                    self.TopTextTimer = TextDisplayTime
                    self.SetScreenMode(i)

                event.handled = True

        # NFX - add copy/paste
        if self.AltHeld:
            if(event.data1 == 46): # ALT+DRUM =  copy 
                ui.copy()
                event.handled = True
            if(event.data1 == 47): # ALT+PERFORM = paste
                ui.paste()
                event.handled = True
            #print('ALT+', event.data1, event.data2)

        if not event.handled:
            if screen.menuShowing():
                if (event.midiId == MIDI_CONTROLCHANGE) & (event.data1 == IDJogWheel):
                    if (event.data2 >= 1) & (event.data2 <= 63):
                        screen.MenuNext()
                    elif (event.data2 >= 64) & (event.data2 <= 127):
                        screen.menuPrev()
                    event.handled = True
                elif (event.midiId == MIDI_NOTEON) & (event.data1 == IDJogWheelDown):
                    screen.menuItemClick()
                    event.handled = True

        if not event.handled:
            if event.midiId == MIDI_CONTROLCHANGE:
                event.handled = True
                if event.data1 == IDJogWheel:
                    HeldMuteBtn = -1
                    for n in range(0, 4):
                        if self.MuteBtnStates[n]:
                            HeldMuteBtn = n
                            break

                    if HeldMuteBtn >= 0:
                        p = patterns.getChannelLoopStyle(patterns.patternNumber(), HeldMuteBtn + self.GetChanRackOfs())
                        if event.data2 == 1:
                            p += 1
                        else:
                            p -= 1
                        SetChanLoop(HeldMuteBtn + self.GetChanRackOfs(), p)

                    else:
                        if self.ShiftHeld & (self.CurrentMode != ModePerf) & (not self.BrowserMode):
                            if event.data2 == 1:
                                transport.globalTransport(FPT_TrackJog, 1)
                            else:
                                transport.globalTransport(FPT_TrackJog, -1)
                            self.CurrentMixerTrack = mixer.trackNumber()
                            self.DisplayTimedText('Mixer : ' + mixer.getTrackName(self.CurrentMixerTrack))

                        elif self.AltHeld & (not self.BrowserMode):

                            m = channels.selectedChannel()
                            if event.data2 == 1:
                                m += 1
                            else:
                                m -= 1
                            m = utils.Limited(m, 0, channels.channelCount() - 1)
                            channels.selectOneChannel(m) #this use group index
                            self.DisplayTimedText('Chan: ' + channels.getChannelName(m))

                            p = self.GetChanRackOfs()
                            R = self.GetGridRect(ModeStepSeq)
                            if event.data2 == 1:
                              p += 1
                              if m - p == R.Bottom - 1:
                                self.SetChanRackOfs(p)
                            else:
                              p -= 1
                              if m == p:
                                self.SetChanRackOfs(p)

                        elif (self.CurrentMode == ModeStepSeq) & self.MixerTrackSelectionMode:

                            m = channels.channelNumber()
                            if m < 0:
                                return
                            p = channels.getTargetFxTrack(m)
                            if event.data2 == 1:
                                p += 1
                            else:
                                p -= 1
                            p = utils.Limited(p, 0, mixer.trackCount() - 1)
                            channels.processRECEvent(channels.getRecEventId(m) + REC_Chan_FXTrack, p, REC_Control | REC_UpdateControl)
                            mixer.setTrackNumber(p, curfxScrollToMakeVisible | curfxMinimalLatencyUpdate)
                            self.DisplayTimedText('Chan ' + str(m + 1) + chr(13) + 'Track: ' + mixer.getTrackName(channels.getTargetFxTrack(m)))

                        elif (self.CurrentMode == ModeStepSeq) & self.AccentMode:

                            if event.data2 == 1:
                                self.AccentParams.Pitch += 1
                            else:
                                self.AccentParams.Pitch -= 1
                            self.AccentParams.Pitch = utils.Limited(self.AccentParams.Pitch, 0, 127)
                            self.DisplayTimedText('Default pitch : ' + utils.GetNoteName(self.AccentParams.Pitch))

                        elif (self.CurrentMode == ModeNotes) & self.LayoutSelectionMode:
                            if event.data2 == 1:
                                self.CurrentNoteMode  += 1
                            else:
                                self.CurrentNoteMode -= 1
                            if self.CurrentNoteMode > NoteModeLast:
                                self.CurrentNoteMode = NoteModeLast
                            elif self.CurrentNoteMode < 0:
                                self.CurrentNoteMode = 0
                            self.CutPlayingNotes()
                            self.ClearBtnMap()
                            self.RefreshNotesMode()
                            self.DisplayTimedText(self.GetNoteModeName())

                        elif (self.CurrentMode == ModeDrum) & self.LayoutSelectionMode:
                            if event.data2 == 1:
                                self.CurrentDrumMode  += 1
                            else:
                                self.CurrentDrumMode -= 1
                            if self.CurrentDrumMode > DrumModeLast:
                                self.CurrentDrumMode = 0
                            elif self.CurrentDrumMode < 0:
                                self.CurrentDrumMode = DrumModeLast
                            self.CutPlayingNotes()
                            self.ClearBtnMap()
                            self.RefreshDrumMode(True)
                            self.DisplayTimedText(DrumModesNamesT[self.CurrentDrumMode])

                        elif self.BrowserMode:
                            text = ui.navigateBrowserMenu(event.data2, self.ShiftHeld)
                            if text != '':
                                self.DisplayTimedText(text)

                        elif (self.CurrentMode == ModeStepSeq) | (self.CurrentMode == ModeNotes) | (self.CurrentMode == ModeDrum):

                            if (len(self.HeldPads) >= 1) & (self.CurrentMode == ModeStepSeq):
                                HandleHeldPadsParam(event.data2, pPitch)
                                p = self.HeldPads[0] - (self.HeldPads[0] // PadsStride) * PadsStride
                                chNum = self.GetChannelNumForPad(self.HeldPads[0])
                                if ui.getVisible(widChannelRack) & (chNum > -1):
                                    channels.showGraphEditor(False, pPitch, p, channels.getChannelIndex(chNum), 0)
                                self.HeldPadsChanged = True

                            else:
                                p = self.GetChanRackOfs()
                                if event.data2 == 1:
                                    p += 1
                                else:
                                    p -= 1
                                self.SetChanRackOfs(p)

                        elif self.CurrentMode == ModePerf:
                            if (event.pmeFlags & PME_System != 0) & (event.data2 == 1):
                                if not self.ShiftHeld:
                                    self.SetOfs(self.GetTrackOfs() + 1, self.GetClipOfs())
                                else:
                                    self.SetOfs(self.GetTrackOfs(), self.GetClipOfs() + 1)

                            elif (event.pmeFlags & PME_System != 0) & (event.data2 == 127):
                                if not self.ShiftHeld:
                                    self.SetOfs(self.GetTrackOfs() - 1, self.GetClipOfs())
                                else:
                                    self.SetOfs(self.GetTrackOfs(), self.GetClipOfs() - 1)

                            playlist.lockDisplayZone(1 + self.GetTrackOfs(), event.data2 > 0)
                            self.DisplayZoneTimer = 30

                elif event.data1 in [IDKnob1, IDKnob2, IDKnob3, IDKnob4]:
                    event.inEv = event.data2
                    if event.inEv >= 0x40:
                        event.outEv = event.inEv - 0x80
                    else:
                        event.outEv = event.inEv
                    event.isIncrement = 1
                    if (self.CurrentKnobsMode == KnobsModeChannelRack) & (self.CurrentMode == ModeStepSeq) & self.AccentMode:

                        if event.data1 == IDKnob1:
                            self.AccentParams.Vel = utils.Limited(self.AccentParams.Vel + self.AdaptKnobVal(event.outEv), 0, 127)
                            self.DisplayBar('Default velocity', self.AccentParams.Vel / 127, False)
                        elif event.data1 == IDKnob2:
                            self.AccentParams.Pan = utils.Limited(self.AccentParams.Pan + self.AdaptKnobVal(event.outEv), 0, 127)
                            self.DisplayBar('Default panning', self.AccentParams.Pan / 127, True)
                        elif event.data1 == IDKnob3:
                            self.AccentParams.ModX = utils.Limited(self.AccentParams.ModX + self.AdaptKnobVal(event.outEv), 0, 127)
                            self.DisplayBar('Default ModX', self.AccentParams.ModX / 127, False)
                        elif event.data1 == IDKnob4:
                            self.AccentParams.ModY = utils.Limited(self.AccentParams.ModY + self.AdaptKnobVal(event.outEv), 0, 127)
                            self.DisplayBar('Default ModY', self.AccentParams.ModY / 127, False)

                    elif (len(self.HeldPads) >= 1) & (self.CurrentMode == ModeStepSeq):
                        if event.data1 == IDKnob1:
                            HandleHeldPadsParam(event.data2, pVelocity)
                        elif event.data1 == IDKnob2:
                            HandleHeldPadsParam(event.data2, pPan)
                        elif event.data1 == IDKnob3:
                            HandleHeldPadsParam(event.data2, pModX)
                        elif event.data1 == IDKnob4:
                            HandleHeldPadsParam(event.data2, pModY)

                        self.HeldPadsChanged = True
                        self.ChangeFlag = True

                    elif self.CurrentKnobsMode == KnobsModeChannelRack:
                        selChanNum = channels.channelNumber()
                        if selChanNum < 0:
                            return
                        if event.data1 == IDKnob1:
                            HandleKnob(channels.getRecEventId(selChanNum) + REC_Chan_Vol, self.AdaptKnobVal(event.outEv), 'Chan Volume', False)
                        elif event.data1 == IDKnob2:
                            HandleKnob(channels.getRecEventId(selChanNum) + REC_Chan_Pan, self.AdaptKnobVal(event.outEv), 'Chan Panning', True)
                        elif event.data1 == IDKnob3:
                            HandleKnob(channels.getRecEventId(selChanNum) + REC_Chan_FCut, self.AdaptKnobVal(event.outEv), 'Chan Filter Freq', False)
                        elif event.data1 == IDKnob4:
                            HandleKnob(channels.getRecEventId(selChanNum) + REC_Chan_FRes, self.AdaptKnobVal(event.outEv), 'Chan Filter BW', False)

                    elif self.CurrentKnobsMode == KnobsModeMixer:

                        self.CurrentMixerTrack = mixer.trackNumber()
                        if (self.CurrentMixerTrack < 0) | (self.CurrentMixerTrack >= mixer.getTrackInfo(TN_Sel)):
                            return

                        if event.data1 == IDKnob1:
                            HandleKnob(REC_Mixer_Vol + mixer.getTrackPluginId(self.CurrentMixerTrack, 0), self.AdaptKnobVal(event.outEv), mixer.getTrackName(self.CurrentMixerTrack) + ' Vol', False)
                        if event.data1 == IDKnob2:
                            HandleKnob(REC_Mixer_Pan + mixer.getTrackPluginId(self.CurrentMixerTrack, 0), self.AdaptKnobVal(event.outEv), mixer.getTrackName(self.CurrentMixerTrack) + ' Pan', True)
                        if event.data1 == IDKnob3:
                            HandleKnob(REC_Mixer_EQ_Gain + 0 + mixer.getTrackPluginId(self.CurrentMixerTrack, 0), self.AdaptKnobVal(event.outEv), mixer.getTrackName(self.CurrentMixerTrack) + ' EQ Lo', True)
                        if event.data1 == IDKnob4:
                            HandleKnob(REC_Mixer_EQ_Gain + 2 + mixer.getTrackPluginId(self.CurrentMixerTrack, 0), self.AdaptKnobVal(event.outEv), mixer.getTrackName(self.CurrentMixerTrack) + ' EQ Hi', True)

                    else:
                        event.handled = False # user modes, free
                        event.data1 += (self.CurrentKnobsMode - KnobsModeUser1) * 4 # so the CC is different for each user mode
                        device.processMIDICC(event)
                        if (general.getVersion() > 9):
                          BaseID = EncodeRemoteControlID(device.getPortNumber(), 0, 0)
                          eventId = device.findEventID(BaseID + event.data1, 0)
                          if eventId != 2147483647:
                            s = device.getLinkedParamName(eventId)
                            s2 = device.getLinkedValueString(eventId)
                            self.TopText = s
                            self.DisplayTimedText(s2)
                            self.TopTextTimer = TextDisplayTime

        # NOTE
            if event.midiId in [MIDI_NOTEON, MIDI_NOTEOFF]:
                if (event.data1 >= PadFirst) & (event.data1 <= PadLast):
                    event.data1 -= PadFirst # event.data1 is now 0..63
                    HeldMuteBtn = -1
                    for n in range(0, 4):
                        if self.MuteBtnStates[n]:
                            HeldMuteBtn = n
                            break
                    if (HeldMuteBtn >= 0) & (self.CurrentMode == ModeStepSeq):
                        y = event.data1 // PadsStride
                        x = event.data1 - y * PadsStride
                        if y == HeldMuteBtn:
                            SetChanLoop(HeldMuteBtn + self.GetChanRackOfs(), x + 1 + self.GetChanRackStartPos())
                    else:
                        if self.CurrentMode == ModeDrum: # drums
                            event.data2 = self.AdaptVelocity(event.data2)
                            if (self.CurrentDrumMode == DrumModeFPC) | (self.CurrentDrumMode == DrumModeFPCCenter):
                                # if (self.CurrentDrumMode == DrumModeFPC):
                                #     event.data1 += 4 # offset to match center layout
                                m = self.GetFPCNoteValue(event.data1)
                                if m >= 0:
                                    event.data1 = m
                                    if event.midiId == MIDI_NOTEON:
                                        self.PlayingNotes.append(event.data1)
                                    else:
                                        self.PlayingNotes.remove(event.data1)
                                    event.handled = False
                                    return
                                else:
                                    event.handled = True
                                    return #: nothing
                            elif self.CurrentDrumMode == DrumModeSlicex:
                                event.data1 = self.GetSlicexNoteValue(event.data1)
                                if event.midiId == MIDI_NOTEON:
                                    self.PlayingNotes.append(event.data1)
                                else:
                                    self.PlayingNotes.remove(event.data1)
                                event.handled = False
                                return
                            elif self.CurrentDrumMode == DrumModeOmni:

                                event.data1 = self.GetOmniNoteValue(event.data1)
                                if event.midiId == MIDI_NOTEON:
                                    m = 127
                                    self.PlayingChannels.append(event.data1)
                                else:
                                    m = -127
                                    if self.PlayingChannels.count(event.data1) > 0:
                                      self.PlayingChannels.remove(event.data1)

                                if utils.InterNoSwap(event.data1, 0, channels.channelCount() - 1):
                                    if not self.AltHeld:
                                        channels.midiNoteOn(event.data1, DotNote_Default, m, 0)
                                    else:
                                        self.CutPlayingNotes()
                                        channels.selectOneChannel(event.data1)
                                        self.DisplayTimedText('Chan: ' + channels.getChannelName(event.data1))

                        elif self.CurrentMode == ModeNotes: # keyboard mode
                            if channels.channelNumber(True) == -1:
                                self.PlayingNotes = bytearray(0)
                                return

                            event.data2 = self.AdaptVelocity(event.data2)
                            y = event.data1 // PadsStride
                            x = event.data1 - y * PadsStride

                            if self.CurrentNoteMode != NoteModeDualKeyb:
                                event.data1 = self.CurrentNoteGrid[x][ y]
                                event.data1 = max(0, min(event.data1, 127))
                                if event.midiId == MIDI_NOTEON:
                                    self.PlayingNotes.append(event.data1)
                                else:
                                    self.PlayingNotes.remove(event.data1)
                                event.handled = False
                                return
                            else:
                                y = PadsH- 1 - y # invert y (we want bottom to top)
                                if y % 2 == 0:
                                    # white notes
                                    event.data1 = self.GetDualKeybWhiteNoteVal(x, y)
                                    if event.data1 < 0:
                                        event.handled = True
                                        return

                                    if event.midiId == MIDI_NOTEON:
                                        self.PlayingNotes.append(event.data1)
                                    else:
                                        self.PlayingNotes.remove(event.data1)
                                    event.handled = False
                                    return
                                else:
                                    # black notes
                                    event.data1 = self.GetDualKeybBlackNoteVal(x, y)
                                    if event.data1 < 0:
                                        event.handled = True
                                        return
                                    if event.midiId == MIDI_NOTEON:
                                        self.PlayingNotes.append(event.data1)
                                    else:
                                        self.PlayingNotes.remove(event.data1)
                                    event.handled = False
                                    return
                        elif (self.CurrentMode == ModeStepSeq):
                            HandleStepSeqPad(event.midiId, event.data1)
                        elif self.CurrentMode == ModePerf:
                            # perf clips

                            y = event.data1 // PadsStride
                            x = event.data1 - y * PadsStride
                            if (x >= PadsW) | (y >= PadsH):
                                return

                            # clip release safety
                            if event.data2 == 0:
                                if self.BtnLastClip[event.data1].TrackNum != MaxInt:
                                    if (event.pmeFlags & PME_System_Safe != 0):
                                        playlist.triggerLiveClip(self.BtnLastClip[event.data1].TrackNum, self.BtnLastClip[event.data1].SubNum, self.BtnLastClip[event.data1].Flags | TLC_Release)
                                    self.BtnLastClip[event.data1].TrackNum = MaxInt
                                    event.handled = True
                                    return

                            if self.OverviewMode:
                                # overview pick
                                if event.data2 > 0:

                                    if y < PadsH:
                                        if x >= PadsW:
                                            self.SetOfs(self.GetTrackOfs(), -y - 1)
                                        else:
                                            self.SetOfs(y * PadsH, x * PadsW)
                                    self.OverviewMode = False
                                    self.RefreshPerfMode(1, playlist.trackCount())

                                event.handled = True
                            else:
                                if (event.pmeFlags & PME_System_Safe != 0):
                                    x2 = x
                                    y2 = y + self.GetTrackOfs() + 1
                                    if self.GetClipOfs() >= 0:
                                        if event.data2 > 0:
                                            # clip launch
                                            m = TLC_MuteOthers | TLC_Fill
                                            x2  += self.GetClipOfs()
                                            if ui.getSnapMode() != Snap_None:
                                                m = m | TLC_GlobalSnap # snap
                                            if self.AltHeld | self.ShiftHeld:
                                                m = m | TLC_ColumnMode # column mode (scene)
                                                if self.ShiftHeld & self.AltHeld:
                                                    m = m | TLC_WeakColumnMode # +scene
                                                elif self.ShiftHeld:
                                                    m = m | TLC_TriggerCheckColumnMode # same mode trigger

                                            playlist.triggerLiveClip(y2, x2, m) # no velocity
                                            self.BtnLastClip[event.data1].TrackNum = y2
                                            self.BtnLastClip[event.data1].SubNum = x2
                                            Flags = m
        # mute buttons
                elif event.data1 in [IDMute1, IDMute2, IDMute3, IDMute4]:
                    c = event.data1 - IDMute1 # so it's 0..3
                    self.MuteBtnStates[c] = (event.midiId == MIDI_NOTEON)
                    if event.midiId == MIDI_NOTEOFF:
                        if (not self.DidTweakLooping) & (self.CurrentMode in [ModeStepSeq, ModeNotes, ModeDrum]):
                            if not utils.InterNoSwap(c + self.GetChanRackOfs(), 0, channels.channelCount() - 1):
                                return
                            m = c + self.GetChanRackOfs();
                            if self.AltHeld:
                                self.CutPlayingNotes()
                                channels.selectOneChannel(m)
                            else:
                                if not self.ShiftHeld:
                                    channels.muteChannel(m)
                                else:
                                    channels.soloChannel(m)
                            self.DisplayTimedText('Chan: ' + channels.getChannelName(m))

                        elif self.CurrentMode == ModePerf:
                            # stop track in perf mode
                            playlist.triggerLiveClip(self.GetTrackOfs() + 1 + c, -1, TLC_MuteOthers | TLC_Fill)
                        self.DidTweakLooping = False

                # shift key
                elif event.data1 == IDShift:
                    self.ShiftHeld = event.midiId == MIDI_NOTEON
                    if event.midiId == MIDI_NOTEON:
                        self.BlinkTimer = 0

                # jogwheel button
                elif event.data1 == IDJogWheelDown:
                    

                    self.JogWheelPushed = event.midiId == MIDI_NOTEON
                    HeldMuteBtn = -1
                    for n in range(0, 3):
                        if self.MuteBtnStates[n]:
                            HeldMuteBtn = n
                            break

                    if (HeldMuteBtn >= 0) & self.JogWheelPushed:
                        p = patterns.getChannelLoopStyle(patterns.patternNumber(), HeldMuteBtn + self.GetChanRackOfs())
                        if (p != ssLoopOff):
                            if (general.getVersion() > 8):
                              patterns.burnLoop(HeldMuteBtn + self.GetChanRackOfs())
                              self.DisplayTimedText(channels.getChannelName(n + self.GetChanRackOfs()) + ': burn loop')
                            else:
                              self.DisplayTimedText('Not implemented in this version!')

                        self.DidTweakLooping = True

                    else:
                        if self.BrowserMode & self.JogWheelPushed:
                            print('wheel down browse mode')
                            if not ui.getVisible(widBrowser):
                                return
                            #SampleListForm.SetFocus
                            nodeFileType = ui.getFocusedNodeFileType()
                            if nodeFileType == -1:
                                return
                            self.DisplayTimedText(ui.getFocusedNodeCaption())
                            if nodeFileType <= -100:
                                ui.enter()
                                #transport.globalTransport(FPT_Enter, 1, PME_System | PME_FromMIDI) # expand/collapse folder
                            else:
                                #screen.MenuNext()
                                # NFX - added the ability to open menu, open in current track (SHIFT) or open in new track (ALT)
                                ui.selectBrowserMenuItem()
                                if(self.ShiftHeld) or (self.AltHeld):
                                    ui.down()
                                    if(self.AltHeld):
                                        ui.down()
                                ui.enter()

                        elif ((self.CurrentMode == ModeNotes) | (self.CurrentMode == ModeDrum)) & self.JogWheelPushed & (channels.channelNumber(True) >= 0):
                            self.LayoutSelectionMode = not self.LayoutSelectionMode
                            if self.LayoutSelectionMode:
                                if self.CurrentMode == ModeNotes:
                                    self.DisplayTimedText(self.GetNoteModeName())
                                else:
                                    self.DisplayTimedText(DrumModesNamesT[self.CurrentDrumMode])

                        elif (self.CurrentMode == ModeStepSeq) & self.JogWheelPushed & (not self.AltHeld) & (channels.channelNumber(True) >= 0):
                            self.MixerTrackSelectionMode = not self.MixerTrackSelectionMode
                            if self.MixerTrackSelectionMode & utils.Limited(channels.channelNumber(), 0, channels.channelCount() - 1) & utils.Limited(channels.getTargetFxTrack(channels.channelNumber()), 0, mixer.trackCount() - 1):
                                self.DisplayTimedText('Chan ' + str(channels.channelNumber() + 1) + chr(13) + 'Track: ' + mixer.getTrackName(channels.getTargetFxTrack(channels.channelNumber())))
                            else:
                                self.DisplayTimedText(chr(13))

                # browser button
                elif event.data1 == IDBrowser:
                    if (event.midiId == MIDI_NOTEON):

                        if self.ShiftHeld:
                            transport.globalTransport(FPT_Undo, 1, event.pmeFlags)
                        else:
                            self.BrowserMode = not self.BrowserMode
                            if self.BrowserMode:
                                self.LayoutSelectionMode = False
                                if not ui.getVisible(widBrowser):
                                    ui.showWindow(widBrowser)
                                    self.BrowserShouldClose = True

                                if ui.isBrowserAutoHide():
                                    ui.setBrowserAutoHide(False)
                                    self.BrowserShouldAutoHide = True

                                #todo SampleListForm.SetFocus
                                self.DisplayTimedText('Browser')
                            else:
                                if self.BrowserShouldAutoHide & (not ui.isBrowserAutoHide()):
                                    ui.setBrowserAutoHide(True)

                                if self.BrowserShouldClose & ui.getVisible(widBrowser):
                                    ui.showWindow(widBrowser)
                                self.BrowserShouldAutoHide = False
                                self.BrowserShouldClose = False
                                if ui.getVisible(widChannelRack):
                                    ui.setFocused(widChannelRack)
                                self.ShowCurrentPadMode()

                # Alt button
                elif event.data1 == IDAlt:
                    self.AltHeld = event.midiId == MIDI_NOTEON

                # navigation
                elif event.data1 == IDPatternUp:
                    self.PatUpBtnHeld = (event.midiId == MIDI_NOTEON)
                    if (event.midiId == MIDI_NOTEON) & (patterns.patternNumber() > 1) & ((self.CurrentMode == ModeStepSeq) | (self.CurrentMode == ModeNotes) | (self.CurrentMode == ModeDrum)):
                        patterns.jumpToPattern(patterns.patternNumber() - 1)
                    elif self.CurrentMode == ModePerf:
                        if self.ShiftHeld:
                            ofsIncrement = 1
                        else:
                            ofsIncrement = 4
                        if (event.midiId == MIDI_NOTEON):
                            self.SetOfs(self.GetTrackOfs() - ofsIncrement, self.GetClipOfs())
                        playlist.lockDisplayZone(1 + self.GetTrackOfs(), event.data2 > 0)

                    # nfx self.SendCC(IDPatternUp, int(event.midiId == MIDI_NOTEON) * SingleColorFull)

                elif event.data1 == IDPatternDown:

                    self.PatDownBtnHeld = (event.midiId == MIDI_NOTEON)
                    if (event.midiId == MIDI_NOTEON) & (patterns.patternNumber() < patterns.patternMax()) & ((self.CurrentMode == ModeStepSeq) | (self.CurrentMode == ModeNotes) | (self.CurrentMode == ModeDrum)):
                        if not self.AltHeld:
                            patterns.jumpToPattern(patterns.patternNumber() + 1)
                        else:
                            patterns.findFirstNextEmptyPat(FFNEP_DontPromptName)
                    elif self.CurrentMode == ModePerf:
                        if self.ShiftHeld:
                            ofsIncrement = 1
                        else:
                            ofsIncrement = 4
                        if (event.midiId == MIDI_NOTEON):
                            self.SetOfs(self.GetTrackOfs() + ofsIncrement, self.GetClipOfs())
                        playlist.lockDisplayZone(1 + self.GetTrackOfs(), event.data2 > 0)

                    #nfx self.SendCC(IDPatternDown, int(event.midiId == MIDI_NOTEON) * SingleColorFull)

                elif event.data1 in [IDBankL, IDBankR]:

                    self.GridUpBtnHeld = (event.midiId == MIDI_NOTEON) & (event.data1 == IDBankL)
                    self.GridDownBtnHeld = (event.midiId == MIDI_NOTEON) & (event.data1 == IDBankR)
                    if event.data1 == IDBankL:
                        m = -1
                    else:
                        m = 1
                    if (event.midiId == MIDI_NOTEON):
                        if self.AltHeld:
                            transport.globalTransport(FPT_WindowJog, m, PME_System | PME_FromMIDI)
                        elif self.BrowserMode:
                            if (event.data1 == IDBankL):
                                ui.closeActivePopupMenu()

                                #NFX added code to open in selected channel
                                ui.selectBrowserMenuItem()
                                ui.down()
                                ui.enter() 

                            elif (event.data1 == IDBankR):
                                ui.previewBrowserMenuItem()

                        elif self.CurrentMode == ModeStepSeq:

                            if len(self.HeldPads) >= 1:
                                general.saveUndo('Fire: Change step shift', UF_PR)
                                HandleHeldPadsParam(m, pShift)
                                p = self.HeldPads[0] - (self.HeldPads[0] // PadsStride) * PadsStride
                                chNum = self.GetChannelNumForPad(self.HeldPads[0])
                                if ui.getVisible(widChannelRack) & (chNum > -1):
                                    if channels.isGraphEditorVisible(): # Change to the new parameter
                                      channels.showGraphEditor(False, pShift, p, channels.getChannelIndex(chNum), 0)
                                    else: # Open the graph editor to the current channel, step & parameter
                                      #channels.showGraphEditor(False, pShift, p, heldChan.ChanIndex, 0)
                                      channels.showGraphEditor(False, pShift, p, channels.getChannelIndex(chNum), 0) # NFX

                                self.HeldPadsChanged = True
                            else:
                                if self.ShiftHeld:
                                    ofsIncrement = 1
                                else:
                                    ofsIncrement = 16
                                self.SetChanRackStartPos(self.GetChanRackStartPos() + ofsIncrement * m)

                        elif (self.KeyOffset > 0) & (self.CurrentMode == ModeNotes):
                            if self.ShiftHeld:
                                ofsIncrement = 1
                            else:
                                ofsIncrement = 12
                            self.CutPlayingNotes()
                            self.KeyOffset = utils.Limited(self.KeyOffset + ofsIncrement * m, 12, 96)
                            self.ClearBtnMap()
                            self.RefreshNotesMode()
                            self.DisplayTimedText('Root note: ' + utils.GetNoteName(self.KeyOffset))

                        elif self.CurrentMode == ModePerf:
                            if self.ShiftHeld:
                                ofsIncrement = 1
                            else:
                                ofsIncrement = 16
                            if (event.midiId == MIDI_NOTEON):
                                self.SetOfs(self.GetTrackOfs(), self.GetClipOfs() + ofsIncrement * m)
                            playlist.lockDisplayZone(1 + self.GetTrackOfs(), event.data2 > 0)

                    self.SendCC(event.data1, int(event.midiId == MIDI_NOTEON) * SingleColorFull)

                # transport
                elif event.data1 == IDPatternSong:
                    if (event.midiId == MIDI_NOTEON):
                        if not self.ShiftHeld:
                            transport.globalTransport(FPT_Loop, 1)
                        else:
                            transport.globalTransport(FPT_Metronome, 1)

                elif event.data1 == IDPlay:
                    if (event.midiId == MIDI_NOTEON):
                        if not self.ShiftHeld:
                            transport.globalTransport(FPT_Play, 1)
                        else:
                            transport.globalTransport(FPT_WaitForInput, 1)

                elif event.data1 == IDStop:
                    if (event.midiId == MIDI_NOTEON):
                        if not self.ShiftHeld:
                            transport.globalTransport(FPT_Stop, 1)
                        else:
                            transport.globalTransport(FPT_CountDown, 1)

                elif event.data1 == IDRec:
                    if (event.midiId == MIDI_NOTEON):
                        if self.AltHeld:
                            pass #ignore
                        elif not self.ShiftHeld:
                            transport.globalTransport(FPT_Record, 1)
                        else:
                            transport.globalTransport(FPT_LoopRecord, 1)

                # knobs modes
                elif event.data1 == IDKnobMode - 1:
                    if (event.midiId == MIDI_NOTEON):
                        if self.ShiftHeld:
                            if self.CurrentKnobsMode == KnobsModeChannelRack:
                                self.CurrentKnobsMode = KnobsModeMixer
                            else:
                                self.CurrentKnobsMode = KnobsModeChannelRack
                        elif self.AltHeld:
                            if self.CurrentKnobsMode == KnobsModeUser1:
                                self.CurrentKnobsMode = KnobsModeUser2
                            else:
                                self.CurrentKnobsMode = KnobsModeUser1
                        else:
                            self.CurrentKnobsMode += 1
                            if self.CurrentKnobsMode > KnobsModeUser2:
                                self.CurrentKnobsMode = KnobsModeChannelRack
                        self.DisplayTimedText(KnobsModesNamesT[self.CurrentKnobsMode])

                # button modes
                elif event.data1 == IDStepSeq:
                    if (event.midiId == MIDI_NOTEON):
                        self.LayoutSelectionMode = False
                        if not self.ShiftHeld:
                            self.CurrentMode = ModeStepSeq
                            self.ShowCurrentPadMode()
                        else:
                            self.AccentMode = not self.AccentMode
                            if self.AccentMode:
                                self.DisplayTimedText('Accent mode ON')
                            else:
                                self.DisplayTimedText('Accent mode OFF')

                elif event.data1 == IDNote:
                    if (event.midiId == MIDI_NOTEON):
                        self.LayoutSelectionMode = False
                        if not self.ShiftHeld:
                            self.NoteColorSet = int(self.AltHeld) & 1
                            self.CurrentMode = ModeNotes
                            self.ShowCurrentPadMode()
                        else:
                            transport.globalTransport(FPT_Snap, 1)

                elif event.data1 == IDDrum:
                    if (event.midiId == MIDI_NOTEON):
                        self.LayoutSelectionMode = False
                        if not self.ShiftHeld:
                            self.CurrentMode = ModeDrum
                            self.ShowCurrentPadMode()
                        else:
                            transport.globalTransport(FPT_TapTempo, 1)

                elif event.data1 == IDPerform:
                    if (event.midiId == MIDI_NOTEON):
                        self.LayoutSelectionMode = False
                        if not self.ShiftHeld:
                            self.CurrentMode = ModePerf
                            self.ShowCurrentPadMode()
                        elif self.CurrentMode == ModePerf:
                            self.OverviewMode = not self.OverviewMode
                            if self.OverviewMode:
                                self.DisplayTimedText('Overview mode')
                            else:
                                self.DisplayTimedText('Performance mode')
                            self.OnUpdateLiveMode(1, playlist.trackCount())

                elif event.data1 in [IDKnob1, IDKnob2, IDKnob3, IDKnob4]:
                    if self.ShiftHeld:
                        # turn them into a CC message so they can be ignored when linking
                        event.midiId = MIDI_CONTROLCHANGE
                        event.data2 = 0
                        event.handled = False
                        return

                    # not a big fan of this, as it way too sensitive IMHO
                    elif event.midiId == MIDI_NOTEON:
                        if (len(self.HeldPads) >= 1) & (self.CurrentMode == ModeStepSeq) & (not self.TouchingKnob):
                            self.TouchingKnob = True
                            self.KnobTouched = event.data1
                            param = -1
                            if event.data1 == IDKnob1:
                                param = pVelocity
                            elif event.data1 == IDKnob2:
                                param = pPan
                            elif event.data1 == IDKnob3:
                                param = pModX
                            elif event.data1 == IDKnob4:
                                param = pModY

                            if len(self.HeldPads) > 0:
                                p = self.HeldPads[0] - (self.HeldPads[0] // PadsStride) * PadsStride
                                chNum = self.GetChannelNumForPad(self.HeldPads[0])

                                if ui.getVisible(widChannelRack) & (chNum > -1) & (param >= 0):
                                    if channels.isGraphEditorVisible(): # Change to the new parameter
                                        channels.showGraphEditor(False, param, p, channels.getChannelIndex(chNum), 0)
                                    else: # Open the graph editor to the current channel, step & parameter
                                        channels.showGraphEditor(False, param, p, channels.getChannelIndex(chNum), 0)

                                self.UHP = general.getUndoHistoryPos()
                                self.UHC = general.getUndoHistoryCount()
                                self.UHL = general.getUndoHistoryLast()
                                self.ChangeFlag = False
                                general.saveUndo('Fire: Change ' + ParamNames[param], UF_PR, True)

                    elif self.KnobTouched == event.data1:
                        self.TouchingKnob = False
                        if self.ChangeFlag:
                            self.ChangeFlag = False
                        else:
                            general.setUndoHistoryPos(self.UHP)
                            general.setUndoHistoryCount(self.UHC)
                            general.setUndoHistoryLast(self.UHL)

            event.handled = True

    def ScaleColor(self, ScaleValue, h, s, v):

        s = min(1.0, (s * 2) * (self.FLFirePadSaturation / 128))
        v = (v * ScaleValue) * (self.FLFirePadBrightness / 128)
        if v > 0.0:
            v = max(v, 0.1)
        r, g, b = utils.HSVtoRGB(h, s, v)
        result = (round((r * 255) - RoundAsFloorS) << 16) + (round((g * 255) - RoundAsFloorS) << 8) + (round((b * 255) - RoundAsFloorS))
        return result, h, s, v

    def OnRefresh(self, Flags):
        self.RefreshTransport()

    def RefreshDrumMode(self, clearFirst = False):
        colors = [0] * 6

        def AddPadDataRGB(x, y, r, g, b):

            if self.BtnMap[x + y * PadsStride] == ((r << 16) + (g << 8) + b):
                return
            dataOut.append(x + y * PadsStride)
            dataOut.append(r)
            dataOut.append(g)
            dataOut.append(b)
            self.BtnMap[x + y * PadsStride] = (r << 16) + (g << 8) + b

        def AddPadDataRGB2(x, y, c):

            if self.BtnMap[x + y * PadsStride] == c:
                return
            dataOut.append(x + y * PadsStride)
            dataOut.append((c & 0x7F0000) >> 16)
            dataOut.append((c & 0x007F00) >> 8)
            dataOut.append((c & 0x7F))
            self.BtnMap[x + y * PadsStride] = c

        # ****

        dataOut = bytearray(0)

        chan = channels.selectedChannel(1)

        if chan >= 0:
            playingNote = self.GetCurStepParam(chan, pPitch)
        else:
            playingNote = -1

        h = 240.0
        s = 0.0
        colors[0] = 0 # unused pad
        v = 0.25
        res, h, s, v = self.ScaleColor(1.0, h, s, v)
        colors[1] = (res & 0xFEFEFE) >> 1 # playing note (from FL)
        v = 1.0
        res, h, s, v = self.ScaleColor(1.0, h, s, v)
        colors[2] = (res & 0xFEFEFE) >> 1 # playing note (by the user)
        h, s, v = utils.RGBToHSVColor(self.KeyColors[self.NoteColorSet][9])
        res, h, s, v = self.ScaleColor(1.0, h, s, v)
        colors[3] = (res & 0xFEFEFE) >> 1 # default drum pad color - bank A
        h, s, v = utils.RGBToHSVColor(self.KeyColors[self.NoteColorSet][10])
        res, h, s, v = self.ScaleColor(1.0, h, s, v)
        colors[4] = (res & 0xFEFEFE) >> 1 # default drum pad color - bank B
        h, s, v = utils.RGBToHSVColor(self.KeyColors[self.NoteColorSet][11])
        res, h, s, v = self.ScaleColor(1.0, h, s, v)
        colors[5] = (res & 0xFEFEFE) >> 1 # default drum pad color - slicex

        if clearFirst:
            for pad in range(0, 64):
                OG_plus_nfx_Helpers.SetPadColor(pad, 0,0) 
            self.FPCNoteMap.clear()

        if (self.CurrentDrumMode == DrumModeFPC) | (self.CurrentDrumMode == DrumModeFPCCenter):
            if self.CurrentDrumMode == DrumModeFPC:
                n = 4
            else:
                n = 0

            # nfx - code to draw FPC with colors
            drumPads = OG_plus_nfx_Helpers.getFPCPads(self.CurrentDrumMode == DrumModeFPC)

            for idx, pad in enumerate(drumPads):
                chanIdx = channels.selectedChannel()
                color = 0xFF0000
                semitone = -1
                dim = 3
                
                if(OG_plus_nfx_Helpers.isFPCChannel(chanIdx)):
                    dim = 1 
                    color = plugins.getPadInfo(chanIdx, -1, OG_plus_nfx_Helpers.PAD_Color, idx)
                    semitone = plugins.getPadInfo(chanIdx, -1, OG_plus_nfx_Helpers.PAD_Semitone, idx)
                    if (playingNote >= 0) & (semitone == playingNote):
                        dim = 0
                    elif self.PlayingNotes.find(semitone) >= 0:
                        dim = 3

                self.FPCNoteMap[pad] = semitone
                OG_plus_nfx_Helpers.SetPadColor(pad, color, dim)


        elif self.CurrentDrumMode == DrumModeSlicex:
            for x in range(0, PadsW):
                for y in range(0, PadsH):
                    if (playingNote >= 0) & (self.GetSlicexNoteValue(x + y * PadsStride) == playingNote):
                        AddPadDataRGB2(x, y, colors[1]) # playing note (from FL)
                    elif self.PlayingNotes.find(self.GetSlicexNoteValue(x + y * PadsStride)) >= 0:
                        AddPadDataRGB2(x, y, colors[2]) # playing note (by the user)
                    else:
                        AddPadDataRGB2(x, y, colors[5]) # default pad color

        elif self.CurrentDrumMode == DrumModeOmni:  # show a pad per channel
            maxChan = min(channels.channelCount(), 64)
            for n in range(0, maxChan):
                y = n // PadsStride
                x = n - y * PadsStride
                y = PadsH- 1 - y # invert y (we want bottom to top)
                if (general.getVersion() > 8):
                  if(channels.getActivityLevel(n) > 0):
                    AddPadDataRGB2(x, y, colors[1]) # playing note (from FL)
                if n in self.PlayingChannels:
                    AddPadDataRGB2(x, y, colors[2]) # playing note (by the user)
                else:
                    c = channels.getChannelColor(n)
                    h, s, v = utils.RGBToHSVColor(c)
                    c, h, s, v = self.ScaleColor(1.0, h, s, v)
                    r = ((c >> 16) & 0xFF) // 2
                    b = (c & 0xFF) // 2
                    g = ((c >> 8) & 0xFF) // 2
                    AddPadDataRGB(x, y, r, g, b)

            # turn off remaining pads
            if maxChan < 63:
                for n in range(maxChan, 64):
                    y = n // PadsStride
                    x = n - y * PadsStride
                    y = PadsH- 1 - y # invert y (we want bottom to top)
                    AddPadDataRGB2(x, y, colors[0]) # unused pad

        if len(dataOut) > 0:
            screen.unBlank(True)
            self.SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)

        self.RefreshStepSeq(True)

    def RefreshNotesMode(self):

        def AddPadDataRGB(x, y, r, g, b):
            if self.BtnMap[x + y * PadsStride] == (r << 16) + (g << 8) + b:
                return
            dataOut.append(x + y * PadsStride)
            dataOut.append(r)
            dataOut.append(g)
            dataOut.append(b)
            self.BtnMap[x + y * PadsStride] = (r << 16) + (g << 8) + b

        def splitColor(c):
            h, s, v = utils.RGBToHSVColor(c)
            c, h, s, v = self.ScaleColor(1.0, h, s, v)
            r2, g2, b2 = utils.HSVtoRGB(h, s, v)
            r = round((r2 * 255) - RoundAsFloorS) >> 1
            g = round((g2 * 255) - RoundAsFloorS) >> 1
            b = round((b2 * 255) - RoundAsFloorS) >> 1
            return r, g, b

     #****
        dataOut = bytearray(0)
        chan = channels.selectedChannel(1)

        if chan >= 0:
            playingNote = self.GetCurStepParam(chan, pPitch)
        else:
            playingNote = -1

        self.OldNoteMode = self.CurrentNoteMode
        r0, g0, b0 = splitColor(self.KeyColors[self.NoteColorSet][0])
        r1, g1, b1 = splitColor(self.KeyColors[self.NoteColorSet][1])
        r2, g2, b2 = splitColor(self.KeyColors[self.NoteColorSet][2])
        r3, g3, b3 = splitColor(self.KeyColors[self.NoteColorSet][3])
        r4, g4, b4 = splitColor(self.KeyColors[self.NoteColorSet][4])

        if self.CurrentNoteMode != NoteModeDualKeyb:
            currentScale = self.CurrentNoteMode - 1
            OG_plus_harmonicScales.BuildNoteGrid(self.CurrentNoteGrid, PadsW, PadsH, self.KeyOffset, 0, currentScale, 3)

            for x in range(0, PadsW):
                for y in range(0, PadsH):
                    if (playingNote >= 0) & (self.CurrentNoteGrid[x][ y] + self.KeyOffset == playingNote):
                        AddPadDataRGB(x, y, r2, g2, b2) # playing note (from FL)
                    elif self.PlayingNotes.find(self.CurrentNoteGrid[x][ y]) >= 0:
                        AddPadDataRGB(x, y, r3, g3, b3) # playing note (by the user)
                    elif OG_plus_harmonicScales.IsRootNote(self.CurrentNoteGrid[x][ y], currentScale, self.KeyOffset):
                        AddPadDataRGB(x, y, r4, g4, b4) # root note
                    elif OG_plus_harmonicScales.IsBlackKey(self.CurrentNoteGrid[x][ y]):
                        AddPadDataRGB(x, y, r0, g0, b0) # black key
                    else:
                        AddPadDataRGB(x, y, r1, g1, b1) # white key

        else:
            # Dual keyboard mode
            for x in range(0, PadsW):
                for y in range(0, PadsH):
                    if y % 2 == 0:
                        # upper row
                        if x in [1, 2, 4, 5, 6, 8, 9, 11, 12, 13, 15]:
                            if (playingNote >= 0) & (self.GetDualKeybBlackNoteVal(x, PadsH- 1 - y) == playingNote):
                                AddPadDataRGB(x, y, r2, g2, b2) # playing note (from FL)
                            elif self.PlayingNotes.find(self.GetDualKeybBlackNoteVal(x, PadsH- 1 - y)) >= 0:
                                AddPadDataRGB(x, y, r3, g3, b3) # playing note (by the user)
                            else:
                                AddPadDataRGB(x, y, r0, g0, b0) # black note
                        else:
                            AddPadDataRGB(x, y, 0, 0, 0) # nothing
                    else:
                        if (playingNote >= 0) & (self.GetDualKeybWhiteNoteVal(x, PadsH- 1 - y) == playingNote):
                            AddPadDataRGB(x, y, r2, g2, b2) # playing note (from FL)
                        elif self.PlayingNotes.find(self.GetDualKeybWhiteNoteVal(x, PadsH- 1 - y)) >= 0:
                            AddPadDataRGB(x, y, r3, g3, b3) # playing note (by the user)
                        elif (x % 7) == 0:
                            AddPadDataRGB(x, y, r4, g4, b4) # root note
                        else:
                            AddPadDataRGB(x, y, r1, g1, b1) # white note

        if len(dataOut) > 0:
            screen.unBlank(True)
            self.SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)

        self.RefreshStepSeq(True)

    def AddPadDataCol(self, dataOut, x, y, Color):
        if self.BtnMap[x + y * PadsStride] == Color:
            return
        r = ((Color >> 16) & 0xFF) // 2
        b = (Color & 0xFF) // 2
        g = ((Color >> 8) & 0xFF) // 2
        dataOut.append(x + y * PadsStride)
        dataOut.append(utils.Limited(r, 0, 0x7F))
        dataOut.append(utils.Limited(g, 0, 0x7F))
        dataOut.append(utils.Limited(b, 0, 0x7F))
        self.BtnMap[x + y * PadsStride] = Color

    def RefreshPerfMode(self, FirstTrackNum, LastTrackNum):
        OverviewColT = ((0x00000000, 0x00200000, 0x04200000), (0x00000110, 0x0000063F, 0x0400063F))
        OnLight = 0x48
        OffLight = -0x1A

    #***
        dataOut = bytearray(0)
        if self.OverviewMode:
            # overview
            R = utils.TRect(0, 0, 0, 0)
            R2 = utils.TRect(0, 0, 0, 0)
            R2.Left = self.GetClipOfs()
            if R2.Left < 0:
                R2.Left -= 128
            R2.Right = R2.Left + PadsW - 1
            R2.Top = 1 + self.GetTrackOfs()
            R2.Bottom = R2.Top + PadsH - 1
            for y in range(0, PadsH):
                for x in range(0, PadsW):
                    R.Left = x * PadsW
                    R.Right = R.Left + PadsW - 1
                    R.Top = 1 + y * PadsH
                    R.Bottom = R.Top + PadsH - 1
                    o = patterns.getBlockSetStatus(R.Left, R.Top, R.Right, R.Bottom)
                    c = OverviewColT[utils.rectOverlapEqual(R, R2), o]
                    hh, ss, vv = utils.RGBToHSV(c)
                    vv = 1
                    c, hh, ss, vv = self.ScaleColor(1.0, hh, ss, vv)
                    self.AddPadDataCol(dataOut, x, y, c)

            if len(dataOut) > 0:
                screen.unBlank(True)
                self.SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)

        else:
            ofs = self.GetTrackOfs()
            i = 0
            self.PlayingPads.clear()
            for y in range(max(FirstTrackNum - ofs, 1), min(LastTrackNum - ofs, PadsH) + 1):
                for x in range(0, PadsW):  # clips
                    m = self.GetClipOfs() + x
                    o = playlist.getLiveBlockStatus(y + ofs, m)
                    if (o & 1) == 0:
                        c = 0
                    else:
                        c = playlist.getLiveBlockColor(y + ofs, m)
                        hh, ss, vv = utils.RGBToHSVColor(c)
                        vv = 1
                        l = 1
                        if ((o & 2) != 0): # scheduled
                            l = 0.25

                        if ((o & 4) != 0): # playing
                            l = 1
                            vv = 1
                            ss = 0
                        c, hh, ss, vv = self.ScaleColor(l, hh, ss, vv)

                        if ((o & 4) != 0): # playing
                          self.PlayingPads.append([x, y - 1, c])

                    self.AddPadDataCol(dataOut, x, y - 1, c)

                # mute (track stop) buttons
                o = playlist.getLiveStatus(y + ofs, LB_Status_Simple)
                if (i < 4):
                    self.SendCC(IDMute1 + i, int(o == 1) * SingleColorFull)
                    self.SendCC(IDTrackSel1 + i, int(o == 1) * SingleColorFull)

                i += 1

        if len(dataOut) > 0:
            screen.unBlank(True)
            self.SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)

    def RefreshStepSeq(self, MuteSelOnly):

        if not device.isAssigned():
            return

        dataOut = bytearray(0)
        crOfs = self.GetChanRackOfs()
        maxChan = min(crOfs + 3, channels.channelCount() - 1)

        for n in range(crOfs, crOfs + 4):
            mute = IDMute1 + (n - crOfs) % 4
            slct = IDTrackSel1 + (n - crOfs) % 4
            if n <= maxChan:
                c = channels.getChannelColor(n)
                if c == CT_ColorT[CT_Sampler]:
                    c = 0xC8C8C8 # white for default pad color
                h, s, v = utils.RGBToHSVColor(c)
                if channels.isChannelMuted(n):
                    self.SendCC(mute, SingleColorOff)
                else:
                    self.SendCC(mute, SingleColorFull)

                if (self.IsLockedByReceiveNotesFrom() >= 0) & (self.CurrentMode == ModeNotes): # no point in showing the selected track in notes mode when the device uses "receives notes from"
                    if self.BlinkTimer >= BlinkSpeed:
                        self.SendCC(slct, SingleColorOff)
                    else:
                        self.SendCC(slct, SingleColorFull)
                else:
                    if channels.isChannelSelected(n):
                        self.SendCC(slct, SingleColorFull)
                    else:
                        self.SendCC(slct, SingleColorOff)

                # steps
                if not MuteSelOnly:
                    ps = self.GetChanRackStartPos()
                    for p in range(ps, ps + 16):
                        blinking = False
                        playing = p == self.CurStep
                        dest = ((n - self.GetChanRackOfs()) * 16) + (p - self.GetChanRackStartPos())
                        if playing:  # check if playing
                            r = 0x0F
                            g = 0x0F
                            b = 0x0F
                            mapVal = 0xFFFFFF
                        else:  # check if blinking
                            mapVal = 0
                            r = 0
                            g = 0
                            b = 0
                            for m in range(0, len(self.HeldPads)):
                                if self.HeldPads[m] == dest:
                                    blinking = True
                                    if self.BlinkTimer < BlinkSpeed:
                                        h2 = h
                                        s2 = s
                                        v2 = v
                                        v2 = 1
                                        c, h2, s2, v2 = self.ScaleColor(utils.Limited(self.GetStepParam(dest, pVelocity) / 127, 0.1, 1), h2, s2, v2)
                                        r2, g2, b2 = utils.HSVtoRGB(h2, s2, v2)
                                        r = round((r2 * 255) - RoundAsFloorS) >> 1
                                        g = round((g2 * 255) - RoundAsFloorS) >> 1
                                        b = round((b2 * 255) - RoundAsFloorS) >> 1
                                        c2 = ((r & 0xFF) << 16) + ((g & 0xFF) << 8) + (b & 0xFF)
                                        mapVal = c2
                                    else:
                                        r = 0
                                        g = 0
                                        b = 0
                                        mapVal = 0
                                    break

                            if not blinking:
                                if channels.getGridBitWithLoop(n, p) > 0:
                                    h2 = h
                                    s2 = s
                                    v2 = v
                                    v2 = 1
                                    res, h2, s2, v2 = self.ScaleColor(utils.Limited(self.GetStepParam(dest, pVelocity) / 127, 0.1, 1), h2, s2, v2)
                                    r2, g2, b2 = utils.HSVtoRGB(h2, s2, v2)
                                    r = round((r2 * 255) - RoundAsFloorS) >> 1
                                    g = round((g2 * 255) - RoundAsFloorS) >> 1
                                    b = round((b2 * 255) - RoundAsFloorS) >> 1
                                    c2 = ((r & 0xFF) << 16) + ((g & 0xFF) << 8) + (b & 0xFF)
                                    mapVal = c2
                                else:
                                    r = 0
                                    g = 0
                                    b = 0
                                    mapVal = 0

                        if self.BtnMap[dest] != mapVal:
                            dataOut.append(dest)
                            dataOut.append(r)
                            dataOut.append(g)
                            dataOut.append(b)
                            self.BtnMap[dest] = mapVal

            else:
                self.SendCC(mute, SingleColorOff)
                self.SendCC(slct, SingleColorOff)
                for p in range(0, 16):
                    dest = (n - self.GetChanRackOfs()) * 16 + p
                    playing = (p + self.GetChanRackStartPos()) == self.CurStep
                    if self.BtnMap[dest] != int(playing) * 0xFFFFFF:
                        dataOut.append(dest)
                        if playing:
                            dataOut.append(0x1F)
                            dataOut.append(0x1F)
                            dataOut.append(0x1F)
                            self.BtnMap[dest] = 0xFFFFFF
                        else:
                            dataOut.append(0)
                            dataOut.append(0)
                            dataOut.append(0)
                            self.BtnMap[dest] = 0

        if len(dataOut) > 0:
            screen.unBlank(True)
            # now send step data
        if (len(dataOut) > 0) & (not MuteSelOnly):
            self.SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)

    def RefreshAnalyzerMode(self):

        BtnMapTemp = [0] * 64

        def GetAnalyzerBars(): #todo

            bandsSrcL = 0
            #if ScopeVisMode == 2:
            #    LockMixThread()
            #    if Assigned(MainForm.MixScope.WAVSample):
            #        bandsSrcL = MixScopeBandsL
            #        if not Assigned(MixScopeBands) | (bandsSrcL < 0):
            #            bandsSrcL = 0
            #        if bandsSrcL > 0:
            #bandsSrcL = utils.Limited(bandsSrcL, 1, 512)
            #            Setlen(bandsSrc, bandsSrcL)
            #            IppsCopy_32F(MixScopeBands, @bandsSrc[0], bandsSrcL)

            #    UnlockMixThread()

            bandsDstL = PadsW
            bandsDst = [0] * bandsDstL
            for i in range(0, bandsDstL - 1):
                bandsDst[i] = 0.0
            if bandsSrcL > 0:
                if bandsSrcL > bandsDstL:
                    bandSrcStep = 1
                    bandDstStep = bandsDstL / bandsSrcL
                else:
                    bandDstStep = 1
                    bandSrcStep = bandsSrcL / bandsDstL

                bandSrc = 0
                bandDst = 0
                mx = 0
                while (bandSrc < bandsSrcL) & (bandDst < bandsDstL):
                    i = utils.Limited(round(bandSrc - RoundAsFloorS), 0, bandsSrcL - 1)
                    mx = utils.max(mx, bandsSrc[i])
                    i2 = utils.Limited(round(bandDst - RoundAsFloorS), 0, bandsDstL - 1)
                    bandsDst[i2] = utils.max(bandsDst[i2], mx)
                    if utils.Limited(round((bandDst + bandDstStep) - RoundAsFloorS), 0, bandsDstL - 1) != i:
                        mx = 0.0
                    bandSrc = bandSrc + bandSrcStep
                    bandDst = bandDst + bandDstStep

            for x in range(0, PadsW):
                mx = utils.Limited((bandsDst[x] * 1) - 0.0, 0.0, 1.0)
                if mx < 0.1:
                    i = -1
                elif (mx < 0.50):
                    i = 0
                elif (mx < 0.70):
                    i = 1
                elif (mx < 0.90):
                    i = 2
                else:
                    i = 3
                for y in range(0, PadsH):
                    padNum = (((PadsH - 1) - y) * PadsW) + x
                    if y > i:
                        c = bgColor
                    else:
                        c = rowColors[y]
                    BtnMapTemp[padNum] = c

        def GetPeakVol(section):

            mx = 0
            if (general.getVersion() > 8):
              mx = mixer.getLastPeakVol(section)
            mx = utils.Limited(mx * 1, 0.0, 1.0) * (PadsH - 1)
            i = round(mx - RoundAsFloorS)
            x = 0
            h = self.AnalyzerHue
            s = 1.0
            v = 1.0
            res, h, s, v = self.ScaleColor(1.0, h, s, v)
            c1 = (res & 0xFEFEFE) >> 1
            res, h, s, v = self.ScaleColor(0.25, h, s, v)
            c2 = (res & 0xFEFEFE) >> 1
            for y in range(0, PadsH):
                padNum = (((PadsH - 1) - y) * PadsW) + x
                if y > i:
                    c = bgColor
                elif y == i:
                    c = c1
                else:
                    c = c2
                BtnMapTemp[padNum] = c

        def ScrollBarsX():

            for y in range(0, PadsH):
                for x in reversed(range(1, PadsW)):
                    BtnMapTemp[(PadsW * y) + x] = BtnMapTemp[(PadsW * y) + x - 1]
                BtnMapTemp[(PadsW * y) + 0] = 0

        def ScrollBarsY():

            for y in range(1, PadsH):
                for x in range(0, PadsW):
                    BtnMapTemp[(PadsW * (y - 1)) + x] = BtnMapTemp[(PadsW * y) + x]

            for x in range(0, PadsW):
                BtnMapTemp[(PadsW * (PadsH - 1) + x)] = 0

        def FlipBarsX():

            for y in range(0, PadsH):
                for x in range(0, (PadsW // 2)):
                    c = BtnMapTemp[(PadsW * y) + x]
                    BtnMapTemp[(PadsW * y) + x] = BtnMapTemp[(PadsW * y) + ((PadsW - 1) - x)]
                    BtnMapTemp[(PadsW * y) + ((PadsW - 1) - x)] = c

        def FlipBarsY():
            for x in range(0, PadsW):
                for y in range(0, (PadsH // 2)):
                    c = BtnMapTemp[(PadsW * y) + x]
                    BtnMapTemp[(PadsW * y) + x] = BtnMapTemp[(PadsW * (PadsH - 1 - y)) + x]
                    BtnMapTemp[(PadsW * (PadsH - 1 - y)) + x] = c

    #***
        if not device.isAssigned():
            return

        bgColor = 0x000000
        rowColors = [0] * PadsH

        for i in range(0, PadsH):
            if (i + 5) <= len(self.KeyColors[self.NoteColorSet]):
                c = (self.KeyColors[self.NoteColorSet][i + 5])
                h, s, v = utils.RGBToHSVColor(c)
                res, h, s, v = self.ScaleColor(1.0, h, s, v)
                c = (res & 0xFEFEFE) >> 1
            rowColors[i] = c

        for padNum in range(0, len(BtnMapTemp)):
            BtnMapTemp[padNum] = self.BtnMap[padNum]

        if self.AnalyzerFlipX:
            FlipBarsX()

        if self.analyzerFlipY:
            FlipBarsY()

        if self.AnalyzerScrollX:
            ScrollBarsX()

        if self.AnalyzerScrollY:
            ScrollBarsY()

        if self.AnalyzerMode == AnalyzerBars:
            GetAnalyzerBars()

        if self.AnalyzerMode == AnalyzerPeakVol:
            GetPeakVol(self.AnalyzerChannel)

        if self.AnalyzerFlipX:
            FlipBarsX()

        if self.analyzerFlipY:
            FlipBarsY()

        dataOut = bytearray((PadsW * PadsH * 4) + 16)
        lenP = 0

        for padNum in range(0, len(BtnMapTemp)):
            if ((BtnMapTemp[padNum] & 0xFF000000) != 0) | (BtnMapTemp[padNum] != self.BtnMap[padNum]):
                if ((BtnMapTemp[padNum] & 0xFF000000) != 0):
                    BtnMapTemp[padNum] = 0
                self.BtnMap[padNum] = BtnMapTemp[padNum]
                lenP += 4
                dataOut[lenP - 4] = padNum
                c = self.BtnMap[padNum]
                dataOut[lenP - 3] = (c & 0x7F0000) >> 16
                dataOut[lenP - 2] = (c & 0x007F00) >> 8
                dataOut[lenP - 1] = (c & 0x00007F) >> 0

        if (lenP > 0):
            dataOut = dataOut[: lenP]  #todo check if needed
            self.SendMessageToDevice(MsgIDSetRGBPadLedState, lenP, dataOut)

    def RefreshTransport(self):

        if (not device.isAssigned()) | self.ShiftHeld:
            return

        if transport.isPlaying() == PM_Playing:
            val = DualColorFull1
            val2 = SingleColorHalfBright
        else:
            val = DualColorHalfBright2
            val2 = SingleColorOff

        if (transport.isPlaying() != PM_Playing) & (not self.ShiftHeld): #donn't update during playback, it's already handled by UpdateBeatIndicator
            self.SendCC(IDPlay, val)
        self.SendCC(IDStop, val2)
        
        if transport.isRecording():
            val = DualColorFull1
        else:
            val = DualColorHalfBright2
        self.SendCC(IDRec, val)

        if transport.getLoopMode() == SM_Pat:
            val = DualColorFull2
        else:
            val = DualColorFull1
        self.SendCC(IDPatternSong, val)

    def SendCC(self, ID, Val):

        if (not device.isAssigned()):
            return
        device.midiOutNewMsg(MIDI_CONTROLCHANGE + (ID << 8) + (Val << 16), ID)

    def SendMessageToDevice(self, ID, l, data):

        if not device.isAssigned():
            return
        
        msg = bytearray(7 + l + 1)
        lsb = l & 0x7F
        msb = (l & (~ 0x7F)) >> 7

        msg[0] = MIDI_BEGINSYSEX
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
        msg[len(msg) - 1] = MIDI_ENDSYSEX
        device.midiOutSysex(bytes(msg))
        
    def DispatchMessageToDeviceScripts(self, ID, data1, data2, data3):

        if not device.isAssigned():
            return

        l = 6
        data = bytearray(l)
               
        data[0] = data1 & 0x7F
        data[1] = (data1 & (~ 0x7F)) >> 7
        data[2] = data2 & 0x7F
        data[3] = (data2 & (~ 0x7F)) >> 7
        data[4] = data3 & 0x7F
        data[5] = (data3 & (~ 0x7F)) >> 7          
        
        msg = bytearray(7 + l + 1)
        lsb = l & 0x7F
        msb = (l & (~ 0x7F)) >> 7

        msg[0] = MIDI_BEGINSYSEX
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
        msg[len(msg) - 1] = MIDI_ENDSYSEX
        device.dispatch(-1, 0xF4, bytes(msg))

    def SetAsMasterDevice(self, Value):
    
        receiverCount = device.dispatchReceiverCount()
        otherDeviceFound = receiverCount > 0 

        if (not otherDeviceFound) & Value:
            return # no need to switch to master if there's only one device
        if Value == True:
            self.MultiDeviceMode = MultiDev_Master
        else:
            self.MultiDeviceMode = MultiDev_Single
        self.MasterDevice = -1
        
        if Value:        
            self.DispatchMessageToDeviceScripts(SM_SetAsSlave, device.getPortNumber(), 0, 0)
            self.DispatchMessageToDeviceScripts(SM_MasterDeviceChanRackOfs, self.ChanRackOfs, 0, 0)
            self.DispatchMessageToDeviceScripts(SM_MasterDeviceChanStartPos, self.ChanRackStartPos, 0, 0)
        else:
            self.DispatchMessageToDeviceScripts(SM_SetAsSingle, device.getPortNumber(), 0, 0)
            self.SetAsSingleDevice 
                    
        if Value:
            self.DisplayTimedText('Multi-device')
        else:
            self.DisplayTimedText('Single device')

    def SetAsSingleDevice(self):
        self.MultiDeviceMode = MultiDev_Single
        self.MasterDevice = -1
        self.SlavedDevices = {}
        self.SlaveLayoutSelectionMode = False
        self.DisplayTimedText('Single device')

    def SetAsSlaveDevice(self, Master):

        self.MultiDeviceMode = MultiDev_Slave
        self.MasterDevice = Master  #master device port number
        self.SlavedDevices = {}
        self.SlaveLayoutSelectionMode = True # so the slave layout selection menu shows up immediately on the slaved device
        self.DisplayTimedText(SlaveModeLayoutNamesT[self.SlaveModeLayout])

    # removed the func because it is already define on line 351
    # def Sign(self, Value):
    #     if Value >= 0: 
    #         return 1
    #     else: 
    #         return -1

    def SetChanRackOfs(self, Value, Dispatch = True):

        if self.MultiDeviceMode != MultiDev_Slave:
            self.ChanRackOfs = utils.Limited(Value, 0, channels.channelCount() - 1)
            if Dispatch:
              self.DispatchMessageToDeviceScripts(SM_MasterDeviceChanRackOfs, self.ChanRackOfs, 0, 0)

            if ui.getVisible(widChannelRack):
                R = self.GetGridRect(ModeStepSeq)
                ui.crDisplayRect(R.Left, R.Top, R.Right, R.Bottom, 2000)
        else:  #slave to master
            if Dispatch:
                self.DispatchMessageToDeviceScripts(SM_SlaveDeviceRackOfs, Value - self.GetChanRackOfs() + 128, 0, 0)
                self.MasterDeviceChanRackOfs = max(self.MasterDeviceChanRackOfs + Value - self.GetChanRackOfs(), 0)

        self.DisplayTimedText('Channels ' + str(self.GetChanRackOfs() + 1) + '-' + str(self.GetChanRackOfs() + 4))

    def SetChanRackStartPos(self, Value, Dispatch = True):

        if self.MultiDeviceMode != MultiDev_Slave:
            self.ChanRackStartPos = utils.Limited(Value, 0, patterns.patternMax() - 16) # TODO check slaves for bounds

            self.DispatchMessageToDeviceScripts(SM_MasterDeviceChanStartPos, self.ChanRackStartPos, 0, 0)
            
            if ui.getVisible(widChannelRack):
                R = self.GetGridRect(ModeStepSeq)
                ui.crDisplayRect(R.Left, R.Top, R.Right, R.Bottom, 2000)
        else:   #slave to master
            if Dispatch:
                self.DispatchMessageToDeviceScripts(SM_SlaveDeviceStartPos, Value - self.GetChanRackStartPos() + 128, 0, 0)

        self.DisplayTimedText('Grid offset: ' + str(self.GetChanRackStartPos()))

    def SetOfs(self, TrackOfsValue, ClipOfsValue, Dispatch= True):

        oTOfs = self.TrackOfs
        oCOfs = self.ClipOfs
        if self.CurrentMode == ModePerf:
            if self.MultiDeviceMode != MultiDev_Slave:      # is master
                self.TrackOfs = utils.Limited(TrackOfsValue, 0, playlist.trackCount() - PadsH)
                R = self.GetGridRect(self.CurrentMode)
                pw = R.Width()

                n = playlist.liveTimeToBlockNum(max(playlist.getSongStartTickPos() - 1, 0))
                self.ClipOfs = utils.Limited(ClipOfsValue, 0, max(n - (pw - 1), 0))

                if Dispatch: # dispatch to slave
                  self.DispatchMessageToDeviceScripts(SM_MasterDeviceSetOfs, self.TrackOfs + 128, self.ClipOfs + 128, 0)

            else:  # is slave
                if Dispatch:  # dispatch to master
                  self.DispatchMessageToDeviceScripts(SM_SlaveDeviceSetOfs, TrackOfsValue - self.GetTrackOfs() + 128, ClipOfsValue - self.GetClipOfs() + 128, 0)
                  self.DispatchMessageToDeviceScripts(SM_UpdateLiveMode, 0, 0, 0)
                  self.OnUpdateLiveMode(1, playlist.trackCount())
                  return

            if device.isAssigned():
                self.OnUpdateLiveMode(1, playlist.trackCount())

            if playlist.getDisplayZone() != 0:
                # Get the actual displayed rectangle so we can compare it to the current view
                R = utils.TRect(playlist.liveBlockNumToTime(self.ClipOfs), self.TrackOfs, playlist.liveBlockNumToTime(self.ClipOfs + PadsW - 1), self.TrackOfs + PadsH - 1)
                if oCOfs > self.ClipOfs: # User moved selection left
                    playlist.scrollTo(0, R.Left)
                elif oCOfs < self.ClipOfs: # User moved selection right
                    playlist.scrollTo(1, R.Left, R.Right)
                elif oTOfs < self.TrackOfs: # User moved down
                    R.Bottom = min(R.Bottom + 1, playlist.trackCount() - PadsH)
                    playlist.scrollTo(2, 0, 0, R.Bottom)
                elif oTOfs > self.TrackOfs: # User moved up
                    R.Top = min(R.Top + 1, playlist.trackCount() - PadsH)
                    playlist.scrollTo(3, 0, 0, R.Top)

                self.OnDisplayZone()

    def SetStepParam(self, Step, Param, Value):

        y = Step // PadsStride
        x = Step - y * PadsStride
        chanIndex = y + self.GetChanRackOfs()
        Step =  x + self.GetChanRackStartPos() #NFX

        if utils.InterNoSwap(chanIndex, 0, channels.channelCount() - 1):
            if channels.getGridBit(chanIndex, Step) == 0:
                channels.setGridBit(chanIndex, Step, 1) # make sure the step is enabled | it won't work !
            index = channels.getChannelIndex(chanIndex) # NFX
            patNum = patterns.patternNumber() # NFX
            Step =  x + self.GetChanRackStartPos() # NFX
            #print('SetStepParam' ,index, patNum, Step , Param, Value, False) 
            if(general.getVersion() >= 37):
                channels.setStepParameterByIndex(index, patNum, Step , Param, Value)  # removed last parameter - NFX
            else:
                channels.setStepParameterByIndex(index, patNum, Step , Param, Value, 1)

    def ShowCurrentPadMode(self):

        self.DisplayTimedText(ModeNamesT[self.CurrentMode])

    def OnUpdateBeatIndicator(self, Value):

        dataOut = bytearray(0)
        if not device.isAssigned():
            return
        if Value == 0:
            val = 0
        elif Value == 1:
            val = DualColorFull2
        elif Value == 2:
            val = DualColorFull1
        else:
            val = 0

        if not self.ShiftHeld:
            self.SendCC(IDPlay, val)

        for n in range(0, len(self.PlayingPads)):
          #NFX fix perfmode ghosting
          if ( (playlist.getPerformanceModeState() == 1) and (self.CurrentMode == ModePerf)) or (playlist.getPerformanceModeState() == 0):
            if Value > 0:
                self.AddPadDataCol(dataOut, self.PlayingPads[n][0], self.PlayingPads[n][1], self.PlayingPads[n][2])
            else:
                self.AddPadDataCol(dataOut, self.PlayingPads[n][0], self.PlayingPads[n][1], 0)

        if len(dataOut) > 0:
            screen.unBlank(True)
            self.SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)

    def UpdateCurrentKnobsMode(self):

        if not device.isAssigned():
            return
        val = 0
        if self.CurrentKnobsMode == KnobsModeChannelRack:
            val = 1
        elif self.CurrentKnobsMode == KnobsModeMixer:
            val = 2
        elif self.CurrentKnobsMode == KnobsModeUser1:
            val = 4
        elif self.CurrentKnobsMode == KnobsModeUser2:
            val = 8

        val = val | 16 # enable bit control of led states

        # knob mode led
        self.SendCC(IDKnobMode, val)
        self.SendCC(IDShift, int(self.ShiftHeld) * SingleColorFull)
        self.SendCC(IDAlt, int(self.AltHeld) * SingleColorFull)
        self.SendCC(IDBrowser, int(self.BrowserMode) * SingleColorFull)

    def AdaptKnobVal(self, Value):

        return Value # signof(Value) to ignore acceleartion

    def AdaptVelocity(self, Value):

        if not self.AccentMode & (Value > 0):
            Value = 100
        elif self.AccentMode & (Value > 0):

            if Value < 64:
                Value = 100
            else:
                Value = 127
        return Value

    def CheckForMasterDevice(self):

        if self.MultiDeviceMode != MultiDev_Slave:
            return # we're not slaved to another device, no need to check for a master
        for n in range(0, len(MIDIInDevices)):
            if (MidiInDevices[n] is TMIDIInDevice_Fire) & (MidiInDevices[n] != Self) & (TMidiInDevice_Fire(MidiInDevices[n]).IsMasterDevice):
                self.MasterDevice = TMidiInDevice_Fire(MidiInDevices[n])

    def ClearAllButtons(self):

        # pads modes
        self.SendCC(IDStepSeq, SingleColorOff)
        self.SendCC(IDNote, SingleColorOff)
        self.SendCC(IDDrum, SingleColorOff)
        self.SendCC(IDPerform, SingleColorOff)
        # knobs modes
        self.SendCC(IDKnobMode, 16)
        # shift button
        self.SendCC(IDShift, SingleColorOff)
        # Alt button
        self.SendCC(IDAlt, SingleColorOff)
        # mute buttons
        self.SendCC(IDMute1, SingleColorOff)
        self.SendCC(IDMute2, SingleColorOff)
        self.SendCC(IDMute3, SingleColorOff)
        self.SendCC(IDMute4, SingleColorOff)
        # track select buttons
        self.SendCC(IDTrackSel1, SingleColorOff)
        self.SendCC(IDTrackSel2, SingleColorOff)
        self.SendCC(IDTrackSel3, SingleColorOff)
        self.SendCC(IDTrackSel4, SingleColorOff)
        # transport buttons
        self.SendCC(IDPlay, SingleColorOff)
        self.SendCC(IDStop, SingleColorOff)
        self.SendCC(IDRec, SingleColorOff)
        self.SendCC(IDPatternSong, SingleColorOff)
        # browser button
        self.SendCC(IDBrowser, SingleColorOff)
        # grid
        self.SendCC(IDBankL, SingleColorOff)
        self.SendCC(IDBankR, SingleColorOff)
        # patterns
        self.SendCC(IDPatternUp, SingleColorOff)
        self.SendCC(IDPatternDown, SingleColorOff)


    def ClearAllPads(self):

        dataOut = bytearray(64 * 4)
        i = 0
        for n in range(0, 64):
            dataOut[i] = n
            dataOut[i + 1] = 0
            dataOut[i + 2] = 0
            dataOut[i + 3] = 0
            i += 4

        self.SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)
        time.sleep(0.5) # sometimes it doesn't clear ?

    def ClearBtnMap(self):

        for n in range(0, 64):
            self.BtnMap[n] = -1
        self.OldNoteMode = -1 # make sure we refresh notes mode

    def ClearDisplayText(self):

        dataOut = bytearray(3)

        dataOut[0] = 0
        dataOut[1] = 0
        for n in range(0, 8):
            dataOut[2] = n
            self.SendMessageToDevice(MsgIDDrawScreenText, len(dataOut), dataOut)

    def ClearDisplay(self):

        screen.fillRect(0, 0, self.DisplayWidth, self.DisplayHeight, self.BgCol)
        screen.update()

    def ClearHeldPads(self):

        self.HeldPads = bytearray()

    def ClearKnobsMode(self):

        self.SendCC(IDKnobMode, 16)

    def UpdateCurrentModeBtns(self):

        if not device.isAssigned():
            return
        self.BtnT[IdxStepSeq] = int(self.CurrentMode == ModeStepSeq)
        self.BtnT[IdxNote] = int(self.CurrentMode == ModeNotes)
        self.SendCC(IDNote, self.BtnT[IdxNote] * SingleColorFull)
        self.BtnT[IdxDrum] = int(self.CurrentMode == ModeDrum)
        self.BtnT[IdxPerform] = int(self.CurrentMode == ModePerf)
        self.SendCC(IDStepSeq, self.BtnT[IdxStepSeq] * SingleColorFull)
        self.SendCC(IDDrum, self.BtnT[IdxDrum] * SingleColorFull)
        self.SendCC(IDPerform, self.BtnT[IdxPerform] * SingleColorFull)

        if self.OverviewMode & (self.CurrentMode == ModePerf):
            if self.BlinkTimer >= BlinkSpeed:
                self.SendCC(IDPerform, SingleColorOff)
            else:
                self.SendCC(IDPerform, SingleColorFull)

    def UpdateCurrentPadsMode(self):

        if self.CurrentMode != self.OldMode:
            self.ClearBtnMap()
            self.CutPlayingNotes()
            self.ClearHeldPads()
            # automatically return submodes when switch pad modes
            self.LayoutSelectionMode = False
            self.BrowserMode = False
            self.AccentMode = False
            self.OverviewMode = False
            self.MixerTrackSelectionMode = False
            channels.closeGraphEditor(True)

        if self.CurrentMode == ModeStepSeq:
            self.RefreshStepSeq(False)
        elif self.CurrentMode == ModeNotes:
            self.RefreshNotesMode()
        elif self.CurrentMode == ModeDrum:
            self.RefreshDrumMode(self.CurrentMode != self.OldMode)
        elif self.CurrentMode in [ModeAnalyzerLeft, ModeAnalyzerRight, ModeAnalyzerMono]:
            self.RefreshAnalyzerMode()
        elif self.CurrentMode == ModePerf:
            if self.CurrentMode != self.OldMode:
                self.RefreshPerfMode(1, playlist.trackCount())
        else:
            self.ClearAllPads() # undefined mode

        self.OldMode = self.CurrentMode

    def OnUpdateLiveMode(self, FirstTrackNum, LastTrackNum):

        if self.CurrentMode == ModePerf:
            self.RefreshPerfMode(FirstTrackNum, LastTrackNum) # is it really needed ? idle might already take care of that

    def SetScreenMode(self, mode):

        if self.ScreenMode != mode:

            self.ScreenMode = mode

            i = screen.findTextLine(0, 20, 128, 20 + 44)
            if (general.getVersion() > 8):
              if (i >= 0):
                screen.removeTextLine(i, 1)
              if mode in [self.ScreenModePeak, self.ScreenModeScope]:
                screen.addMeter(mode, 0, 20, 128, 20 + 44)

    def SetAnalyzerMode(self, mode):

      self.AnalyzerScrollX = False
      self.AnalyzerScrollY = False
      self.AnalyzerFlipX = False
      self.AnalyzerFlipY = False
      self.AnalyzerChannel = 0
      self.AnalyzerMode = AnalyzerBars
      if mode == ModeAnalyzerLeft:
        self.AnalyzerScrollX = True
        self.AnalyzerFlipX = True
        self.AnalyzerMode = AnalyzerPeakVol
        self.AnalyzerChannel = 0
      elif mode == ModeAnalyzerRight:
        self.AnalyzerScrollX = True
        self.AnalyzerFlipX = False
        self.AnalyzerMode = AnalyzerPeakVol
        self.AnalyzerChannel = 1
      self.ClearBtnMap()

# Fire = TFire() 

# def OnInit():
#     Fire.OnInit()

# def OnDeInit():
#     Fire.OnDeInit()

# def OnDisplayZone():
#     Fire.OnDisplayZone()

# def OnIdle():
#     Fire.OnIdle()

# def OnMidiIn(event):
#     Fire.OnMidiIn(event)

# def OnMidiMsg(event):
#     Fire.OnMidiMsg(event)

# def OnRefresh(Flags):
#     Fire.OnRefresh(Flags)

# def OnUpdateLiveMode(LastTrackNum):
#     Fire.OnUpdateLiveMode(1, LastTrackNum)

# def OnUpdateBeatIndicator(Value):
#     Fire.OnUpdateBeatIndicator(Value)
