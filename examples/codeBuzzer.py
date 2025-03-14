import board
import simpleio

# Define pin connected to piezo buzzer. This is fixed on the board
PIEZO_PIN = board.GP21

# Define a list of tones/music notes to play.
TONE_FREQ = [ 262,  # C4
              294,  # D4
              330,  # E4
              349,  # F4
              392,  # G4
              440,  # A4
              494 ] # B4

# Play tones going from start to end of list.
for i in range(len(TONE_FREQ)):
    simpleio.tone(PIEZO_PIN, TONE_FREQ[i], duration=0.5)
