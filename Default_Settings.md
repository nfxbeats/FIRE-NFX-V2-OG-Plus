# Fire NFX Default Settings Documentation

This document describes all available settings that can be controlled in Fire NFX. These are the default values that come with the system.

> **IMPORTANT**: Requires FL24+ -  A Settings.json file is created after the first run of the script. You can edit this file and restart the script for changes to take effect.



## Color Settings

### Valid Colors
- 0xRRGGBB (for example 0xFF0000)
- cWhite
- cBlue
- cGreen
- cRed
- cYellow
- cCyan
- cPurple
- cOrange
- cMagenta
- cOff
- cChannel (the color of the currently active channel) 

| Setting | Default Value | Description |
|---------|--------------|-------------|
| PAD_PRESSED_COLOR | cYellow | Color of pads when pressed |
| ROOT_NOTE_COLOR | cChannel | Color of root notes in NOTE mode |



## Note and Scale Settings

| Setting | Default Value | Description |
|---------|--------------|-------------|
| NOTE_NAMES | NotesListSharps | How to display notes - can be NotesListSharps or NotesListFlats |
| ROOT_NOTE | 'C' | Default Root Note (use '#' for sharps or 'b' for flats based on NOTE_NAMES) |
| OCTAVE | 3 | Lowest octave in NOTE mode (range: 1-5) |
| SCALE | 0 | Default Scale in NOTES mode |

### Available Scales
- 0 = CHROMATIC
- 1 = Major/IONIAN
- 2 = DORIAN
- 3 = PHRYGIAN
- 4 = LYDIAN
- 5 = MIXOLYDIAN
- 6 = AEOLIAN/Minor
- 7 = LOCRIAN
- 8 = Major Pentatonic
- 9 = Minor Pentatonic

## Display and Visual Settings

| Setting | Default Value | Description |
|---------|--------------|-------------|
| SHOW_ALL_MATCHING_CHORD_NOTES | False | When playing chords in chord mode, it Show all pads with same/repeated note mappings |
| SHOW_CHANNEL_WITH_SHARED_MIXER_CHANNELS | False | Light channel strip for shared mixer routing |
| SHOW_PLAYBACK_NOTES | False | Show playing notes in NOTE and DRUM mode (mono only) |
| DISPLAY_RECT_TIME_MS | 5000 | Duration of red boxes in FL Studio (milliseconds, 0 = disabled) |
| SHOW_PRN | False | Show extra debugging info |
| SHOW_AUDIO_PEAKS | False | Display audio peaks on playback |
| SHOW_CHANNEL_MUTES | True | Display channel mute states |
| SHOW_PIANO_ROLL_MACROS | False | Display piano roll macros |
| SHOW_CUSTOM_MACROS | False | Display custom macros |

## Navigation and Browser Settings

| Setting | Default Value | Description |
|---------|--------------|-------------|
| BROWSER_STEPS | 64 | Default knob wheel precision |
| SHIFT_BROWSER_STEPS | 128 | Knob wheel precision when SHIFT is held |
| ALT_BROWSER_STEPS | 8 | Knob wheel precision when ALT is held |
| TOGGLE_CR_AND_BROWSER | False | Toggle between Channel Rack and Browser. When browser closed, CR opens and vice versa |
| HIDE_BROWSER | True | Actually hide browser when closing with BROWSER button |
| FORCE_UDLR_ON_BROWSER | False | Force UDLR macro grid navigation when in browser |
| MENU_DELAY | 0.025 | Delay when navigating FL menus |

## Pattern Settings

| Setting | Default Value | Description |
|---------|--------------|-------------|
| PATTERN_NAME | "{}-Pattern" | Pattern naming template ({} replaced with number) |
| PROMPT_NAME_FOR_NEW_PATTERN | False | Show naming prompt for new patterns |
| DETECT_AND_FIX_DEFAULT_PATTERNS | True | Detect and fix default 'ghost' pattern issues |

## Window and Interface Settings

| Setting | Default Value | Description |
|---------|--------------|-------------|
| REOPEN_WINDOWS_AFTER_CLOSE_ALL | False | Reopen core windows after closing all via macro |
| AUTO_SWITCH_KNOBMODE | True | Auto switch knob modes for Mixer/Channel Rack - requires WATCH_WINDOW_SWITCHING to be True |
| WATCH_WINDOW_SWITCHING | False | Monitor window switching |
| AUTO_SWITCH_TO_MAPPED_MIXER_EFFECTS | False | Auto switch to mapped mixer effects |

## Performance Settings

| Setting | Default Value | Description |
|---------|--------------|-------------|
| ACCENT_ENABLED | False | Enable accent feature for better velocity mapping |
| ACCENT_CURVE_SHAPE | 0.4 | Accent curve shape (0.1 = steep, 1.0 = linear) |
| MUTE_PLTRACK_IMMEDIATELY | True | Immediate muting of playlist tracks when in PL mode |
| UNDO_STYLE | 0 | Undo behavior (0 = multiple times, 1 = last only) |

## Startup and Display Settings

| Setting | Default Value | Description |
|---------|--------------|-------------|
| STARTUP_TEXT_TOP | "-={FIRE-NFX}=-" | Fire Display Top text on startup |
| STARTUP_TEXT_BOT | "Version 2.0" | Fire Display Bottom text on startup |
| STARTUP_FL_HINT | "^c FIRE-NFX-V2" | FL Studio hint text on startup |
| DBL_TAP_DELAY_MS | 220 | Double-tap delay in milliseconds |
| DBL_TAP_ZOOM | 4 | Double-tap zoom level on PL and PR |
| MARKER_PREFIX_TEXT | "{}-Marker" | Prefix for markers created by script {} is replaced by a number |

## Plugin and Control Settings

| Setting | Default Value | Description |
|---------|--------------|-------------|
| AUTO_MAP_KNOWN_PARAMS_TO_USER_KNOBS | True | Auto-map parameters to user knobs. These are defined in pluginXXXX files |
| GLOBAL_CONTROL_NAME | 'GLOBAL CTRL' | Name for global control |
| ALT_DRUM_MODE_BANKS | True | Use 4x4 banks in ALT+DRUM mode |
| AUTO_COLOR_ENABLED | False | Enable automatic coloring |

## Arrays and Collections

| Setting | Default Value | Description |
|---------|--------------|-------------|
| DEFAULT_MACROS_ORDER | [] | Order of default macros |
| CUSTOM_MACROS | [] | List of custom macros |
| AUTO_COLORS | {} | Automatic color mappings |
