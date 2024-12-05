#
# Various class definitions
#
from fireNFX_Defs import *
from fireNFX_FireUtils import FLColorToPadColor
import plugins
import channels
import playlist 
import mixer
import midi 
import general 
from fireNFX_Helpers import GetMixerGenParamVal

def clonePluginParams(srcPlugin, destPlugin):
    """
    Clone parameters from source plugin to destination plugin.
    
    Args:
        srcPlugin: Source plugin to copy from.
        destPlugin: Destination plugin to copy to.
    
    Returns:
        Updated destination plugin.
    """
    destPlugin.InvertOctaves = srcPlugin.InvertOctaves
    destPlugin.isNative = srcPlugin.isNative 
    destPlugin.AlwaysRescan = srcPlugin.AlwaysRescan 
    destPlugin.PresetPrev = srcPlugin.PresetPrev
    destPlugin.PresetNext = srcPlugin.PresetNext

    for param in srcPlugin.Parameters:
        newParam = TnfxParameter(param.Offset, param.Caption, param.Value, param.ValueStr, param.Bipolar, param.StepsInclZero)
        if newParam.Caption in ['?', ''] and newParam.Offset > -1:
            if plugins.isValid(channels.selectedChannel()):
                newParam.Caption = plugins.getParamName(newParam.Offset, channels.selectedChannel(), -1)
        destPlugin.addParamToGroup(param.GroupName, newParam)
    
    for knob in range(4):
        for userKnobs, kmUser in [(srcPlugin.User1Knobs, KM_USER1), (srcPlugin.User2Knobs, KM_USER2), (srcPlugin.User3Knobs, KM_USER3)]:
            param = userKnobs[knob]
            newParam = TnfxParameter(param.Offset, param.Caption, param.Value, param.ValueStr, param.Bipolar, param.StepsInclZero)
            if newParam.Caption in ['?', ''] and newParam.Offset > -1:
                if plugins.isValid(channels.selectedChannel()):
                    newParam.Caption = plugins.getParamName(newParam.Offset, channels.selectedChannel(), -1)
            destPlugin.assignParameterToUserKnob(kmUser, knob, newParam)

    return destPlugin

cpGlobal, cpChannel, cpChannelPlugin, cpMixer, cpMixerPlugin = range(5)

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

