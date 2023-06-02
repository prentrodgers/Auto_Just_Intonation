import sys
sys.path.insert(0, '../Diamond_Music') # you must have already obtained the Diamond_Music repo from github and put it in the right dir.
import diamond_music_utils as dmu
import numpy as np
from fractions import Fraction
rng = np.random.default_rng()
from functools import cache
import os
import muspy
from mido import MidiFile
import music21 as m21
import logging
from itertools import count, combinations, permutations

def set_accidentals(flats):
    if flats: 
        keys = np.array(['C♮', 'D♭', 'D♮', 'E♭', 'E♮', 'F♮', 'G♭', 'G♮', 'A♭', 'A♮', 'B♭', 'B♮'])
    else: keys = np.array(['C♮', 'C♯', 'D♮', 'D♯', 'E♮', 'F♮', 'F♯', 'G♮', 'G♯', 'A♮', 'A♯', 'B♮'])
    return keys

def init_voice_time():
      voice_time = {                                                             # "time_tracker_number" is reset at the end of the function to consecutive numbers 0-n
            "fing1": {"full_name": "finger piano 1", "start": 0, "csound_voice": 1,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 2, "max_oct": 7},
            "fing2": {"full_name": "finger piano 2", "start": 0, "csound_voice": 1,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 2, "max_oct": 7},
            "fing3": {"full_name": "finger piano 3", "start": 0, "csound_voice": 1,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 2, "max_oct": 7},
            "bfin1": {"full_name": "bass finger piano 1", "start": 0, "csound_voice": 24,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 1, "max_oct": 5},
            "fing4": {"full_name": "finger piano 4", "start": 0, "csound_voice": 1,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 2, "max_oct": 7},
            "fing5": {"full_name": "finger piano 5", "start": 0, "csound_voice": 1,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 2, "max_oct": 7},
            "fing6": {"full_name": "finger piano 6", "start": 0, "csound_voice": 1,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 2, "max_oct": 7},
            "bfin2": {"full_name": "bass finger piano 2", "start": 0, "csound_voice": 24,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 1, "max_oct": 5},

            "vlip1": {"full_name": "violin pizzicato1", "start": 0, "csound_voice": 2,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 3, "max_oct": 6},
            "vlip2": {"full_name": "violin pizzicato2", "start": 0, "csound_voice": 2,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 3, "max_oct": 6},
            "vlap1": {"full_name": "viola pizzicato1", "start": 0, "csound_voice": 3,"time_tracker_number": 0,  "volume_factor": 1, "min_oct":  2, "max_oct": 5},
            "celp1": {"full_name": "cello pizzicato1", "start": 0, "csound_voice": 4,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 1, "max_oct": 5},
            "vlip3": {"full_name": "violin pizzicato1", "start": 0, "csound_voice": 2,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 3, "max_oct": 6},
            "vlip4": {"full_name": "violin pizzicato2", "start": 0, "csound_voice": 2,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 3, "max_oct": 6},
            "vlap2": {"full_name": "viola pizzicato1", "start": 0, "csound_voice": 3,"time_tracker_number": 0,  "volume_factor": 1, "min_oct":  2, "max_oct": 5},
            "celp2": {"full_name": "cello pizzicato1", "start": 0, "csound_voice": 4,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 1, "max_oct": 5},

            "mari1": {"full_name": "marimba1", "start": 0, "csound_voice": 5,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 9},
            "xylp1": {"full_name": "xylophone1", "start": 0, "csound_voice": 6,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 9},
            "vibp1": {"full_name": "vibraphone1", "start": 0, "csound_voice": 7,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 3, "max_oct": 9},
            "harp1": {"full_name": "harp1", "start": 0, "csound_voice": 8,"time_tracker_number": 0,  "volume_factor": 2, "min_oct": 2, "max_oct": 9},

            "bgui1": {"full_name": "baritone guitar1", "start": 0, "csound_voice": 20,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 1, "max_oct": 6},
            "ebss1": {"full_name": "Ernie Ball Super Slinky1", "start": 0, "csound_voice": 21,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 6},
            "long1": {"full_name": "long string1", "start": 0, "csound_voice": 22,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 1, "max_oct": 6},
            "stri1": {"full_name": "original string1", "start": 0, "csound_voice": 23,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 1, "max_oct": 6},

            "vlim1": {"full_name": "violin martele1", "start": 0, "csound_voice": 9,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 6},
            "vlim2": {"full_name": "violin martele2", "start": 0, "csound_voice": 9,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 6},
            "vlim3": {"full_name": "violin martele3", "start": 0, "csound_voice": 9,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 6},
            "vlim4": {"full_name": "violin martele4", "start": 0, "csound_voice": 9,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 6},
            "vlam1": {"full_name": "viola martele1", "start": 0, "csound_voice": 10,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 5},
            "vlam2": {"full_name": "viola martele2", "start": 0, "csound_voice": 10,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 2, "max_oct": 5},
            "celm1": {"full_name": "cello martele1", "start": 0, "csound_voice": 11,"time_tracker_number": -1,  "volume_factor": 0, "min_oct": 2, "max_oct": 5},
            "celm2": {"full_name": "cello martele2", "start": 0, "csound_voice": 11,"time_tracker_number": -1,  "volume_factor": 0, "min_oct": 2, "max_oct": 5},

            "clar1": {"full_name": "clarinet1", "start": 0, "csound_voice": 13,"time_tracker_number": 0,  "volume_factor": -1, "min_oct": 3, "max_oct": 6},
            "clar2": {"full_name": "clarinet2", "start": 0, "csound_voice": 13,"time_tracker_number": 0,  "volume_factor": -1, "min_oct": 3, "max_oct": 6},
            "flut1": {"full_name": "flute1", "start": 0, "csound_voice": 14,"time_tracker_number": 0,  "volume_factor": 2, "min_oct": 3, "max_oct": 6},
            "flut2": {"full_name": "flute2", "start": 0, "csound_voice": 14,"time_tracker_number": 0,  "volume_factor": 2, "min_oct": 3, "max_oct": 6},
            "oboe1": {"full_name": "oboe1", "start": 0, "csound_voice": 15,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 6},
            "oboe2": {"full_name": "oboe2", "start": 0, "csound_voice": 15,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 6},
            "frnh1": {"full_name": "french horn1", "start": 0, "csound_voice": 16,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 1, "max_oct": 5},
            "frnh2": {"full_name": "french horn2", "start": 0, "csound_voice": 16,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 1, "max_oct": 5},
            "basn1": {"full_name": "bassoon1", "start": 0, "csound_voice": 12,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 1, "max_oct": 6},
            "basn2": {"full_name": "bassoon2", "start": 0, "csound_voice": 12,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 1, "max_oct": 6},
            
            "vliv1": {"full_name": "violin with vib1", "start": 0, "csound_voice": 17,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 6},
            "vliv2": {"full_name": "violin with vib2", "start": 0, "csound_voice": 17,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 6},
            "vliv3": {"full_name": "violin with vib3", "start": 0, "csound_voice": 17,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 6},
            "vliv4": {"full_name": "violin with vib4", "start": 0, "csound_voice": 17,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 6},
            "vlav1": {"full_name": "viola with vib1", "start": 0, "csound_voice": 18,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 5},
            "vlav2": {"full_name": "viola with vib2", "start": 0, "csound_voice": 18,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 3, "max_oct": 5},
            "celv1": {"full_name": "cello with vib1", "start": 0, "csound_voice": 19,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 1, "max_oct": 5},
            "celv2": {"full_name": "cello with vib2", "start": 0, "csound_voice": 19,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 1, "max_oct": 5},

            "trmp1": {"full_name": "trumpet1", "start": 0, "csound_voice": 25,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 2, "max_oct": 6},
            "trmp2": {"full_name": "trumpet2", "start": 0, "csound_voice": 25,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 2, "max_oct": 6},
            "trmp3": {"full_name": "trumpet3", "start": 0, "csound_voice": 25,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 2, "max_oct": 6},
            "trmp4": {"full_name": "trumpet44", "start": 0, "csound_voice": 25,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 2, "max_oct": 6},
            "trmb1": {"full_name": "trombone1", "start": 0, "csound_voice": 26,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 1, "max_oct": 5},
            "trmb2": {"full_name": "trombone2", "start": 0, "csound_voice": 26,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 1, "max_oct": 5},
            "tuba1": {"full_name": "tuba1", "start": 0, "csound_voice": 27,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 1, "max_oct": 4},
            "tuba2": {"full_name": "tuba2", "start": 0, "csound_voice": 27,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 1, "max_oct": 4},
            }
      for inx, voice in zip(count(0,1), voice_time):
            # print(voice)
            voice_time[voice]["time_tracker_number"] = inx
      return (voice_time)

