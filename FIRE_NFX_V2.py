# name=FIRE-NFX-V2.9
# supportedDevices=FL STUDIO FIRE
#
# author: Nelson F. Fernandez Jr. <nfxbeats@gmail.com>
#
# develoment started:   11/24/2021
# first public beta:    07/13/2022
#
# thanks to: HDSQ, TayseteDj, CBaum83, MegaSix, rd3d2, DAWNLIGHT, Jaimezin, a candle, Miro and Image-Line and more...
# thanks to GeorgBit (#GS comments in code) for velocity curve for accent mode featue.
#

VERSION = "2.2024.0819"
print('VERSION ' + VERSION)   

import device
import midi
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

from math import exp, log   #GS

from fireNFX_Utils import * 
from fireNFX_Display import *
from fireNFX_PluginDefs import *
from fireNFX_Helpers import *
from fireNFX_FireUtils import *
from fireNFX_Colors import *
from fireNFX_PadDefs import *
from fireNFX_HarmonicScales import *
from fireNFX_DefaultSettings import * 
from fireNFX_Classes import *
from fireNFX_Defs import * 

#from fireNFX_Classes import rd3d2PotParams, rd3d2PotParamOffsets
from fireNFX_SysMacros import * 
from fireNFX_Globals import * 

import fireNFX_Bridge 

# fix
# widPlugin = 5
# widPluginEffect = 6
# widPluginGenerator = 7

# not safe to use as of Aug 20, 2022
# import thread 
# task = True
# def task(self,a,b):
#     while (task) and (a < b):
#         a += 1
#         print('working...', a)
#         time.sleep(1)
#     print('done')
# def startTask(self):
#     id = thread.start_new_thread(task, (0,100))
#     print('task started', id)