class TnfxChannelPlugin:
    """
    Represents a channel plugin in the Fire NFX system.
    """
    def __init__(self, name, username="", type=cpChannelPlugin):
        self.Name = name
        self.PluginName = name
        self.UserName = username
        self.ParameterGroups = {}  # { groupName: [TnfxParameters] }
        self.Parameters = []
        self.TweakableParam = None
        self.User1Knobs = []
        self.User2Knobs = []
        self.User3Knobs = []
        self.isNative = False
        self.AlwaysRescan = True
        self.FLChannelType = -1
        self.PresetGroups = {}
        self.Type = type
        self.InvertOctaves = False
        self.ParamPadMaps = []
        self.PresetPrev = -1
        self.PresetNext = -1
        for i in range(4):
            p = TnfxParameter(-1, '', i, '', False)
            self.User1Knobs.append(p)
            self.User2Knobs.append(p)
            self.User3Knobs.append(p)

    def copy(self):
        """Create a copy of the plugin."""
        newPlugin = TnfxChannelPlugin(self.PluginName, self.UserName, self.Type)
        return clonePluginParams(self, newPlugin)

    def getID(self):
        """Get a unique identifier for the plugin."""
        chanName = channels.getChannelName(channels.selectedChannel())
        number = channels.selectedChannel()
        if self.Type == cpMixerPlugin:
            number = mixer.trackNumber()
            chanName = mixer.getTrackName(number)
        presetName = "NONE"
        if plugins.isValid(channels.selectedChannel()):
            presetName = plugins.getName(channels.selectedChannel(), -1, 6, -1)
        return "{}-{}-{}-{}".format(self.PluginName, chanName, presetName, number)

    def getParamNamesForGroup(self, groupName):
        """Get parameter names for a specific group."""
        return [p.Caption for p in self.ParameterGroups.get(groupName, [])]

    def getParamFromOffset(self, offset):
        """Get a parameter by its offset."""
        for param in self.Parameters:
            if param.Offset == offset:
                return param
        return None

    def getGroupNames(self):
        """Get all group names."""
        return list(self.ParameterGroups.keys())
        
    def addParamToGroup(self, groupName, nfxParameter):
        """Add a parameter to a group."""
        nfxParameter.GroupName = groupName 
        self.Parameters.append(nfxParameter)
        if groupName in self.ParameterGroups:
            self.ParameterGroups[groupName].append(nfxParameter)
        else:
            self.ParameterGroups[groupName] = [nfxParameter]

    def assignKnobsFromParamGroup(self, groupName):
        """Assign knobs based on a parameter group."""
        offslist = [param.Offset for param in self.ParameterGroups.get(groupName, [])]
        if offslist:
            self.assignKnobs(offslist)
            return True
        return False

    def getCurrentKnobParamOffsets(self):
        """Get current knob parameter offsets."""
        res = []
        for user_knobs in [self.User1Knobs, self.User2Knobs, self.User3Knobs]:
            res.extend([knob.Offset for knob in user_knobs if knob.Offset > -1])
        return res
        
    def assignParameterToUserKnob(self, knobMode, knobIdx, nfxParameter):
        """Assign a parameter to a user knob."""
        if 0 <= knobIdx < 4:
            if knobMode == KM_USER1:
                self.User1Knobs[knobIdx] = nfxParameter
            elif knobMode == KM_USER2:
                self.User2Knobs[knobIdx] = nfxParameter
            elif knobMode == KM_USER3:
                self.User3Knobs[knobIdx] = nfxParameter

    def assignOffsetToUserKnob(self, usermode, knob, paramOffs):
        """Assign an offset to a user knob."""
        self.assignParameterToUserKnob(usermode, knob, self.getParamFromOffset(paramOffs))

    def assignKnobsFromParamList(self, paramList):
        """Assign knobs from a parameter list."""
        self.assignKnobs([param.Offset for param in paramList])

    def assignKnobs(self, offsetList, PresetGroup=''):
        """Assign knobs based on offset list."""
        res = 0
        for idx, offs in enumerate(offsetList):
            if idx > 11:
                break
            km = KM_USER1 + idx // 4
            ko = idx % 4
            if offs < 0 or self.getParamFromOffset(offs) is None:
                self.assignParameterToUserKnob(km, ko, None)
            else:
                self.assignOffsetToUserKnob(km, ko, offs)
            res = idx + 1
        if PresetGroup:
            self.PresetGroups[PresetGroup] = res
        return res

class TnfxParameter:
    """Represents a parameter in the Fire NFX system."""
    def __init__(self, offset, caption, value=0, valuestr='', bipolar=False, stepsInclZero=0):
        self.Offset = offset 
        self.Caption = caption
        self.Value = value
        self.ValueStr = valuestr
        self.Bipolar = bipolar 
        self.StepsInclZero = stepsInclZero
        self.GroupName = ''

    def __str__(self):
        return "{}, '{}', {}, '{}'".format(self.Offset, self.Caption, self.Value, self.ValueStr)

    def getFullName(self):
        """Get the full name of the parameter."""
        return self.GroupName + "-" + self.Caption 

    def updateCaption(self, caption):
        """Update the caption of the parameter."""
        self.Caption = caption 

class TnfxWindow:
    """Represents a window in the Fire NFX system."""
    def __init__(self, name, id, type):
        self.Name = name
        self.ID = id
        self.Type = type

    def __str__(self):
        return "{}, '{}', {}".format(self.Name, self.ID, self.Type)

class TnfxUserKnob:
    """Represents a user knob in the Fire NFX system."""
    def __init__(self, knobOffset, pluginName='', paramOffset=-1, caption=''):
        self.Offset = paramOffset 
        self.Caption = caption
        self.PluginName = pluginName 
        self.KnobOffset = knobOffset

    def __str__(self):
        return "{}, {}, '{}'".format(self.PluginName, self.Offset, self.Caption)

class TnfxPadMode:
    """Represents a pad mode in the Fire NFX system."""
    def __init__(self, name, mode, btnId=IDStepSeq, isAlt=False):
        self.Name = name 
        self.Mode = mode
        self.ButtonID = btnId
        self.IsAlt = isAlt 
        self.NavSet = TnfxNavigationSet(nsDefault)
        self.AltNavSet = TnfxNavigationSet(nsDefault)
        self.AllowedNavSets = [nsDefault]
        self.CurrentNavSetIdx = 0
        self.LayoutIdx = 0
        self.TempNavSets = [nsPianoRoll, nsPlaylist, nsChannel, nsMixer]
        self.NavSetHist = []
    
    def isTempNavSet(self):
        """Check if the current nav set is temporary."""
        return self.NavSet.NavSetID in self.TempNavSets
    
    def SetNavSet(self, navSet):
        """Set the navigation set."""
        if self.NavSet.NavSetID in self.AllowedNavSets:
            self.NavSetHist.append(self.NavSet.NavSetID)
            if len(self.NavSetHist) > 10:
                self.NavSetHist.pop(0)
        self.NavSet.SetNavSet(navSet)

    def RecallPrevNavSet(self):
        """Recall the previous navigation set."""
        prevNS = self.AllowedNavSets[0]
        if self.NavSetHist:
            prevNS = self.NavSetHist.pop()
        self.SetNavSet(prevNS)