def find_root_mode(midi_file_name):
      keys = set_accidentals(False) # this use of keys is to search through the letters. It requires only the naturals and sharps
      # logging.debug(f'determining root & mode for: {file_name = }')
      s = m21.converter.parse(midi_file_name)
      fis = str(s.analyze('key'))
      # logging.debug(f'music21 says: {fis = }')
      key_name, mode = fis.split()
      # logging.debug(f'after split. {key_name = }, {mode = }')
      i = 0
      root = 9999
      for key in keys:
            letter_only = key[0]
            # logging.debug(f'{letter_only = }, {key_name = }')
            if letter_only.upper() == key_name.upper():
                  root = i
                  # logging.debug(f'found a match between music21 {letter_only = }, and {key = } as {root = }, {mode = }')
                  break
            i += 1
      if root == 9999: return (9999)
      return (root, mode, s)

def midi_to_music21(midi_file_name, chorale_number):
      root, mode, s = find_root_mode(midi_file_name)
      logging.debug(f'just back from find_root_mode. {root = }')
      # mid = MidiFile(os.path.join(midi_file_name))
      numpy_file = 'chorale' + str(chorale_number) + '.npy'
      chorale = np.load(numpy_file)
      # chorale = np.concatenate((chorale, np.zeros((4,1),dtype=int)),axis = 1) # add a bit at the end so you don't loose the ending
      logging.debug(f'{chorale_number = }, {root = }, {mode = }, {chorale.shape = }')
      return chorale, root, mode, s

# this is passed a muspy music object
def muspy_to_sample_root_mode(music):
    if music.key_signatures != []: # check if the midi file includes a *key signature* - some don't
        root = music.key_signatures[0].root 
        mode = music.key_signatures[0].mode # major or minor
    else: 
        logging.debug('Warning: no key signature found. Assuming C major')
        mode = "major"
        root = 0    
    if music.time_signatures != []: # check if the midi file includes a *time signature* - some don't
        numerator = music.time_signatures[0].numerator
        denominator = music.time_signatures[0].denominator 
    else: 
        logging.debug('Warning: no time signature found. Assuming 4/4')
        numerator = 4
        denominator = 4
    # turn it into a piano roll
    piano_roll = muspy.to_pianoroll_representation(music, encode_velocity=False)
    # boolean piano roll if False, default True, one-hot encoded notes
    # logging.debug(piano_roll.shape) # should be one time step for every click in the midi file
    q = music.resolution # quarter note value in this midi file. Default resolution is 24. 
    # This means each quarter note consumes 24 time slots. 1/8th note is 12, 1/16th note is 6. 
    # This implies that I could pick up every 6th note and get everything I need. Or compress the result by 6x. 
    q16 = q // 4 # 24 / 4 = 6 which equates to catching every 1/16th note
    print(f'time signatures: {numerator}/{denominator}')
    time_steps = int(np.ceil(piano_roll.shape[0] / q16))
    print(f'music.resolution: {q = }. {q16 = }, {time_steps = } 1/16th notes. {piano_roll.shape = }') # q = 24
    # piano_roll.shape = (1537, 128)
    decoded_piano_roll = np.argmax(piano_roll, axis = 1)
    print(f'{decoded_piano_roll.shape = }')
    pit_cl_ent = muspy.pitch_class_entropy(music)
    pcu = muspy.n_pitch_classes_used(music)    
    # This loop is able to load an array of shape N,4 with the notes that are being played in each time step
    sample = np.zeros(shape=(time_steps, 4), dtype = int) # typical chorale has 257 time_steps. Lasso has more.   
    print(f'{piano_roll.shape = }, {pit_cl_ent = }, {pcu = }, {sample.shape = }')
    for click in np.arange(0, piano_roll.shape[0], q16): # send every 6th note in the piano roll to be processed
        time_interval = click // q16
        voice = 3 # assign the first to the low voices and decrement voice for the higher voices
        for inx in np.arange(piano_roll.shape[1]): # 128 check if any notes are non-zero, that will be the one-hot item
              if (piano_roll[click][inx]): # if velocity anything but zero - unless you set encode_velocity = False
                    sample[time_interval][voice] = inx # IndexError: index 1438 is out of bounds for axis 0 with size 1438 which is the time_interval
                    voice -= 1 # next instrument will get the higher note
    print(f'{sample.shape = }') # (257, 4)
    if np.sum(sample[-1:] == 0):
          sample = sample[0:-1,:]
          print(f'{sample.shape = }') # (256, 4)
    if np.sum(sample[-1:] == 0):
          sample = sample[0:-1,:]
          print(f'{sample.shape = }') # (256, 4)
    return (sample, root, mode, pit_cl_ent, pcu)     

