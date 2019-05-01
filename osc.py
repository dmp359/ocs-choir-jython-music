from gui import *
from random import *   
from music import *
from osc import *
import math

notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
supported_colors = [Color.WHITE, Color.RED, Color.LIGHT_GRAY, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.DARK_GRAY,
          Color.BLUE, Color.CYAN, Color.MAGENTA, Color.BLACK, Color.PINK]

# Constants
SCALE            = MAJOR_SCALE      # scale used by instrument.
BASS_PORT        = 57110
TENOR_PORT       = 57111
ALTO_PORT        = 57112

# Return the closest pitch to input amount in voice's n note range
def closestPitch(amount, voice):
    num_pitches = len(voice.pitches)
    split_point = 1.0 / float(num_pitches)
    if (split_point <= 0): # Safety catch
        return 'C0'
    closest_index = int(math.floor(amount / split_point))
    if (closest_index >= num_pitches): # If amount is 1.0 (or greater)
        closest_index = num_pitches - 1
    return voice.pitches[closest_index]
    
    
# Midi value to note name (60 => 0, 61 => 1)
def midi_number_to_note_num(num):
    return num % 12

def midi_number_to_note_name(num):
    return notes[midi_number_to_note_num(num)]

# Return a string note name/octave for MIDI number
def midi_number_to_string(notenum):
    octave = int(notenum / 12) - 1
    note = midi_number_to_note_name(notenum)
    return "{}{}".format(note, octave)

# Convert a string (such as C4) to a number (60)
def string_to_midi_number(s):
    print(s)
    octave = int(s[-1]) # 0 through 6
    note = s[:-1]
    note_value = notes.index(note) # 0 through 11
    return (octave + 1) * 12 + note_value 

# Class to encapsulate instrument and its pitches to use
# Also methods to play notes
class Voice:
    def __init__(self, name, pitches, instrument, channel, color):
        self.name = name             # String name for debugging
        self.pitches = pitches       # Midi values
        self.channel = channel       # For playing notes
        self.currentPitch = 0        # Currently playing a note, this should be greater than -1
        self.color = color  
        self.visual = None
        self.label = None
        Play.setInstrument(instrument, channel)    

    def stop_playing(self):
        if (self.currentPitch > 0):
            Play.noteOff(self.currentPitch, self.channel) # Stop playing previous note
            self.currentPitch = 0
    
    def remove_active_note(self, x, y):
        self.stop_playing()
        d.remove(self.visual)
        d.remove(self.label)

    '''
    Draw an appropriate circle to represent the current pitch
    '''
    def draw_pitch(self):
        numerator = float(self.currentPitch) - float(LOWEST_PITCH_REPRESENTED)
        denominator = float(HIGHEST_PITCH_REPRESENTED) - float(LOWEST_PITCH_REPRESENTED)
        percentage_in_range = 1 - (numerator / denominator)
        y = int(percentage_in_range * d.getHeight())
        height = 30
        if (self.visual is not None):
            d.remove(self.visual)
            d.remove(self.label)

        self.visual = Rectangle(0, y, d.getWidth(), y + height, self.color, True)
        d.add(self.visual)                                 # add it to display
        
        label1 = Label(midi_number_to_string(int(self.currentPitch)))
        label1.setBackgroundColor(Color.BLACK)    
        label1.setForegroundColor(Color.WHITE)
        self.label = label1
        OFFSET = 7
        d.add(self.label, d.getWidth() / 2, y + OFFSET)
        self.visual.onMouseClick(self.remove_active_note)  # ability to mute note by clicking on it


    '''
    Play new pitch and draw
    '''
    def play_new_pitch(self, pitch, volume):
        if (pitch != self.currentPitch):
            self.stop_playing()
            Play.noteOn(pitch, volume, self.channel)      # Play new note
            self.currentPitch = pitch
            self.draw_pitch()
           
    def lowest_pitch(self):
        return self.pitches[0]
    
    def highest_pitch(self):
        return self.pitches[-1]
    

##### create main display #####
d = Display("Phone Music", 1200, 760) 

def change_bg_color():
    pitch_range = HIGHEST_PITCH_REPRESENTED - LOWEST_PITCH_REPRESENTED
    midi_p1 = int(midi_number_to_note_num(v1.currentPitch))
    midi_p2 = int(midi_number_to_note_num(v2.currentPitch))
    midi_p3 = int(midi_number_to_note_num(v3.currentPitch))

    low_color = supported_colors[midi_p1]
    high_color = supported_colors[midi_p2]

    cg = colorGradient(low_color, high_color, pitch_range / 2) + colorGradient(high_color, Color.WHITE, pitch_range / 2) + [Color.WHITE]
    d.setColor(cg[midi_p3])

def play(v):
    global horizAmount, d, SCALE
    # map device pitch to note pitch
    # pitch = mapScale(horizAmount, 0, 1.0, v.lowest_pitch(), v.highest_pitch(), SCALE)
    pitch = closestPitch(horizAmount, v)
    percentage = horizAmount
    volume = 127
    
    v.play_new_pitch(pitch, volume)
    change_bg_color()

def detect_horizontal_bass(message):
    """Sets global variable 'horizAmount' from OSC message and plays the note."""
        
    global horizAmount, v1
    args = message.getArguments()  # get OSC message's arguments
    horizAmount = args[0]
    play(v1)