class TFireNFX():

    def __init__(self):
        SetPallette(Settings.Pallette)
        if 'MISSING' in Settings.DEVMODE:
            Settings.add_field('DEVMODE', "0")
            persist.save_object(Settings, 'Settings.json')


    #region FL MIDI API Events
    def OnInit(self):
        global ScrollTo 
        global User1Knobs
        global User2Knobs
        global User3Knobs



        for knob in range(4):
            User1Knobs.append(TnfxUserKnob(knob)) 
            User2Knobs.append(TnfxUserKnob(knob))
            User3Knobs.append(TnfxUserKnob(knob))

        if Settings.SHOW_AUDIO_PEAKS:
            device.setHasMeters()

        ScrollTo = True
        self.ClearAllPads()

        # FIRE NFX V2 pattern lights
        # SendCC(IDPatternUp, SingleColorOff)
        # SendCC(IDPatternDown, SingleColorHalfBright)
        print("FIRE NFX V2")

        # Refresh the control button states        
        # Initialize Some lights
        self.RefreshKnobMode()       # Top Knobs operting mode

        #  turn off top buttons: the Pat Up/Dn, browser and Grid Nav buttons
        # SendCC(IDPatternUp, SingleColorOff)
        # SendCC(IDPatternDown, SingleColorOff)
        SendCC(IDBankL, SingleColorOff)
        SendCC(IDBankR, SingleColorOff)
        SendCC(IDBrowser, SingleColorOff)    

        self.InititalizePadModes()

        self.RefreshPageLights()             # PAD Mutes akak Page
        self.ResetBeatIndicators()           # 
        self.RefreshPadModeButtons()
        self.RefreshShiftAltButtons()
        self.RefreshTransport()    

        global shuttingDown
        shuttingDown = False

        # Init some data
        InitDisplay()
        ScrollTo = False  
        ui.setHintMsg(Settings.STARTUP_FL_HINT)
        ui.showWindow(widChannelRack) # helps the script to have a solid starting window.
        self.RefreshAll()
   
    def OnDeInit(self):
        print('OnDeInit V2')
        global task

        task = False
        time.sleep(1)
        global shuttingDown
        shuttingDown = True
        
        DisplayTextAll(' ', ' ', ' ')    
        DeInitDisplay()

        # turn of the lights and go to bed...
        self.ClearAllPads()
        SendCC(IDKnobModeLEDArray, 16)
        for ctrlID in getNonPadLightCtrls():
            SendCC(ctrlID, 0)
        
        self.Reset()

    def ClearAllPads(self):
        # clear the Pads
        for pad in range(0,64):
            SetPadColor(pad, 0x000000, 0)
        
    def OnDoFullRefresh(self):
        self.RefreshAll() 

    def OnIdle(self):
        global lastHints
        global BlinkTimer
        global BlinkLast
        global ToBlinkOrNotToBlink
        global lastFocus
        global lastWindowID
        global IsOnIdleRefreshing
        global peakCheckTime
        global pressCheckTime 
        global pressisRepeating
        global BlinkSeconds 


        if(shuttingDown):
            return 

        if(pressCheckTime != None):
            pMapPressed = next((x for x in PadMap if x.Pressed == 1), None) 
            if(pMapPressed != None):
                elapsed = time.time() - pressCheckTime
                prevTime = pressCheckTime
                pressCheckTime = None # prevent it from checking until we are done
                #print('pressed Pad', pMapPressed.PadIndex, 'time', elapsed, 'isPressRep?', pressisRepeating)
                if(pressisRepeating):
                    if (elapsed >= LONG_PRESS_DELAY):
                        if(pMapPressed.PadIndex in [pdUp, pdDown, pdLeft, pdRight]):
                            self.HandleNav(pMapPressed.PadIndex)
                        pressCheckTime = time.time()
                    else:
                        pressCheckTime = prevTime
                else:
                    pressisRepeating = (elapsed >= LONG_PRESS_DETECT) # turn on 'pad' repeat mode
                    pressCheckTime = prevTime

            else:        
                pressCheckTime = None

        if(peakCheckTime != None): # we are waiting for next chek
            if not self.adjustForAudioPeaks():
                peakCheckTime == None
            else:
                elapsed = time.time() - peakCheckTime
                if(elapsed > PEAKTIME):
                    if self.adjustForAudioPeaks():
                        if(PadMode.Mode == MODE_DRUM) and (self,not isAltMode): # FPC
                            self.RefreshFPCSelector()
                        if(PadMode.Mode == MODE_PATTERNS):
                            if(self.getFocusedWID() in [widMixer, widChannelRack, widPlaylist]):
                                if self.isMixerMode():
                                    self.RefreshMixerStrip()
                                elif self.isChannelMode():
                                    self.RefreshChannelStrip()
                                elif self.isPlaylistMode():
                                    self.RefreshPlaylist()

                    peakCheckTime = time.time()
        else:
            if self.adjustForAudioPeaks():
                peakCheckTime = time.time()

        if(Settings.WATCH_WINDOW_SWITCHING):
            currFormID = self.getFocusedWID()
            self.UpdateLastWindowID(currFormID)
            if(currFormID in windowIDNames.keys()) and (currFormID != lastFocus):  
                # print('WWS from ', windowIDNames[_lastFocus], 'to',  windowIDNames[currFormID], '   calling OnRefresh(HW_Dirty_FocusedWindow)')
                self.OnRefresh(HW_Dirty_FocusedWindow)
                


        if(MONITOR_HINTS): # needs a condition
            hintMsg = ui.getHintMsg()
            if( len(lastHints) == 0 ):
                lastHints.append('')
            if(hintMsg != lastHints[-1]):
                lastHints.append(hintMsg)
                if(len(lastHints) > MAX_HINTS):
                    lastHints.pop(0)

        # 
        # if(self.isPlaylistMode()):
        #     CheckAndRefreshSongLen()

        # determines if we need show note playback
        if(Settings.SHOW_PLAYBACK_NOTES) and (transport.isPlaying() or transport.isRecording()):
            if(PadMode.Mode in [MODE_DRUM, MODE_NOTE]):
                self.HandleShowNotesOnPlayback()

        if PadMode.Mode == MODE_PERFORM:
            BlinkTimer = transport.isPlaying() == 1

        if(BlinkTimer):
            if(BlinkLast == 0):
                BlinkLast = time.time()
            else:            
                elapsed = time.time() - BlinkLast
                if(elapsed >= BlinkSeconds):
                    BlinkLast = time.time()
                    ToBlinkOrNotToBlink = not ToBlinkOrNotToBlink
                    if(PadMode.NavSet.BlinkButtons):
                        self.RefreshGridLR()
                    #print('blink', ToBlinkOrNotToBlink)

    def UpdateLastWindowID(self,currFormID): 
        # this tracks which of the 3 main windows was last focused.
        global lastWindowID
        if(currFormID in [widChannelRack, widPlaylist, widMixer]):
            lastWindowID = currFormID
        elif(currFormID in [widPlugin, widPluginEffect, widPianoRoll]):
            lastWindowID = widChannelRack
        elif(currFormID == widPluginEffect):
            lastWindowID = widMixer

    def getNoteForChannel(self,chanIdx):
        return channels.getCurrentStepParam(chanIdx, mixer.getSongStepPos(), pPitch)

    def HandleShowNotesOnPlayback(self):
        global PadMode
        global  lastNote
        if (PadMode.Mode in [MODE_DRUM, MODE_NOTE]):
            note = self.getNoteForChannel(getCurrChanIdx()) # channels.getCurrentStepParam(getCurrChanIdx(), mixer.getSongStepPos(), pPitch)
            if(lastNote != note):
                self.ShowNote(lastNote, False)
                if(note > -1) and (note in NoteMap):
                    self.ShowNote(note, True)
                lastNote = note

    def CheckAndRefreshSongLen(self):
        global lastNote
        global SongLen
        global SHOW_PROGRESS

        currSongLen = transport.getSongLength(SONGLENGTH_BARS)
        if(currSongLen != SongLen): # song length has changed
            if(SHOW_PROGRESS):
                self.UpdateAndRefreshProgressAndMarkers()
            SongLen = currSongLen
        
    def OnMidiMsg2(self,event):
        if(event.data1 in KnobCtrls) and (KnobMode in [KM_USER1, KM_USER2, KM_USER3]): # user defined knobs
            # this code from the original script with slight modification:
            data2 = event.data2
            event.inEv = event.data2
            if event.inEv >= 0x40:
                event.outEv = event.inEv - 0x80
            else:
                event.outEv = event.inEv
            event.isIncrement = 1

            event.handled = False # user modes, free
            event.data1 += (KnobMode-KM_USER1) * 4 # so the CC is different for each user mode
            device.processMIDICC(self,event)
            
            if (general.getVersion() > 9):
                BaseID = EncodeRemoteControlID(device.getPortNumber(), 0, 0)
                eventId = device.findEventID(BaseID + event.data1, 0)
                if eventId != 2147483647:
                    s = device.getLinkedParamName(eventId)
                    s2 = device.getLinkedValueString(eventId)
                    DisplayTextAll(s, s2, '')        

    def OnUpdateBeatIndicator(self,value):
        global Beat
        if(not transport.isPlaying()):
            self.RefreshTransport()
            self.ResetBeatIndicators()
            return
        
        if(value == 0):
            SendCC(IDPlay, IDColPlayOn)
        elif(value == 1):
            SendCC(IDPlay, IDColPlayOnBar)
            Beat = 0
            if(SHOW_PROGRESS):
                if(PadMode.Mode == MODE_PATTERNS) and self.isPlaylistMode(self):
                    self.UpdateAndRefreshProgressAndMarkers()
        elif(value == 2):
            SendCC(IDPlay, IDColPlayOnBeat)
            Beat += 1


        if Beat > len(BeatIndicators):
            Beat = 0

        isLastBar = transport.getSongPos(SONGLENGTH_BARS) == transport.getSongLength(SONGLENGTH_BARS)

        for i in range(0, len(BeatIndicators) ):
            
            if(Beat >= i):
                if(isLastBar):
                    SendCC(BeatIndicators[i], SingleColorHalfBright) # red
                else:
                    SendCC(BeatIndicators[i], SingleColorFull) # green
            else:
                SendCC(BeatIndicators[i], SingleColorOff)
        
        if(PadMode.Mode == MODE_PERFORM):
            if PadMode.IsAlt:
                self.RefreshAltPerformanceMode()
            else:
                self.RefreshPerformanceMode(Beat)

    #gets calledd too often
    def OnDirtyMixerTrack(self,track):
        pass
        #OnRefresh(HW_DirtyLEDs)

    def OnSysEx(self, event):
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

    def OnDirtyChannel(self,chan, flags):
        global DirtyChannelFlags
        # Called on channel rack channel(s) change, 
        # 'index' indicates channel that changed or -1 when all channels changed
        # NOTE PER DOCS: 
        #     collect info about 'dirty' channels here but do not handle channels(s) refresh, 
        #     wait for OnRefresh event with HW_ChannelEvent flag    
        #
        # CE_New	0	new channel is added
        # CE_Delete	1	channel deleted
        # CE_Replace	2	channel replaced
        # CE_Rename	3	channel renamed
        # CE_Select	4	channel selection changed    
        DirtyChannelFlags = flags

    def OnRefresh(self, flags):
        global PadMode
        global isAltMode
        global lastFocus
        global ignoreNextMixerRefresh
        global FollowChannelFX

        # print('OnRefresh', flags)
        if(flags == HW_CustomEvent_ShiftAlt):
            # called by HandleShiftAlt
            toptext = ''
            midtext = ''
            bottext = ''

            if(AltHeld and ShiftHeld):
                toptext = 'SHIFT + ALT +'
            elif(ShiftHeld):
                toptext = 'SHIFT +'
                midtext = 'Options'
                self.RefreshShiftedStates() 
                if(DoubleTap):
                    macShowScriptWindow.Execute()
                if(PadMode.Mode == MODE_PATTERNS):
                    if(self.isChannelMode()):
                        bottext = ''
            elif(AltHeld):
                toptext = 'ALT +'
                #feels like this code should be elsewhere
                if(PadMode.Mode == MODE_PATTERNS):
                    if(self.isChannelMode()):
                        midtext = 'Ptn = Clone'
                        bottext = 'Chn = Edit FX'
            else: # released
                self.RefreshDisplay()
                
            # show the options on screen
            if(toptext != ''):
                DisplayTextAll(toptext, midtext, bottext)

            self.RefreshPadModeButtons()
            self.RefreshShiftAltButtons()
            self.RefreshTransport()
            return # no more processing needed.
        
        if(HW_Dirty_ControlValues & flags):
            # transport movement triggers this
            if(PadMode.Mode == MODE_PATTERNS):
                if(self.isPlaylistMode()):
                    self.RefreshPlaylist()
                    self.RefreshProgress()

        if(HW_Dirty_LEDs & flags):
            self.RefreshTransport()

        if(HW_Dirty_Names & flags):
            #print('nameflag', flags)
            if Settings.AUTO_COLOR_ENABLED:
                # newcol = GetColorFor(name) 
                chan = channels.channelNumber()
                trk = mixer.trackNumber()
                pat = patterns.patternNumber()
        
        if(HW_Dirty_FocusedWindow & flags):
            newWID = self.getFocusedWID()
            focusedID = newWID
            t = -1
            s = -1
            name = windowIDNames[newWID]
            
            if(ui.getFocusedFormID() > 1000): # likely a mixer effect
                focusedID = ui.getFocusedFormID()
                t, s = self.getTrackSlotFromFormID(focusedID)
                newWID = widPluginEffect
                pname, uname, vname = getPluginNames(t, s)
                name = pname +  " (" + plugins.getPluginName(t, s) + ") Track: {}, Slot: {}".format(t, s+1)
            elif(focusedID in [widPlugin, widPluginGenerator]): 
                newWID = focusedID
                chanIdx = getCurrChanIdx()
                if(plugins.isValid(chanIdx, -1)):
                    pname, uname, vname = getPluginNames(chanIdx, -1)
                    name =  pname + " (" + uname + ") Channel: " + str(chanIdx)
            # print('Focus: ', name, focusedID)
            # if(focusedID in [widMixer, widPlaylist, widChannelRack]):
            #     HandlePadModeChange(IDStepSeq)

            if(lastFocus != newWID ):
                # print('Focus changed from ', windowIDNames[_lastFocus], 'to',  name, focusedID, t, s)
                self.RefreshModes()
                self.UpdateAndRefreshWindowStates()

            #if(Settings.AUTO_SWITCH_TO_MAPPED_MIXER_EFFECTS):
                #print('checking mixer effects')
                # formCap = ui.getFocusedFormCaption()
                # UpdateAndRefreshWindowStates()
                # if(lastFocus in widDict.keys()):
                #     print('=====> Changed to ', widDict[lastFocus], formCap)
                #     pass
                # elif(lastFocus == -1):
                #     print('=====> None')
                #     pass
                # else:
                #     slotIdx, uname, pname = GetActiveMixerEffectSlotInfo()
                #     if isKnownMixerEffectActive():
                #         RefreshModes()
                #         RefreshEffectMapping() #GBMapTest()
                #     else:
                #         print("=====> FormCap ", formCap)
                #         pass


        if(HW_Dirty_Performance & flags): # called when new channels or patterns added
            if(PadMode.Mode == MODE_PATTERNS):
                # RefreshChannelStrip()
                self.RefreshPatternStrip()
                self.RefreshChannelStrip()

        if(HW_Dirty_Patterns & flags):
            #print('dirty patterns')
            self.CloseBrowser()
            self.HandlePatternChanges()
        if(HW_Dirty_ChannelRackGroup & flags):
            self.HandleChannelGroupChanges()    
        if(HW_ChannelEvent & flags):
            self.CloseBrowser()
            self.UpdateChannelMap()  
            

            # DirtyChannelFlags should have the specific CE_xxxx flags if needed
            # https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm#OnDirtyChannelFlag

            # something change in FL 21.0.2, that makes the mixer no longer follow when the selected channel changes
            # so I check if it needs to move here
            if (PadMode.Mode != MODE_PERFORM): # ignore when in perf mode
                if(CE_Select & DirtyChannelFlags) and (FollowChannelFX): 
                    trk = channels.getTargetFxTrack(getCurrChanIdx())
                    if(trk != mixer.trackNumber()):
                        #self.prnt('forcing chanfx')
                        self.SelectAndShowMixerTrack(trk)
                        # mixer.setTrackNumber(trk, curfxScrollToMakeVisible)
                        # ui.miDisplayRect(trk, trk, rectTime, CR_ScrollToView)

            if (PadMode.Mode == MODE_DRUM):
                if(not self.isFPCActive()):
                    PadMode = modeDrumAlt
                    isAltMode = True
                    self.SetPadMode()
                self.RefreshDrumPads()
            elif(PadMode.Mode == MODE_PATTERNS):
                scrollTo = CurrentChannel != channels.channelNumber()
                self.RefreshChannelStrip(scrollTo)
            elif(PadMode.Mode == MODE_NOTE):
                self.RefreshNotes()

        if(HW_Dirty_Colors & flags):
            if (PadMode.Mode == MODE_DRUM):
                self.RefreshDrumPads()
            elif(PadMode.Mode == MODE_PATTERNS):
                self.RefreshChannelStrip()

        if(HW_Dirty_Tracks & flags):
            if(self.isPlaylistMode()):
                self.UpdatePlaylistMap()
                self.RefreshPlaylist()

        if(HW_Dirty_Mixer_Sel & flags):
            if(self.isMixerMode()):
                #UpdateMixerMap(-2)
                self.RefreshMixerStrip(True)

        self.RefreshDisplay()

    def OnProjectLoad(self, status):
        #print('Window active:', self.isChannelMode(), self.isPlaylistMode(), self.isMixerMode())
        # status = 0 = starting load?
        if(status == 0):
            DisplayTextAll('Project Loading', '-', 'Please Wait...')
        if(status >= 100): #finished loading
            self.SetPadMode()
            #UpdateMarkerMap()
            self.RefreshPadModeButtons()        
            self.UpdatePatternModeData()
            self.RefreshAll()
            

    def OnSendTempMsg(self, msg, duration):
        global tempMsg 
        global tempMsg2 
        tempMsg = msg
        # if(' - ' in msg):
        #     tempMsg = msg
        #print('TempMsg', "[{}]".format(tempMsg), duration, 'inMenu', ui.isInPopupMenu())
        # else:
        #     tempMsg2 = msg
        #     print('TempMsg2', "[{}]".format(tempMsg2), duration, 'inMenu', ui.isInPopupMenu())

    def FLHasFocus(self):
        ui.showWindow(widChannelRack)
        transport.globalTransport(90, 1)
        time.sleep(0.025)
        ui.down()
        res = tempMsg.startswith("File -") or tempMsg.startswith("Menu - File")
        if (ui.isInPopupMenu()):
            ui.closeActivePopupMenu()
        return res

    def isKnownPlugin(self):
        name, uname = self.getCurrChanPluginNames()
        return name in KNOWN_PLUGINS.keys()

    def OnMidiIn(self,event):
        global proctime
        global prevCtrlID
        global DoubleTap

        ctrlID = event.data1 # the low level hardware id of a button, knob, pad, etc

        #self.prnt('OnMidiIn', ctrlID, event.data2)

        # check for double tap
        if(event.data2 > 0) and (ctrlID not in [IDKnob1, IDKnob2, IDKnob3, IDKnob4, IDSelect]):
            prevtime = proctime
            proctime = time.monotonic_ns() // 1000000
            elapsed = proctime-prevtime

            if (prevCtrlID == ctrlID):
                DoubleTap = (elapsed < Settings.DBL_TAP_DELAY_MS)
            else:
                prevCtrlID = ctrlID
                DoubleTap = False
        
        # handle shift/alt
        if(ctrlID in [IDAlt, IDShift]):
            self.HandleShiftAlt(event, ctrlID)
            event.handled = True
            return    

        if(ctrlID in KnobCtrls):  #if false, it's a custom userX knob link
            event.handled = self.OnMidiIn_KnobEvent(event)
            return

    def OnMidiMsg(self,event):
        global ShiftHeld
        global AltHeld
        global PadMap
        global pressCheckTime
        global pressisRepeating
        global isPMESafe
        global isModalWindowOpen
        global User1Knobs
        global User2Knobs
        global User3Knobs


        ctrlID = event.data1 # the low level hardware id of a button, knob, pad, etc
        #self.prnt('OnMidiMsg', ctrlID, event.data2, 'status', event.status)

        # check PME flags. note that these will be different from OnMidiIn PME values 
        isModalWindowOpen = (event.pmeFlags & PME_System_Safe == 0)
        isPMESafe = (event.pmeFlags & PME_System != 0)
        if(not isPMESafe):
            self.prnt('pme not safe', event.pmeFlags)
            event.handled = True
            return 

        if(event.data1 in KnobCtrls) and (KnobMode in [KM_USER1, KM_USER2, KM_USER3]): # user defined knobs
            knobOffset = KnobCtrls.index(event.data1)

            event.data1 += (KnobMode-KM_USER1) * 4 # so the CC is different for each user mode
            # self.prnt(self,'knob CC', event.data1)
            if not (event.status in [MIDI_NOTEON, MIDI_NOTEOFF]): # to prevent the mere touching of the knob generating a midi note event.
                # this code from the original script with slight modification:
                event.inEv = event.data2
                if event.inEv >= 0x40:
                    event.outEv = event.inEv - 0x80
                else:
                    event.outEv = event.inEv
                event.isIncrement = 1

                event.handled = False # user modes, free
                device.processMIDICC(event)

            # USER KNOB
            if(KnobMode == KM_USER1):
                userknob = User1Knobs[knobOffset]
            elif(KnobMode == KM_USER2):
                userknob = User2Knobs[knobOffset]
            else:
                userknob = User3Knobs[knobOffset]

            if (general.getVersion() > 9):
                BaseID = EncodeRemoteControlID(device.getPortNumber(), 0, 0)
                recEventIDIndex = device.findEventID(BaseID + event.data1, 0)
                if recEventIDIndex != 2147483647: # check if it has been assigned to a control yet... 
                    # show the name/value on the display
                    Name = device.getLinkedParamName(recEventIDIndex)
                    currVal = device.getLinkedValue(recEventIDIndex)
                    valstr = device.getLinkedValueString(recEventIDIndex)
                    Bipolar = device.getLinkedInfo(recEventIDIndex) == Event_Centered
                    DisplayBar2(Name, currVal, valstr, Bipolar)
                    if (userknob.PluginName == ''):
                        name = LastActiveWindow.Name # ui.getFocusedFormCaption()
                        userknob.PluginName = name
                        #print('assigning knob', name, 'tweak', Name)
                    else:
                        #print('knob', userknob.PluginName, 'tweak', Name, currVal, valstr, Bipolar)
                        pass

        
        # handle a pad
        if( IDPadFirst <=  ctrlID <= IDPadLast):
            padNum = ctrlID - IDPadFirst
            pMap = PadMap[padNum]
            cMap = getColorMap()
            col = cMap[padNum].PadColor
            if (col == cOff):
                col = Settings.PAD_PRESSED_COLOR

            if(event.data2 > 0): # pressed
                pMap.Pressed = 1
                SetPadColor(padNum, col,dimBright, False) # False will not save the color to the ColorMap
            else: #released
                pMap.Pressed = 0
                # SetPadColor(padNum, -1, dimNormal) # -1 will rever to the ColorMap color
            
            # if no other pads held, reset the long press timer
            pMapPressed = next((x for x in PadMap if x.Pressed == 1), None) 
            if(pMapPressed == None):
                pressCheckTime = None 
                pressisRepeating = False
            else:
                pressCheckTime = time.time()

            #PROGRESS BAR
            if(SHOW_PROGRESS):
                if(PadMode.Mode == MODE_PATTERNS) and (self.isPlaylistMode()):
                    progPads = self.getProgressPads()
                    if(padNum in progPads) and (pMap.Pressed == 1): # only handle on pressed.
                        event.handled = self.HandleProgressBar(padNum)
                        return event.handled

            padsToHandle = pdWorkArea
            if(self.isNoNav()):
                padsToHandle = pdAllPads
            

            # # handle effects when active
            if(Settings.AUTO_SWITCH_TO_MAPPED_MIXER_EFFECTS) and self.isMixerMode(): 
                #print('mixer effect mode', padNum)
                #is an effect mapped?
                if(self.isKnownMixerEffectActive()) and (padNum in ParamPadMapDict.keys()):
                    self.RefreshEffectMapping()
                    if(padNum in ParamPadMapDict.keys()):
                        self.ForceNaveSet(nsNone)
                        event.handled = self.HandleEffectPads(padNum)
                        return 

            if(padNum in padsToHandle):
                if(PadMode.Mode == MODE_DRUM): # handles on and off for PADS
                    event.handled = self.HandlePads(event, padNum)
                    return 
                elif(PadMode.Mode == MODE_NOTE): # handles on and off for NOTES
                    event.handled = self.HandlePads(event, padNum)
                    return 
                elif(PadMode.Mode == MODE_PERFORM): # handles on and off for PERFORMANCE
                    if(pMap.Pressed == 1):
                        if PadMode.IsAlt:
                            event.handled = self.HandleAltPerform(padNum)
                        else:
                            event.handled = self.HandlePerform(padNum)
                    else:
                        event.handled = True 
                    return 
                elif(PadMode.Mode == MODE_PATTERNS): # if STEP/PATTERN mode, treat as controls and not notes...
                    if(pMap.Pressed == 1): # On Pressed
                        event.handled = self.HandlePads(event, padNum)
                        return 
                    else:
                        event.handled = True #prevents a note off message
                        return 

            # special handler for color picker
            if(PadMode.NavSet.ColorPicker):
                if(padNum in pdPallette) or (padNum in pdCurrColors):
                    event.handled = self.HandleColorPicker(padNum)
                    return 

            if(not self.isNoNav()):
                # always handle macros
                if(padNum in pdMacros):
                    if (pMap.Pressed): 
                        event.handled = self.HandleMacros(pdMacros.index(padNum))
                        self.RefreshMacros()
                        self.UpdateAndRefreshWindowStates()
                    else:
                        event.handled = True #prevents a note off message
                    return 

                # always handle nav
                if(padNum in pdNav):
                    if (pMap.Pressed): 
                        event.handled = self.HandleNav(padNum)
                    else:
                        #self.RefreshNavPads()
                        event.handled = True #prevents a note off message
                    return  
            return 

        # handle other "non" Pads
        # here we will get a message for on (press) and off (release), so we need to
        # determine where it's best to handle. For example, the play button should trigger 
        # immediately on press and ignore on release, so we code it that way
        if(event.data2 > 0) and (not event.handled): # Pressed
            if(ShiftHeld):
                self.HandleShifted(event)
            if( ctrlID in PadModeCtrls):
                event.handled = self.HandlePadModeChange(event.data1) # ctrlID = event.data1 
            elif( ctrlID in TransportCtrls ):
                event.handled = self.HandleTransport(event)
            elif( ctrlID in PageCtrls): # defined as [IDMute1, IDMute2, IDMute3, IDMute4]
                event.handled = self.HandlePage(event, ctrlID)  
            elif( ctrlID == KnobModeCtrlID):
                event.handled = self.HandleKnobMode()
            elif( ctrlID in KnobCtrls):
                event.handled = self.HandleKnob(event, ctrlID)
            elif( ctrlID in PattUpDnCtrls):
                event.handled = self.HandlePattUpDn(ctrlID)
            elif( ctrlID in GridLRCtrls):
                event.handled = self.HandleGridLR(ctrlID)
            elif( ctrlID == IDBrowser ):
                event.handled = self.HandleBrowserButton()
            elif(ctrlID in SelectWheelCtrls):
                event.handled = self.HandleSelectWheel(event, ctrlID)
        else: # Released
            event.handled = True 

    def OnNoteOn(self,event):
        #self.prnt('OnNoteOn()', utils.GetNoteName(event.data1),event.data1,event.data2)
        self.ShowNote(event.data1, True)
        pass

    def OnNoteOff(self,event):
        #self.prnt('OnNoteOff()', utils.GetNoteName(event.data1),event.data1,event.data2)
        self.ShowNote(event.data1, False)
        pass

    def OnSysEx(self, event):
        pass

    #endregion 

    #region Handlers
    def HandleChannelStrip(self,padNum): #, isChannelStripB):
        global PatternMap
        global ChannelMap
        global CurrentChannel 
        # global PreviousChannel
        global ChannelCount
        global OrigColor
        global rectTime 

        if(self.isMixerMode()):
            return self.HandleMixerEffectsStrip(padNum)
        
        if(self.isPlaylistMode()):
            if(SHOW_PROGRESS):
                return self.HandleProgressBar(padNum)
            else:
                return True

        prevChanIdx = getCurrChanIdx() # channels.channelNumber()
        pageOffset = self.getChannelOffsetFromPage()
        padOffset = 0

        chanApads, chanBPads = self.getChannelPads()

        if(padNum in chanApads):
            padOffset = chanApads.index(padNum)
            isChannelStripB = False
        elif(padNum in chanBPads):
            padOffset = chanBPads.index(padNum)
            isChannelStripB = True

        chanIdx = padOffset + pageOffset
        channelMap = self.getChannelMap()
        channel = None
        if(chanIdx < len(channelMap) ):
            channel = channelMap[chanIdx]
        
        if(channel == None):
            return True

        newChanIdx = channel.FLIndex # pMap.FLIndex
        newMixerIdx = channel.Mixer.FLIndex
        if (newChanIdx > -1): #is it a valid chan number?

            if(not isChannelStripB): # its the A strip

                if(PadMode.NavSet.ColorPicker): # color picker mode
                    if(self,not isChannelStripB):
                        OrigColor = FLColorToPadColor(channels.getChannelColor(getCurrChanIdx()), 1) # xxxx
                        channels.setChannelColor(getCurrChanIdx(), PadColorToFLColor(NewColor))
                        self.RefreshColorPicker()
                    self.SetPadMode()
                    return True
                elif(newChanIdx == prevChanIdx): # if it's already on the channel, toggle the windows
                    if(ShiftHeld) and (Settings.SHOW_CHANNEL_MUTES): # new
                        if(DoubleTap):
                            ui.showWindow(widPianoRoll)
                            macZoom.Execute(Settings.DBL_TAP_ZOOM)                     
                        else: 
                            self.ShowPianoRoll(-1) 
                    else: 
                        self.ShowChannelEditor(-1)
                else:
                    self.SelectAndShowChannel(newChanIdx)


            else: # is B STrip
                if(ShiftHeld):
                    if (Settings.SHOW_CHANNEL_MUTES): # new
                        channels.soloChannel(newChanIdx)
                        ui.crDisplayRect(0, newChanIdx, 0, 1, rectTime, CR_ScrollToView + CR_HighlightChannelMute) # CR_HighlightChannels + 
                        self.RefreshChannelStrip(False)
                    else: #old
                        channels.muteChannel(newChanIdx)
                        ui.crDisplayRect(0, newChanIdx, 0, 1, rectTime, CR_ScrollToView + CR_HighlightChannelMute) # CR_HighlightChannels + 
                        self.RefreshChannelStrip(False)
                else: #not SHIFTed
                    if (Settings.SHOW_CHANNEL_MUTES): # new
                        channels.muteChannel(newChanIdx)
                        ui.crDisplayRect(0, newChanIdx, 0, 1, rectTime, CR_ScrollToView + CR_HighlightChannelMute) # CR_HighlightChannels + 
                        self.RefreshChannelStrip(False)
                    else: #old 
                        if(newChanIdx == prevChanIdx): # if it's already on the channel, toggle the windows
                            if(DoubleTap):
                                ui.showWindow(widPianoRoll)
                                macZoom.Execute(Settings.DBL_TAP_ZOOM)                     
                            else:
                                self.ShowPianoRoll(-1) 
                        else: #'new' channel, close the previous windows first
                            self.SelectAndShowChannel(newChanIdx)

        ChannelCount = channels.channelCount()
        self.RefreshDisplay()
        return True

    def HandleAltPerform(self, padNum):
        if len(UserMacros) > 0:
            self.RunMacro(UserMacros[padNum])
        return True

    def HandlePerform(self,padNum):
        global PerformanceBlocks 


        if isPMESafe:
            if(padNum in PerformanceBlocks.keys()):
                block = PerformanceBlocks[padNum]
                # self.prnt('handling block', block, 'alt', AltHeld, 'shift', ShiftHeld)
                tlcMode = TLC_MuteOthers | TLC_Fill
                if(AltHeld and ShiftHeld):
                    playlist.soloTrack(block.FLTrackIndex, -1)
                elif(ShiftHeld):
                    tlcMode = -1 # stop all
                elif(AltHeld):
                    playlist.muteTrack(block.FLTrackIndex)
                block.Trigger(tlcMode)
                self.RefreshPerformanceMode(-1)
        return True 

    def HandlePlaylist(self,padNum):
        plPadsA, plPadsB = self.getPlaylistPads()

        flIdx = PadMap[padNum].FLIndex
        if(flIdx > -1):
            if(padNum in plPadsA):       
                playlist.selectTrack(flIdx)
            if(padNum in plPadsB):
                patNum = patterns.patternNumber() 
                if(ShiftHeld):
                    playlist.soloTrack(flIdx)
                else:
                    playlist.muteTrack(flIdx)

                #workaround 
                if Settings.MUTE_PLTRACK_IMMEDIATELY:
                    patterns.jumpToPattern(patNum+1)
                    patterns.jumpToPattern(patNum)

            self.UpdatePlaylistMap()
        self.RefreshPlaylist()
        self.RefreshDisplay()
        return True

    def HandleProgressBar(self,padNum):
        progPads = self.getProgressPads()
        padOffs = progPads.index(padNum)
        prgMap = ProgressMapSong[padOffs]
        newSongPos = transport.getSongPos(SONGLENGTH_ABSTICKS) # current location

        if(prgMap.BarNumber > 0):
            newSongPos = prgMap.SongPosAbsTicks

        transport.setSongPos(newSongPos, SONGLENGTH_ABSTICKS)
        
        if(AltHeld):
            markerOffs = padOffs + 1
            arrangement.addAutoTimeMarker(prgMap.SongPosAbsTicks, Settings.MARKER_PREFIX_TEXT.format(markerOffs))

        if(ShiftHeld):
            if arrangement.selectionEnd() == -1: 
                endPos = transport.getSongLength(SONGLENGTH_ABSTICKS)
                transport.markerSelJog(0) # set the selection
                arrangement.jumpToMarker(0, True) # alt
                if(arrangement.selectionEnd() == -1): # BUG CHECK - if -1 we may be at the last marker and it will not go to the en position
                    arrangement.liveSelection(newSongPos, False)
                    arrangement.liveSelection(endPos, True)
            else:
                arrangement.liveSelection(newSongPos, False) # clear

        #UpdateAndRefreshProgressAndMarkers()
        self.RefreshProgress()
        self.RefreshDisplay()
        return True

    def HandleEffectPads(self,padNum):
        # for handling effect values to pads ie. gross beat
        #is an effect mapped?
        if(padNum in ParamPadMapDict.keys()):
            slotIdx, slotName, pluginName = self.GetActiveMixerEffectSlotInfo()
            # get Param Value from the pressed pad 
            offset, value = ParamPadMapDict[padNum]
            #value = ParamPadMapDict[padNum].GetValueFromPad(padNum)
            #print('SetMixerPluginParamVal', offset, value, -1, slotIdx)
            SetMixerPluginParamVal(offset, value, -1, slotIdx)
            self.RefreshEffectMapping()
        return True

    def HandlePads(self,event, padNum):  
        # 'perfomance'  pads will need a pressed AND release...
        if(PadMode.Mode == MODE_DRUM):
            if (padNum in self.DrumPads()):
                return self.HandleDrums(event, padNum)
        elif(PadMode.Mode == MODE_NOTE):
            if(padNum in pdWorkArea):
                return self.HandleNotes(event, padNum)

        # some pads we only need on pressed event
        if(event.data2 > 0): # On Pressed

            # macros are handled in OnMidiIn

            # if(Settings.AUTO_SWITCH_TO_MAPPED_MIXER_EFFECTS): 
            #     #is an effect mapped?
            #     if(self.isKnownMixerEffectActive()) and (padNum in ParamPadMapDict.keys()):
            #         slotIdx, slotName, pluginName = GetActiveMixerEffectSlotInfo()
            #         # get Param Value from the pressed pad 
            #         offset, value  = ParamPadMapDict[padNum] #.Offset
            #         #value = ParamPadMapDict[padNum].GetValueFromPad(padNum)
            #         SetMixerPluginParamVal(offset, value, -1, slotIdx)
            #         RefreshEffectMapping()
            #     return True

            if(PadMode.Mode == MODE_NOTE):
                if(padNum in pdNav):
                    self.HandleNav(padNum)
            if(PadMode.Mode == MODE_DRUM):
                if(padNum in pdFPCChannels):
                    self.HandleDrums(event, padNum)
            elif(PadMode.Mode == MODE_PATTERNS):
                row0, row1 = self.getPatternPads()
                row2, row3 = self.getChannelPads()
                if(padNum in row0) or (padNum in row1): # top two rows, 
                    event.handled = self.HandlePatternStrip(padNum)
                elif(padNum in row2) or (padNum in row3): # bottom two rows
                    event.handled = self.HandleChannelStrip(padNum) 

        return True

    def HandleNav(self,padIdx):
        # print('HandleNav', padIdx)

        global NoteRepeat
        global SnapIdx
        hChanPads = PadMode.NavSet.ChanNav
        hPresetNav = PadMode.NavSet.PresetNav
        hUDLR = PadMode.NavSet.UDLRNav
        hSnapNav = PadMode.NavSet.SnapNav
        hNoteRepeat = PadMode.NavSet.NoteRepeat
        hScaleNav = PadMode.NavSet.ScaleNav
        hOctaveNav = PadMode.NavSet.OctaveNav 
        hLayoutNav = PadMode.NavSet.LayoutNav
        hPRNav = PadMode.NavSet.PianoRollNav
        hRename = PadMode.NavSet.Rename 

        if(PadMode.NavSet.ColorPicker): # handled in MIDI IN
            return True

        if(PadMode.NavSet.CustomMacros): # handle custom macros here
            # TODO 
            # macro = ???
            # RunMacro(macro)
            return True

        if(hRename) and (padIdx == pdRename):
            self.RunMacro(macRename)
            return True
        if(hChanPads):
            if(padIdx in pdShowChanPads):
                if(padIdx == pdShowChanEditor):
                    self.ShowChannelEditor(-1)
                elif(padIdx == pdShowChanPianoRoll):
                    self.ShowPianoRoll(-1)
                return True
        if(hPresetNav):
            if(padIdx in pdPresetNav):
                self.ShowChannelEditor(1)
                if(padIdx == pdPresetPrev):
                    ui.previous()
                elif(padIdx == pdPresetNext):
                    ui.next()
                return True
        if(hPRNav):
            if(padIdx in pdNavMacros):
                idx = pdNavMacros.index(padIdx)
                macro = PianoRollMacros[idx]
                self.RunMacro(macro)

        if(hSnapNav):
            if(padIdx in pdSnapNav):
                self.HandleSnapNav(padIdx)
        elif(hLayoutNav):
            if(padIdx == pdLayoutPrev):
                self.NavLayout(-1)
            elif(padIdx == pdLayoutNext):
                self.NavLayout(1)

        if(hNoteRepeat):
            if(padIdx == pdNoteRepeatLength):
                self.NavNoteRepeatLength(1)
            if(padIdx == pdNoteRepeat):
                self.ToggleRepeat()

        if(hUDLR):
            if(padIdx in pdUDLR):
                return self.HandleUDLR(padIdx)

        if(hOctaveNav) or (hScaleNav):
            if(padIdx == pdOctaveNext):
                self.NavOctavesList(-1)
            elif(padIdx == pdOctavePrev):
                self.NavOctavesList(1)
            if(hScaleNav):
                if(padIdx == pdScaleNext):
                    self.NavScalesList(1)
                elif(padIdx == pdScalePrev):
                    self.NavScalesList(-1)
                elif(padIdx == pdRootNoteNext):
                    self.NavNotesList(-1)
                elif(padIdx == pdRootNotePrev):
                    self.NavNotesList(1)         

        if(PadMode.Mode == MODE_NOTE):
            self.RefreshNotes()
        elif(PadMode.Mode == MODE_DRUM):
            self.RefreshDrumPads()

        self.RefreshNavPads()
        self.RefreshDisplay()
        
        return True 

    def HandleSnapNav(self,padIdx):
        if(padIdx == pdSnapUp):
            ui.snapMode(-1)  # dec by 1
        else:
            ui.snapMode(1)  # inc by 1
        SnapIdx = SnapModesList.index(ui.getSnapMode())
        self.DisplaySnap(SnapIdx)

    def DisplaySnap(self, SnapIdx):
        DisplayTextTop('Snap:')
        DisplayTimedText(SnapModesText[SnapIdx])

    def HandleMacros(self,macIdx):
        if(PadMode.NavSet.MacroNav == False):
            return 
        macro = MacroList[macIdx]
        
        if(PadMode.NavSet.CustomMacros):
            macro = CustomMacros[macIdx]

        # print('Macro:', macro.Name, (macro.Execute==None))
        if(macro.Execute == None):
            if( macro.Name == "ChanRack"): #macIdx == 1):
                self.ShowChannelRack(-1)
                if(Settings.TOGGLE_CR_AND_BROWSER):
                    self.RefreshBrowserDisplay()    
            elif(macro.Name == "Playlist"): # "macIdx == 2):
                if(DoubleTap):
                    ui.showWindow(widPlaylist)
                    macZoom.Execute(Settings.DBL_TAP_ZOOM) 
                else:    
                    self.ShowPlaylist(-1)
            elif(macro.Name == "Mixer"): #"macIdx == 3):
                self.ShowMixer(-1)        
            else:
                return False 
        else:
            self.RunMacro(macro)
        return True 
       
    def HandleNotes(self,event, padNum):
        global ChordInvert
        global Chord7th
        global isRepeating
        

        event.data1 = PadMap[padNum].NoteInfo.MIDINote
        event.data2 = self.translateVelocity(event.data2)
        noteOn = (event.data2 > 0)

        if(ShowChords) and (GetScaleNoteCount(ScaleIdx) == 7):
            if (padNum in pdChordBar):
                chordNum = pdChordBar.index(padNum)+1
                noteVelocity = event.data2
                chan = getCurrChanIdx() # channels.channelNumber()
                self.HandleChord(chan, chordNum, noteOn, noteVelocity, Chord7th, ChordInvert)
                if(noteOn):
                    SetPadColor(padNum, cBlue, dimBright)
                else:
                    SetPadColor(padNum, cBlue, dimNormal)
                return True
            elif(padNum in pdChordFuncs) and (event.data2 > 0):
                chordType = '' # normal
                if (padNum == pd7th): 
                    Chord7th = not Chord7th
                    if(Chord7th):
                        chordType += '7th'
                elif(padNum == pdInv1):
                    ChordInvert = 1 
                    chordType += ' 1st Inv'
                elif(padNum == pdInv2):
                    ChordInvert = 2
                    chordType += ' 2nd Inv'
                elif(padNum == pdNormal): 
                    ChordInvert = 0
                
                self.RefreshNotes()
                DisplayTimedText(chordType)
                return True 
            

        # if(event.data2 < 32): # min velocity is 32, so anything below that s/b note off
        #     self.RefreshNotes()
        # else:
        #     SetPadColor(padNum, cWhite, dimBright)

        return False # to continue processing regular notes

    def HandleDrums(self,event, padNum):
        global isRepeating
        global OrigColor

        event.data2 = self.translateVelocity(event.data2)

        # do the note repeat BEFORE changing the note so the note is retriggered properly
        if(NoteRepeat):
            if(event.data2 < 32): # min velocity is 32, so anything below that s/b note off
                device.stopRepeatMidiEvent()
                isRepeating = False
            elif(not isRepeating):
                isRepeating = True
                ui.setSnapMode(BeatLengthSnap[_NoteRepeatLengthIdx])
                ms = self.getBeatLenInMS(BeatLengthDivs[_NoteRepeatLengthIdx])
                device.repeatMidiEvent(event, ms, ms)

        # if(PadMode.NavSet.ColorPicker): # color picker mode
        #     pads = DrumPads(self)
        #     idx = pads.index(padNum)
        #     chanIdx = getCurrChanIdx
        #     if(self.isFPCActive()):
        #         OrigColor = plugins.getPadInfo(chanIdx, -1, PAD_Color, idx)
        #         plugins.setPadInfo(chanIdx, -1, PAD_Color, idx)
        #         SetPadColor(padNum, FLColorToPadColor(color, 2),dimNormal)
        #         RefreshModes()
        #         return True

        # FPC Quick select
        if(not isAltMode) and (padNum in pdFPCChannels):
            chanNum = PadMap[padNum].ItemIndex
            if(chanNum > -1): # it's an FPC quick select
                self.SelectAndShowChannel(chanNum)
                self.ShowChannelEditor(1)
                self.RefreshDisplay()

        #shoudl return the pads list
        pads =self.DrumPads() 

        if(padNum in pads):
            event.data1 = PadMap[padNum].NoteInfo.MIDINote
            SetPadColor(padNum, PadMap[padNum].Color, dimNormal)
            #print("Pad {} Color: {}".format(padNum, PadMap[padNum].Color))  
            return False
        else:
            return True # mark as handled to prevent processing

    def HandleMixerEffectsStrip(self,padNum):
        stripA, stripB = self.getMixerEffectPads()
        if padNum in stripA:
            slotIdx = stripA.index(padNum)
            trk = mixer.trackNumber()

            effectSlots = self.GetAllEffectsForMixerTrack(trk)
            fx = effectSlots[slotIdx] 
            fx.Update()
            if( not fx.Used):
                return True
            
            if (general.getVersion() >= 32):
                # color picker mode
                if(PadMode.NavSet.ColorPicker) and (self,padNum in stripA): 
                    OrigColor = FLColorToPadColor( mixer.getSlotColor(trk, slotIdx), 1)
                    mixer.setSlotColor(trk, slotIdx, NewColor)
                    self.RefreshColorPicker()
                    self.SetPadMode()
                    return True                

            formidExpected = self.getFormIDFromTrackSlot(trk, slotIdx)
            formidActual = ui.getFocusedFormID()
            if FLVersionAtLeast("21.0.3"):
                if( mixer.getActiveEffectIndex() != (trk, slotIdx) ):
                    mixer.focusEditor(trk, slotIdx)
                    #print('focused editor. new ffid', ui.getFocusedFormID(), 'isEffectFocused', ui.getFocused(widPluginEffect), 'getFWID',  self.getFocusedWID())
                else:
                    #print('closing effect editor?')
                    ui.escape() # should close the active effect
                    # ui.hideWindow(widPluginEffect)
                    # ui.hideWindow(widPlugin)
                    # ui.hideWindow(widPluginGenerator)
                #print("ative formid s/b: ", formidExpected, 'info', mixer.getActiveEffectIndex())

        if padNum in stripB:
            slotIdx = stripB.index(padNum)
            newMute = int(not GetMixerGenParamVal(REC_Plug_Mute, -1, slotIdx))
            SetMixerGenParamVal(REC_Plug_Mute, newMute, -1, slotIdx)
            self.RefreshMixerEffectStrip(True)

        self.RefreshDisplay()
        return True

    def HandleMixerStrip(self,padNum):
        global MixerMap
        global OrigColor 
        global ignoreNextMixerRefresh

        stripA, stripB = self.getMixerStripPads()
        trkNum, mMap = self.getMixerTrackFromPad(padNum)
        if(trkNum == -1):
            return True

        # color picker mode
        if(PadMode.NavSet.ColorPicker) and (self,padNum in stripA): 
            OrigColor = FLColorToPadColor( mixer.getTrackColor(trkNum), 1)
            mixer.setTrackColor(trkNum, NewColor)
            self.RefreshColorPicker()
            self.SetPadMode()
            return True

        if(trkNum != mixer.trackNumber()):
            if(padNum in stripA):
                self.SelectAndShowMixerTrack(trkNum)
                # mixer.setTrackNumber(trkNum, curfxScrollToMakeVisible)
                # ui.miDisplayRect(trkNum, trkNum, rectTime, CR_ScrollToView)
        
        if (padNum in stripB):
            if(AltHeld):
                mixer.armTrack(trkNum)
            elif(ShiftHeld):
                mixer.soloTrack(trkNum)
            else:
                mixer.muteTrack(trkNum) # toggles
        
        self.RefreshMixerStrip()
        self.RefreshDisplay()
        return True 

    def HandlePatternStrip(self,padNum):
        global PatternMap
        global PatternSelectedMap
        global OrigColor

        if(self.isMixerMode()):
            return self.HandleMixerStrip(padNum)
        
        if(self.isPlaylistMode()):
            return self.HandlePlaylist(padNum)

        patternStripA, patternStripB = self.getPatternPads()
        pattNum, pMap = self.getPatternNumFromPad(padNum)
        if(pattNum == -1):
            return True


        if(patterns.patternNumber() != pattNum): 
            if(padNum in patternStripA):
                patterns.jumpToPattern(pattNum)
            else:
                if(isAltMode):
                    patterns.jumpToPattern(pattNum)
                else:
                    if(patterns.isPatternSelected(pattNum)):
                        patterns.selectPattern(pattNum, 0)
                    else:
                        patterns.selectPattern(pattNum, 1)
                self.UpdatePatternModeData()                
                self.RefreshPatternStrip()

        if(AltHeld):
            if FLVersionAtLeast('21.0.3'):
                patterns.clonePattern(pattNum)
        
        # color picker mode
        if(PadMode.NavSet.ColorPicker) and (self,padNum in patternStripA): 
            OrigColor = FLColorToPadColor( patterns.getPatternColor(patterns.patternNumber()), 1)
            patterns.setPatternColor(patterns.patternNumber(), PadColorToFLColor(NewColor) )
            # patterns.setPatternColor(patterns.patternNumber(), NewColor )
            self.UpdatePatternModeData()                
            self.RefreshPatternStrip()
            self.RefreshColorPicker()
            return True

        return True 

    def HandleChannelGroupChanges(self):
        self.UpdatePatternModeData()
        self.RefreshAll()    

    def HandlePatternChanges(self):
        global PatternCount
        global CurrentPattern
        global CurrentPage 

        if (PatternCount > 0) and (PadMode.Mode == MODE_PATTERNS): # do pattern mode
            
            if(PatternCount != patterns.patternCount()):
                PatternCount = patterns.patternCount()
                self.UpdatePatternModeData() 
                self.RefreshPatternStrip()

            else:
                if CurrentPattern != patterns.patternNumber():
                    self.UpdatePatternModeData() 
                    self.RefreshPatternStrip(True)
                else:
                    self.UpdatePatternModeData() 
                    self.RefreshPatternStrip()

            CurrentPattern = patterns.patternNumber()

        if(patterns.patternCount() == 0) and (CurrentPattern == 1): # empty project, set to 1
            PatternCount = 1

        self.RefreshDisplay()

    def HandlePattUpDn(self,ctrlID):
        moveby = 1
        if(ctrlID == IDPatternUp):
            moveby = -1

        if(ShiftHeld):
            newChanIdx = getCurrChanIdx() + moveby
            if(0 <= newChanIdx < ChannelCount):
                self.SelectAndShowChannel(newChanIdx) 
        else:
            newPattern = patterns.patternNumber() + moveby
            if( 0 <= newPattern <= patterns.patternCount()):   #if it's a valid spot then move it
                patterns.jumpToPattern(newPattern)
            else:
                setPatternName = False
                if(Settings.PROMPT_NAME_FOR_NEW_PATTERN):
                    patterns.findFirstNextEmptyPat(FFNEP_FindFirst)
                    # if we dont have a valid name, use the DEFAULT
                    if(patterns.patternNumber() > patterns.patternCount() ):
                        setPatternName = True
                else:
                    patterns.findFirstNextEmptyPat(FFNEP_DontPromptName)
                    setPatternName = True 
                
                if(setPatternName):
                    newPatt = patterns.patternNumber()
                    pattName = Settings.PATTERN_NAME.format(newPatt)
                    patterns.setPatternName(newPatt, pattName)

        self.RefreshDisplay()
        self.RefreshNavPads()

        return True 

    def HandleGridLR(self,ctrlID):
        global ScrollTo
        global PerfTrackOffset

        if(PadMode.Mode == MODE_PERFORM):
            
            pass
        else:
            if(ctrlID == IDBankL):
                self.NavSetList(-1)
            elif(ctrlID == IDBankR):
                self.NavSetList(1)
            ScrollTo = True
            if(self.isNoNav()):
                for pad in pdNav :
                    SetPadColor(pad, cOff,dimNormal)

            self.RefreshModes()
        return True

    def HandleKnobMode(self):
        self.SetKnobMode()
        self.RefreshModes()
        self.RefreshDisplay()
        return True

    def HandleKnob(self,event, ctrlID, useparam = None, displayUpdateOnly = False):
        global lastKnobCtrlID
        global NewColor

        steps =  Settings.BROWSER_STEPS  # default

        if(event.isIncrement != 1):
            event.inEv = event.data2
            if event.inEv >= 0x40:
                event.outEv = event.inEv - 0x80
            else:
                event.outEv = event.inEv
            event.isIncrement = 1
        value = event.outEv

        if displayUpdateOnly:
            value = 0

        if(PadMode.NavSet.ColorPicker) and (ctrlID in [ IDKnob1, IDKnob2, IDKnob3]):
            r, g, b = utils.ColorToRGB(NewColor)
            # print('color picker mode', value, hex(NewColor), r, g, b)
            Name = 'Color'

            if ctrlID == IDKnob1:
                r += value
                r = max(0, min(r, 127))
                Name = 'Color (R)'
                
            elif ctrlID == IDKnob2:
                g += value
                g = max(0, min(g, 127))
                Name = 'Color (G)'
                
            elif ctrlID == IDKnob3:
                b += value 
                b = max(0, min(b, 127))
                Name = 'Color (B)'
            
            NewColor = utils.RGBToColor(r, g, b)
            valstr = f'#{NewColor:06x}'.upper()
            DisplayBar2(Name, value, valstr, False)

            SetPadColor(pdNewColor, NewColor, dimBright)
            # self.RefreshColorPicker()

            return True

        chanNum = getCurrChanIdx() #  channels.channelNumber()
        recEventID = channels.getRecEventId(chanNum)

        plID, plugin = self.getCurrChanPlugin()
        
        if(ctrlID == IDSelect) and (useparam != None): # tweaking via Select Knob
            if(not FLChannelFX) and (self.isGenPlug()): # for plugins/generators
                recEventID += REC_Chan_Plugin_First

            if (useparam.StepsInclZero > 0):
                steps = useparam.StepsInclZero
                #knobres = 1/useparam.StepsInclZero
            if(ShiftHeld):
                steps = Settings.SHIFT_BROWSER_STEPS
                #knobres = shiftres
            elif(AltHeld):
                steps = Settings.ALT_BROWSER_STEPS
                #knobres = altres
            return self.HandleKnobReal(recEventID + useparam.Offset,  value, useparam.Caption + ': ', useparam.Bipolar, steps)

        
        if KnobMode == KM_USER0 and self.isChannelMode(): # KM_CHANNEL :
            if chanNum > -1: # -1 is none selected
                # check if a pad is being held for the FPC params
                pMapPressed = next((x for x in PadMap if x.Pressed == 1), None) 
                heldPadIdx = -1
                chanName = channels.getChannelName(chanNum)

                if(pMapPressed != None):
                    if(pMapPressed.PadIndex in pdFPCA):
                        heldPadIdx = pdFPCA.index(pMapPressed.PadIndex)
                    elif(pMapPressed.PadIndex in pdFPCB):
                        heldPadIdx = pdFPCB.index(pMapPressed.PadIndex) + 64 # internal offset for FPC Params Bank B

                if ctrlID == IDKnob1:
                    if(PadMode.Mode == MODE_DRUM) and (heldPadIdx > -1) and (self.isFPCActive()):
                        return self.HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Volume.Offset + heldPadIdx, event.outEv, ppFPC_Volume.Caption, ppFPC_Volume.Bipolar)
                    else:
                        ui.crDisplayRect(0, chanNum, 0, 1, 10000, CR_ScrollToView + CR_HighlightChannelPanVol)
                        return self.HandleKnobReal(recEventID + REC_Chan_Vol,  value, 'Ch Vol: ' + chanName, False)
                elif ctrlID == IDKnob2:
                    if(PadMode.Mode == MODE_DRUM) and (heldPadIdx > -1) and (self.isFPCActive()):
                        return self.HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Pan.Offset + heldPadIdx, event.outEv, ppFPC_Pan.Caption, ppFPC_Pan.Bipolar)
                    else:
                        ui.crDisplayRect(0, chanNum, 0, 1, 10000, CR_ScrollToView + CR_HighlightChannelPanVol)
                        return self.HandleKnobReal(recEventID + REC_Chan_Pan, value, 'Ch Pan: ' + chanName, True)

                elif ctrlID == IDKnob3:
                    if(PadMode.Mode == MODE_DRUM) and (heldPadIdx > -1) and (self.isFPCActive()):
                        return self.HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Tune.Offset + heldPadIdx, event.outEv, ppFPC_Tune.Caption, ppFPC_Tune.Bipolar)
                    else:
                        return self.HandleKnobReal(recEventID + REC_Chan_FCut, value, 'Ch Flt: ' + chanName, False)

                elif ctrlID == IDKnob4:
                    return self.HandleKnobReal(recEventID + REC_Chan_FRes, value, 'Ch Res: ' + chanName, False)

                else:
                    return True 
        elif KnobMode == KM_USER0 and self.isMixerMode(): # KM_MIXER :
            mixerNum = mixer.trackNumber()
            mixerName = mixer.getTrackName(mixerNum) 
            recEventID = mixer.getTrackPluginId(mixerNum, 0)
            if not ((mixerNum < 0) | (mixerNum >= mixer.getTrackInfo(TN_Sel)) ): # is one selected?
                if ctrlID == IDKnob1:
                    return self.HandleKnobReal(recEventID + REC_Mixer_Vol,  value, 'Mx Vol: ' + mixerName , False)
                elif ctrlID == IDKnob2:
                    if(ShiftHeld):
                        return self.HandleKnobReal(recEventID + REC_Mixer_SS,  value, 'Mx S.Sep: '+ mixerName, True)
                    else:
                        return self.HandleKnobReal(recEventID + REC_Mixer_Pan,  value, 'Mx Pan: '+ mixerName, True)
                elif ctrlID == IDKnob3:
                    if(ShiftHeld):
                        return self.HandleKnobReal(recEventID + REC_Mixer_EQ_Freq,  value, 'Lo Freq: '+ mixerName, True)
                    else:
                        return self.HandleKnobReal(recEventID + REC_Mixer_EQ_Gain,  value, 'Lo Gain: '+ mixerName, True)
                elif ctrlID == IDKnob4:
                    #return self.HandleKnobReal(recEventID + REC_Mixer_EQ_Gain + 2,  value, 'Mix EQHi: '+ mixerName, True)
                    if(ShiftHeld):
                        return self.HandleKnobReal(recEventID + REC_Mixer_EQ_Freq + 1,  value, ' Mid Freq: '+ mixerName, True)
                    else:
                        return self.HandleKnobReal(recEventID + REC_Mixer_EQ_Gain + 1,  value, 'Mid Gain: '+ mixerName, True)
        elif(self.isKnownPlugin() and (KnobMode in [KM_USER1, KM_USER2, KM_USER3] )):
            knobParam = None
            recEventID = channels.getRecEventId(getCurrChanIdx()) + REC_Chan_Plugin_First
            pluginName, plugin = self.getCurrChanPlugin()
            if(plugin == None): # invalid plugin
                return True
            
            if(plugin.Type == cpGlobal):
                recEventID = 0

            knobOffs = ctrlID - IDKnob1
            value = event.outEv
            if displayUpdateOnly:
                value = 0
            if(KnobMode == KM_USER1):
                knobParam = plugin.User1Knobs[knobOffs]
                knobParam.Caption = plugin.User1Knobs[knobOffs].Caption
            if(KnobMode == KM_USER2):
                knobParam = plugin.User2Knobs[knobOffs]
                knobParam.Caption = plugin.User2Knobs[knobOffs].Caption
            if(KnobMode == KM_USER3):
                knobParam = plugin.User3Knobs[knobOffs]
                knobParam.Caption = plugin.User3Knobs[knobOffs].Caption
            if(  knobParam.Offset > -1  ): # valid offset?
                return self.HandleKnobReal(recEventID + knobParam.Offset,  value, knobParam.Caption + ': ', knobParam.Bipolar)
            return True
        else:  #user modes..
            if (event.status in [MIDI_NOTEON, MIDI_NOTEOFF]):
                event.handled = True
            return True # these knobs will be handled in OnMidiMsg prior to this.

    def HandleKnobForColor(self, value, Name):
        global NewColor
        valstr = "{}".format(hex(NewColor))
        DisplayBar2(Name, value, valstr, False)

        
        return True
    
    def HandleKnobReal(self,recEventIDIndex, value, Name, Bipolar, stepsInclZero = 0):
        knobres = 1/64
        if(stepsInclZero > 0):
            knobres = 1/stepsInclZero
        # general.processRECEvent(recEventIDIndex, value, REC_MIDIController) doesnt support knobres
        
        if(value != 0): # value is the knob direction.  0 would mean no movement
            mixer.automateEvent(recEventIDIndex, value, REC_MIDIController, 0, 1, knobres) 
        
        # show the name/value on the display
        currVal = device.getLinkedValue(recEventIDIndex)
        valstr = device.getLinkedValueString(recEventIDIndex)
        DisplayBar2(Name, currVal, valstr, Bipolar)
        
        return True

    def HandlePage(self,event, ctrlID):
        global ShowChords
        global PatternPage
        global ChannelPage
        global progressZoomIdx

        #differnt modes use these differently   
        if(PadMode.Mode == MODE_PATTERNS):
            print('hp', ctrlID)
            if(ctrlID in [IDPage0, IDPage2]): # pgUp
                val = -1
            elif(ctrlID in [IDPage1, IDPage3]): # pgDn
                val = 1

            if(ctrlID in [IDPage0, IDPage1]): # top set
                if(self.isMixerMode()):
                    self.MixerPageNav(val)
                elif(self.isChannelMode()):
                    self.PatternPageNav(val)
                elif(self.isPlaylistMode()):
                    self.PlaylistPageNav(val)
            elif(ctrlID in [IDPage2, IDPage3]): # bottom set
                if(self.isChannelMode()):
                    self.ChannelPageNav(val)
                elif(self.isPlaylistMode()):
                    self.ProgressZoomNav(val)
            self.RefreshModes()
        elif(PadMode.Mode == MODE_NOTE) and (self,ctrlID == IDPage0): 
            if (GetScaleNoteCount(ScaleIdx) == 7): #if(ScaleIdx > 0):
                ShowChords = not ShowChords
            else:    
                ShowChords = False
                # make the mute led turn red
            self.RefreshNotes()
        elif(PadMode.Mode == MODE_PERFORM):
            pass 

        self.RefreshPageLights()
        self.RefreshDisplay()
        return True

    def HandleShiftAlt(self,event, ctrlID):
        global ShiftHeld
        global AltHeld
        global ShiftLock
        global AltLock

        if(ctrlID == IDShift):
            ShiftHeld = (event.data2 > 0)
            ShiftLock = DoubleTap
        elif(ctrlID == IDAlt):
            AltHeld = (event.data2 > 0)
            AltLock = DoubleTap
        self.OnRefresh(HW_CustomEvent_ShiftAlt)

    def HandlePadModeChange(self,ctrlID):
        global isAltMode
        global isShiftMode
        global PadMode 

        if (PadMode.isTempNavSet()):
            PadMode.RecallPrevNavSet()

        if(not AltHeld) and (not ShiftHeld): #normal pad mode switch
            isShiftMode = False
            isAltMode = False
            if(ctrlID == IDStepSeq):
                PadMode = modePattern
            elif(ctrlID == IDNote):
                PadMode = modeNote
            elif(ctrlID == IDDrum):
                PadMode = modeDrum
            elif(ctrlID == IDPerform):
                PadMode = modePerform
                if(checkFLVersionAtLeast('20.99.0')):
                    if(playlist.getPerformanceModeState() == 1): # in performance mode
                        PadMode = modePerform
        elif(AltHeld) and (not ShiftHeld): # Alt modes
            isShiftMode = False
            isAltMode = True 
            if(ctrlID == IDStepSeq):
                PadMode = modePatternAlt
            if(ctrlID == IDNote):
                PadMode = modeNoteAlt
            if(ctrlID == IDDrum):
                PadMode = modeDrumAlt
            if(ctrlID == IDPerform): #force a refresh on the pl tack bar A to clear it
                PadMode = modePerformAlt
                

        elif(AltHeld) and (ShiftHeld): # Shift modes
            isShiftMode = True 
            isAltMode = True

        self.SetPadMode()
        return True
        
    def HandleTransport(self, event):
        global turnOffMetronomeOnNextPlay

        # if(ShiftHeld):
        #     HandleShifted(event)

        if(AltHeld):
            return True

        if(event.data1 == IDPatternSong):
            if(ShiftHeld):
                pass
            else:
                transport.setLoopMode()

        if(event.data1 == IDPlay):
            if turnOffMetronomeOnNextPlay and ui.isMetronomeEnabled():
                turnOffMetronomeOnNextPlay = False
                transport.globalTransport(FPT_Metronome, 1)
            
            if(transport.isPlaying()):
                transport.stop()
                self.ResetBeatIndicators()
            else:
                self.UpdateMarkerMap()
                transport.start()

        if(event.data1 == IDStop):
            transport.stop()
            self.ResetBeatIndicators()
            if(self.isPlaylistMode()):
                self.UpdateMarkerMap()
            transport.setSongPos(0.0)
            self.RefreshModes()

        if(event.data1 == IDRec):
            transport.record()

        self.RefreshTransport()

        return True 

    def HandleShifted(self,event):
        '''
            self.Handles the SHIFTED states for the bottom row buttons (modes, transport)
        '''
        global turnOffMetronomeOnNextPlay
        global AccentEnabled #GS

        ctrlID = event.data1
        if(ctrlID == IDAccent):
            if(AccentEnabled):   #GS
                AccentEnabled = False
            else:
                AccentEnabled = True        
        elif(ctrlID == IDSnap):
            transport.globalTransport(FPT_Snap, 1)
        elif(ctrlID == IDTap):
            if(ui.isMetronomeEnabled()):
                transport.globalTransport(FPT_TapTempo, 1)
            else:
                transport.globalTransport(FPT_Metronome, 1)
                turnOffMetronomeOnNextPlay = True 
                transport.globalTransport(FPT_TapTempo, 1)
        elif(ctrlID == IDOverview):
            pass 
        elif(ctrlID == IDMetronome):
            transport.globalTransport(FPT_Metronome, 1)
        elif(ctrlID == IDWait):
            transport.globalTransport(FPT_WaitForInput, 1)
        elif(ctrlID == IDCount):
            transport.globalTransport(FPT_CountDown, 1)
        elif(ctrlID == IDLoop):
            transport.globalTransport(FPT_LoopRecord, 1)
        
        self.RefreshShiftedStates()
        event.handled = True 

    def HandleSelectWheel(self,event, ctrlID):
        '''
            Handles the select wheel rotation and pressed events
        '''
        global menuItemSelected
        global menuItems
        global chosenItem
        global lastBrowserFolder 

        jogNext = 1
        jogPrev = 127

        if(PadMode.Mode == MODE_PERFORM):

            if PadMode.IsAlt:
                self.RefreshAltPerformanceMode()
            else:
                if(event.data2 == jogNext):
                    self.NavPerfTrackOffset(+16)
                else:
                    self.NavPerfTrackOffset(-16)
                self.UpdatePerformanceBlocks()            
                self.RefreshPerformanceMode(-1)
            return True
        elif(ui.getFocused(widBrowser)):
            if(ctrlID == IDSelect):
                caption = ''
                if(event.data2 == jogNext):
                    #ui.down
                    if(FLVersionAtLeast('20.99.0')):
                        #ui.down()
                        caption = ui.navigateBrowser(FPT_Down, ShiftHeld)  # added in FL21
                        #caption = ui.navigateBrowserMenu(1, ShiftHeld)                    
                    else:
                        caption = ui.navigateBrowserMenu(1, ShiftHeld)
                elif(event.data2 == jogPrev):
                    #ui.up
                    if(FLVersionAtLeast('20.99.0')):
                        #ui.up()  
                        caption = ui.navigateBrowser(FPT_Up, ShiftHeld)
                        #caption = ui.navigateBrowserMenu(0, ShiftHeld)
                    else:
                        caption = ui.navigateBrowserMenu(0, ShiftHeld)
                
                self.RefreshBrowserDisplay(caption)

                # ftype = ui.getFocusedNodeFileType()
                # actions = ''
                # if(ftype <= -100):
                #     actions = '[]'
                # else:
                #     actions = '[] S+[] A+[]'
                # DisplayTimedText2('Browser', caption, actions )
            elif(ctrlID == IDSelectDown):
                if(ui.getFocusedNodeFileType() <= -100):
                    lastBrowserFolder = '>' + ui.getFocusedNodeCaption()
                    ui.enter()
                else:
                    ui.selectBrowserMenuItem() # brings up menu
                    if(ShiftHeld) or (AltHeld):
                        ui.down()
                        if(AltHeld):
                            ui.down()
                        ui.enter()            
            return True 
        elif(not ShowMenu):
            if(ctrlID == IDSelectDown):
                #HandleBrowserButton()
                ui.enter()
            else:
                numIdx = -1
                name = ''
                window = ''
                if(not ShiftHeld) and (not AltHeld):
                    if(event.data2 == jogNext):
                        if(ui.getFocused(widMixer)):
                            ui.right()
                        else:
                            ui.down()
                    elif(event.data2 == jogPrev):
                        if(ui.getFocused(widMixer)):
                            ui.left()
                        else:
                            ui.up()
                    time.sleep(0.02) # if no delay, it reads the previous info
                
                if(ui.getFocused(widMixer)):
                    window = 'Mixer'    
                    numIdx = mixer.trackNumber()
                    name = mixer.getTrackName(numIdx) 
                    if(ShiftHeld):
                        if(event.data2 == jogNext):
                            ui.right()
                        if(event.data2 == jogPrev):
                            ui.left()

                elif(ui.getFocused(widChannelRack)):
                    window = 'Channel Rack'
                    numIdx = getCurrChanIdx()
                    name = channels.getChannelName(numIdx)
                elif(ui.getFocused(widPlaylist)):
                    window = 'Playlist'
                elif(ui.getFocused(widPianoRoll)):
                    window = 'Piano Roll'

                if(window in ['Piano Roll', 'ChannelRack']):
                    if(ShiftHeld):
                        if(event.data2 == jogNext):
                            ui.right()
                        if(event.data2 == jogPrev):
                            ui.left()
                if(window in ['Playlist']): # 'Piano Roll' crashes ATM
                    print('PL scrolling')
                    if(AltHeld):
                        if(ShiftHeld):
                            window += 'vZoom'
                            if(event.data2 == jogNext):
                                ui.verZoom(2)
                            if(event.data2 == jogPrev):
                                ui.verZoom(-2)
                        else:
                            window += 'hZoom'
                            if(event.data2 == jogNext):
                                ui.horZoom(2)
                            if(event.data2 == jogPrev):
                                ui.horZoom(-2)
                            self.SetTop()
                    elif(ShiftHeld):
                        if(event.data2 == jogNext):
                            ui.right()
                            print('pl right')
                        if(event.data2 == jogPrev):
                            ui.left()
                            print('pl left')

                if(numIdx > -1):                    
                    DisplayTimedText2(window, "{}-{}".format(numIdx, name), '')
                else:
                    DisplayTimedText2(window, '', '')
                    
            
            return True

        self.ShowMenuItems()
        paramName, plugin = self.getCurrChanPlugin()
        if(plugin == None): # invalid plugin
            return True

        if(ctrlID == IDSelectDown):
            chosenItem = menuItemSelected
            itemstr = menuItems[menuItemSelected]
            if(menuItems[menuItemSelected] == menuBackText) or (len(menuHistory) == MAXLEVELS):
                menuItemSelected = menuHistory.pop()
            else:
                if(len(menuHistory) < MAXLEVELS): 
                    menuHistory.append(menuItemSelected) 
                    menuItemSelected = 0

                if(len(menuHistory) == MAXLEVELS):
                    #groupName = list(plugin.ParameterGroups.keys())[menuHistory[0]]
                    groupName =  plugin.getGroupNames()[menuHistory[0]]
                    plugin.TweakableParam = plugin.ParameterGroups[groupName][chosenItem]

            chosenItem = menuItemSelected

            if(len(menuHistory) == MAXLEVELS) and (plugin.TweakableParam != None):
                return self.HandleKnob(event, IDSelect, plugin.TweakableParam, True)
            else:
                self.ShowMenuItems()
                return True 

                    
        
        elif(ctrlID == IDSelect):

            if(len(menuHistory) == MAXLEVELS) and (plugin.TweakableParam != None):
                return self.HandleKnob(event, ctrlID, plugin.TweakableParam)

            if(event.data2 == jogNext) and (menuItemSelected < (len(menuItems)-1) ):
                menuItemSelected += 1
                if(menuItemSelected > len(menuItems)-1):
                    menuItemSelected = 0
            elif(event.data2 == jogPrev): # and (menuItemSelected > 0):
                menuItemSelected += -1
                if(menuItemSelected < 0):
                    menuItemSelected = len(menuItems)-1

            self.ShowMenuItems()
            return True 

    def HandleBrowserButton(self):
        global ShowMenu 
        global menuItems
        global menuItemSelected
        global menuHistory
        global FLChannelFX
        # global ShowBrowser

        self.prnt('handle browser button', ShiftHeld, AltHeld)

        # in a menu
        if (ui.isInPopupMenu()):
            ui.closeActivePopupMenu()

        # regular File browser....
        if(not ShiftHeld) and (not AltHeld) and (not ShowMenu):
            if(ui.getFocused(widBrowser) == 1):
                if (Settings.TOGGLE_CR_AND_BROWSER):
                    self.ShowChannelRack(1)
                else:
                    if(Settings.HIDE_BROWSER):
                        self.ShowBrowser(0)
            else:
                if (Settings.TOGGLE_CR_AND_BROWSER):
                    self.ShowChannelRack(0)
                self.ShowBrowser(1)

            self.RefreshBrowserDisplay()
            self.UpdateAndRefreshWindowStates()
            
            return True

        #
        # para /settings menus    
        ShowMenu = not ShowMenu
        if(ShowMenu):
            # self.prnt('showing alt menu', ShiftHeld, AltHeld)
            FLChannelFX = ShiftHeld
            menuHistory.clear()
            menuItemSelected = 0
            SendCC(IDBrowser, SingleColorFull)  #SingleColorHalfBright
            self.ShowMenuItems()
            if(FLChannelFX):
                channels.showEditor(getCurrChanIdx(), 1) 
                ui.right()
        else:
            # self.prnt('hiding alt menu', ShiftHeld, AltHeld)
            if(FLChannelFX):
                channels.showEditor(getCurrChanIdx(), 0) 
            FLChannelFX = False
            SendCC(IDBrowser, SingleColorOff) 
            self.RefreshDisplay()
        return True

    def HandleChord(self,chan, chordNum, noteOn, noteVelocity, play7th, playInverted):
        global ChordNum
        global ChordInvert
        global Chord7th
        play7th = Chord7th
        playInverted = ChordInvert
        realScaleIdx = ScaleIdx #  HarmonicScalesLoaded[_ScaleIdx] #  ScalesList[ScaleIdx]

        if (GetScaleNoteCount(realScaleIdx) != 7): #if not enough notes to make full chords, do not do anything
            return 

        chordTypes = ['','m','m','','','m','dim']
        chordName = ''

        note =  -1  #the target root note
        note3 = -1
        note5 = -1
        note7 = -1
        note5inv = -1  
        note3inv = -1  
        offset = 0

        if(0 < chordNum < 8): #if a chord, then use the ScaleNotes to find the notes
            offset = GetScaleNoteCount(realScaleIdx) + (chordNum-1)
            note = ScaleNotes[offset]
            note3 = ScaleNotes[offset + 2]
            note5 = ScaleNotes[offset + 4]
            note7 = ScaleNotes[offset + 6]
            note7inv = ScaleNotes[offset - 1]
            note3inv = ScaleNotes[offset - 5] 
            note5inv = ScaleNotes[offset - 3] 
            chordName = NotesList[note % 12]
            chordName += chordTypes[ ((ScaleIdx + chordNum) % 7)-2 ]

        if(noteOn):
            #
            ChordNum = chordNum
            chordinv = ''


            if(playInverted == 1):
                chordinv = '1st.Inv'
                self.PlayMIDINote(chan, note3inv, noteVelocity)
                self.PlayMIDINote(chan, note5inv, noteVelocity)
                if(play7th):
                    chordName += '7 '
                    self.PlayMIDINote(chan, note7inv, noteVelocity)                 
                self.PlayMIDINote(chan, note, noteVelocity)
            elif(playInverted == 2):
                chordinv = '2nd.Inv'
                self.PlayMIDINote(chan, note5inv, noteVelocity)
                if(play7th):
                    chordName += '7 '
                    self.PlayMIDINote(chan, note7inv, noteVelocity)                 
                self.PlayMIDINote(chan, note, noteVelocity)
                self.PlayMIDINote(chan, note3, noteVelocity)
            else:
                self.PlayMIDINote(chan, note, noteVelocity)
                self.PlayMIDINote(chan, note3, noteVelocity)
                self.PlayMIDINote(chan, note5, noteVelocity)
                if(play7th):
                    chordName += '7 '
                    self.PlayMIDINote(chan, note7, noteVelocity)                 

            # RefreshNotes()
            self.RefreshChordType()
            DisplayTimedText2('Chord:',  chordName, chordinv)

        else:
            # turn off the chord
            self.PlayMIDINote(chan, note3inv, noteVelocity)
            self.PlayMIDINote(chan, note5inv, noteVelocity)
            self.PlayMIDINote(chan, note7inv, noteVelocity)
            self.PlayMIDINote(chan, note7, noteVelocity)
            self.PlayMIDINote(chan, note, noteVelocity)
            self.PlayMIDINote(chan, note3, noteVelocity)
            self.PlayMIDINote(chan, note5, noteVelocity)
        
        

    def HandleColorPicker(self,padNum):
        '''
            Hanldes the ColorPicker events. padNum is the 0..63 pad offset and padIndex is the 0..15 index within the pdMacroNav pads.
        '''
        global NewColor
        pl = list(Settings.Pallette.values())
        if(padNum == pdOrigColor):
            NewColor = OrigColor
        elif(padNum in pdPallette):
            NewColor = pl[pdPallette.index(padNum)]
        if(padNum == pdChanColor): # curr chan color
            NewColor = FLColorToPadColor(channels.getChannelColor(getCurrChanIdx()), 1)
        elif(padNum == pdPattColor): # curr pattern color
            NewColor = FLColorToPadColor(patterns.getPatternColor(patterns.patternNumber()), 1)
        elif(padNum == pdMixColor):
            NewColor = FLColorToPadColor(mixer.getTrackColor(mixer.trackNumber()), 1)
        self.RefreshColorPicker()
        return True 

    def HandleUDLR(self,padIndex):
        isFL21Browser = ui.getFocused(widBrowser) and (ui.getVersion(0) >= 21)

        if(padIndex == pdTab):
            if(not ShiftHeld):
                if isFL21Browser:
                    ui.navigateBrowserTabs(FPT_Right)
                else:
                    ui.selectWindow(0)
            else:   
                if isFL21Browser:
                    ui.navigateBrowserTabs(FPT_Left)
                else:
                    ui.nextWindow()
        elif(padIndex == pdMenu):
            NavigateFLMenu('', AltHeld)
        elif(padIndex == pdUp):
            if(ui.isInPopupMenu()) and (ui.getFocused(widBrowser)) and (ShiftHeld): 
                NavigateFLMenu(',UUUUE')
            else:
                ui.up()
        elif(padIndex == pdDown):
            if(ui.isInPopupMenu()) and (ui.getFocused(widBrowser)) and (ShiftHeld): 
                NavigateFLMenu(',UUUE')
            else:
                ui.down()
        elif(padIndex == pdLeft):
            ui.left()
        elif(padIndex == pdRight):
            ui.right()
        elif(padIndex == pdEsc):
            ui.escape()
        elif(padIndex == pdEnter):
            if isFL21Browser:
                ui.selectBrowserMenuItem() # brings up menu
                if(ShiftHeld) or (AltHeld):
                    ui.down()
                    if(AltHeld):
                        ui.down()
                    ui.enter()            
            else:
                ui.enter()
        else:
            return False 
        return True
    #endregion 

    #region Refresh
    def RefreshAll(self):
        self.prn(lvlA, 'RefreshAll')
        self.UpdateMixerMap(-1)
        self.RefreshPageLights()
        self.RefreshModes()
        self.RefreshMacros()
        self.RefreshNavPads()
        self.RefreshDisplay()
        self.UpdateAndRefreshWindowStates()
        return 

    def RefreshModes(self):
        global ScrollTo
        if(PadMode.Mode == MODE_DRUM):
            self.RefreshDrumPads()
        elif(PadMode.Mode == MODE_PATTERNS):

            # if(True) and (not transport.isPlaying()):
            #     UpdatePlaylistMap(False, True)
            #     playlist.deselectAll()
            #     playlist.selectTrack(1)
            
            self.UpdatePatternModeData() # must be don ehere
            if(self.isChannelMode()):
                self.RefreshPatternStrip(ScrollTo) 
                self.RefreshChannelStrip(ScrollTo)
            elif(self.isMixerMode()):
                self.RefreshMixerStrip(ScrollTo)
                self.RefreshMixerStrip()
            elif(self.isPlaylistMode(True)): # only when focused, in case in a color dialog or menu
                self.UpdatePlaylistMap()
                self.RefreshPlaylist()
                if(SHOW_PROGRESS):
                    self.UpdateAndRefreshProgressAndMarkers()
            else:
                self.RefreshPatternStrip(ScrollTo) 
                self.RefreshChannelStrip(ScrollTo)

            ScrollTo = False
        elif(PadMode.Mode == MODE_NOTE):
            self.RefreshNotes()
        elif(PadMode.Mode == MODE_PERFORM):
            if PadMode.IsAlt:
                self.RefreshAltPerformanceMode()
            else:
                self.RefreshPerformanceMode(-1)
            
    def RefreshPadModeButtons(self):
        if(ShiftHeld): 
            self.RefreshShiftedStates()    
            return 

        SendCC(IDStepSeq, DualColorOff)
        SendCC(IDNote, DualColorOff)
        SendCC(IDDrum, DualColorOff)
        SendCC(IDPerform, DualColorOff)



        if(PadMode.Mode == MODE_PATTERNS):
            SendCC(IDStepSeq, DualColorFull2)
        elif(PadMode.Mode == MODE_NOTE):
            SendCC(IDNote, DualColorFull2)
        elif(PadMode.Mode == MODE_DRUM):
            SendCC(IDDrum, DualColorFull2)
        elif(PadMode.Mode == MODE_PERFORM):
            SendCC(IDPerform, DualColorFull2)

        # update the bridge
        padmode = ''
        if(PadMode.IsAlt):
            padmode = 'Alt + '
        padmode = padmode + PadModeNames[PadMode.Mode]
        fireNFX_Bridge.WriteINI('General', 'padmode', padmode)
        

    def RefreshShiftAltButtons(self):
        if(ShiftHeld): 
            self.RefreshShiftedStates()    
            return 

        if(AltHeld):
            SendCC(IDAlt, SingleColorFull)
        elif(isAltMode):
            SendCC(IDAlt, SingleColorFull)
        # elif(AltLock):
        #     SendCC(IDAlt, SingleColorHalfBright)
        else:
            SendCC(IDAlt, SingleColorOff)

        if(ShiftHeld):
            self.RefreshShiftedStates()
            self.RefreshChannelStrip(False)
        # elif(ShiftLock):
        #     SendCC(IDShift, DualColorHalfBright2)
        else:  
            SendCC(IDShift, DualColorOff)
            self.RefreshChannelStrip(False)
            self.RefreshPadModeButtons()
            self.RefreshTransport()

    def RefreshTransport(self):
        if(ShiftHeld): 
            self.RefreshShiftedStates()    
            return 

        if(transport.getLoopMode() == SM_Pat):
            SendCC(IDPatternSong, IDColPattMode)
        else:
            SendCC(IDPatternSong, IDColSongMode)

        if(transport.isPlaying()):
            SendCC(IDPlay, IDColPlayOn)
        else:
            SendCC(IDPlay, IDColPlayOff)
            if PadMode.Mode == MODE_NOTE:
                self.RefreshNotes()
            

        SendCC(IDStop, IDColStopOff)

        if(transport.isRecording()):
            SendCC(IDRec, IDColRecOn)
        else:
            # if(ui.isLoopRecEnabled()):
            #     SendCC(IDLoop, DualColorFull2)
            # else:
            SendCC(IDRec, IDColRecOff)

    def RefreshShiftedStates(self):
        ColOn = DualColorFull2 
        ColOff = DualColorOff

        if(ShiftHeld):
            SendCC(IDShift, DualColorFull1)
            if(PadMode.Mode == MODE_PATTERNS):
                self.RefreshChannelStrip()
        else:
            SendCC(IDShift, ColOff)

        SendCC(IDAccent, ColOff)
        SendCC(IDSnap, ColOff)
        SendCC(IDTap, ColOff)
        SendCC(IDOverview, ColOff)
        SendCC(IDPatternSong, ColOff)
        SendCC(IDPlay, ColOff)
        SendCC(IDStop, ColOff)
        SendCC(IDRec, ColOff)

        if(ui.getSnapMode() != Snap_None):
            SendCC(IDSnap, ColOn)

        if(ui.isMetronomeEnabled()):
            SendCC(IDPatternSong, ColOn)

        if(ui.isStartOnInputEnabled()):
            SendCC(IDWait, ColOn)

        if(ui.isPrecountEnabled()):
            SendCC(IDCount, ColOn)

        if(ui.isLoopRecEnabled()):
            SendCC(IDLoop, ColOn)

        if(AccentEnabled):   #GS
            SendCC(IDAccent, ColOn)
        
    def RefreshPadsFromPadMap(self):
        for pad in range(0,64):
            SetPadColor(pad, PadMap[pad].Color,dimNormal) 

    def RefreshMacros(self):
        # refreshes the top two rows of the macro grid 
        self.prn(lvlA, 'RefreshMacros') 
        if self.isNoMacros():
            for pad in pdMacros :
                fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdMacros.index(pad)), '---')
                fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdMacros.index(pad)), cOff)            
            return 
        if(PadMode.NavSet.CustomMacros):
            for idx, pad in enumerate(pdMacroNav):
                SetPadColor(pad, CustomMacros[idx].PadColor,dimNormal)
        else:
            for idx, pad in enumerate(pdMacros):
                SetPadColor(pad, MacroList[idx].PadColor,dimNormal)
                fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(idx), MacroList[idx].Name)
                fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(idx), ColorWithAlpha( MacroList[idx].PadColor) )

    def RefreshMarkers(self):
        for pad in pdMarkers:
            idx = pdMarkers.index(pad)
            SetPadColor(pad, getShade(cOrange, shDim),dimNormal)

    def RefreshNavPads(self):
        global PadMode
        global ChannelMap
        # mode specific
        showPresetNav = PadMode.NavSet.PresetNav 
        showNoteRepeat = PadMode.NavSet.NoteRepeat
        showUDLRNav = PadMode.NavSet.UDLRNav
        showChanWinNav = PadMode.NavSet.ChanNav
        showSnapNav = PadMode.NavSet.SnapNav
        showScaleNav = PadMode.NavSet.ScaleNav
        showOctaveNav = PadMode.NavSet.OctaveNav
        showLayoutNav = PadMode.NavSet.LayoutNav
        showPRNav = PadMode.NavSet.PianoRollNav
        showRename = PadMode.NavSet.Rename 

        self.RefreshGridLR()        
        currChan = getCurrChanIdx()

        if(PadMode.NavSet.ColorPicker):
            self.RefreshColorPicker()
            return 
        if(PadMode.NavSet.CustomMacros):
            # TODO 
            # RefreshCustomMacros()
            return

        if(showUDLRNav):
            self.RefreshUDLR()
            return 

        if(self.isNoNav()):
            for pad in pdNav :
                fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pad)+8), '---')
                fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pad)+8), cOff)            
            return
    # no
        
        #clear first
        for pad in pdNav :
            SetPadColor(pad, cOff,dimNormal, False)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pad)+8), '---')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pad)+8), cOff)
        
        if(showRename):
            SetPadColor(pdRename, colRename, dimNormal)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pdRename)+8), 'Rename')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pdRename)+8), colRename) 

        if(showChanWinNav) or (showPRNav):
            self.RefreshChanWinNav(currChan)

        if(showPresetNav):
            for idx, pad in enumerate(pdPresetNav):
                color = colPresetNav[idx]
                name = pdPresetText[idx]
                SetPadColor(pad, color,dimNormal)
                fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pad)+8), name)
                fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pad)+8), color)

        if(showPRNav):
            for idx, macro in enumerate(PianoRollMacros):
                padIdx = pdNavMacros[idx]
                SetPadColor(padIdx, macro.PadColor,dimNormal)
                #TODO bridge write
            return 

        # these two are exclusive as they use the same pads in diff modes
        if(showScaleNav):
            for idx, pad in enumerate(pdNoteFuncs):
                color = colNoteFuncs[idx]
                text =  pdNoteFuncsText[idx]
                SetPadColor(pad, color,dimNormal)
                fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pad)+8), text)
                fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pad)+8), color)


        elif(showOctaveNav) and (not showNoteRepeat): 
            SetPadColor(pdOctaveNext, colOctaveNext,dimNormal)
            SetPadColor(pdOctavePrev, colOctavePrev,dimNormal)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pdOctaveNext)+8), 'OctUp')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pdOctaveNext)+8), colOctaveNext)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pdOctavePrev)+8), 'OctDown')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pdOctavePrev)+8), colOctavePrev)
            

        if(showNoteRepeat):
            if(NoteRepeat):
                SetPadColor(pdNoteRepeat, colNoteRepeat,dimBright)
                SetPadColor(pdNoteRepeatLength, colNoteRepeatLength,dimDim)
            else:
                SetPadColor(pdNoteRepeat, colNoteRepeat,dimNormal)
                SetPadColor(pdNoteRepeatLength, colNoteRepeatLength,dimDim)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pdNoteRepeat)+8), 'NoteRpt')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pdNoteRepeat)+8), colNoteRepeat)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pdNoteRepeatLength)+8), 'NoteRptLen')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pdNoteRepeatLength)+8), colNoteRepeatLength)

        # these two are exclusive as they use the same pads in diff modes
        if(showSnapNav):
            SetPadColor(pdSnapUp, colSnapUp,dimNormal)
            SetPadColor(pdSnapDown, colSnapDown,dimDim)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pdSnapUp)+8), 'SnapUp')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pdSnapUp)+8), colSnapUp)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pdSnapDown)+8), 'SnapDown')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pdSnapDown)+8), colSnapDown)
        elif(showLayoutNav):
            SetPadColor(pdLayoutPrev, colLayoutPrev,dimNormal)
            SetPadColor(pdLayoutNext, colLayoutNext,dimNormal)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pdLayoutPrev)+8), 'LayoutUp')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pdLayoutPrev)+8), colLayoutPrev)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pdLayoutNext)+8), 'LayoutDown')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pdLayoutNext)+8), colLayoutNext)

    def RefreshChanWinNav(self,currChan = -1):
        if (PadMode.NavSet.ChanNav):
            if(currChan == -1):
                currChan = getCurrChanIdx()
            color = FLColorToPadColor(ChannelMap[currChan].Color)
            SetPadColor(pdShowChanEditor, color, dimNormal)
            # SetPadColor(pdShowChanEditor, color, ChannelMap[currChan].DimA)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pdShowChanEditor) + 8), 'ChanEdit')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pdShowChanEditor) + 8), color)
            
            prColor = cWhite
            if(ui.getFocused(widPianoRoll)):
                # SetPadColor(pdShowChanPianoRoll, ChannelMap[currChan].PadBColor, ChannelMap[currChan].DimB)            
                prColor = color 
            SetPadColor(pdShowChanPianoRoll, prColor,dimBright)
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(pdNav.index(pdShowChanPianoRoll) + 8), 'PianoRoll')
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(pdNav.index(pdShowChanPianoRoll) + 8), prColor)

    def RefreshPageLights(self, clearOnly = False):
        global PadMode
        SendCC(IDPage0, SingleColorOff)
        SendCC(IDPage1, SingleColorOff)
        SendCC(IDPage2, SingleColorOff)
        SendCC(IDPage3, SingleColorOff)                    
        SendCC(IDTrackSel1, SingleColorOff)    
        SendCC(IDTrackSel2, SingleColorOff)    
        SendCC(IDTrackSel3, SingleColorOff)    
        SendCC(IDTrackSel4, SingleColorOff)    

        if(clearOnly):
            return 

        if(PadMode.Mode == MODE_NOTE):
            if(ShowChords):
                SendCC(IDPage0, SingleColorHalfBright)
            if (GetScaleNoteCount(ScaleIdx) == 7): # Can use the chord bar
                SendCC(IDTrackSel1, DualColorFull2)  
            else:
                SendCC(IDTrackSel1, DualColorHalfBright1)
        elif(PadMode.Mode == MODE_PERFORM):
            if(PadMode.IsAlt):
                SendCC(IDPage0 + progressZoomIdx, SingleColorHalfBright)
        elif(PadMode.Mode == MODE_PATTERNS):
            page = PatternPage
            if(self.isMixerMode()):
                page = MixerPage
            if(self.isPlaylistMode()):
                page = PlaylistPage
            # pattern page / mixer page
            if(page > 0):
                SendCC(IDPage0, SingleColorFull)
            if(page > 1):
                SendCC(IDTrackSel1, SingleColorFull)
            if(page > 2):
                SendCC(IDPage1, SingleColorFull)
            if(page > 3):
                SendCC(IDTrackSel2, SingleColorFull)

            # channel page / effects page
            page = ChannelPage
            if(self.isMixerMode()):
                page = -1
            elif(self.isPlaylistMode()):
                page = progressZoomIdx
                if progressZoomIdx == 4:
                    page = 3
                elif progressZoomIdx > 4:
                    page = 4

            if(page > 0):
                SendCC(IDPage2, SingleColorFull)
            if(page > 1):
                SendCC(IDTrackSel3, SingleColorFull)
            if(page > 2):
                SendCC(IDPage3, SingleColorFull)
            if(page > 3):
                SendCC(IDTrackSel4, SingleColorFull)

    def RefreshNotes(self):
        global PadMap
        global NoteMap
        global NoteColorMap 

        self.RefreshPageLights()

        if(self.isChromatic()):
            rootNote = 0 # C
            showRoot = False
        else:
            rootNote = NoteIdx
            showRoot = True 

        baseOctave = OctavesList[OctaveIdx]

        id, pl = self.getCurrChanPlugin()
        invert = False 
        if (pl != None):
            invert = pl.InvertOctaves

        self.GetScaleGrid(ScaleIdx, rootNote, baseOctave, invert) #this will populate PadMap.NoteInfo

        dim = dimNormal

        for p in pdWorkArea:
            color = cDimWhite
            if(self.isChromatic()): #chromatic,
                if(len(utils.GetNoteName(PadMap[p].NoteInfo.MIDINote) ) > 2): # is black key?
                    color = cOff # cDimWhite #-1
                else:
                    color = cWhite 
                    dim = dimNormal
            # elif(ChromaticOverlay):

            else: #non chromatic
                if(PadMap[p].NoteInfo.IsRootNote) and (showRoot):
                    dim = dimNormal
                    if(Settings.ROOT_NOTE_COLOR == cChannel):
                        color = FLColorToPadColor(channels.getChannelColor(getCurrChanIdx()))
                    else:
                        color = Settings.ROOT_NOTE_COLOR
                else:
                    color = cOff #cWhite
                    dim = dimDim


            if(ShowChords) and (GetScaleNoteCount(ScaleIdx) == 7):
                if(p in pdChordBar):
                    SetPadColor(p, cBlue,dimNormal)
                # elif(p in pdChordFuncs):
                #     SetPadColor(p, cOff,dimNormal)
                else:
                    SetPadColor(p, color,dimNormal)
                self.RefreshChordType()
            else:
                SetPadColor(p, color, dim)

            NoteColorMap[p].PadColor = color

    def RefreshMode(self):
        # set the specific mode related funcs here

        # RefreshMacros() 
        # RefreshNavPads()
        self.RefreshDisplay()

    def RefreshChordType(self):
        if(Chord7th):
            SetPadColor(pd7th, cYellow,dimBright)
        else:
            SetPadColor(pd7th, cYellow,dimDim) # extra dim
        if(ChordInvert == 1):
            SetPadColor(pdInv1, cWhite,dimNormal)
        elif(ChordInvert == 2):
            SetPadColor(pdInv2, cWhite,dimNormal)
        else:
            SetPadColor(pdNormal, cWhite,dimNormal)

    def RefreshDrumPads(self):
        global PadMap
        global NoteMapDict
        NoteMapDict.clear()
        chanIdx = getCurrChanIdx() 
        pads = self.DrumPads()

        if(isAltMode): # function in NON FPC mode
            colors = [cWhite, cCyan, cBlue, cOrange, cGreen, cYellow]
            changeEvery = 16

            if(PadMode.LayoutIdx  == lyStrips):
                changeEvery = 12

            #if(Settings.ALT_DRUM_MODE_BANKS == False):
            #    changeEvery = 12

            id, pl = self.getCurrChanPlugin()
            rootNote = 12 # 12 = C1 ?
            startnote = rootNote + (OctavesList[OctaveIdx] * 12) 

            for idx, p in enumerate(pads):
                invert = False
                if pl != None:
                    invert = pl.InvertOctaves
                # if(invert):
                #     print('inv', rootNote)
                # else:
                #     print('noinv', rootNote)

                colIdx =  idx//changeEvery
                color = colors[colIdx]

                self.MapNoteToPad(p, startnote + idx, color)
                SetPadColor(p, color, dimNormal)

                

            
            self.RefreshDisplay()
        
        else: # FPC mode
            #do this first to force it to change to an FPC instance if available.
            self.RefreshFPCSelector()
            # FPCNotesDict.clear()
            
            if( self.isFPCActive()):  # Show Custom FPC Colors
                # FPC A Pads
                semitone = 0
                color = cOff
                dim = dimNormal
                for idx, p in enumerate(pads): 
                    color = plugins.getPadInfo(chanIdx, -1, PAD_Color, idx) #fpcpadIdx) # plugins.getColor(chanIdx, -1, GC_Semitone, fpcpadIdx)
                    semitone = plugins.getPadInfo(chanIdx, -1, PAD_Semitone, idx) #fpcpadIdx)
                    color = FLColorToPadColor(color, 2)
                    self.MapNoteToPad(p, semitone, color)
                    SetPadColor(p, color, dim)
            else: # 
                for p in pads:
                    SetPadColor(p, cOff,dimNormal)
                    PadMap[p].Color = cOff

        #RefreshMacros() 
        #RefreshNavPads()

    def MapNoteToPad(self,padNum, note, color):
        global NoteMap
        global PadMap
        global NoteMapDict

        if(note in NoteMapDict):
            NoteMapDict[note].append(padNum)
        else:
            NoteMapDict[note] = [padNum]
        
        # maintain these here for now
        PadMap[padNum].NoteInfo.MIDINote = note
        PadMap[padNum].Color = color
        NoteMap[padNum] = note

    def RefreshFPCSelector(self):
        self.getFPCChannels() # always refresh

        if len(pdFPCChannels) == 0:
            DisplayTimedText('No FPC')
            return
        
        if not self.isFPCActive():
            return

        # go through the FPC selector pads...
        for idx, padNum in enumerate(pdFPCChannels):

            # defaults
            padColor = cOff
            chanIdx = -1
            dim =dimNormal

            # check if we have an FPC to use
            if(idx < len(FPCChannels)):
                chanIdx = FPCChannels[idx]

                # if an FPC is not selected, choose the first one we see
                if(not self.isFPCActive()):
                    channels.selectOneChannel(chanIdx)
                    # SelectAndShowChannel(chanIdx)

                padColor = FLColorToPadColor(channels.getChannelColor(chanIdx))

                if(getCurrChanIdx()  == chanIdx):
                    dim =dimBright
                
                if(self.adjustForAudioPeaks()):
                    self.SetPadColorPeakVal(padNum, padColor, channels.getActivityLevel(chanIdx), True)
                else: # otherwise...
                    SetPadColor(padNum, padColor, dim)
            else:
                SetPadColor(padNum, padColor, dim)

            PadMap[padNum].Color = padColor
            PadMap[padNum].ItemIndex = chanIdx 

    def RefreshKnobMode(self):
        '''
            Lights up the appropriate knob mode led indicators
        '''
        global UserModeLEDValues
        global UserKnobModeIndex

        mode = ''
        value = UserModeLEDValues[UserKnobModeIndex]
        usermode = UserModeLEDValues.index(value)  
        
        if(self.isMixerMode()):
            value += 2
            mode = 'Mixer'
        elif(self.isChannelMode()):
            value += 1
            mode = 'Channel'
        
        if usermode > 0:
            mode = 'USER ' + str(usermode)
        
        SendCC(IDKnobModeLEDArray, value | 16)

        fireNFX_Bridge.WriteINI('Knobs', 'Mode', mode)

        self.UpdateBridgeKnobs()


    def UpdateBridgeKnobs(self):
        if Settings.DEVMODE in ["0"]:
            fireNFX_Bridge.WriteINI('Knobs', 'ModeText', 'Not Yet Implemented')
            return
        
        knobs  = ['', '', '', '']
        knobsa = ['', '', '', '']
        knobsb = ['', '', '', '']
        modetext = ''
        modealt = ''

        if(PadMode.NavSet.ColorPicker):
            knobs  = ['Red', 'Green', 'Blue', '']

        if KnobMode == KM_USER0:
                
            if self.isChannelMode():
                chanNum = channels.selectedChannel()
                chanName = channels.getChannelName(chanNum)
                modetext = chanName 
                knobs = ['Volume', 'Pan', 'Filter', 'Filter Res']
                if self.isFPCActive():
                    fireNFX_Bridge.WriteINI('Knobs', 'ModeAlt', 'Held Pad')
                    knobsa = ['Pad Vol', 'Pad Pan', 'Pad Tune', '']
                    modealt = 'FPC Hold Pad'
            elif self.isMixerMode():
                mixerNum = mixer.trackNumber()
                mixerName = mixer.getTrackName(mixerNum) 
                modetext = mixerName
                modealt = 'SHIFT'
                modealt2 = 'ALT'
                knobs = ['Volume', 'Pan', 'Filter', 'Filter Res']
                knobs  = ['Volume', 'Pan', 'EQ Lo Gain', 'EQ Mid Gain']
                knobsa = ['', 'Stereo Sep', 'EQ Lo Freq', 'EQ Mid Freq']
        else:

            if self.isChannelMode():
                chanNum = channels.selectedChannel()
                chanName = channels.getChannelName(chanNum)            
                modetext = ' ' + chanName
            elif self.isKnownMixerEffectActive():
                slotIdx, slotName, pluginName = self.GetActiveMixerEffectSlotInfo()
                mixerNum = mixer.trackNumber()
                mixerName = mixer.getTrackName(mixerNum) 
                modetext = ' ' + mixerName + ' - ' + pluginName



            if self.isKnownPlugin():
                pl = self.getPlugin(channels.selectedChannel())   
                paramName = ''
                for idx, knobID in enumerate(KnobCtrls):
                    knobRecID = knobID + ( (KnobMode-KM_USER1) * 4 )
                    User1Knobs[idx] = TnfxUserKnob(idx, pluginName = pl.Name, paramOffset = pl.User1Knobs[idx].Offset, caption = pl.User1Knobs[idx].Caption)
                    # print('added', idx, pl.Name, pl.User1Knobs[idx].Offset, pl.User1Knobs[idx].Caption)
                    User2Knobs[idx] = TnfxUserKnob(idx, pluginName = pl.Name, paramOffset = pl.User2Knobs[idx].Offset, caption = pl.User2Knobs[idx].Caption)
                    User3Knobs[idx] = TnfxUserKnob(idx, pluginName = pl.Name, paramOffset = pl.User3Knobs[idx].Offset, caption = pl.User3Knobs[idx].Caption)
                    # if (general.getVersion() > 9):
                        # BaseID = EncodeRemoteControlID(device.getPortNumber(), 0, 0)
                        # recEventIDIndex = device.findEventID(BaseID + knobRecID, 0)
                        # if recEventIDIndex != 2147483647:
                        #     # show the name/value on the display
                        #     paramName = device.getLinkedParamName(recEventIDIndex)
                        #     print('linked', recEventIDIndex, paramName)
                    if KnobMode == KM_USER1:
                        paramName = pl.User1Knobs[idx].Caption
                    elif KnobMode == KM_USER2:
                        paramName = pl.User2Knobs[idx].Caption
                    elif KnobMode == KM_USER3:
                        paramName = pl.User3Knobs[idx].Caption
                    knobs[idx] = paramName


            else: # custom user macros
                for idx, knobID in enumerate(KnobCtrls):
                    knobRecID = knobID + ( (KnobMode-KM_USER1) * 4 )
                    paramName = ''
                    if (general.getVersion() > 9):
                        BaseID = EncodeRemoteControlID(device.getPortNumber(), 0, 0)
                        recEventIDIndex = device.findEventID(BaseID + knobRecID, 0)
                        if recEventIDIndex != 2147483647:
                            # show the name/value on the display
                            paramName = device.getLinkedParamName(recEventIDIndex)
                            if KnobMode == KM_USER1:
                                paramName = User1Knobs[idx].PluginName + ' - ' + paramName
                            elif KnobMode == KM_USER2:
                                paramName = User2Knobs[idx].PluginName + ' - ' + paramName
                            elif KnobMode == KM_USER3:
                                paramName = User3Knobs[idx].PluginName + ' - ' + paramName
                    knobs[idx] = paramName
        
        fireNFX_Bridge.WriteINI('Knobs', 'ModeText', modetext)
        fireNFX_Bridge.WriteINI('Knobs', 'ModeAlt', modealt)
        for i in range(4):
            fireNFX_Bridge.WriteINI('Knobs', 'knob' + str(i + 1), knobs[i])
            fireNFX_Bridge.WriteINI('Knobs', 'knob' + str(i + 1) + 'a', knobsa[i])
            fireNFX_Bridge.WriteINI('Knobs', 'knob' + str(i + 1) + 'b', knobsb[i])


    def RefreshPlaylist(self):
        global PadMap
        global pdPlaylistStripA
        global pdPlaylistStripB
        global pdPlaylistMutesA
        global pdPlaylistMutesB 

        if (PadMode.Mode != MODE_PATTERNS):
            return 

        pdPlaylistStripA, pdPlaylistMutesA = self.getPlaylistPads()
        pageSize = len(pdPlaylistStripA)
        plMap = self.getPlaylistMap() # PlaylistMap
        if(len(plMap) == 0):
            return 

        if(isAltMode) and ( len(plMap) <  len(pdPlaylistStripA) ): #not enough for paging.
            pageSize = len(PlaylistSelectedMap)

        firstTrackOnPage = (PlaylistPage - 1) * pageSize # 0-based

        for padOffs in range(pageSize): #gives me 0..12 or 0..selected when less than 12
            padTrackA = pdPlaylistStripA[padOffs]
            padMuteA  = pdPlaylistMutesA[padOffs]
            dimA =dimNormal
            muteColorA = cNotMuted 
            trackIdx = firstTrackOnPage + padOffs
            pageSize = len(plMap) - (firstTrackOnPage + pageSize)
            plTrack = TnfxPlaylistTrack(-1)
            if trackIdx < len(plMap): # 
                plTrack = plMap[trackIdx]
                plTrack.Update()
                if(plTrack.Selected):
                    dimA =dimBright
                if(plTrack.Muted):
                    muteColorA = cMuted

            if self.adjustForAudioPeaks() and (plTrack.FLIndex > -1):
                isLast = padOffs == (pageSize-1) #triggers the buffer to flush and a small sleep
                self.SetPadColorPeakVal(padTrackA, plTrack.Color, playlist.getTrackActivityLevelVis(plTrack.FLIndex), isLast)
            else:
                SetPadColor(padTrackA, plTrack.Color, dimA)

            SetPadColor(padMuteA, muteColorA,dimNormal) 

            # update the pad map
            PadMap[padTrackA].Color = plTrack.Color
            PadMap[padTrackA].FLIndex = plTrack.FLIndex 
            PadMap[padMuteA].Color = muteColorA
            PadMap[padMuteA].FLIndex = plTrack.FLIndex 
        
    def RefreshMixerEffectStrip(self,force = False):
        global MixerMap
        global lastMixerTrack 

        formID = ui.getFocusedFormID()
        currTrk = mixer.trackNumber()

        if(lastMixerTrack != currTrk) or (force):
            lastMixerTrack = currTrk
            aPads, bPads = self.getMixerEffectPads()
            channelStripA, channelStripB = self.getChannelPads()        
            for pad in channelStripA:
                SetPadColor(pad, cOff,dimNormal)
            for pad in channelStripB:
                SetPadColor(pad, cOff,dimNormal)

            formTrack, formSlot = self.getTrackSlotFromFormID(formID) # in case its a mixer effect
            
            effectSlots = self.GetAllEffectsForMixerTrack(currTrk)
            for slot in effectSlots.keys(): # s/b 0-9
                fx = effectSlots[slot] # TnfxMixerEffectSlot(slot, '', cSilver)
                fx.Update()

                if(fx.Used):
                    if(currTrk == formTrack) and (slot == formSlot): # is it active?
                        if (general.getVersion() >= 32):
                            SetPadColor(aPads[fx.SlotIndex], fx.Color,dimBright)
                        else:
                            SetPadColor(aPads[fx.SlotIndex], cRed,dimBright)
                    else:
                        SetPadColor(aPads[fx.SlotIndex], fx.Color,dimNormal)
                else:
                    SetPadColor(aPads[fx.SlotIndex], fx.Color,dimDim)

                #print('RMES', fx)
                
                if(fx.Muted):
                    SetPadColor(bPads[fx.SlotIndex], cMuted,dimNormal)
                else:
                    SetPadColor(bPads[fx.SlotIndex], cNotMuted,dimNormal)

    def RefreshChannelStrip(self,scrollToChannel = False):
        global ChannelMap
        global CurrentChannel
        global PatternMap
        global ChannelPage

        #only run when in paatern mode
        if(PadMode.Mode != MODE_PATTERNS):
            return

        if(self.isMixerMode()):
            #print('rcs')
            self.RefreshMixerEffectStrip()
            return  
        
        if(self.isPlaylistMode()):
            if(SHOW_PROGRESS):
                self.UpdateAndRefreshProgressAndMarkers()
            return

        if(len(ChannelMap) == 0):
            return
        
        channelMap = self.getChannelMap() #ChannelMap
        currChan = getCurrChanIdx() # 
        currMixerNum = channels.getTargetFxTrack(currChan)

        # determine the offset. 
        channelsPerPage = self.getChannelModeLength()
        pageFirstChannel = self.getChannelOffsetFromPage() 
        pageNum = (currChan // channelsPerPage) + 1 # 1-based

        channelStripA, channelStripB = self.getChannelPads()

        # is the current channel visible and do we care?
        if(scrollToChannel) and (pageNum != ChannelPage):
            if(ChannelPage != pageNum):
                ChannelPage = pageNum 
                self.ChannelPageNav(0)
                pageFirstChannel = self.getChannelOffsetFromPage()    

        for padOffset in range(channelsPerPage):
            chanIdx = padOffset + pageFirstChannel
            padAIdx = channelStripA[padOffset]
            padBIdx = channelStripB[padOffset]
            channel = None

            if(chanIdx < len(channelMap)):
                channel = channelMap[chanIdx]
            
            dimA =dimNormal
            dimB =dimNormal
            bColor = cOff
            aColor = cOff

            if(channel == None): # if not defined
                SetPadColor(padAIdx, cOff,dimNormal)
                SetPadColor(padBIdx, cOff,dimNormal)

            elif(channel.FLIndex >= 0): # is it a valid chan #?

                aColor = FLColorToPadColor(channel.Color, 1)

                if(currChan == channel.FLIndex): # the channel is selected
                    bColor = cWhite
                    dimB =dimBright
                    dimA = dimBright
                    if(ui.getFocused(widPlugin) or ui.getFocused(widPluginGenerator)):
                        dimA =dimBright
                    if(ui.getFocused(widPianoRoll)):
                        bColor = aColor
                        dimB =dimBright

                if(channels.isChannelMuted(channel.FLIndex)):
                    bColor = cMuted
                else: 
                    bColor = cNotMuted

                # if we are showing the audio peaks do this...
                if(self.adjustForAudioPeaks()):
                    isLast = padOffset == (channelsPerPage-1) #triggers the buffer to flush and a small sleep
                    self.SetPadColorPeakVal(padAIdx, aColor, channels.getActivityLevel(channel.FLIndex), isLast)
                else: # otherwise...
                    SetPadColor(padAIdx, aColor, dimA)

                SetPadColor(padBIdx, bColor, dimB)
                
                #ChannelMap[channel.FLIndex].PadColor = aColor # not needed, this gets set in SetPadColor()
                ChannelMap[channel.FLIndex].DimA = dimA
                ChannelMap[channel.FLIndex].PadBColor = bColor
                ChannelMap[channel.FLIndex].Dimb = dimB

                if(PadMode.NavSet.ChanNav) and (currChan == channel.FLIndex):
                    self.RefreshChanWinNav(-1)

                if(ShiftHeld): # Shifted will display Mute states
                    col = cNotMuted
                    if(self.isMixerMode()):
                        if (channel.Mixer.FLIndex > -1):
                            if(mixer.isTrackMuted(channel.Mixer.FLIndex)):
                                col = cMuted
                    elif(self.isChannelMode()):
                        if(channels.isChannelMuted(channel.FLIndex)):
                            col = cMuted
                    SetPadColor(padBIdx, col,dimNormal) #cWhite,dimBright
            else:
                #not used
                SetPadColor(padAIdx, cOff,dimNormal)
                SetPadColor(padBIdx, cOff,dimNormal)

    def RefreshMixerStrip(self,scrollToChannel = False):
        global MixerPage

        if( PadMode.Mode != MODE_PATTERNS):
            return 

        mixerMap = self.getMixerMap()
        pageOffset = self.getMixerOffsetFromPage()
        mixerStripA, mixerStripB = self.getMixerStripPads()
        mixerTracksPerPage = self.getMixerModeLength()

        # is the current track visible and do we care?
        if(scrollToChannel):
            currTrackNum = mixer.trackNumber()
            #pageNum = (currTrackNum // (mixerTracksPerPage+1)) + 1 # 1-based
            newPageNum = (currTrackNum // mixerTracksPerPage) + 1 # 1- based
            if(MixerPage != newPageNum):
                self.MixerPageNav(0) # passing 0 resets the paging
                pageOffset = self.getMixerOffsetFromPage() # update the offset, for the new page

        # go through the pads...
        for padOffset in range(0, mixerTracksPerPage):
            trackIdx = padOffset + pageOffset   # mixer track num
            padAIdx = mixerStripA[padOffset]    # Top Pad #
            padBIdx = mixerStripB[padOffset]    # bottom pad #

            # is there room to use an available pattern?
            if(padOffset < mixerTracksPerPage) and (trackIdx < len(mixerMap)): 

                mixerMap[trackIdx].Update()
                mixerTrack = mixerMap[trackIdx] 
                color = mixerTrack.Color
                dim =dimNormal

                # check if current
                if(mixer.trackNumber() == mixerTrack.FLIndex): 
                    dim =dimBright

                # check for mute
                if(not mixerTrack.Muted):
                    SetPadColor(padBIdx, cNotMuted, dim)
                else:
                    SetPadColor(padBIdx, cMuted, dim)
                
                if(mixerTrack.Armed):
                    SetPadColor(padBIdx, cRed, dim)


                # if we are showing the audio peaks do this...
                if(self.adjustForAudioPeaks()):
                    isLast = padOffset == (mixerTracksPerPage-1) #triggers the buffer to flush and a small sleep
                    self.SetPadColorPeakVal(padAIdx, color, mixer.getTrackPeaks(trackIdx, PEAK_LR), isLast)
                    # if(self.isLast):
                    #     time.sleep(0.07)
                else: # otherwise...
                    SetPadColor(padAIdx, color, dim)

            else: #not used
                SetPadColor(padAIdx, cOff,dimDim)
                SetPadColor(padBIdx, cOff,dimDim)  

        if(not self.adjustForAudioPeaks()):
            self.RefreshMixerEffectStrip(True)          

    def RefreshPatternStrip(self,scrollToChannel = False):
        # should rely upon PatternMap or PatternMapSelected only. should not trly upon PadMap
        # should use PatternPage accordingly 
        global PatternPage

        if (PadMode.Mode != MODE_PATTERNS):
            return 
        
        if(self.isMixerMode()):
            self.RefreshMixerStrip(True)
            return 
        
        if(self.isPlaylistMode()):
            self.RefreshPlaylist()
            return 

        patternMap = self.getPatternMap()

        # determine the offset. 
        pageOffset = self.getPatternOffsetFromPage() 

        patternStripA, patternStripB = self.getPatternPads()
        patternsPerPage = self.getPatternModeLength()

        # is the current pattern visible and do we care?
        if(scrollToChannel):
            currPat = patterns.patternNumber()
            pageNum = (currPat // (patternsPerPage+1)) + 1
            if(PatternPage != pageNum):
                PatternPage = pageNum 
                self.PatternPageNav(0)
                pageOffset = self.getPatternOffsetFromPage()
                
        for padOffset in range(0, patternsPerPage):
            patternIdx = padOffset + pageOffset
            padAIdx = patternStripA[padOffset]
            padBIdx = patternStripB[padOffset]
            if(padOffset < patternsPerPage) and (patternIdx < len(patternMap)): # room to use an available pattern?
                pattern = patternMap[patternIdx] 
                if(patterns.patternNumber() == pattern.FLIndex): #current pattern
                    SetPadColor(padAIdx, pattern.Color,dimBright)
                    SetPadColor(padBIdx, cWhite,dimBright)
                else:
                    if(pattern.Selected):
                        SetPadColor(padAIdx, pattern.Color,dimNormal)
                        SetPadColor(padBIdx, cWhite,dimDim)
                    else:
                        SetPadColor(padAIdx, pattern.Color,dimNormal)
                        SetPadColor(padBIdx, cOff,dimNormal)
            else: #not used
                SetPadColor(padAIdx, cOff,dimDim)
                SetPadColor(padBIdx, cOff,dimDim)            

    def RefreshDisplay(self):
        global menuItemSelected

        if shuttingDown:
            return

        chanTypes = ['S', 'H', 'V', 'L', 'C', 'A']
        toptext = ''
        bottext = ''
        offset = 0
        um = KnobModeShortNames[UserKnobModeIndex] 
        pm = PadModeShortNames[PadMode.Mode] + " - " + um
        toptext = pm 
        sPatNum = '' # str(patterns.patternNumber())
        midtext = ''
        bottext = '' 

        menuItemSelected = chosenItem # reset this for the next menu

        if( len(ChannelMap) == 0):
            self.UpdateChannelMap()    

        if(ShowMenu):
            self.ShowMenuItems()    
            return     
        else:

            chanIdx = getCurrChanIdx() # 
            if( len(ChannelMap) > (chanIdx - 1)):
                self.UpdateChannelMap()
            
            cMap = ChannelMap[chanIdx]
            patName = patterns.getPatternName(patterns.patternNumber())
        
            if(self.isChannelMode()):
                offset += 1
            if(self.isMixerMode()):
                offset += 2
        
            midtext = sPatNum + 'P:' + patName 
            bottext = chanTypes[cMap.ChannelType] + ': ' + cMap.Name

            if(PadMode.Mode == MODE_PATTERNS):
                if(self.isChannelMode()):
                    toptext = 'Pat-Chan ' + str(PatternPage) + '-' + str(ChannelPage)
                elif(self.isPlaylistMode()):
                    toptext = 'Playlist ' + str(PlaylistPage)
                elif (self.isMixerMode()):
                    trkNum = mixer.trackNumber()
                    mute = ''
                    mx = MixerMap[trkNum] 
                    if(mx.Muted):
                        mute = '[M] '
                    toptext = 'Mixer ' + str(MixerPage) 
                    midtext = '{}.{}'.format(trkNum, mixer.getTrackName(trkNum))
                    bottext = 'FX: {}/10  {}'.format(len(mx.EffectSlots), mute)
                elif(ui.getFocused(widPianoRoll)):
                    toptext = 'Piano Roll'
                elif(ui.getFocused(widPlugin) or ui.getFocused(widPluginGenerator)):
                    toptext = 'Chan Editor'
                elif(ui.getFocused(widPluginEffect)):
                    toptext = 'Effect Slot'
                    track, slot = self.getTrackSlotFromFormID(ui.getFocusedFormID())
                    midtext = 'Trk {}, Slot {}'.format(track, slot)
                else:
                    toptext = 'UNK' 
                    # if(KnobModeShortNames[_UserKnobModeIndex]  in ['U1', 'U2', 'U3']):
                    #     toptext = pm + '   ' # on less space
                    # toptext = toptext + str(PatternPage) + ' - ' + str(ChannelPage)

            if(PadMode.Mode == MODE_NOTE):
                midtext = '' + ScaleDisplayText
                # if(ShowChords):
                if(ShowChords) and (GetScaleNoteCount(ScaleIdx) == 7):
                    toptext = pm + " - ChB"

            if(PadMode.Mode == MODE_DRUM):
                layout = 'DRM-FPC'
                oct = ''
                toptext = "{}".format(layout)
                if(PadMode.IsAlt):
                    oct = OctavesList[OctaveIdx]
                    if(PadMode.LayoutIdx == 0):
                        layout = 'DRM-A'
                    else:
                        layout = 'DRM-B'
                    toptext = "{} - {} - 0{}".format(layout, um, oct)

            if(PadMode.Mode == MODE_PERFORM):
                if(playlist.getPerformanceModeState() == 1):
                    firstTrack = self.getTrackMatrix(PerfTrackOffset)[0].FLIndex
                    lastTrack = self.getTrackMatrix(PerfTrackOffset)[-1].FLIndex
                    toptext = 'PERF Tracks'
                    midtext = "  {}-{}".format(firstTrack, lastTrack)
                    bottext = " "
                else:
                    if not PadMode.IsAlt:
                        toptext = 'NOT IN'
                        midtext = 'PERFORMANCE'
                        bottext = "MODE"
                    else:
                        toptext = 'USER'
                        midtext = 'MACRO'
                        bottext = 'MODE'


        DisplayTextTop(toptext)
        DisplayTextMiddle(midtext)
        DisplayTextBottom(bottext)

        fireNFX_Bridge.WriteINI('Display', 'Line1', toptext)
        fireNFX_Bridge.WriteINI('Display', 'Line2', midtext)
        fireNFX_Bridge.WriteINI('Display', 'Line3', bottext)
        
        self.prn(lvlD, '  |-------------------------------------')
        self.prn(lvlD, '  | ', toptext)
        self.prn(lvlD, '  | ', midtext)
        self.prn(lvlD, '  | ', bottext)
        self.prn(lvlD, '  |-------------------------------------')

    def UpdateBridge(self, section, key, value):
        pass 


    def RefreshCustomMacros(self):
        # TODO
        return

    def RefreshColorPicker(self):
        chanColor = FLColorToPadColor(channels.getChannelColor(getCurrChanIdx()))
        mixColor = FLColorToPadColor(mixer.getTrackColor(mixer.trackNumber()))
        pattColor = FLColorToPadColor(patterns.getPatternColor(patterns.patternNumber()))
        pl = list(Settings.Pallette.values())

        SetPadColor(pdNewColor, NewColor,dimBright)
        SetPadColor(pdChanColor, chanColor,dimNormal)
        SetPadColor(pdPattColor, pattColor,dimNormal)
        SetPadColor(pdMixColor, mixColor,dimNormal)

        textlist = ['NewColor', 'Channel', 'Pattern', 'MixTrk']
        colorlist = [NewColor, chanColor, pattColor, mixColor]
        keys_list = list(Settings.Pallette.keys())

        for idx, pad in enumerate(pdPallette):
            if (pad != pdOrigColor):
                color = FLColorToPadColor(pl[idx],1)
                SetPadColor(pad, color,dimBright)
                textlist.append(keys_list[idx])
                colorlist.append(color)
        
        SetPadColor(pdOrigColor, OrigColor,dimNormal)
        textlist.append('OrigColor')
        colorlist.append(OrigColor)

        for idx, pad in enumerate(pdMacroNav):
            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(idx), textlist[idx])
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(idx), colorlist[idx]) 


    def RefreshUDLR(self):
        for idx, pad in enumerate(pdUDLR):
            color = pdUDLRColors[idx]
            text = pdUDLRText[idx]

            SetPadColor(pad, color,dimNormal)

            fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(idx + 8), text)
            fireNFX_Bridge.WriteINI('Macros', 'macropadcolor' + str(idx + 8), color)


            # if(pad == pdMenu):
            #     SetPadColor(pad, cBlue, dimNormal)
            #     fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(idx + 8), 'Menu')
            # elif(pad == pdTab):
            #     SetPadColor(pad, cCyan,dimBright)
            #     fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(idx + 8), 'Tab')
            # elif(pad == pdEsc):
            #     SetPadColor(pad, cRed,dimNormal)
            #     fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(idx + 8), 'Esc')
            # elif(pad == pdEnter):
            #     SetPadColor(pad, cGreen,dimNormal)
            #     fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(idx + 8), 'Enter')
            # else:
            #     SetPadColor(pad, cWhite,dimNormal)
            #     arrow = 'Up' 
            #     if(pad == pdDown):
            #         arrow = 'Down'
            #     elif(pad == pdLeft):
            #         arrow = 'Left'
            #     elif(pad == pdRight):
            #         arrow = 'Right'
            #     fireNFX_Bridge.WriteINI('Macros', 'macropad' + str(idx + 8), arrow)

    def RefreshProgress(self):
        if(PadMode.Mode == MODE_PATTERNS) and (self.isPlaylistMode(self)):
            # if len(ProgressMapSong) == 0:
            #     self.UpdateMarkerMap()
            #     self.UpdateProgressMap()
            
            progMap = ProgressMapSong
            songLenBars = transport.getSongLength(SONGLENGTH_BARS)
            progPads = self.getProgressPads()
            numPads = len(progPads)
            ticksPerBar = getAbsTicksFromBar(2) # returns the ticks in 1 bar 
            barMap, barsPerPad = self.mapBarsToPads(numPads, songLenBars)        
            prevBar = -1
            currBar = transport.getSongPos(SONGLENGTH_BARS)
            
            for pPad in progMap:
                if pPad != None:
                    startBar = pPad.BarNumber
                    endBar = startBar + (barsPerPad - 1)
                    if(startBar < 1):
                        SetPadColor(pPad.PadIndex, cOff, dimBright)
                    elif(startBar <= currBar <= endBar ):
                        SetPadColor(pPad.PadIndex, getShade(cYellow, shNorm),dimBright)
                    elif(startBar < currBar):
                        SetPadColor(pPad.PadIndex, getShade(pPad.Color, shNorm),dimBright)
                    else:
                        SetPadColor(pPad.PadIndex, getShade(pPad.Color, shNorm),dimDim)

    def RefreshBrowserDisplay(self,caption = ''):
        if(ui.getFocused(widBrowser)):
            ftype = ui.getFocusedNodeFileType()
            actions = ''
            if(caption == ''):
                caption = ui.getFocusedNodeCaption()
            if(ftype <= -100):
                actions = '[Open/Close]'
            else:
                actions = '[]  S[]  A[]'
            DisplayTimedText2('Browser', caption, actions )
        else:
            self.RefreshDisplay()

    def RefreshBrowserButton(self):
        if(ui.getFocused(widBrowser)):
            SendCC(IDBrowser, SingleColorHalfBright)
            self.RefreshBrowserDisplay()
        elif(ShowMenu):
            SendCC(IDBrowser, SingleColorFull)
        else:
            SendCC(IDBrowser, SingleColorOff)  # 

    def RefreshWindowStates(self):
        global lastFocus

        self.prn(lvlA, 'RefreshWindowStates')

        self.RefreshChannelStrip()
        self.RefreshBrowserButton()


        if self.isNoMacros():
            return 

        if(ui.getVisible(widChannelRack)):
            dim =dimNormal
            if(self.isChannelMode()):
                dim =dimBright
            SetPadColor(pdMacros[1], FLColorToPadColor(MacroList[1].PadColor), dim)

        if(ui.getVisible(widPianoRoll)):
            if(ui.getFocused(widPianoRoll)):
                self.RefreshChannelStrip()

        if(ui.getVisible(widPlaylist)):
            dim =dimNormal
            if(self.isPlaylistMode()):
                dim =dimBright 
            SetPadColor(pdMacros[2], FLColorToPadColor(MacroList[2].PadColor), dim)

        if(ui.getVisible(widMixer)):
            dim =dimNormal
            if(self.isMixerMode()):
                dim =dimBright
            SetPadColor(pdMacros[3], FLColorToPadColor(MacroList[3].PadColor), dim)

    def RefreshEffectMapping(self,updateOnly = False):
        # for mapping effect values to pads ie. gross beat
        global PadMap 
        global ParamPadMapDict
        
        ParamPadMapDict.clear()
        slotIdx, slotName, pluginName = self.GetActiveMixerEffectSlotInfo()
        print('REM', slotIdx, slotName, pluginName )
        pl = self.getPlugin(pluginName, slotIdx)
        #print('REM', pl)
        if (pl != None):
            print('REM', pl.ParamPadMaps)
            for paramMap in pl.ParamPadMaps:
                #print('REM PM1', paramMap)
                currVal = GetMixerPluginParamVal(paramMap.Offset, 1, 0)
                padList = paramMap.Pads
                size = len(paramMap.Pads) - 1 # -1 because FL calcs this way
                incby = 1 / size
                nv = incby
                #print('REM PM2', currVal, padList, size, incby)
                for idx, pad in enumerate(paramMap.Pads):
                    dim =dimDim
                    if(pad > -1):
                        padVal = idx * incby 
                        ParamPadMapDict[pad] = paramMap.Offset, padVal
                        if(currVal == padVal):
                            dim =dimBright
                        if(not updateOnly):
                            SetPadColor(pad, paramMap.Color, dim)
                    nv += incby

    def RefreshAltPerformanceMode(self):
        for pad in range(0,64):
            if pad in UserMacros.keys():
                SetPadColor(pad, UserMacros[pad].PadColor, dimNormal)
            else:
                SetPadColor(pad, 0x000000, 0) 

    def RefreshPerformanceMode(self,beat):
        if isPMESafe:
            if(len(PerformanceBlocks.keys()) > 0):

                for padNum in PerformanceBlocks.keys():
                    block = PerformanceBlocks[padNum]
                    block.Update()
                    status = block.LastStatus
                    color = block.Color
                    dim = 2 # not active nor playing
                    # if(playlist.isTrackMuted(block.FLTrackIndex)):
                    #     dim = 3
                    #     color = self.getShade(color, shDark)
                    # else:
                    if( status == 0): # no block
                        color = cOff
                    else:
                        isactive = (status & 2)

                        if isactive: # scheduled - AKA active
                            dim = 0
                            # color = AdjustColorBrightness(color, 1)
                        else:
                            dim = 2

                        if( status & 4) and not isactive: # playing
                            if(beat in [0,2]): # or (ToBlinkOrNotToBlink):
                                dim -= 1 

                    SetPadColor(padNum, color, dim)
                    
            else:
                self.UpdatePerformanceBlocks()
    
    #endregion 

    #region Updates / Resets
    def UpdateAndRefreshProgressAndMarkers(self):
        self.UpdateMarkerMap()                
        self.UpdateProgressMap()
        self.RefreshProgress()

    def UpdatePlaylistMap(self):  #, mapExtra = True):
        global PlaylistMap
        global PlaylistSelectedMap
        global PadMap

        PlaylistMap.clear()
        PlaylistSelectedMap.clear()

        for plt in range(playlist.trackCount()):
            flIdx = plt + 1
            plMap = TnfxPlaylistTrack(flIdx)

            PlaylistMap.append(plMap)
            if(plMap.Selected):
                PlaylistSelectedMap.append(plMap)
        
        # if(mapExtra):
        #     playlist.deselectAll()
        #     playlist.selectTrack(1)

    def UpdatePatternMap(self):
        # this function should read ALL patterns from FL and have update two global lists of type <TnfxPattern>:
        #   1. PatternMap - all of the patterns from FL
        #   2. PatternSelectedMap - the selected patterns from FL . includes the currently active pattern
        #
        #   This function is needed by: UpdatePadMap(), getPatternMap() 
        #
        global PatternMap
        global PatternCount
        global CurrentPattern
        global PatternSelectedMap

        PatternCount = patterns.patternCount()
        PatternMap.clear()
        PatternSelectedMap.clear()

        if (PatternCount == 0): # presume new project with no patterns
            PatternCount = 1

        for pat in range(1, PatternCount+1): # FL patterns start at 1

            if patterns.isPatternDefault(pat) and (Settings.DETECT_AND_FIX_DEFAULT_PATTERNS): 
                # is the initial default pattern on a new project?
                # make it a 'real' pattern
                patterns.setPatternName(pat, Settings.PATTERN_NAME.format(pat))

            patMap = TnfxPattern(pat, patterns.getPatternName(pat))
            patMap.Color = FLColorToPadColor(patterns.getPatternColor(pat))  
            patMap.Selected = patterns.isPatternSelected(pat)



            PatternMap.append(patMap)
            if(patMap.Selected):
                PatternSelectedMap.append(patMap)

        CurrentPattern = patterns.patternNumber()

    def UpdateProgressMap(self,autodetect = True):
        '''
        Updates the internal list of progress points that will map to the pads
        '''
        global ProgressMapSong
        global ProgressMapPatterns
        global progressZoomIdx

        newMap = list()

        #todo: need to be aware of song pode/patt mode here?
        isPatternMode = transport.getLoopMode() == SM_Pat

        progPads = self.getProgressPads()
        songLenAbsTicks = transport.getSongLength(SONGLENGTH_ABSTICKS)
        songLenBars = transport.getSongLength(SONGLENGTH_BARS)
        numPads = len(progPads)
        ticksPerBar = getAbsTicksFromBar(2) # returns the ticks in 1 bar 
        
        if(isPatternMode):
            patLen = patterns.getPatternLength(patterns.patternNumber())
            songLenBars =  patLen // 16
            songLenAbsTicks = songLenBars * ticksPerBar

        barMap, barsPerPad = self.mapBarsToPads(numPads, songLenBars)

        

        selStart = arrangement.selectionStart()
        selEnd = arrangement.selectionEnd()
        selBarStart = getBarFromAbsTicks(selStart)
        selBarEnd =  getBarFromAbsTicks(selEnd) + 1

        if(selEnd > -1): #this will be -1 if nothing selected
            songLenBars = selBarEnd - selBarStart
            barMap, barsPerPad = self.mapBarsToPads(numPads, songLenBars)
        else:
            selBarStart = 1 # 
            selStart = songLenBars

        for padIdx, progBarNumber in enumerate(barMap):

            progPad = TnfxProgressStep(progPads[padIdx], cOff, -1, -1, -1)
            
            if(progBarNumber != None) and (songLenAbsTicks > 0):
                if(selEnd == -1):
                    progressPosAbsTicks = (progBarNumber-1) * ticksPerBar
                    progressPos = progressPosAbsTicks / songLenAbsTicks
                    nextAbsTick = progressPosAbsTicks + ticksPerBar # to check if a marker is within
                else:
                    progressPosAbsTicks = selStart + ( (progBarNumber-1) * ticksPerBar )
                    progressPos = progressPosAbsTicks / songLenAbsTicks
                    nextAbsTick = progressPosAbsTicks + ticksPerBar # to check if a marker is within

                progPad.BarNumber = getBarFromAbsTicks(progressPosAbsTicks)
                progPad.Color = cWhite
                progPad.SongPos = progressPos
                progPad.SongPosAbsTicks = progressPosAbsTicks

                # determine what markers are in this range.
                for marker in MarkerMap:
                    if(progressPosAbsTicks <= marker.SongPosAbsTicks < nextAbsTick):
                        if(progressPosAbsTicks == marker.SongPosAbsTicks): # or ((progressPosAbsTicks+1 == marker.SongPosAbsTicks)): # I need to fix my math
                            progPad.Color = cGreen
                        else:
                            progPad.Color = cOrange
                        progPad.Markers.append(marker)
            
            newMap.append(progPad)

        ProgressMapSong.clear()
        ProgressMapSong.extend(newMap)

    def UpdateMarkerMap(self):
        global MarkerMap

        # should only run when not playing
        if(transport.isPlaying()):
            return 
        
        if not self.isPlaylistMode(True): # PL must have focus
            return 

        songPos = transport.getSongPos()

        MarkerMap.clear()
        transport.stop()
        transport.setSongPos(1) # end of song will force the marker to restart at beginning
        markerCount = 0
        for i in range(100):
            if(arrangement.getMarkerName(i) != ""):
                markerCount += 1
            else:
                break

        if(markerCount > 0):
            transport.setSongPos(1) # by starting at the end, we wrap around and find the first marker
            for m in range(markerCount):
                markerNum = arrangement.jumpToMarker(1, False)
                markerName = arrangement.getMarkerName(markerNum)
                markerTime = arrangement.currentTime(1) # returns in ticks
                m = TnfxMarker(markerNum, markerName, markerTime)
                MarkerMap.append(m)

        transport.setSongPos(songPos)

    def UpdateMixerMap(self,trkNum = -1):
        global MixerMap

        if trkNum == -1:
            MixerMap.clear()
            for mixNum in range(mixer.trackCount()): # always 127?
                mix = TnfxMixer(mixNum)
                mix.EffectSlots = self.GetAllEffectsForMixerTrack(mixNum)
                MixerMap.append(mix)
        elif trkNum > -1:
            MixerMap[trkNum].Update()

    def UpdateChannelMap(self):
        global ChannelMap
        global ChannelCount
        global CurrentChannel
        global ChannelSelectedMap
        global WalkerChanIdx

        ChannelCount = channels.channelCount()
        ChannelMap.clear()
        ChannelSelectedMap.clear()

        for chan in range(ChannelCount):
            chnl = TnfxChannel(chan)
            if(chnl.Name == WalkerName):
                WalkerChanIdx = chnl.FLIndex

            ChannelMap.append(chnl)
            if(chnl.Selected):
                ChannelSelectedMap.append(chnl)
                self.UpdateBridgeKnobs() 

    def UpdatePatternModeData(self):
        self.ResetPadMaps(False)
        self.UpdatePatternMap()
        self.UpdateChannelMap()

    def Reset(self):
        global AltHeld
        global ShiftHeld

        AltHeld = False
        ShiftHeld = False

    def ResetBeatIndicators(self):
        for i in range(0, len(BeatIndicators) ):
            SendCC(BeatIndicators[i], SingleColorOff)

    def UpdateMenuItems(self,level):
        global menuItems
        
        pluginName, plugin = self.getCurrChanPlugin()
        if(plugin == None):
            menuItems.clear()
            menuItems.append('UNSUPPORTED')
            return 
        if(level == 0):
            menuItems = plugin.getGroupNames() # list(plugin.ParameterGroups.keys()) #['Set Params']
            menuItems.append('[Assign Knobs]')
        elif(level == 1):
            selText = menuItems[menuItemSelected]
            if(selText == '[Assign Knobs]'):
                menuItems = ['Knob-1', 'Knob-2', 'Knob-3', 'Knob-4',]
            else:
                group = plugin.getGroupNames()[menuHistory[level-1]]
                menuItems = plugin.getParamNamesForGroup(group)
        if(level > 0) and (menuBackText not in menuItems):
            menuItems.append(menuBackText)

    def UpdatePerformanceBlockMap(self):
        global PerformanceBlockMap

        self.prnt('upbm')
        width = 4
        if(playlist.getPerformanceModeState() == 1):
            self.UpdatePlaylistMap()
            PerformanceBlockMap.clear()
            for plTrack in PlaylistMap:
                for blockNum in range(width):
                    block = TnfxPerformanceBlock(plTrack.FLIndex, blockNum )
                    PerformanceBlockMap.append(block)
        else:
            self.prnt('not in performance mode')

    def UpdatePerformanceBlocks(self,width = 4):
        self.prnt('upb')
        height = 4
        if playlist.getPerformanceModeState() == 1:
            tracksToShow = self.getTrackMatrix(PerfTrackOffset)
            for idx, track in enumerate(tracksToShow):
                bank = idx // 4  # - startTrack # 4 banks
                line = idx % 4 # height
                for block in range(width):
                    padNum = anim._BankList[bank][line][block]
                    block = TnfxPerformanceBlock(track.FLIndex, block)
                    PerformanceBlocks[padNum] = block
        #    print(*getTrackMatrix(PerfTrackOffset), sep = '\n')
            if(PadMode.Mode == MODE_PERFORM):
                firstTrack = self.getTrackMatrix(PerfTrackOffset)[0].FLIndex
                lastTrack = self.getTrackMatrix(PerfTrackOffset)[-1].FLIndex
                playlist.liveDisplayZone(0, firstTrack, 4, lastTrack+1, Settings.DISPLAY_RECT_TIME_MS)
        else:
            self.prnt('not in performacnce mode')

    def UpdateAndRefreshWindowStates(self):
        global PadMode
        global lastFocus
        global lastWindowID
        global LastActiveWindow

        if(PadMode.Mode == MODE_PERFORM):
            return 

        formID = self.getFocusedWID()
        isPluginFocused = formID in [widPlugin, widPluginGenerator]
        isEffectFocused = formID == widPluginEffect  # ui.getFocused(widPlugin) or ui.getFocused(widPluginGenerator)
        prevFormID = lastFocus
        lastFocus = formID
        focusedformCaption = ui.getFocusedFormCaption()
        focusformID = ui.getFocusedFormID()


        wintype = -1
        if(isPluginFocused):
            wintype = 1
        elif isEffectFocused:
            wintype = 2
        
        if (wintype > -1):
            LastActiveWindow.Name = remove_non_printable(focusedformCaption)
            # print('law', LastActiveWindow.Name)
            LastActiveWindow.Type = wintype
            LastActiveWindow.ID = focusformID

        self.UpdateLastWindowID(formID)
        #print('formID', formID)

        if(Settings.TOGGLE_CR_AND_BROWSER) and (formID == widBrowser): # (ui.getFocused(widBrowser)):
            if ui.getVisible(widChannelRack) == 1: # close CR when broswer shows
                self.ShowChannelRack(0)
        
        if(Settings.AUTO_SWITCH_KNOBMODE):
            if(prevFormID != formID): # only switch on a window change or force
                #print('auto switch', 'prevID',  prevFormID, 'newId', formID)
                self.RefreshKnobMode()
                self.RefreshModes()

        dimA =dimNormal
        dimB =dimNormal
        bColor = cOff
        currChan = getCurrChanIdx()
        self.UpdateChannelMap()

        if(len(ChannelMap) < 1):
            return 

        # macro area channel buttons
        if(currChan >= 0): # hilight when the plugin or piano roll has focus
            bColor = cDimWhite
            if isPluginFocused:
                dimA =dimBright
            if(formID == widPianoRoll):
                bColor = ChannelMap[currChan].PadAColor 
                dimB =dimBright
                if(Settings.SHOW_PIANO_ROLL_MACROS) and (PadMode.NavSet not in [nsPianoRoll, nsMixer, nsChannel, nsPlaylist]):
                    self.ForceNaveSet(nsPianoRoll)
            elif(PadMode.isTempNavSet()):
                PadMode.RecallPrevNavSet()
                self.RefreshNavPads()

            ChannelMap[currChan].DimA = dimA
            ChannelMap[currChan].PadBColor = bColor
            ChannelMap[currChan].DimB = dimB

        if self.isNoMacros():
            return 
        else:
            self.RefreshMacros()

        if(getCurrChanIdx() >= len(ChannelMap)):
            self.UpdateChannelMap()

        self.RefreshWindowStates()

    #endregion 

    #region Helper function 
    
    def translateVelocity(self,rawVelocity):
        '''
        Translates the raw velocity from the device to a curve to make it feel more natural.
        '''
        if(AccentEnabled):   #GS
            if(0 < rawVelocity < AccentVelocityMin):
                rawVelocity = AccentVelocityMin
            elif(rawVelocity >= AccentVelocityMin):
                factExp = AccentCurveShape
                logEvent = math.log(rawVelocity / 127)
                factCurve = math.exp(logEvent * factExp)
                outCurve = int(VelocityMax * factCurve)
                rawVelocity = outCurve
        else:
            if(0 < rawVelocity < VelocityMin):
                rawVelocity = VelocityMin
            elif(rawVelocity > VelocityMin):
                rawVelocity = VelocityMax
        return rawVelocity 
 
    def mapBarsToPads(self,num_pads, num_bars):
        bars_per_pad = math.ceil(num_bars / num_pads)
        
        pad_tobar_map = []
        currentbar = 1
        
        for pad_num in range(num_pads):
            if currentbar > num_bars:
                pad_tobar_map.append(None)
            else:
                pad_tobar_map.append(currentbar)
                currentbar += bars_per_pad
        
        return pad_tobar_map, bars_per_pad

    def isFPCChannel(self,chanIdx):
        if(self.isGenPlug(chanIdx)): #ChannelMap[chanIdx].ChannelType == CT_GenPlug):
            pluginName = plugins.getPluginName(chanIdx, -1, 0)      
            return (pluginName == 'FPC')     

    def isFPCActive(self):
        chanIdx = getCurrChanIdx() # channels.channelNumber()
        return self.isFPCChannel(chanIdx)

    def CopyChannel(self,chanIdx):
        self.ShowChannelRack(1)
        chanIdx = getCurrChanIdx() # channels.channelNumber()
        self.SelectAndShowChannel(chanIdx)
        ui.copy
        name = channels.getChannelName(chanIdx)
        color = channels.getChannelColor(chanIdx)
        # crap, cant be done - no way to insert a channel via API
        return 

    def CopyPattern(self,FLPattern):
        global ScrollTo
        ui.showWindow(widChannelRack)
        chanIdx = getCurrChanIdx() # channels.channelNumber()
        self.SelectAndShowChannel(chanIdx)
        ui.copy 
        name = patterns.getPatternName(FLPattern)
        color = patterns.getPatternColor(FLPattern)
        patterns.findFirstNextEmptyPat(FFNEP_DontPromptName)
        newpat = patterns.patternNumber()
        if("#" in name):
            name = name.split('#')[0]
        name += "#{}".format(newpat)
        patterns.setPatternName(newpat, name)
        patterns.setPatternColor(newpat, color)
        patterns.jumpToPattern(newpat)
        self.SelectAndShowChannel(chanIdx)
        ui.paste 
        ScrollTo = True
        self.RefreshModes()    
        
    def ResetPadMaps(self,bUpdatePads = False):
        global PadMap
        global NoteMap
        PadMap.clear()
        NoteMap.clear()
        NoteMapDict.clear()
        for padIdx in range(0, 64):
            PadMap.append(TnfxPadMap(padIdx, -1, 0x000000, ""))
            NoteMap.append(-1) # populates later on GetScaleGrid call along with the NoteMapDict
        if(bUpdatePads):
            self.RefreshPadsFromPadMap()

    def isChromatic(self):
        return (ScaleIdx == 0) #chromatic

    def PlayMIDINote(self,chan, note, velocity):   
        if(chan > -1):
            isOn = velocity > 0
            channels.midiNoteOn(chan, note, velocity)
            self.ShowNote(note, isOn)

            # if(velocity > 0):
            #     channels.midiNoteOn(chan, note, velocity)
            #     self.ShowNote(note, True)
            # else:
            #     channels.midiNoteOn(chan, note, 0)
            #     self.ShowNote(note, False)

    def RunMacro(self,macro):
        if(macro == None):
            return
        if(macro.Execute != None):
            DisplayTimedText(macro.Name)
            macro.Execute()    
            return True
        else:
            #DisplayTimedText('Failed! ' + macro.Name)
            return False

    def ToggleRepeat(self):
        global NoteRepeat
        NoteRepeat = not NoteRepeat
        DisplayTimedText('Note Rpt: ' + showText[NoteRepeat])
        if(isRepeating):
            device.stopRepeatMidiEvent()

    def isBrowserMode(self):
        return ui.getFocused(widBrowser)

    def isMixerMode(self):
        res = (lastWindowID == widMixer) # fastest check
        if not res:
            return ui.getFocused(widMixer) or (lastWindowID == widMixer) or (ui.getFocusedFormID() > 1000)
        else: 
            return res

    def isChannelMode(self):
        res = (lastWindowID == widChannelRack)
        if not res:
            res = ui.getFocused(widChannelRack) and (ui.getFocusedFormID() < 1000) 
            #print('res', res, ui.getFocused(widChannelRack), ui.getFocusedFormID())
        return res 

    def isPlaylistMode(self,focusOnly = False):
        res = (lastWindowID == widPlaylist)
        if focusOnly or (not res):
            res = ui.getFocused(widPlaylist)
        return res

    def isGenPlug(self,chan = -1):
        return (self.getChannelType(chan) in [CT_GenPlug])

    def isSampler(self,chan = -1):
        return (self.getChannelType(chan) in [CT_Sampler])

    def isAudioClip(self,chan = -1):
        return (self.getChannelType(chan) in [CT_AudioClip])
        
    def isNoNav(self):
        return PadMode.NavSet.NoNav

    def isNoMacros(self):
        return (PadMode.NavSet.MacroNav == False) or (self.isNoNav()) or (PadMode.NavSet.ColorPicker)

    def isKnownMixerEffectActive(self):
        slotIdx, slotName, pluginName = self.GetActiveMixerEffectSlotInfo()
        return (slotIdx > -1) and (pluginName in KNOWN_PLUGINS.keys())

    def p(self,args):
        print(args)

    def mapRange(self,value, inMin, inMax, outMin, outMax):
        return outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))
    
    def prnt(self,*args, **kwargs):
        currenttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"[{currenttime}] ", end="")
        print(*args, **kwargs)
    
    def prn(self,lvl, *objects):
        if(not debugprint):
            return
        prefix = prnLevels[lvl][1]
        if(DebugPrn and (lvl >= DebugMin)) or (lvl == lvlA):
            print(prefix, *objects)    

    #endregion 

    #region setters/getters      XXXXXXXXXXXXXXX
    def getMixerMap(self):
        if(len(MixerMap) == 0):
            self.UpdateMixerMap()
        return MixerMap

    def getChannelMap(self):
        if(len(ChannelMap) != channels.channelCount()):
            self.UpdateChannelMap()
        return ChannelMap

    def getPlaylistMap(self):
        self.UpdatePlaylistMap()
        if isAltMode:
            return PlaylistSelectedMap
        else:
            return PlaylistMap

    def getPatternMap(self):
        if(len(PatternMap) != patterns.patternCount() ):
            self.UpdatePatternMap()
        patternMap = PatternMap
        if(isAltMode):
            patternMap = PatternSelectedMap
        return patternMap

    def getMixerTrackFromPad(self,padNum):
        trkIdx = -1
        trkNum = -1
        mixerMap = self.getMixerMap()
        trkOffset = self.getMixerOffsetFromPage()
        padsA, padsB = self.getPatternPads()
        if(padNum in padsA):
            trkIdx = padsA.index(padNum)
        elif(padNum in padsB):
            trkIdx = padsB.index(padNum)
        newTrkIdx = trkIdx + trkOffset
        if(newTrkIdx < len(mixerMap)):
            if(trkIdx >= 0):
                if( len(mixerMap) >= (newTrkIdx + 1)):
                    trkNum = mixerMap[newTrkIdx].FLIndex
                if(trkIdx > -1):
                    return trkNum, mixerMap[newTrkIdx]
        else:
            return mixer.trackNumber(), None

    def getPatternNumFromPad(self,padNum):
        patternMap = self.getPatternMap()
        pattIdx = -1
        pattNum = -1
        pattOffset = self.getPatternOffsetFromPage()
        patternStripA, patternStripB = self.getPatternPads()
        if(padNum in patternStripA):
            pattIdx = patternStripA.index(padNum)
        elif(padNum in patternStripB):
            pattIdx = patternStripB.index(padNum)
        newPatIdx = pattIdx + pattOffset
        if(newPatIdx < len(patternMap)):
            if(pattIdx >= 0):
                if( len(patternMap) >= (newPatIdx + 1) ):
                    pattNum = patternMap[newPatIdx].FLIndex
            if(pattIdx > -1):
                return pattNum, patternMap[newPatIdx]
        else:
            return patterns.patternNumber(), None

    def getMixerOffsetFromPage(self):
        pattAStrip, pattBStrip = self.getPatternPads() #using the pattern pads for this...
        return (MixerPage-1) * len(pattAStrip)    

    def getPlaylistOffsetFromPage(self):
        pattAStrip, pattBStrip = self.getPatternPads() #using the pattern pads for this...
        return (PlaylistPage-1) * len(pattAStrip)    

    def getChannelOffsetFromPage(self):
        # returns the index of the first pattern to show on the pattern strip based on the active page
        chanAStrip, chanBStrip = self.getChannelPads()
        return (ChannelPage-1) * len(chanAStrip)

    def getPatternOffsetFromPage(self):
        # returns the index of the first pattern to show on the pattern strip based on the active page
        pattAStrip, pattBStrip = self.getPatternPads()
        return (PatternPage-1) * len(pattAStrip)

    def getChannelPads(self): 
        if(self.isNoNav()):
            return pdChanStripANoNav, pdChanStripBNoNav
        return pdChanStripA, pdChanStripB

    def getMixerEffectPads(self):
        return self.getChannelPads()

    def getPlaylistPads(self):
        return self.getPatternPads()

    def getProgressPads(self):
        pads = []
        a, b = self.getChannelPads()
        pads.extend(a)
        pads.extend(b)
        return pads

    def getMixerStripPads(self):
        return self.getPatternPads()

    def getPatternPads(self):
        if(self.isNoNav()):
            return pdPatternStripANoNav, pdPatternStripBNoNav
        return pdPatternStripA, pdPatternStripB

    def getPatternModeLength(self):
        return len(self.getPatternPads()[0])

    def getMixerModeLength(self):
        return len(self.getMixerStripPads()[0])

    def getChannelModeLength(self):
        a, b = self.getChannelPads()
        return len(a)

    def GetScaleGrid(self,newModeIdx=0, rootNote=0, startOctave=2, invertOctaves=False):
        global PadMap 
        global ScaleNotes 
        global ScaleDisplayText
        global ScaleIdx
        global NoteMap
        global NoteMapDict
        global RootNoteMap

        if(len(HarmonicScalesLoaded) == 0):
            InitScales()

        if(len(HarmonicScalesLoaded) < (newModeIdx+1)):
            return

        faveNoteIdx = rootNote
        ScaleIdx = newModeIdx
        #print('hs', ScaleIdx, newModeIdx, HarmonicScalesLoaded[newModeIdx])
        harmonicScaleIdx = ScaleIdx
        gridlen = 12

        ScaleNotes.clear()
        RootNoteMap.clear()

        if(isAltMode) and (PadMode.Mode == MODE_DRUM):
            harmonicScaleIdx = HarmonicScalesLoaded[0]
            gridlen = 64

        # get lowest octave line
        lineGrid = [[0] for y in range(gridlen)] # init with 0
        notesInScale = GetScaleNoteCount(harmonicScaleIdx)
        
        #build the lowest <gridlen> notes octave and transpose up from there
        BuildNoteGrid(lineGrid, gridlen, 1, rootNote, startOctave, harmonicScaleIdx)

        # first I make a 5 octave list of notes to refernce later
        for octave in range(0, 5):
            for note in range(0, notesInScale):
                ScaleNotes.append(lineGrid[note][0] + (12*octave) )

        # next I fill in the notes from the bottom to top
        NoteMapDict.clear()

        if(PadMode.Mode == MODE_NOTE):
            for colOffset in range(0, gridlen):
                for row in range(0, 4): # 3
                    
                    if(notesInScale < 6): 
                        noteVal = lineGrid[colOffset][0] + (24*row) # for pentatonic scales 
                    else:
                        noteVal = lineGrid[colOffset][0] + (12*row)

                    revRow = 3-row  # reverse to go from bottom to top (FPC)
                    
                    if(invertOctaves):
                        revRow = row # to go top to bottom (Battery 4)
                        print('revRow')

                    rowOffset = 16 * revRow  # rows start on 0,16,32,48
                    padIdx = rowOffset + colOffset

                    self.MapNoteToPad(padIdx, noteVal, cRed)

                    if(row == 3): # and (GetScaleNoteCount(scale) == 7): #chord row
                        PadMap[padIdx].NoteInfo.ChordNum = colOffset + 1
                    else:
                        PadMap[padIdx].NoteInfo.ChordNum = -1
                    
                    NoteMap[padIdx] = noteVal

                    if(PadMap[padIdx].NoteInfo.ChordNum < 0): # not a chord pad, so its ok
                        if(noteVal not in NoteMapDict.keys()): 
                            NoteMapDict[noteVal] = [padIdx]
                        elif(Settings.SHOW_ALL_MATCHING_CHORD_NOTES):
                            if(padIdx not in NoteMapDict[noteVal]):
                                NoteMapDict[noteVal].append(padIdx)

                    isRoot = (colOffset % notesInScale) == 0
                    PadMap[padIdx].NoteInfo.IsRootNote = isRoot #(colOffset % notesInScale) == 0 # (colOffset == 0) or (colOffset == notesInScale)
                    if isRoot:
                        RootNoteMap.append(noteVal)



            ScaleDisplayText = NotesList[faveNoteIdx] + str(startOctave) + " " + HarmonicScaleNamesT[harmonicScaleIdx]

    def getFPCChannels(self):
        global FPCChannels
        FPCChannels.clear()
        for chanIdx in range(channels.channelCount()):
            if(self.isGenPlug(chanIdx)):
                if(plugins.getPluginName(chanIdx, -1, 0) == "FPC"):
                    FPCChannels.append(chanIdx)
        return FPCChannels
        
    def GetPatternMapActive(self):
        return PatternMap[_CurrentPattern-1]

    def SetPadMode(self):
        self.RefreshShiftAltButtons()
        if(PadMode.Mode == MODE_PATTERNS):
            self.UpdatePatternModeData()
        elif(PadMode.Mode == MODE_PERFORM):
            if PadMode.IsAlt:
                self.RefreshAltPerformanceMode()
            else:
                self.RefreshPerformanceMode(-1)        
        self.RefreshPadModeButtons() # lights the button
        self.RefreshAll()

        # fireNFX_Bridge.WriteINI('General', 'Mode', PadMode.Mode)

    def getCurrChanPluginID(self):
        name, plugin = self.getCurrChanPlugin()
        if(plugin == None):
            return ""
        return plugin.getID()

    def getCurrChanPluginNames(self):
        if(self.isSampler()):
            name = channels.getChannelName(getCurrChanIdx())
            if( name == Settings.GLOBAL_CONTROL_NAME):
                return name, name
            return 'Sampler', name
        else:
            if(plugins.isValid(getCurrChanIdx(), -1, 0)):
                return plugins.getPluginName(getCurrChanIdx(), -1, 0), plugins.getPluginName(getCurrChanIdx(), -1, 1)
            else:
                return None, None

    def getCurrChanPlugin(self):
        plName, uName  = self.getCurrChanPluginNames()
        if(FLChannelFX):
            plName = FLEFFECTS
        if (plName == 'Sampler') and (uName == Settings.GLOBAL_CONTROL_NAME):
            plName = uName
        plugin = self.getPlugin(plName)
        if plugin == None:
            return NOSUPPTEXT, None
        return plugin.getID(), plugin

    def getTrackSlotFromFormID(self,formID = -1):
        if formID < 0:
            formID = ui.getFocusedFormID()
        track = -1
        slot = -1
        if formID > 1000:
            track = (formID >> 6) >> 16
            slot = (formID - (( track << 6) << 16 ) ) >> 16 # formID - (track << 6) 
        return track, slot

    def getFormIDFromTrackSlot(self,trackNum, slotNum):
        return ((trackNum << 6) + slotNum) << 16

    def getFocusedWID(self):
        formID = -1 #  was ui.getFocusedFormID() but this functions returne 0-7 for channels and 0-7 for widXXX constants and cannot be used for windows < 8
        if ui.getFocused(widPluginEffect):
            formID = widPluginEffect
        elif ui.getFocused(widPluginGenerator):
            formID = widPluginGenerator 
        elif ui.getFocused(widPlugin):
            formID = widPlugin
        elif ui.getFocused(widBrowser):
            formID = widBrowser
        elif ui.getFocused(widChannelRack):
            formID = widChannelRack
        elif ui.getFocused(widPlaylist):
            formID = widPlaylist
        elif ui.getFocused(widMixer):
            formID = widMixer
        elif ui.getFocused(widPianoRoll):
            formID = widPianoRoll
        # else:
        #     formID = ui.getFocusedFormID()
        return formID

    def GetPadMode(self):
        return PadMode    
    
    def SetTop(self):
        if(ui.getFocused(widPlaylist)):
            self.SetPlaylistTop()
        elif(ui.getFocused(widPianoRoll)):
            self.SetPianoRollTop()

    def SetPlaylistTop(self):
        ui.scrollWindow(widPlaylist, 1)
        ui.scrollWindow(widPlaylist, 1, 1)

    def SetPianoRollTop(self):
        ui.scrollWindow(widPianoRoll, 1)
        ui.scrollWindow(widPianoRoll, 1, 1)

    def getPlugin(self,pluginName, slotIdx = -1):
        ''' Loads the plugin from either (in this order):

            1) from knownPlugins if it exists
            2) from customized TnfxPLugin (ie. FLKeys, FLEX) if exists. add entry to knownPlugins
            3) real-time loading of params with non empty names. adds an entry to knownPlugins
            
            NOTE: passing an empty string will load the current channel's plugin
        '''
        global LOADED_PLUGINS


        if(slotIdx > -1): # its a mixer effect
            baseEffectName, userEffectName = GetMixerSlotPluginNames(-1, slotIdx)
            if(baseEffectName != 'INVALID'):
                if(baseEffectName in KNOWN_PLUGINS.keys()): # is this instance a known plugin?
                    #print('GP KNOWN', baseEffectName)
                    pl = KNOWN_PLUGINS[baseEffectName].copy()  
                    pl.ParamPadMaps = KNOWN_PLUGINS[baseEffectName].ParamPadMaps
                else:
                    #print('GP NOT KNOWN', baseEffectName)
                    pl = self.getPluginInfo(-1, False, False, slotIdx) # unknown, read the info
                
                #print('GP RESULT', pl.Name, pl.Type,  pl.ParamPadMaps)

                return pl

            return None 


        if(pluginName == "GLOBAL CTRL"): # and (self.isSampler()):
            return plGlobal

        if(self.isSampler()):
            return plSampler


        if(pluginName == FLEFFECTS):
            plFLChanFX.FLChannelType = self.getChannelType()
            return plFLChanFX

        if(not plugins.isValid(channels.selectedChannel())):
            return None 

        basePluginName, userPluginName = self.getCurrChanPluginNames()
        pl = TnfxChannelPlugin(basePluginName, userPluginName) # in case we need a new instance

        if(pl.getID() in LOADED_PLUGINS.keys()): # is this instance already loaded?
            return LOADED_PLUGINS[pl.getID()]

        UseExternalKnobPresets = False
        if(basePluginName in KNOWN_PLUGINS.keys()): # is this instance a known plugin?
            pl = KNOWN_PLUGINS[basePluginName].copy()  
        else:
            pl = getPluginInfo(-1, False, False, slotIdx) # unknown, read the info
        
        # rd3d2Present = ('rd3d2 Ext' in pl.ParameterGroups.keys())
        # UseExternalKnobPresets = (len(pl.getCurrentKnobParamOffsets()) == 0) and rd3d2Present

        # if(UseExternalKnobPresets):
        #     pl.assignKnobs(rd3d2PotParamOffsets)
        #     plist = rd3d2PotParams.get(pl.PluginName)
        #     pl.assignKnobsFromParamList(plist)
        #     print('rd3d2 params loaded for {}'.format(pl.Name))
        
        LOADED_PLUGINS[pl.getID()] = pl
        return pl 

    def getChannelRecEventID(self):
        chanNum = getCurrChanIdx()
        return channels.getRecEventId(chanNum)

    def setSnapMode(self,newmode):
        ui.setSnapMode(newmode)
        i = 0
        mode = ui.getSnapMode(self)
        while(mode < newmode):
            ui.snapMode(1)  # inc by 1
            mode = ui.getSnapMode(self)
            i += 1
            if i > 100:
                return
        while(mode > newmode):
            ui.snapMode(-1)  # inc by 1
            mode = ui.getSnapMode(self)
            i += 1
            if i > 100:
                return 

    def getChannelType(self,chan = -1):
        if(chan < 0):
            chan = getCurrChanIdx()
        return channels.getChannelType(chan)

    def getMixer(self,mixerNum = -1):
        if(mixerNum == -1):
            mixerNum = mixer.trackNumber()
        res = TnfxMixer(mixerNum)
        res.Update()
        return res

    def getEventData(self,ctrlID):
        s = ''
        s2 = ''
        if (general.getVersion() > 9):
            BaseID = EncodeRemoteControlID(device.getPortNumber(), 0, 0)
            eventId = device.findEventID(BaseID + ctrlID, 0)
            if eventId != 2147483647:
                s = device.getLinkedParamName(eventId)
                s2 = device.getLinkedValueString(eventId)
                DisplayTextAll(s, s2, '')  

    def GetCurrMixerPlugin(self):
        # gets the names for a specific slot
        trkNum = mixer.trackNumber()
        slotIdx, slotName, pluginName = self.GetActiveMixerEffectSlotInfo()
        if(pluginName != 'INVALID'):
            plugin = self.getPlugin(pluginName, slotIdx)
            if plugin != None:
                return plugin.getID(), plugin
        return '', None

    def GetAllEffectsForMixerTrack(self,trkNum = -1):
        # list of TnfxMixerEffect
        res = {}
        for fx in range(10): # 0-9
            name, uname = GetMixerSlotPluginNames(trkNum, fx)
            if(name == 'INVALID'):
                name = 'Slot'+str(fx+1)
            mxfx = TnfxMixerEffectSlot(fx, name, cWhite, trkNum)
            mxfx.Update()
            res[fx] = mxfx
        return res        

    def GetUsedEffectsForMixerTrack(self,trkNum = -1):
        # gets the non-empty slots only list of TnfxMixerEffects
        res = {}
        for fx in range(10): # 0-9
            name, uname = GetMixerSlotPluginNames(trkNum, fx)
            if(name != 'INVALID'):
                mxfx = TnfxMixerEffectSlot(fx, name, cWhite, trkNum)
                mxfx.Update()
                res[fx] = mxfx 
        return res

    def GetActiveMixerEffectSlotInfo(self):
        global lastSlotIdx
        slotIdx = -1
        formID = self.getFocusedWID() 
        formCap = ui.getFocusedFormCaption()
        slotName = getAlphaNum(formCap.partition(" (")[0].strip(), True)
        pluginName = ui.getFocusedPluginName()
        uname = ''
        for fx in self.GetAllEffectsForMixerTrack().values():
            #print('GAMESI slot fx', fx) 
            pname, uname = GetMixerSlotPluginNames(-1, fx.SlotIndex) # 0-based
            if(uname == fx.Name): 
                slotIdx = fx.SlotIndex
                pluginName = pname
                slotName = fx.Name
                lastSlotIdx = slotIdx
                #print('GAMESI ACTIVE: slotIdx={}."{}",  plugin="{}"'.format(slotIdx, slotName, pluginName))
                
        return slotIdx, slotName, pluginName

    def SetArp(self,enabled, arpTime = 1024, arpRange = 1, arpRepeat = 2):
        if(enabled):
            SetChannelFXParam(REC_Chan_Arp_Mode, 1)
            SetChannelFXParam(REC_Chan_Arp_Time, arpTime)
            SetChannelFXParam(REC_Chan_Arp_Range, arpRange)
            SetChannelFXParam(REC_Chan_Arp_Repeat, arpRepeat)
        else:
            SetChannelFXParam(REC_Chan_Arp_Mode, 0)
    #endregion

    #region Nav helpers
    
    def navigate(self,states, currentindex, steps):
        num_states = len(states)
        if(num_states > 0):
            new_index = (currentindex + steps) % num_states
        else:
            new_index = currentindex
        return new_index

    def SetKnobMode(self,mode=-1, formID = -1):
        global KnobMode
        global UserKnobModeIndex

        if(mode == -1):
            UserKnobModeIndex += 1
        elif(mode == -2):
            pass
        else:
            UserKnobModeIndex = mode

        if( UserKnobModeIndex >= len(UserKnobModes) ):
            UserKnobModeIndex = 0

        KnobMode = UserKnobModes[UserKnobModeIndex]

    #    print('set km', KnobMode, 'um', UserKnobModeIndex)
        self.RefreshKnobMode()
    
    def PlaylistPageNav(self,moveby):
        global PlaylistPage
        pageSize = self.getPatternModeLength()
        newPage = PlaylistPage + moveby 
        maxPageNum = (playlist.trackCount() // pageSize) + 1

        if(newPage < 1): # paging is 1-based
            newPage = maxPageNum

        firstTrackOnPage = (newPage-1) * pageSize # first channel track will be #0, second page will be pageSize, then pageSize*2, etc

        if(0 <= firstTrackOnPage <= playlist.trackCount() ) and (newPage <= maxPageNum): # allow next page when there tracks to show
            PlaylistPage = newPage
        else:
            PlaylistPage = 1
            
        self.RefreshPageLights()

    def  MixerPageNav(self,moveby):
        global MixerPage

        pageSize = self.getPatternModeLength()
        newPage = MixerPage + moveby 
        maxPageNum = (mixer.trackCount() // pageSize) + 1
        if(newPage < 1): # paging is 1-based
            newPage = maxPageNum
        firstTrackOnPage = (newPage-1) * pageSize # first channel track will be #0, second page will be pageSize, then pageSize*2, etc
        if(0 <= firstTrackOnPage <= mixer.trackCount() ) and (newPage <= maxPageNum): # allow next page when there tracks to show
            MixerPage = newPage
        else:
            MixerPage = 1
        self.RefreshPageLights()

    def PatternPageNav(self,moveby):
        global PatternPage
        pageSize = self.getPatternModeLength()
        newPage = PatternPage + moveby 
        maxPageNum = (patterns.patternCount() // pageSize) + 1
        if(newPage < 1):
            newPage = maxPageNum
        elif(newPage > maxPageNum):
            newPage = 1
        firstPatternOnPage = (newPage-1) * pageSize # first page will = 0
        if(0 <= firstPatternOnPage <= PatternCount ): # allow next page when there are patterns to show
            PatternPage = newPage
        self.RefreshPageLights()

    def ProgressZoomNav(self,moveby):
        global progressZoomIdx
        progressZoomIdx = self.navigate(progressZoom, progressZoomIdx, moveby)
        # newZoomIdx = progressZoomIdx + moveby
        # if(newZoomIdx >= len(progressZoom)):
        #     newZoomIdx = 0
        # elif(newZoomIdx < 0):
        #     newZoomIdx = len(progressZoom)-1
        self.RefreshPageLights()

    def ChannelPageNav(self,moveby):
        global ChannelPage
        pageSize = self.getPatternModeLength()
        newPage = ChannelPage + moveby 
        maxPageNum = (channels.channelCount() // pageSize) + 1
        if(newPage < 1):
            newPage = maxPageNum
        elif(newPage > maxPageNum):
            newPage = 1
        firstChannelOnPage = (newPage-1) * pageSize # first page will = 0
        if(0 <= firstChannelOnPage <= ChannelCount ): # allow next page when there are patterns to show
            ChannelPage = newPage
        self.RefreshPageLights()
        ui.crDisplayRect(0, firstChannelOnPage, 0, pageSize, rectTime, CR_ScrollToView + CR_HighlightChannelName)

    def NavNotesList(self,val):
        global NoteIdx
        NoteIdx = self.navigate(NotesList, NoteIdx, val)

    def NavLayout(self,val):
        global PadMode
        PadMode.LayoutIdx = self.navigate(Layouts, PadMode.LayoutIdx, val)
        # oldIdx = PadMode.LayoutIdx
        # newIdx = (oldIdx + val) % len(Layouts)
        # PadMode.LayoutIdx = newIdx 

    def NavOctavesList(self,val):
        global OctaveIdx
        OctaveIdx = self.navigate(OctavesList, OctaveIdx, val)
        # OctaveIdx += val
        # if( OctaveIdx > (len(OctavesList)-1) ):
        #     OctaveIdx = 0
        # elif( OctaveIdx < 0 ):
        #     OctaveIdx = len(OctavesList)-1

    def ForceNavSet(self,navSet):
        global PadMode
        global BlinkTimer
        PadMode.SetNavSet(navSet)
        BlinkTimer = PadMode.NavSet.BlinkButtons
        self.RefreshMacroGrid()

    def ForceNavSetIdx(self,navSetIdx):
        global PadMode
        global BlinkTimer
        navset = PadMode.AllowedNavSets[navSetIdx]
        PadMode.SetNavSet(navset)
        BlinkTimer = PadMode.NavSet.BlinkButtons
        self.RefreshMacroGrid()

    def RefreshMacroGrid(self):
        if(PadMode.NavSet.ColorPicker):
            self.RefreshColorPicker()
        elif(PadMode.NavSet.CustomMacros):
            # TODO
            # RefreshCustomMacros()
            pass
        else:
            self.RefreshMacros()
            self.RefreshNavPads()

    def NavSetList(self,val):
        global PadMode 
        newNavSetIdx = self.navigate(PadMode.AllowedNavSets, PadMode.CurrentNavSetIdx, val)

        # newNavSetIdx = PadMode.CurrentNavSetIdx + val 
        # if(newNavSetIdx > (len(PadMode.AllowedNavSets)-1)):
        #     newNavSetIdx = 0
        # elif(newNavSetIdx < 0):
        #     newNavSetIdx = len(PadMode.AllowedNavSets)-1

        self.ForceNavSetIdx(newNavSetIdx)
        PadMode.CurrentNavSetIdx = newNavSetIdx 

    def RefreshGridLR(self):
        navSet = PadMode.NavSet.NavSetID
        SendCC(IDLeft, SingleColorOff)
        SendCC(IDRight, SingleColorOff)

        if(navSet in [nsDefault, nsDefaultDrum] ):
            SendCC(IDLeft, SingleColorHalfBright)
        elif(navSet in [nsScale, nsDefaultDrumAlt]):
            SendCC(IDRight, SingleColorHalfBright)
        elif(navSet == nsUDLR):
            SendCC(IDLeft, SingleColorHalfBright)
            SendCC(IDRight, SingleColorHalfBright)
        elif(navSet == nsColorPicker):
            if(ToBlinkOrNotToBlink):
                SendCC(IDLeft, SingleColorFull)
                SendCC(IDRight, SingleColorHalfBright)
            else:
                SendCC(IDLeft, SingleColorHalfBright)
                SendCC(IDRight, SingleColorFull)
        elif(navSet == nsCustomMacros):
            if(ToBlinkOrNotToBlink):
                SendCC(IDLeft, SingleColorHalfBright)
                SendCC(IDRight, SingleColorHalfBright)
            else:
                SendCC(IDLeft, SingleColorOff)
                SendCC(IDRight, SingleColorOff)

    def NavPerfTrackOffset(self,val):
        global PerfTrackOffset
        if(len(PlaylistMap) == 0):
            self.UpdatePlaylistMap()

        PerfTrackOffset = self.navigate(PlaylistMap, PerfTrackOffset, val) # 16 = 4 x 4
        # self.prnt('new PerfTrackOffset is', PerfTrackOffset)
        self.RefreshDisplay()

    def NavScalesList(self,val):
        global ScaleIdx
        ScaleIdx = self.navigate(HarmonicScalesLoaded, ScaleIdx, val)
        # ScaleIdx += val
        # if( ScaleIdx > (len(HarmonicScalesLoaded)-1) ):
        #     ScaleIdx = 0
        # elif( ScaleIdx < 0 ):
        #     ScaleIdx = len(HarmonicScalesLoaded)-1

    def NavNoteRepeatLength(self,val):
        global NoteRepeatLengthIdx
        NoteRepeatLengthIdx = self.navigate(BeatLengthDivs, NoteRepeatLengthIdx, val)
        # NoteRepeatLengthIdx += val
        # if(NoteRepeatLengthIdx > (len(BeatLengthDivs) -1) ):
        #     NoteRepeatLengthIdx = 0
        # elif(NoteRepeatLengthIdx < 0):
        #     NoteRepeatLengthIdx = len(BeatLengthDivs) - 1
        DisplayTimedText2('Repeat Note', BeatLengthNames[NoteRepeatLengthIdx], '')
    #endregion

    #region UI Helpers - Show/Hide - Close
    def ShowPianoRoll(self,showVal, bUpdateDisplay = False, forceChanIdx = -1):
        if(showVal == -1):  # toggle
            if(ui.getVisible(widPianoRoll)):
                showVal = 0
            else:
                showVal = 1

        if(showVal == 1):
            if(forceChanIdx == -1):
                ui.showWindow(widPianoRoll)
            else:
                ui.openEventEditor(channels.getRecEventId(forceChanIdx) + REC_Chan_PianoRoll, EE_PR)
        else:
            ui.hideWindow(widPianoRoll)
            ui.showWindow(widChannelRack)
        
        self.OnRefresh(HW_Dirty_FocusedWindow)
            
        self.RefreshChannelStrip()

        if(bUpdateDisplay):
            DisplayTimedText('Piano Roll: ' + showText[showVal])

    def ShowChannelSettings(self,showVal, bSave, bUpdateDisplay = False):
        global PatternMap
        global ShowCSForm

        currVal = 0

        # if(True):
        #     self.ForceNaveSet(nsChannel, True)

        if(len(PatternMap) > 0):
            selPat = self.GetPatternMapActive() # PatternMap[_CurrentPattern-1]  # 0 based
            currVal = selPat.ShowChannelSettings

        if(showVal == -1):  # toggle
            if(currVal == 0):
                showVal = 1
            else:
                showVal = 0
        
        chanNum = channels.selectedChannel(0, 0, 0)
        channels.showCSForm(chanNum, showVal)
        if(showVal == 0): # make CR active
            self.ShowChannelRack(1)
            ShowCSForm = False
        else:
            ShowCSForm = True

        if(bUpdateDisplay):
            DisplayTimedText('Chan Sett: ' + showText[showVal])

        self.OnRefresh(HW_Dirty_FocusedWindow)
        self.RefreshChannelStrip()

        if(bSave):
            if(len(PatternMap) > 0):
                selPat.ShowChannelSettings = showVal

    def ShowChannelEditor(self,showVal, bUpdateDisplay = False):
        global ChannelMap
        global ShowChannelEditor
        global ShowCSForm

        if(len(ChannelMap) <= 0):
            return

        isFocused = ui.getFocused(widPlugin) or ui.getFocused(widPluginGenerator)
        channel = ChannelMap[getCurrChanIdx()]
        if(showVal == -1):  # toggle
            if(isFocused):
                showVal = 0
            else:
                showVal = 1
        if( channel.ChannelType in [CT_Hybrid, CT_GenPlug] ):
            channels.showEditor(channel.FLIndex, showVal)
        elif(channel.ChannelType in [CT_Layer, CT_AudioClip, CT_Sampler, CT_AutoClip]):
            channels.showCSForm(channel.FLIndex, showVal)

        if(bUpdateDisplay):
            DisplayTextBottom('ChanEdit: ' + showText[showVal])

        if showVal == 0: # revert to channel rack when closed
            ui.showWindow(widChannelRack)
            self.OnRefresh(HW_Dirty_FocusedWindow)

        self.RefreshChannelStrip()

    def ShowPlaylist(self,showVal, bUpdateDisplay = False):
        # global ShowPlaylist
        
        isShowing = ui.getVisible(widPlaylist)
        isFocused = ui.getFocused(widPlaylist)

        if(isShowing == 1) and (isFocused == 1) and (showVal <= 0):
            showVal = 0
        else:
            showVal = 1
        
        if(showVal == 1):        
            ui.showWindow(widPlaylist)
            ui.setFocused(widPlaylist)
        else:
            ui.hideWindow(widPlaylist)
        
        # ShowPlaylist = showVal    
        self.OnRefresh(HW_Dirty_FocusedWindow)

        if(bUpdateDisplay): 
            DisplayTimedText('Playlist: ' + showText[showVal])

    def ShowMixer(self,showVal, bUpdateDisplay = True):
        if(ui.getFocused(widMixer) and showVal < 1):
            ui.hideWindow(widMixer)
        else:
            ui.showWindow(widMixer)
            ui.setFocused(widMixer)

        self.OnRefresh(HW_Dirty_FocusedWindow)

        if(bUpdateDisplay): 
            DisplayTimedText('Mixer: ' + showText[ui.getFocused(widMixer)])

    def ShowChannelRack(self,showVal, bUpdateDisplay = False):
        # global ShowChanRack 

        isShowing = ui.getVisible(widChannelRack)
        isFocused = ui.getFocused(widChannelRack)

        if(showVal == -1): #toggle
            if(isShowing):
                showVal = 0
                if(not isFocused):      # if not focused already, activate it
                    showVal = 1
            else:
                showVal = 1

        if(showVal == 1):
            ui.showWindow(widChannelRack)
            ui.setFocused(widChannelRack)
        else:
            ui.hideWindow(widChannelRack)

        # ShowChanRack = showVal
        self.OnRefresh(HW_Dirty_FocusedWindow)
        

        

        if(bUpdateDisplay):
            DisplayTimedText('Chan Rack: ' + showText[showVal])

    def ShowBrowser(self,showVal, bUpdateDisplay = False):
        # global ShowBrowser
        global resetAutoHide
        global prevNavSet

        isAutoHide = ui.isBrowserAutoHide() # or Settings.ALWAYS_HIDE_BROWSER

        if(showVal == -1): # toggle
            if(ui.getFocused(widBrowser)):
                showVal = 0
            else:
                showVal = 1        
            
        if(showVal == 1):
            if(isAutoHide):
                resetAutoHide = True
                ui.setBrowserAutoHide(False)  # if hidden it will become visible
                # shoudl show automatically
            else:
                ui.showWindow(widBrowser)

            if(Settings.FORCE_UDLR_ON_BROWSER):
                self.ForceNavSet(nsUDLR)

        else: # closing
            if(self.isAutoHide):
                if(resetAutoHide) :
                    p('resetting AH')
                    ui.setBrowserAutoHide(True)
                    resetAutoHide = False
                    # if(ui.getVersion(0) > 20): # BUG: can't reopen pre FL 21, so we don't close it.
                    #     ui.hideWindow(widBrowser)
            else:
                ui.hideWindow(widBrowser) 

            # if(resetAutoHide):
            #     ui.setBrowserAutoHide(True) # BUG? does not auto close
            #     resetAutoHide = False
            # elif(self.isAutoHide):
            #     if(ui.getVersion(0) > 20): # BUG: can't reopen pre FL 21, so we don't close it.
            #         ui.hideWindow(widBrowser)
            #     ui.setBrowserAutoHide(True) # BUG? does not auto close
            #     resetAutoHide = True

            if(Settings.FORCE_UDLR_ON_BROWSER):
                if(PadMode.NavSet != nsUDLR):
                    prevNavSet = PadMode.NavSet.NavSetID
                    self.ForceNaveSet(nsUDLR)
                
                if(prevNavSet > -1):
                    self.ForceNaveSet(nsUDLR)
                    prevNavSet = -1
        
        self.OnRefresh(HW_Dirty_FocusedWindow)
        if(bUpdateDisplay):
            DisplayTimedText('Browser: ' + showText[showVal])

    def ShowMenuItems(self):
        global menuItems
        pageLen = 3 # display is 3 lines tall
        selPage = menuItemSelected//pageLen
        selItemOffs = menuItemSelected % pageLen    
        pageFirstItemOffs = (selPage * pageLen) 
        
        level = len(menuHistory)
        self.UpdateMenuItems(level)
        maxItem = len(menuItems)-1
        displayText = ['','','']

        for i in range(0,3):
            item = i + pageFirstItemOffs
            if(item < maxItem):
                preText = ' '
                if(menuItemSelected == item):
                    preText = '-->'
            elif(item == maxItem):
                preText = ''
                if(menuItemSelected == item):
                    preText = '-->'
                    if(level > 0):
                        preText = '<--'
            
            if(level == MAXLEVELS):
                pass
                #displayText[i] = "[" + menuItems[item].upper() + "]" 
            elif(item < len(menuItems)):
                if(menuItems[item] == NOSUPPTEXT):
                    preText = ''
                displayText[i] = preText + menuItems[item]
            else:
                displayText[i] = ''

        DisplayTextAll(displayText[0], displayText[1], displayText[2])
        
    def ShowMenuItems2(self):
        pageLen = 3 # display is 3 lines tall
        selPage = int(menuItemSelected/pageLen) # 
        selItemOffs = menuItemSelected % pageLen    #
        pageFirstItemOffs = (selPage * pageLen)       # 
        maxItem = len(menuItems)
        displayText = ['','','']
        
        for i in range(0,3):
            item = i + pageFirstItemOffs
            if(item < maxItem):
                preText = '...'
                if(menuItemSelected == item):
                    preText = '-->'
                displayText[i] = preText + menuItems[item]

        DisplayTextAll(displayText[0], displayText[1], displayText[2])
    
    def SelectAndShowMixerTrack(self,trkNum):
        mixer.setTrackNumber(trkNum, curfxScrollToMakeVisible)
        # mixer.setActiveTrack(trkNum) # in v27 of api but has no scroll option
        ui.miDisplayRect(trkNum, trkNum, rectTime, CR_ScrollToView)

    def SelectAndShowChannel(self,newChanIdx):
        global CurrentChannel
        oldChanIdx = getCurrChanIdx()
        
        if(newChanIdx < 0) or (oldChanIdx < 0):
            return

        channels.selectOneChannel(newChanIdx)
        ui.crDisplayRect(0, newChanIdx, 0, 1, rectTime, CR_ScrollToView + CR_HighlightChannels)

        # change to and show the rect  for the linked mixer track
        if(not ShiftHeld) and (not AltHeld):
            mixerTrk = channels.getTargetFxTrack(newChanIdx)
            self.SelectAndShowMixerTrack(mixerTrk)

        if( oldChanIdx != newChanIdx ): # if the channel has changed...
            self.ShowChannelEditor(0) 
            if(ui.getFocused(widPianoRoll)):
                self.ShowPianoRoll(1, False, newChanIdx)
            elif(ui.getVisible(widPianoRoll)):
                self.ShowPianoRoll(0)

    def CloseBrowser(self):
        if(ShowMenu):
            self.HandleBrowserButton()
    
    
    #endregion

    # work area/utility 
    def ShowNote(self,note, isOn = True):
        if(note == -1):
            return

        dim =dimNormal

        isRoot = False
        showRoot = not self.isChromatic() and PadMode.Mode == MODE_NOTE


        if(isOn):
            dim =dimBright
        else:
            dim =dimNormal
            if PadMode.Mode == MODE_DRUM:
                dim =dimNormal
        
        noteDict = NoteMapDict
        
        
        if(note in noteDict):
            pads = noteDict[note]
            if PadMode.Mode == MODE_NOTE:
                if showRoot and not isOn:
                    if note in RootNoteMap:
                        dim = dimNormal
                for pad in pads:
                    color = getNotePadColor(pad)
                    if color == cOff and isOn:
                        color = Settings.PAD_PRESSED_COLOR                    
                    SetPadColor(pad,  color, dim, False)
            elif PadMode.Mode == MODE_DRUM:
                for pad in pads:
                    color = PadMap[pad].Color
                    # if color == cOff and isOn:
                    #     color = Settings.PAD_PRESSED_COLOR
                    SetPadColor(pad,  color, dim, False)

    
    def DrumPads(self):
        id, pl = self.getCurrChanPlugin()
        invert = False
        if(pl != None):
            invert = pl.InvertOctaves
        return getDrumPads(isAltMode, self.isNoNav(), PadMode.LayoutIdx, invert)
        
    def NotePads(self):
        if(self.isNoNav()):
            return pdAllPads
        else:
            return pdWorkArea

    def InititalizePadModes(self):
        
        global PadMode 
        global modePattern
        global modePatternAlt
        global modeNote
        global modeNoteAlt
        global modeDrum
        global modeDrumAlt
        global modePerform
        global modePerformAlt

        # PadMode will be assigned one of these on mode change
        modePattern.NavSet = TnfxNavigationSet(nsDefault)
        modePattern.AllowedNavSets = [nsDefault, nsUDLR, nsNone, nsColorPicker]

        modePatternAlt.NavSet = TnfxNavigationSet(nsDefault)
        modePatternAlt.AllowedNavSets = [nsDefault, nsUDLR, nsNone]

        modeNote.NavSet = TnfxNavigationSet(nsScale)
        modeNote.AllowedNavSets = [nsScale, nsDefault, nsUDLR]

        modeNoteAlt.NavSet = TnfxNavigationSet(nsScale)
        modeNoteAlt.AllowedNavSets = [nsScale, nsDefault, nsUDLR]

        modeDrum.NavSet = TnfxNavigationSet(nsDefaultDrum)
        modeDrum.AllowedNavSets = [nsDefaultDrum, nsUDLR, nsColorPicker]

        modeDrumAlt.NavSet = TnfxNavigationSet(nsDefaultDrumAlt)
        modeDrumAlt.AllowedNavSets = [nsDefaultDrumAlt, nsDefaultDrum, nsUDLR, nsColorPicker, nsNone]

        modePerform.NavSet = TnfxNavigationSet(nsNone)
        modePerform.AllowedNavSets = [nsNone, nsDefault, nsUDLR]

        modePerformAlt.NavSet = TnfxNavigationSet(nsNone)
        modePerformAlt.AllowedNavSets = [nsNone, nsDefault, nsUDLR]

        PadMode = modePattern
    
    def OpenMainMenu(self,menuName = 'Patterns'):            
        res = False
        NavigateFLMenu('', False)
        time.sleep(Settings.MENU_DELAY)
        msg = tempMsg

        if(msg == menuName):
            return True
        
        for i in range(10):
            ui.left()
            time.sleep(Settings.MENU_DELAY * 2)
            msg = tempMsg
            match1 = 'Menu - {}'.format(menuName)
            match2 = '{} -'.format(menuName)
            if(msg.startswith(match1)) or (msg.startswith(match2)):
                res = True
                break
        return res

    def ClonePattern(self):
        self.NavigateFLMainMenu('Patterns', 'Clone')

    def ClonePattern2(self):
        self.NavMainMenu('Patterns', ['Clone'])

    def ViewCurrentProject(self):
        if self.NavMainMenu('View', ['Remote']):
            ProcessKeys(',ELLLLR')

    def ViewCurrentProjec1t(self):
        self.NavMainMenu('View', ['Plugin database'])

    def MenuNavTo(self,menuItemStartsWith, verticalNav = True, hasMenuItems = False):
        visitedMenuItems = []
        matched = False
        msg = ''
        while (not matched):
            msg = tempMsg   # getting a copy of this value in case it changes
            matched = msg.startswith(menuItemStartsWith) or " - {}".format(menuItemStartsWith) in msg
            if(not matched):
                if verticalNav:
                    ui.down()
                else:
                    ui.right
                time.sleep(Settings.MENU_DELAY)

            matched = lastHints[-1].startswith(menuItemStartsWith)

            if(hasMenuItems):
                ui.right()
            else:
                ui.enter()

            if (msg not in visitedMenuItems):        
                visitedMenuItems.append(msg)
            else:
                break

        return matched

    def NavMainMenu(self,mainMenu = 'File', subMenuNav = ['New']):
        if self.OpenMainMenu(mainMenu):
            lastItem = subMenuNav[-1]
            for menuItem in subMenuNav:
                print('looking for ', "[{}]".format(menuItem), "lastHint", lastHints[-1])
                if not self.MenuNavTo(menuItem, True, (menuItem != lastItem)):
                    return False
            return True        
        else:
            return False

    def NavigateFLMainMenu(self,menu1 = 'Patterns', menu2 = 'Clone', menu3 = ''):
        visited = []
        self.OpenMainMenu(menu1)
        if(not ui.isInPopupMenu()):
            ui.down()
            time.sleep(0.25)
        match = '{} - {}'.format(menu1, menu2)
        matched = False
        msg = ''
        while (not matched):
            msg = tempMsg   # getting a copy of this value in case it changes
            print('tm looking for ', "[{}]".format(match), "msg", msg)
            matched = msg.startswith(match)
            if(not matched):
                ui.down()
                time.sleep(Settings.MENU_DELAY//2)
            else:
                ui.enter()
            if (msg not in visited):        
                visited.append(msg)
            else:
                break

        return matched, msg, tempMsg, (msg in visited)

    def AdjustColorBrightness(self,color, brightlevel):
        r, g, b = nfxutils.ColorToRGB(color)
        h, s, v = utils.RGBToHSV(r, g, b) # colorsys.rgb_tohsv(r, g, b)
        newV = int(self.mapRange(round(brightlevel,1), 0.0, 1.0, 8, 127)) 
        r, g, b = utils.HSVtoRGB(h, s, newV) # colorsys.hsv_torgb(h,s,newV)
        color = nfxutils.RGBToColor(int(r), int(g), int(b) ) 
        return color 

    def SetPadColorPeakVal(self,pad = 0, color = cPurple, peakval = 1, flushBuffer= True):
        r, g, b = nfxutils.ColorToRGB(color)
        h, s, v = utils.RGBToHSV(r, g, b) # colorsys.rgb_tohsv(r, g, b)
        newV = int(self.mapRange(round(peakval,1), 0.0, 1.0, 8, 255)) 
        r, g, b = utils.HSVtoRGB(h, s, newV) # colorsys.hsv_torgb(h,s,newV)
        color = nfxutils.RGBToColor(int(r), int(g), int(b) ) 
        SetPadColorDirect(pad, color, 0)
        #if(flushBuffer):
        #    time.sleep(.1)

    def TestPeaks(self):
        mixMap = self.getMixerMap()
        while transport.isPlaying():
            mixerStripA, mixerStripB = self.getMixerStripPads()
            numTrks = len(mixerStripA)
            for trk in range(numTrks):
                mx = MixerMap[trk]
                isLast = (trk == (numTrks-1))
                self.SetPadColorPeakVal(trk, mx.Color, mixer.getTrackPeaks(mx.FLIndex, PEAK_LR), isLast)
                self.SetPadColorPeakVal(trk, mx.Color, mixer.getTrackPeaks(mx.FLIndex, PEAK_LR), isLast)
            #TestLumi(0, cRed, mixer.getTrackPeaks(0, PEAK_LR))
            time.sleep(0.1)

    def TestLumi(self,pad = 0, color = cPurple, peakval = 1, dim = 0):
        #
        r, g, b = ColorToRGB(color)
        h, s, v = colorsys.rgb_tohsv(r, g, b)
        #print('input', r, g, b, ' and ', h, s, v )
        v = self.mapRange(peakval, 0.0, 1.0, 128, 254)
        r, g, b = colorsys.hsv_torgb(h,s,v)
        #print('output', r, g, b, ' and ', h, s, v )
        color = RGBToColor(int(r), int(g), int(b) )
        SetPadColor(pad, color, dim)
        time.sleep(0.1)
        
    def TestColorMap(self,delay = 0.02, steps = 20, toBuffer = True):
        # adapted from: https://stackoverflow.com/questions/66341745/python-make-a-hue-color-cycle 
        num_steps = steps
        hue = 0.0
        step_val = 1.0 / num_steps
        for zz in range(num_steps):
            rgb = colorsys.hsv_torgb(hue, 1, 1)
            hue += step_val
            hue %= 1.0 # cap hue at 1.0
            maxrgb = 127 # 255
            r = round(rgb[0] * maxrgb)
            g = round(rgb[1] * maxrgb)
            b = round(rgb[2] * maxrgb)
            rgb_ints = (r, g, b)
            print(rgb_ints)
            for pad in range(64):
                if(toBuffer):
                    SetPadColorBuffer(pad, RGBToColor(r,g,b), 0, (pad == 63)) # flushed on pad == 63
                else:
                    SetPadColorDirect(pad, RGBToColor(r,g,b), 0) 
            time.sleep(delay)


    def adjustForAudioPeaks(self):
        return Settings.SHOW_AUDIO_PEAKS and transport.isPlaying()

    def getTrackMatrix(self,startTrack):
        self.prnt('gtm')
        res = []
        self.UpdatePerformanceBlockMap()
        # UpdatePlaylistMap()
        startOffset = startTrack # * 4
        lastTrack = startOffset + 16
        if(lastTrack > playlist.trackCount() ):
            lastTrack = playlist.trackCount()
        for track in PlaylistMap[startOffset: lastTrack]:
            # print('trackNum', track.FLIndex, track.Name, hex(track.Color) )
            res.append(track)
        return res 

    def OnUpdateLiveMode(self, firstTrack, lastTrack):
        # self.prnt('oulm', lastTrack)
        pass 

    def OnMidiIn_KnobEvent(self,event):
        if (event.status in [MIDI_NOTEON, MIDI_NOTEOFF]): # to prevent the mere touching of the knob generating a midi note event.
            event.handled = True

        ctrlID = event.data1

        pName, plugin = self.getCurrChanPlugin()

        # check if we have predefined user knob settings, if NOT shortcut out 
        # to be processed by OnMidiMsg() to use processMIDICC per the docs
        if(KnobMode in [KM_USER1, KM_USER2, KM_USER3]):
            if(plugin == None): # invalid plugin
                return False
            
            hasParams = False
            if(KnobMode == KM_USER1):
                hasParams = len( [a for a in plugin.User1Knobs if a.Offset > -1]) > 0
            elif(KnobMode == KM_USER2):
                hasParams = len( [a for a in plugin.User2Knobs if a.Offset > -1]) > 0
            elif(KnobMode == KM_USER3):
                hasParams = len( [a for a in plugin.User3Knobs if a.Offset > -1]) > 0

            if(not hasParams): # is a user knob and is handled in OnMidiMsg()
                event.handled = False
                return False

            event.handled = self.HandleKnob(event, ctrlID, None, event.handled)

        return event.handled

    def TestPLScroll(self):
        ui.showWindow(widPlaylist)
        ui.setFocused(widPlaylist)
        time.sleep(1.0)
        for i in range(0, 5):
            print('ui down')
            #ui.down()
            transport.globalTransport(FPT_Down, 1)
        for i in range(0, 5):
            print('ui right')
            #ui.right()        
            transport.globalTransport(FPT_Right, 1)

#####
# Fire = TFireNFX() 

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