def read_from_corpus(work):
      s = m21.corpus.parse(work) # use music21 to pull a chorale from the corpus. For example Herzliebster is 'bwv244.3'
      # then immediately convert it to a muspy object. 
      muspy_object = muspy.from_music21(s)
      logging.debug(f'{muspy_object = }')
      sample, root, mode, pit_cl_ent, pcu = muspy_to_sample_root_mode(muspy_object)
      logging.debug(f'{sample.shape = }, {root = }, {mode = }, {round(pit_cl_ent,2) = }, {pcu = }')
      chorale = sample.T
      logging.debug(f'{chorale.shape = }')
      return chorale, root, mode, s


def read_from_numpy(chorale_number):
      file_name = 'sample' + str(chorale_number) + '.mid' # pull from the set of synthetic chorales
      chorale, root, mode, s = midi_to_music21(file_name, chorale_number)
      return chorale, root, mode, s

def _find_limit(ratio_string):
        if len(ratio_string) == 1: # Fraction returns a '1' for the ratio 1/1. All other Fraction ops return a ratio
            den = ratio_string
            num = '1'
        else:
            num, den = ratio_string.split('/')
        max_num_den = int(num) + int(den)
      #   max_num_den = np.max((int(num), int(den))) # I originally just used either the num or den, they switched to sum
        return max_num_den # int(num), int(den) 

def build_tonal_diamond(limit_value):
    tonal_diamond_ratios = np.array(dmu.build_all_ratios(limit_value = limit_value)) # assemble an array floating point ratios to the 31 limit # limit_value = limit_value
    tonal_diamond_ratios = np.append(tonal_diamond_ratios, [2.0], axis=0)
    tonal_diamond_ratios = np.unique(tonal_diamond_ratios, axis = 0) # reduce from 256 to a sorted list of 213 values
    
    # you now have a list of all the ratios in the tonality diamond to the 31 limit 
    # convert the ratios to cents. 
    tonal_diamond_cents = np.array([int(round(dmu.ratio_to_cents(just_ratio),0)) for just_ratio in tonal_diamond_ratios])
    # You now have a list of cent values that are within the tonality diamond to the 31 limit
    # assemble a list of numerators and denominators for all of the values in the ratio and cent arrays
    tonal_diamond_num_den = np.array([_find_limit(str(Fraction(just_ratio).limit_denominator(50))) for just_ratio in tonal_diamond_ratios])
    # this array will enable you to score based on the numerators and denominators of the ratios to the 31 limit
    # Each array has 256 values
    tonal_diamond_values = np.array([(ratio, cents, num_dem) for ratio, cents, num_dem in zip(tonal_diamond_ratios, tonal_diamond_cents, tonal_diamond_num_den)])
    logging.debug(f'{[var.shape for var in [tonal_diamond_ratios, tonal_diamond_cents, tonal_diamond_num_den, tonal_diamond_values]]}') # [(256,), (256,), (256, 2)]
    # from now on, the arrays are sorted, so you can use np.searchsorted to find where the desired value would go if it existed. 
    logging.debug(f'{tonal_diamond_values.shape = }')
    return tonal_diamond_values

stringify = lambda x: '1/1' if x == 1 else str(Fraction(x).limit_denominator(50))

# when provided with a 4 note chord in midi_numbers (0-127) this function returns the steps in cents (1200 EDO)
# I started off just assigning cent values based on the 12TET cent values. But I wanted to try assigning typical just values to the notes to see if that would improve the interval selection.
def note_to_1200_edo(midi_numbers, original_12 = np.arange(0, 1200, 100)):
      # Convert a midi_number value of zero to -1. 0 indicates no number in this midi time_step format.
      if np.sum(midi_numbers) == 0: # watch out for a chord of all zeros. That's not right.
            logging.debug(f'{midi_numbers = }')
            return np.zeros(4, dtype = int)
      # convert all the midi_numbers to steps in cents unless 0
      #     original_12 = np.array([note * 100 for note in initial_12_cent_values])
      ifzero = lambda num: -1 if num == 0 else original_12[num % 12] # do I still need this? Yes because otherwise you end up with zeros in notes.
      step_in_1200_edo = np.array([ifzero(note) for note in midi_numbers]) # execute the lambda function in a list comprehension
      # at this point you have converted the notes with zero values to another note value in the chord, so it won't influence the inteval calculations.
      return step_in_1200_edo

def limit_format(values):
      ratio = values[0]
      cents = values[1]
      num_dem = values[2]
      return stringify(ratio), int(round(cents)), int(num_dem)