def detect_horizontal_tenor(message):
    """Sets global variable 'horizAmount' from OSC message and plays the note."""

    global horizAmount, v2
    args = message.getArguments()  # get OSC message's arguments
    horizAmount = args[0]
    play(v2)

def detect_horizontal_alto(message):
    """Sets global variable 'horizAmount' from OSC message and plays the note."""
    
    global horizAmount, v3        
    args = message.getArguments()  # get OSC message's arguments
    horizAmount = args[0]
    play(v3)

# Seperate file: hard mode with no mapping
LOWEST_PITCH_REPRESENTED = 36 - 2 # 2 below C2
HIGHEST_PITCH_REPRESENTED = 84

BASS_PITCHES     = [G2,   A2,   B2]
TENOR_PITCHES    = [E3,   A3,   B3]
ALTO_PITCHES     = [CS4,  D4,   DS4]

v1 = Voice("BASS", BASS_PITCHES, CHOIR_AHHS, 0, Color.BLACK)
v2 = Voice("TENOR", TENOR_PITCHES, CHOIR_AHHS, 1, Color.BLACK)
v3 = Voice("ALTO", ALTO_PITCHES, CHOIR_AHHS, 2, Color.BLACK)

'''
HACK
I'm not proud of any of this dropdown stuff but it works. Jython limits GUI callbacks to just one function name...
So as a result...we get this
'''
def bass_selected_note_low(s):
    BASS_PITCHES[0] = string_to_midi_number(s)
    
def bass_selected_note_middle(s):
    BASS_PITCHES[1] = string_to_midi_number(s)

def bass_selected_note_high(s):
    BASS_PITCHES[2] = string_to_midi_number(s)

def tenor_selected_note_low(s):
    TENOR_PITCHES[0] = string_to_midi_number(s)
    
def tenor_selected_note_middle(s):
    TENOR_PITCHES[1] = string_to_midi_number(s)

def tenor_selected_note_high(s):
    TENOR_PITCHES[2] = string_to_midi_number(s)
    
def alto_selected_note_low(s):
    ALTO_PITCHES[0] = string_to_midi_number(s)
    
def alto_selected_note_middle(s):
    ALTO_PITCHES[1] = string_to_midi_number(s)

def alto_selected_note_high(s):
    ALTO_PITCHES[2] = string_to_midi_number(s)

def show_dropdowns():
    all_notes = []
    num_octaves = 4 # between 2 and 6
    offsetX = 75 
    offsetY = 50
    labelOffsetY = 4
    for octave in range(num_octaves):
        for note in notes:
            all_notes.append(note + str(octave + 2))

    bass_label = Label("Bass:")
    bass_label.setPosition(12, labelOffsetY)
    d.add(bass_label)
    xPos = offsetX
    localX = 0
    bass_funcs = [bass_selected_note_low, bass_selected_note_middle, bass_selected_note_high]
    for i in range(len(BASS_PITCHES)):
        ddl_bass = DropDownList(all_notes, bass_funcs[i])
        localX = i * offsetX + (offsetX - 30)
        d.add(ddl_bass, localX, offsetY * 0)
        xPos = localX # Keep track of how far we are
    
    tenor_label = Label("Tenor:")
    new_x = xPos + offsetX + 5 + labelOffsetY
    tenor_label.setPosition(new_x + labelOffsetY, labelOffsetY)
    d.add(tenor_label)
    tenor_funcs = [tenor_selected_note_low, tenor_selected_note_middle, tenor_selected_note_high]
    new_x += offsetX
    for i in range(len(TENOR_PITCHES)):
        ddl_tenor = DropDownList(all_notes, tenor_funcs[i])
        localX = i * offsetX + new_x - (offsetX - 45)
        d.add(ddl_tenor, localX, offsetY * 0)
        xPos = localX
        
    new_x = (xPos + offsetX * 2) + labelOffsetY
    alto_label = Label("Alto:")
    alto_label.setPosition(new_x - offsetX + 13, labelOffsetY)
    d.add(alto_label)
    alto_funcs = [alto_selected_note_low, alto_selected_note_middle, alto_selected_note_high]
    for i in range(len(ALTO_PITCHES)):
        ddl_alto = DropDownList(all_notes, alto_funcs[i])
        localX = i * offsetX + new_x - (offsetX - 45)
        d.add(ddl_alto, localX, offsetY * 0)
    
menu = Menu('Tools')
menu.addItem('Change Pitche Ranges', show_dropdowns)
d.addMenu(menu)

##### establish connection to input OSC device (an OSC client) #####
oscInBass = OscIn(BASS_PORT)    # get input from OSC devices on port n    
oscInTenor = OscIn(TENOR_PORT)    # get input from OSC devices on port n + 1
oscInAlto = OscIn(ALTO_PORT)    # get input from OSC devices on port n + 2

# associate callback functions with OSC message addresses
oscInBass.onInput("/hfosc/horizontalmotion", detect_horizontal_bass) 
oscInTenor.onInput("/hfosc/horizontalmotion", detect_horizontal_tenor)
oscInAlto.onInput("/hfosc/horizontalmotion", detect_horizontal_alto) 