class TnfxProgressStep:
    """Represents a progress step in the Fire NFX system."""
    def __init__(self, padIdx, color, songpos, abspos, barnum, selected=False):
        self.PadIndex = padIdx
        self.Color = color
        self.SongPos = songpos
        self.SongPosAbsTicks = abspos
        self.Selected = selected
        self.BarNumber = barnum 
        self.Markers = []

    def __str__(self):
        return "ProgressStep PadIdx: {}, SongPos: {}%, {} ticks, Bar #{}, color:{} ".format(
            self.PadIndex, self.SongPos, self.SongPosAbsTicks, self.BarNumber, hex(self.Color))

class TnfxMarker:
    """Represents a marker in the Fire NFX system."""
    def __init__(self, number, name, ticks):
        self.Number = number
        self.Name = name
        self.SongPosAbsTicks = ticks

    def __str__(self):
        return "Marker #{}, {}, SongPos: {}".format(self.Number, self.Name, self.SongPosAbsTicks)

class TnfxMixerEffectSlot:
    """Represents a mixer effect slot in the Fire NFX system."""
    def __init__(self, slotIdx, pluginName, color=0xFFFFFF, trackNum=-1):
        self.SlotIndex = slotIdx
        self.Name = pluginName
        self.Color = color
        self.Muted = False
        self.MixLevel = 0
        self.TrackNumber = trackNum
        self.Used = False
        self.Update()

    def __str__(self):
        return "Effect Slot #{}, {}, Muted: {}, Mix: {}, , color: {}, Slot In Use: {}".format(
            self.SlotIndex, self.Name, self.Muted, self.MixLevel, hex(self.Color), self.Used)

    def Update(self):
        """Update the mixer effect slot state."""
        if self.TrackNumber < 0:
            self.TrackNumber = mixer.trackNumber()
        self.Muted = GetMixerGenParamVal(midi.REC_Plug_Mute, self.TrackNumber, self.SlotIndex) == 0
        self.MixLevel = GetMixerGenParamVal(midi.REC_Plug_MixLevel, self.TrackNumber, self.SlotIndex)
        self.Used = plugins.isValid(self.TrackNumber, self.SlotIndex)
        if general.getVersion() >= 32:
            self.Color = mixer.getSlotColor(self.TrackNumber, self.SlotIndex)
        else:
            self.Color = 0xFFFFFF

class TnfxMixer:
    """Represents a mixer in the Fire NFX system."""
    def __init__(self, flIdx, fxSlots=None):
        self.FLIndex = flIdx
        self.Name = ''
        self.Color = 0x000000 
        self.Muted = False
        self.Solo = False
        self.Selected = False
        self.Enabled = False
        self.Armed = False
        self.EffectSlots = fxSlots or {}
        self.Update()

    def __str__(self):
        return "Mixer #{}.{}  (color = {})  Muted:{}, Selected:{}, SlotsInUse({}/10)".format(
            self.FLIndex, self.Name, hex(self.Color), self.Muted, self.Selected, len(self.EffectSlots))

    def getRecEventID(self, pluginOffs=0):
        """Get the record event ID for the mixer."""
        return mixer.getTrackPluginId(self.FLIndex, pluginOffs)

    def Update(self):
        """Update the mixer state."""
        self.Name = mixer.getTrackName(self.FLIndex)
        self.Color = FLColorToPadColor(mixer.getTrackColor(self.FLIndex))
        self.Muted = mixer.isTrackMuted(self.FLIndex)
        self.Selected = mixer.isTrackSelected(self.FLIndex)
        self.Solo = mixer.isTrackSolo(self.FLIndex)
        self.Enabled = mixer.isTrackEnabled(self.FLIndex)
        self.Armed = mixer.isTrackArmed(self.FLIndex)