# This function is passed a 1 to 4 note chord in 1200 edo (cents), and returns the score.
# The score is calculated by examining the cent distance between each note and every other note in the chord. 6 compares.
# When it finds the ratio distance of an interval in tonal_diamond_values, it then sums the numerator and denominator of the ratio distance and returns the sum of the two as a score for that interval. 
# I'm still not certain if I should return the max of numerator and denominator or the product of the same. The latter will make the score difference much more pronounced.
# It sums the results of those six compares.
# what if the distance ratio is not found. With all the rounding I'm doing, it's sometimes has a mismatch. 
# @cache Can't cache numpy arrays, only hashable types like tuples. TypeError: unhashable type: 'numpy.ndarray'
def score_chord_cents(chord_1200, tonal_diamond_values, ratio_factor = 1):
      score = 0
      logging.debug(f'in score_chord_cents')
      for notes in combinations(chord_1200, 2):
      # for inx1 in np.arange(chord_1200.shape[0] - 1): # compare this note with all the others
            # for inx2 in np.arange(inx1 + 1, chord_1200.shape[0]): # compare this note with all the others
            distance = abs(notes[0] - notes[1])
            # need to search for this distance in the tonal_diamond_cents array
            logging.debug(f'{notes = }, {distance = }')
            found = False
            index_to_limits = 0
            if distance > 0:
                  for gap in np.array([0, -1, 1]): # it checks the distance plus or minus one cent
                        logging.debug(f'checking near distances. {gap = }')
                        index_to_limits = np.searchsorted(tonal_diamond_values[:,1], distance + gap)
                        logging.debug(f'{index_to_limits = }, {distance + gap = }') # gap = 0, distance = 316, index = 56
                        if index_to_limits > tonal_diamond_values.shape[0]:
                              logging.debug(f'{index_to_limits = }, should not exceed {tonal_diamond_values.shape = }')
                        if tonal_diamond_values[index_to_limits, 1] == distance + gap: # example: 316 is in the table
                              found = True
                              logging.debug(f'found a cent in the table. {limit_format(tonal_diamond_values[index_to_limits])}')
                              break
                  if not found:
                        score += 1000 # this is a stopgap remedy to prevent moving a note. 
                  # logging.debug(f'{tonal_diamond_values[index_to_limits,2] = }')
                  score += ratio_factor * tonal_diamond_values[index_to_limits, 2] # 2 is max of num_den
      logging.debug(f'in score_chord_cents. {round(score / ratio_factor,0) = }')
      return round(score / ratio_factor,1)

# this function takes in a 4-note chord in cents and returns a optimized chord also in cents
# it picks the best choice for the six intervals in a 4-note chord, optimized by low integer ratios and distance from original.
# this function takes in a 4-note chord in cents and returns a optimized chord also in cents
# it picks the best choice for the six intervals in a 4-note chord, optimized by low integer ratios and distance from original.
def find_intervals(initial_chord, tonal_diamond_values, dist_factor = 1.0, ratio_factor = 1.0, range = 6):
      # this function does not use ratio_factor, except to pass it on to the score_chord_cents function.
      # saved_cent_moves = np.empty(0, dtype = int)
      already_changed = np.array([False, False, False, False]) # keep track of any changes made to each note in the chord
      # this could be 
      """
      for inx, chord in zip(count(0,1), combinations(initial_chord,2)): # take each interval of the 6 intervals one at a time consisting of a pair of notes. Pick the best for that interval.
      # I tried to use that construction, but since it doesn't allow me to change the initial chord values I had to revert to the old way.
      """
      # what could I do to reorder the interval selection?
      order_of_compares = np.array([[0,1], [1,2], [2,3], [3,0], [0,2], [0,3], [1,3], [1,0], [2,0], [3,1], [2,1], [3,2]])
      # order_of_compares = np.array([[0,1], [1,2], [2,3], [3,0], [0,2], [0,3]])
      for inx1, inx2 in order_of_compares:
      # for inx1 in np.arange(initial_chord.shape[0] - 1): # 0, 1, 2
      #       for inx2 in np.arange(inx1 + 1, initial_chord.shape[0]): # 1, 2, 3
                  first = initial_chord[inx1]
                  sec = initial_chord[inx2]
                  logging.debug(f'{inx1 = }, {inx2 = }, {first = }, {sec = }')
                  distance = abs(first - sec) # distance in cents from one note to the another
                  if first < sec: 
                       cent_moves = 1
                  else:
                       cent_moves = -1

                  logging.debug(f'from {first = } to {sec = }: {distance = }')
                  if distance == 0:
                        break
                  # this returns the indexes into tonal_diamond_values for those cent values in the range less or more than the range
                  initial_ratio_index = np.searchsorted(tonal_diamond_values[:,1], distance)
                  logging.debug(f'{initial_ratio_index = }')
                  indeciis_to_tonal_diamond =  np.arange(initial_ratio_index - range, initial_ratio_index + range, 1) # pick cent values from ratios higher and lower than the initial 
                  indeciis_to_tonal_diamond = np.array([inx for inx in indeciis_to_tonal_diamond if inx < tonal_diamond_values.shape[0] and inx >= 0])
                  logging.debug(f'{indeciis_to_tonal_diamond.shape = } ratios to evaluate: {indeciis_to_tonal_diamond}')       
                  logging.debug(f'{[(inx, limit_format(tonal_diamond_values[inx])) for inx in indeciis_to_tonal_diamond]}')
                  # choose the ratio that provides a cent value that is close to the interval cent value, which may be 12TET or may have drifted from 12TET. 
                  # should it include the ratio_factor? yes, because you would like it to influence the choice of ratios.
                  # best_choice_overall = np.argmin(abs(tonal_diamond_values[indeciis_to_tonal_diamond,1] - distance) * dist_factor + tonal_diamond_values[indeciis_to_tonal_diamond,2])
                  best_choice_overall = np.argmin(abs(tonal_diamond_values[indeciis_to_tonal_diamond,1] - distance) * dist_factor + tonal_diamond_values[indeciis_to_tonal_diamond,2] * ratio_factor) % 1200
                  # logging.debug(f'% 1200. {best_choice_overall = }')
                  cent_deviation = abs(distance - tonal_diamond_values[indeciis_to_tonal_diamond[best_choice_overall], 1])
                  logging.debug(f'Optimizer: {limit_format(tonal_diamond_values[indeciis_to_tonal_diamond[best_choice_overall]])}, {cent_deviation = }')
                  if tonal_diamond_values[indeciis_to_tonal_diamond[best_choice_overall], 1] == distance: # if the new value will not change don't do it
                        logging.debug(f'in find_intervals. no change needed to  {initial_chord[inx2] = }. already at the desired cent value')
                  else: # you might want to change the second note in the interval if it makes the chord score lower
                        if already_changed[inx2]:
                              logging.debug(f'Already changed {inx1} to {inx2}')
                              # you have already changed this chord note once. Evaluate if you should change it again.
                              prev_score = score_chord_cents(initial_chord, tonal_diamond_values, ratio_factor = ratio_factor) # before the second change to this note
                              logging.debug(f'score for the chord before changing {initial_chord = }: score = {prev_score}')
                              prev_chosen_note = initial_chord[inx2] # save what it used to be
                              new_note = (initial_chord[inx1] + cent_moves * tonal_diamond_values[indeciis_to_tonal_diamond[best_choice_overall], 1]) % 1200 
                              logging.debug(f'proposed {new_note = }')
                              initial_chord[inx2] = new_note # stick the new one into the array temporarily 
                              new_score = score_chord_cents(initial_chord, tonal_diamond_values, ratio_factor = ratio_factor)
                              logging.debug(f'score for the chord after making a change to {initial_chord = }: score = {new_score}')
                              if new_score > prev_score:
                                    logging.debug(f'{new_score = } is higher than the {prev_score = }. undoing the change ')
                                    initial_chord[inx2] = prev_chosen_note
                        else: # not already_changed[inx2] go ahead and make the change. It can be overriden later if a better choice is found.
                              initial_chord[inx2] = (initial_chord[inx1] + cent_moves * tonal_diamond_values[indeciis_to_tonal_diamond[best_choice_overall], 1]) % 1200
                              logging.debug(f'First change to {inx2}: {initial_chord = }')
                        already_changed[inx2] = True
                  logging.debug(f'new {inx2 = }, {initial_chord = }')
      return initial_chord 
      

def try_permutations(initial_chord, tonal_diamond_values, ratio_factor = 1, dist_factor = 1,  max_score = 70, original_12 = np.arange(0, 1200, 100)):
      logging.debug(f'in try_permutations.')
      chord_in_1200 = np.array(note_to_1200_edo(initial_chord, original_12))
      logging.debug(f'{chord_in_1200 = }')
      best_choice = chord_in_1200
      best_score = 99_999
      for inx, initial_chord in zip(count(0,1),np.array(list(permutations(chord_in_1200.reshape(4,))))):
            if inx in np.array([0, 18, 16, 9]): # skip the ones that were already checked in improve_chord_rolls
                 logging.debug(f'skipping {inx = }, already checked')
            else:
                  logging.debug(f'permutation: {inx}. start here {initial_chord = }, midi numbers: {[int(round(note / 100,0)) for note in initial_chord]}')
                  # find_intervals expects one 4-note chord in cents
                  result = find_intervals(initial_chord, tonal_diamond_values, ratio_factor = ratio_factor, dist_factor = dist_factor) 
                  score = score_chord_cents(result, tonal_diamond_values, ratio_factor = ratio_factor)
                  if score < best_score:
                        best_choice = result
                        best_score = score
                  if best_score <= max_score: 
                        logging.debug(f'found good enough {score = }, after {inx = } permutations as directed by {max_score = }')
                        break
                  logging.debug(f'permutations results_so_far: {result = }, {score = }')
      # this is redundant. I should just return the best_choice and best_score
      logging.debug(f'after permutations. starting {chord_in_1200 = }, ending {best_choice = }, {best_score = }')
      # I decided not to rearange to optimize voicing in this function, but to do it in transpose_top_notes
      # best_choice_12 = np.array([round(note / 100,0) % 12 for note in best_choice])
      # chord_in_12 = np.array([round(note / 100,0) % 12 for note in chord_in_1200])
      # best_voicing = np.argmin(np.array([sum(np.array(abs(chord_in_12 -  voicing))) for voicing in np.array(list(permutations(best_choice_12)))]))
      # final_result = np.array(list(permutations(best_choice)))[best_voicing]
      # logging.debug(f'in try_permutations. after rearranging. {best_score = }, {final_result = }')
      return best_choice, best_score


def transpose_top_notes(final_result, top_notes, chord_number, score, midi_notes):
      # This function is presented with a tuned chord, and an array of top_notes with (12TET value, cent value)
      # the goal of the function is to strive to move the chord so that the highest priority top_notes appear at the requested cent value.
      # It starts by finding notes in the chord that are also in the top_notes, and then
      # assembles an array if distances between the final_result cents and the desired top_notes cents.
      # If one of the notes is not in the top_notes 12TET list, we don't do anything with it.
      # but I plan to include all 12 in the future, with the idea to only transpose to meet the first top_notes in the list.
      # 
      logging.debug(f'in transpose_top_notes. before rearranging. {score = }, {final_result = }')
      best_choice_12 = np.array([round(note / 100,0) % 12 for note in final_result]) # find the 12TET scale equivalent of final_result
      chord_in_12 = midi_notes % 12 # find the 12TET scale equivalent of the original midi chord
      best_voicing = np.argmin(np.array([sum(np.array(abs(chord_in_12 -  voicing))) for voicing in np.array(list(permutations(best_choice_12)))]))
      final_result = np.array(list(permutations(final_result)))[best_voicing]
      best_choice_12 = np.array([round(note / 100,0) % 12 for note in final_result]) # find the new locations for 12TET scale 
      logging.debug(f'in transpose_top_notes. after rearranging. {score = }, {final_result = }')
      for top_note, top_cent in top_notes.T: # step through the top_notes until you find one to transpose
            logging.debug(f'Checking {top_cent = }, {top_note = } to determine if transposition is advised')
            if top_note in best_choice_12: # you found one of the top_notes in the chord. 
                  logging.debug(f'{top_note = } is in {best_choice_12 = }')
                  found = np.where(best_choice_12 == top_note, 1, 0) # where is this top_note midi value in the chord? Stick a 1 where found
                  logging.debug(f'located {top_note} in {best_choice_12} at locations: {found}')
                  if found.any() > 0: # found at least one match between the midi_note values in the chord and the top_notes
                        logging.debug(f'at least one note in final_result was in top_notes {final_result[np.nonzero(found)] = }')
                        if final_result[np.nonzero(found)][0] == top_cent:  # if the cent value in the chord and in top_notes is the same
                              logging.debug(f'{top_cent = } is right where it belongs. first come, first served. Bail.')
                        else:
                              expected_value = top_cent
                              if expected_value == 0 and final_result[np.nonzero(found)][0] > 1150: expected_value = 1200
                              gap = expected_value - final_result[np.nonzero(found)][0]
                              # check to see if making this change would change the original the midi_note to another midi_note. 
                              # if so, don't do it.
                              logging.debug(f'check to ensure this gap will not change the midi_note value. {gap = }')
                              f_12 = np.array([int(round(note / 100, 0)) % 12 for note in final_result + gap])
                              m_12 = midi_notes % 12
                              if np.array_equal(f_12, m_12):
                                    final_result = final_result + gap
                                    logging.debug(f'made a transposition to the chord. {gap = } {final_result = } ')
                                    break
                              else: logging.debug(f'arrays not equal. Do not transpose: {f_12} ne {m_12}')
                              
      final_result = final_result % 1200
      logging.debug(f'after transposition: {chord_number = }, {final_result = }, {score = }')
      # here is where I should do the rearrangement of the chord to find the best voicing. But I need the original midi chord to do that.
     
      return final_result