class TnfxChannel:
    """Represents a channel in the Fire NFX system."""
    def __init__(self, flIdx):
        if flIdx == -1:
            flIdx = channels.channelNumber()

        self.FLIndex = flIdx 
        self.Name = ''
        self.Color = 0x000000
        self.Muted = False
        self.Solo = False
        self.Selected = False 
        self.Mixer = None
        self.ChannelType = -1

        self.GlobalIndex = -1
        self.ItemIndex = flIdx
        self.LoopSize = 0
        self.PadAColor = 0
        self.DimA = 3
        self.PadBColor = 0
        self.DimB = 3 
        self.Update()

    def __str__(self):
        return "Channel #{} - {} - Selected: {}".format(self.FLIndex, self.Name, self.Selected)        

    def Update(self):
        """Update the channel state."""
        self.Name = channels.getChannelName(self.FLIndex)
        self.Color = channels.getChannelColor(self.FLIndex)
        self.Muted = channels.isChannelMuted(self.FLIndex)
        self.Solo = channels.isChannelSolo(self.FLIndex)
        self.Selected = channels.isChannelSelected(self.FLIndex)
        self.ChannelType = channels.getChannelType(self.FLIndex)
        self.Mixer = TnfxMixer(channels.getTargetFxTrack(self.FLIndex))

    def getRecEventID(self): 
        """Get the record event ID for the channel."""
        return channels.getRecEventId(self.FLIndex)

nsNone, nsDefault, nsScale, nsUDLR, nsDefaultDrum, nsDefaultDrumAlt, nsChannel, nsPlaylist, nsMixer, nsPianoRoll, nsColorPicker, nsCustomMacros = range(12)

class TnfxNavigationSet:
    """Represents a navigation set in the Fire NFX system."""
    def __init__(self, navSet):
        self.NavSetID = navSet
        self.Index = -1
        self.InitData()
        self.SetNavSet(navSet) 

    def InitData(self):
        """Initialize navigation set data."""
        self.ChanNav = False
        self.ScaleNav = False
        self.SnapNav = False
        self.NoteRepeat = False
        self.OctaveNav = False
        self.LayoutNav = False
        self.PresetNav = False
        self.UDLRNav = False 
        self.MacroNav = True 
        self.NoNav = False
        self.PianoRollNav = False
        self.ChannelNav = False
        self.PlaylistNav = False
        self.MixerNav = False
        self.ColorPicker = False 
        self.CustomMacros = False
        self.BlinkButtons = False
        self.Rename = False

    def SetNavSet(self, navSet):
        """Set the navigation set."""
        self.NavSetID = navSet
        self.InitData()
        if navSet == nsDefault:
            self.ChanNav = self.SnapNav = self.PresetNav = self.Rename = True
        elif navSet == nsPianoRoll:
            self.ChanNav = self.PianoRollNav = self.PresetNav = True
        elif navSet == nsDefaultDrum:
            self.ChanNav = self.SnapNav = self.NoteRepeat = self.PresetNav = True
        elif navSet == nsDefaultDrumAlt:
            self.ChanNav = self.LayoutNav = self.OctaveNav = self.PresetNav = True
        elif navSet == nsScale:
            self.ChanNav = self.ScaleNav = True
        elif navSet == nsUDLR:
            self.UDLRNav = True
        elif navSet == nsColorPicker:
            self.ColorPicker = self.BlinkButtons = True
        elif navSet == nsCustomMacros:
            self.CustomMacros = self.BlinkButtons = True
        elif navSet == nsNone:
            self.MacroNav = False
            self.NoNav = True

class TnfxPattern:
    """Represents a pattern in the Fire NFX system."""
    def __init__(self, flIdx, name):
        self.Name = name 
        self.FLIndex = flIdx 
        self.ItemIndex = flIdx - 1
        self.Channels = []
        self.Mixer = None
        self.Muted = 0
        self.ShowChannelEditor = 0
        self.ShowPianoRoll = 0
        self.ShowChannelSettings = 0
        self.Color = 0x000000
        self.MutePreset1 = 0
        self.MutePreset2 = 1
        self.FilterParam = -1
        self.ResParam = -1
        self.PluginName = ''
        self.Parameters = [] 
        self.ParamPages = []
        self.ParamPageIdx = -1
        self.Selected = False 

    def __str__(self):
        return "Pattern #{} - {} - Selected: {}".format(self.FLIndex, self.Name, self.Selected)