# this function takes in a midi 4 note chord and returns the best tuned chord it could find in cents
# It is only called if the score is really bad. The roll takes care of the majority.
def improve_chord_rolls(initial_chord, top_notes, chord_number, tonal_diamond_values, \
            roll = 4, dist_factor = .2, ratio_factor = .2, stop_when = 25, \
            flats = True, min_score_perm = 100, original_12 = np.arange(0, 1200, 100)):
      # this uses the variable stop_when to end the rolls looking for a better score
      if roll == 0: roll = 1
      chord_in_1200 = np.array(note_to_1200_edo(initial_chord, original_12)) # assign an initial 1200 edo step to each midi note
      keys = set_accidentals(flats)
      logging.debug(f'{chord_number = }, {initial_chord = }, {keys[initial_chord % 12]}')
      score = 99_999
      best_score = 99_999
      best_choice = chord_in_1200
      for inx in np.arange(roll):
            result = find_intervals(np.roll(best_choice,inx), tonal_diamond_values, ratio_factor = ratio_factor, dist_factor = dist_factor) 
            score = score_chord_cents(result, tonal_diamond_values, ratio_factor = ratio_factor)
            if score < best_score:
                  best_choice = result
                  best_score = score
            if best_score < stop_when: 
                  logging.debug(f'found good score {score = }, after {inx = } rolls as directed by {stop_when = }')
                  break
            logging.debug(f'rolls results_so_far: {result = }, {score = }')
      logging.debug(f'after rolls, before rearranging. original chord: {chord_in_1200}, rolls {best_choice = }')
      # 4/25/23 Changed this routine to a roll instead of permutation. Roll is sufficient for checking tuning and transposition for most chords. If the score is above 500, or even better 100, use the permutation method. It's been scrubbed of checking the same arrangements as roll does.
      if best_score > min_score_perm:
            logging.debug(f'results_so_far: {best_score = }, > {min_score_perm = }. Not good enough. call try permutations with {initial_chord = }')
            final_result, best_score = try_permutations(initial_chord, tonal_diamond_values, max_score = 70, original_12 = original_12) # this is a permutation, not a roll. It's slower, but more thorough. It also does the rearanging. No need to do it again.
      else: # your score is below min_score_perm, so you can allow the current cent values.
            # rounded_best_choice_12 = np.array([int(round(note / 100,0)) % 12 for note in best_choice]) # what the algorithm thinks is the best cent values for the notes in the chord
            # rounded_chord_in_1200 =  np.array([int(round(note / 100,0)) % 12 for note in chord_in_1200]) # what the initial chord looked like before optimizing. Make sure the final result is in the same order as the original chord.
            # logging.debug(f'original chord: {chord_in_1200}, Optimized chord: {best_choice}')
            # logging.debug(f'rounded to 12T: {rounded_best_choice_12 = }, {rounded_chord_in_1200 =}')
            # sum_of_rolls = [[abs(val1 - val2) for val1, val2 in zip(np.roll(rounded_best_choice_12, inx), rounded_chord_in_1200)] for inx in np.arange(4)]
            # sum_of_sums = [sum(values) for values in sum_of_rolls]
            # logging.debug(f'{sum_of_sums = }')
            # final_result = np.roll(best_choice,np.argmin(sum_of_sums))
            final_result = best_choice
      logging.debug(f'after rolling and permutations. {best_score = }, {final_result = }')
      final_result = transpose_top_notes(final_result, top_notes, chord_number, best_score, initial_chord)  # transpose to keep the top notes stable over chord changes
      final_result = final_result % 1200
      logging.debug(f'{chord_number}, improve_chord_rolls after adjustment. {final_result = }')
      return final_result, best_score

# This function clips all the notes in the notes_features_15 array to the min and max octaves and volumes for the voice
def clip_note_features(notes_features_15, voice_time): # start here
      for inx in np.arange(notes_features_15.shape[0]): # how many notes with 15 features are in the input stream?
            short_name, _ = dmu.show_voice_time_short_name(notes_features_15[inx,[6]], voice_time) # returns short_name, csound_voice_number. Discard the latter value.
            logging.debug(f'{inx = }, {short_name = }\n{[round(feature,0) for feature in notes_features_15[inx,[6,4,5,14]]]}') # [[6, 4, 5, 14]] voice, note, octave, volume  array([[ 0., 86.,  5.,  7.],
            logging.debug(f'{voice_time[short_name]["min_oct"] = }, {voice_time[short_name]["max_oct"] = }, {voice_time[short_name]["volume_factor"] = }') # clipping octave volume information
            note_cents = notes_features_15[inx,4] # at some point I'll clip the octave if it's at the max and the note_cents is greater than 300 cents.
            logging.debug(f'before adjusting the volume by {voice_time[short_name]["volume_factor"] = }, {round(notes_features_15[inx,14],1) = }]')
            if notes_features_15[inx,14] > 0: notes_features_15[inx,14] += voice_time[short_name]["volume_factor"]
            logging.debug(f'after adjusting the volume {round(notes_features_15[inx,14],1) = }, before adjusting octave: {notes_features_15[inx,5] = }]')
            
            notes_features_15[inx,5] = np.max((voice_time[short_name]["min_oct"], notes_features_15[inx,5]))
            notes_features_15[inx,5] = np.min((voice_time[short_name]["max_oct"], notes_features_15[inx,5]))
            logging.debug(f'after adjusting octave: {notes_features_15[inx,5] = }, cent value of note: {notes_features_15[inx,4] = }]')
            if notes_features_15[inx,5] == voice_time[short_name]["max_oct"] and note_cents > 350:
                  notes_features_15[inx,5] -= 1 # take it down an octave it's at the max and has a high cent value
            logging.debug(f'{inx = }, {[round(feature,0) for feature in notes_features_15[inx,[6,4,5,14]]]}') #   
      logging.debug(f'in clip_note_features. {np.sum(notes_features_15[5]) = }')
      return notes_features_15

# This function will inspect MIDI chords and replace any 0's with another note that is not zero. This is to prevent polution of the scores for a chord
# zeros in midi numbers mean the note is silent. Zeros in a score function assumes it's a C.
def remove_zeros_from_midi(initial_chord):
      saved_values = np.array(np.nonzero(initial_chord))
      zeros = 0
      # print(f'{saved_values.shape = }')
      if saved_values.shape == (1,0):
            return np.zeros(4,dtype = int)
      if saved_values.shape[1] < 4: 
            for inx, note in zip(count(0,1), initial_chord):
                  if note == 0:
                        logging.debug(f'in remove_zeros_from_midi. {initial_chord = }, {initial_chord % 12} {zeros = }, {note = }, {saved_values = }')
                        initial_chord[inx] = initial_chord[saved_values[0, zeros % saved_values.shape[1]]]
                        zeros +=1
      return initial_chord

# This function is passed a 4-note midi chord and checks if it's in the cache. If found, it returns the cent value of a previously analyzed chord, if any. If not found it returns 4 zeros
def scan_chord_cache(chord, chord_cache):
    for cache in chord_cache:
        if np.array_equal(chord, cache[:4]):
            logging.debug(f'found a match and returning {cache = }')
            return(cache[4:]) # cent values for this chord
    logging.debug(f'no match found in {chord_cache.shape[0] = }')
    return np.zeros((1, 4), dtype = int)