class TnfxPlaylistTrack:
    """Represents a playlist track in the Fire NFX system."""
    def __init__(self, flIdx):
        self.FLIndex = flIdx
        self.Name = ''
        self.Color = 0x000000
        self.Muted = False
        self.Solo = False
        self.Selected = False 
        self.ChanIdx = -1
        self.MixerIdx = -1

        if flIdx > -1:
            self.Update()
    
    def Update(self):
        """Update the playlist track state."""
        self.Color = playlist.getTrackColor(self.FLIndex)
        self.Name = playlist.getTrackName(self.FLIndex)
        self.Muted = playlist.isTrackMuted(self.FLIndex)
        self.Selected = playlist.isTrackSelected(self.FLIndex)
        self.Solo = playlist.isTrackSolo(self.FLIndex)

    def __str__(self):
        return "Playlist Track #{} - {}".format(self.FLIndex, self.Name)

class TnfxNoteInfo:
    """Represents note information in the Fire NFX system."""
    def __init__(self):
        self.MIDINote = -1
        self.ChordNum = -1
        self.IsRootNote = False
        self.Highlight = False

ptUndefined, ptPattern, ptChannel, ptPlaylistTrack, ptNote, ptDrum, ptMacro, ptNav, ptProgress, ptParameter = range(-1, 9)

class TnfxParamPadMapping:
    """Represents parameter pad mapping in the Fire NFX system."""
    def __init__(self, offset, color=0x000000, padList=None):
        self.Offset = offset
        self.Color = color
        self.Pads = padList or []

    def getValueFromPad(self, padIdx):
        """Get value from pad index."""
        if padIdx in self.Pads:
            size = len(self.Pads) - 1
            incby = 1.0 / size
            return self.Pads.index(padIdx) * incby 
        return -1

class TnfxPerformanceBlock:
    """Represents a performance block in the Fire NFX system."""
    def __init__(self, flIdx, blockNum):
        self.FLTrackIndex = flIdx 
        self.Number = blockNum
        self.Color = 0x00
        self.LastStatus = 0
        self.Update()

    def getStatus(self):
        """Get the status of the performance block."""
        self.LastStatus = playlist.getLiveBlockStatus(self.FLTrackIndex, self.Number, midi.LB_Status_Default)
        return self.LastStatus

    def Update(self):
        """Update the performance block state."""
        self.LastStatus = self.getStatus()
        self.Color = playlist.getLiveBlockColor(self.FLTrackIndex, self.Number)

    def Trigger(self, tlcMode=midi.TLC_MuteOthers | midi.TLC_Fill):
        """Trigger the performance block."""
        if tlcMode == -1:
            self.StopAll()
        else:
            playlist.triggerLiveClip(self.FLTrackIndex, self.Number, tlcMode)

    def StopAll(self):
        """Stop all performance blocks."""
        playlist.triggerLiveClip(self.FLTrackIndex, -1, midi.TLC_Fill)

    def __str__(self):
        return "Block Track# {} - Block# {} - Color: {} - LastStatus: {}".format(
            self.FLTrackIndex, self.Number, hex(self.Color), self.LastStatus)

class TnfxPadMap:
    """Represents a pad map in the Fire NFX system."""
    def __init__(self, padIndex, flIndex, color, tag):
        self.PadIndex = padIndex
        self.FLIndex = flIndex
        self.Color = color
        self.Pressed = -1 
        self.Tag = tag
        self.ItemType = ptUndefined 
        self.ItemObject = object()
        self.ItemIndex = -1
        self.NoteInfo = TnfxNoteInfo()

class TnfxMacro:
    """Represents a macro in the Fire NFX system."""
    def __init__(self, name, color, command=None):
        self.Name = name
        self.PadIndex = -1
        self.PadColor = color 
        self.Execute = command
        self.PadModesAllowed = []

class TnfxMenuItems:
    """Represents menu items in the Fire NFX system."""
    def __init__(self, text, object=None):
        self.Level = 0
        self.Parent = None
        self.Text = text
        self.Value = 0
        self.Selected = False
        self.Object = object
        self.SubItems = []

    def __str__(self):
        return "TnfxMenuItem( {}, {}, {} ) - {} subitem(s) - parent: {}".format(
            self.Level, self.Text, self.Value, len(self.SubItems), self.Parent)

    def addSubItem(self, item):
        """Add a sub-item to the menu item."""
        item.Level = self.Level + 1
        item.Parent = self
        item.Value = len(self.SubItems)
        if not any(id(item) == id(mi) for mi in self.SubItems):
            self.SubItems.append(item)

# Commented out rd3d2 Pot Parameters code