# This function takes in a chorale of midi note numbers, the anchored notes with their preferred cent values, and an array of ratios and cent values, and returns an array of cent values and octaves
def midi_to_notes_octaves(chorale, top_notes, tonal_diamond_values, ratio_factor = .2, dist_factor = .2, stop_when = 36, flats = True, min_score_perm = 100, original_12 = np.arange(0, 1200, 100)):
      
      logging.debug(f'In midi_to_notes_octaves. {chorale.shape = }') # In midi_to_notes_octaves. chorale.shape = (4, 256)
      # this function is passed a numpy array of note numbers in midi format, four per time step SATB. input is of the form: voice, midi_note
      # it converts the midi numbers into two features: cents and octaves
      # It returns a numpy array of (voices, notes, features), but only two features
      # logging.debug(f'midi note value frequencies by voice. {[np.unique(voice, return_counts=True) for voice in chorale]}')
      keys = set_accidentals(flats)
      octave = np.array([midi_number // 12 for midi_number in chorale])
      logging.debug(f'octave values & counts by voice:')
      logging.debug([np.unique(voice, return_counts=True) for voice in octave])
      logging.debug(f'{chorale.T.shape = }')
      notes = np.empty((4,0), dtype = int)
      total_improve_chord_rolls = 0
      cache_hit = 0
      previous_chord = np.zeros(4,dtype = int)
      for chord_number, chord in zip(count(0,1), chorale.T): # go through them by chord
            chord = remove_zeros_from_midi(chord) # replace any zeros in the MIDI file with other non-zero notes in the chord
            logging.debug(f'In midi_to_notes_octaves. {chord_number = }, {chord = }, {keys[chord % 12]}')

            if chord_number == 0: # if this is the first chord, we don't have a previous one to compare to
                  previous_chord = chord
                  chord_1200, score = improve_chord_rolls(previous_chord, top_notes, chord_number, tonal_diamond_values, dist_factor = dist_factor, ratio_factor = ratio_factor, stop_when = stop_when, flats = flats, min_score_perm = min_score_perm, original_12 = original_12) # optimize to cents in the limit_31_values array
                  total_improve_chord_rolls += 1
                  chord_cache = np.hstack((chord, chord_1200), dtype = int).reshape(1,8) # start the cache off with the initial value
                  logging.debug(f'{chord = }, {chord_1200 = }')
            logging.debug(f'{chord = }, {previous_chord = }')
            if not np.array_equal(chord, previous_chord): # if this is a new chord, then calculate the conversion to cents for previous_chord
                  logging.debug(f'new chord arrived. {chord_number = }, {chord = }')
                  # check the cache to see if you have already found the chord_1200 and score for this chord.
                  cache_results = scan_chord_cache(chord, chord_cache)
                  if np.max(cache_results) == 0: # not in the cache of chords - run improve_chord_rolls to find the best just cents
                        chord_1200, score = improve_chord_rolls(chord, top_notes, chord_number - 1, tonal_diamond_values, dist_factor = dist_factor, ratio_factor = ratio_factor, stop_when = stop_when, flats = flats, min_score_perm = min_score_perm, original_12 = original_12)
                        total_improve_chord_rolls += 1
                  else: # we found a value for the cents in the cache, no need to run it through improve_chord_rolls
                        chord_1200 = cache_results
                        cache_hit += 1
                  chord_and_cents = np.hstack((chord, chord_1200), dtype = int).reshape(1,8)
                  chord_cache = np.concatenate((chord_cache, chord_and_cents), axis = 0)
                  logging.debug(f'{chord_number = } improved the chord. {chord_1200 = }, {score = }')
            logging.debug(f'about to concatenate. {chord_1200 = } to {notes.shape = }')
            notes = np.concatenate((notes, chord_1200.reshape(4,-1)), axis = 1)
            previous_chord = chord
      
      logging.debug(f'cent value counts by voice. {[np.unique(voice, return_counts=True) for voice in notes]}')
      # return np.stack((note, octave), axis = 0) #  (2, 4, 73) feature, voice, note
      logging.debug(f'{notes.shape = }, {octave.shape = }')
      logging.debug(f'{total_improve_chord_rolls = }, {cache_hit = }')
      return np.stack((notes, octave), axis = 2) # voice_note_feature.shape = (4, 73, 2) (voices, notes, features)

# the goal of this function is to string a bunch of octave changes together 
# target_array_value = np.array([[1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,-1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
#                 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,-1,-1,-1,-1,-1,-1,-1,-1],
#                 [-1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2],
#                 [2,2,2,2,2,2,2,2,-1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1]])
#
# once target_array_value is assembled, you will add it to the octave_array, then the result is multiplied by the octave_mask
# the octave_mask is the same dimension and contains only 0's and 1's
# dimension of target_array_value must be (voices, chorale.shape[1])
# repeats is how many times each 1/16th note is repeated in the chorale.
# notice that row 1 is the same as row 0 rolled by some number that is a multiple of repeats. 
# This could be used to create all voices, just roll the initial array to create additional dimensions.
# How long you stay in place must be a multiple of repeats. Stay is the maximum length to stay in place, multiplied by repeats. like repeats * 3 or repeats * 6 at max
# 
def build_octave_alteration_mask(repeats, voices, chorale, \
            octave_stretch = 4, p1 = [.2, .3, .3, .2], octave_reduce = 2, stay = 7, \
            p2 =  [.1, .1, .2, .2, .2, .1, .1]):
    octave_alteration_mask = np.empty(0, dtype = int)
    done = False
    while not done:
        some_octave_change = rng.choice(octave_stretch, p = p1) - octave_reduce # returns a single number 0,1,2,3,4,5 - 2 = -2,-1,0,1,2,3 rarely hitting the largest and smallest values
        some_repeat_value = (1 + rng.choice(stay, p = p2)) * repeats
        repeated_octave_change = np.repeat(some_octave_change, some_repeat_value, axis = 0)
        octave_alteration_mask = np.concatenate((octave_alteration_mask, repeated_octave_change), axis = 0)
        done = octave_alteration_mask.shape[0] > chorale.shape[1] 
    octave_alteration_mask = octave_alteration_mask[:chorale.shape[1]] # cut off the excess array elements
    return np.array([np.roll(octave_alteration_mask, iteration * repeats, axis = 0) for iteration in np.arange(voices)])

# the following is designed to build a mask that sets long strings of zeros and ones.
# the result is an octave mask that has long held notes followed by long rests, at least as long as the repeats value
# This is used in the woodwind_part to create the long held notes. It does not spread the octaves out
def build_long_mask(repeats, voices, chorale, p1 = [.5, .5], stay = 7, p2 =  [.1, .1, .2, .2, .2, .1, .1]):
      octave_alteration_mask = np.empty(0, dtype = int)
      done = False
      while not done:
            some_octave_change = rng.choice(2, p = p1)  # returns a zero or one
            some_repeat_value = (1 + rng.choice(stay, p = p2)) * repeats # pick a number between 1 and 7 inclusive to stay a zero or one
            repeated_octave_mask = np.repeat(some_octave_change, some_repeat_value, axis = 0)
            octave_alteration_mask = np.concatenate((octave_alteration_mask, repeated_octave_mask), axis = 0)
            done = octave_alteration_mask.shape[0] > chorale.shape[1] 
      octave_alteration_mask = octave_alteration_mask[:chorale.shape[1]] # cut off the excess array elements
      return np.array([np.roll(octave_alteration_mask, iteration * repeats, axis = 0) for iteration in np.arange(voices)])

# This functions fills out the gliss, upsamples, envelopes, and velocities for each note in as interesting a way as possible
def add_features(voices_notes_features, guev_array):
      gls, gls_p, ups, ups_p, env, env_p, vel, vel_p = np.moveaxis(guev_array, 0, 0)
      # logging.debug(f'gls, gls_p, ups, ups_p, env, env_p, vel, vel_p: {[value for value in (gls, gls_p, ups, ups_p, env, env_p, vel, vel_p)]}')
      # voices_notes_features shape = (4, 256, 2) (voices, notes, features (note, octave))
      break_point = voices_notes_features.shape[1] // env.shape[0] # # of notes divided by the shape of env
         
      notes = voices_notes_features[:,:,0] # the 0th feature is the note # (4, 256)
      octaves = voices_notes_features[:,:,1] # the 1th feature is the octave # (4, 256)
      # set the features for each note in the chorale, all voices
      gliss = np.zeros(notes.shape, dtype = int)
      upsample = np.zeros(notes.shape, dtype = int)   
      envelope = np.zeros(notes.shape, dtype = int)
      velocity = np.zeros(notes.shape, dtype = int)  
      
      # move from one set of features to the next. gls, ups, env, vel
      for voice in np.arange(notes.shape[0]):
            # for every note in the voice
            # logging.debug(f'first note in voice: {voice = } {notes[voice, 0] = }')
            gls_i = 0
            ups_i = 0
            env_i = 0
            vel_i = 0   
            prev_note = notes[voice, 0]
            prev_gls = rng.choice(gls[gls_i], p = gls_p[gls_i])
            prev_ups = rng.choice(ups[ups_i], p = ups_p[ups_i])
            prev_env = rng.choice(env[env_i], p = env_p[env_i])
            prev_vel = rng.choice(vel[vel_i], p = vel_p[vel_i])
            for note in np.arange(notes.shape[1]):
                  if notes[voice, note] != prev_note:
                        # logging.debug(f'new note: {voice = }, {note = }, {notes[voice, note] = }, {gls_i = }')
                        gliss[voice, note] = rng.choice(gls[gls_i], p = gls_p[gls_i])
                        upsample[voice, note] = rng.choice(ups[ups_i], p = ups_p[ups_i])
                        envelope[voice, note] = rng.choice(env[env_i], p = env_p[env_i])
                        velocity[voice, note] = rng.choice(vel[vel_i], p = vel_p[vel_i])
                        prev_note = notes[voice, note]
                        prev_gls = gliss[voice, note]
                        prev_ups = upsample[voice, note]
                        prev_env = envelope[voice, note]
                        prev_vel = velocity[voice, note]
                  else:
                        # logging.debug(f'{notes[voice, note] = }')
                        gliss[voice, note] = prev_gls
                        upsample[voice, note] = prev_ups
                        envelope[voice, note] = prev_env
                        velocity[voice, note] = prev_vel

                  if note % break_point == 0 and note > 0:
                        # logging.debug(f'{note = }, {note % break_point = }, {env_i = } {env[env_i]}')
                        gls_i = np.min((gls.shape[0] - 1, gls_i + 1))
                        ups_i = np.min((ups.shape[0] - 1, ups_i + 1))
                        env_i = np.min((env.shape[0] - 1, env_i + 1))
                        vel_i = np.min((vel.shape[0] - 1, vel_i + 1))
                        # logging.debug(f'increased indeciis: {env_i = } {env[env_i]}')
              
      return np.stack((notes, octaves, gliss, upsample, envelope, velocity), axis = 0) 

