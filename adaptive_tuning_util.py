import sys
sys.path.insert(0, '../Diamond_Music') # you must have already obtained the Diamond_Music repo from github and put it in the right dir.
import diamond_music_utils as dmu
import numpy as np
from fractions import Fraction
rng = np.random.default_rng()
from functools import cache
import os
import muspy
import mido
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

            "mari1": {"full_name": "marimba1", "start": 0, "csound_voice": 5,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 4, "max_oct": 7},
            "xylp1": {"full_name": "xylophone1", "start": 0, "csound_voice": 6,"time_tracker_number": 0,  "volume_factor": 0, "min_oct": 4, "max_oct": 7},
            "vibp1": {"full_name": "vibraphone1", "start": 0, "csound_voice": 7,"time_tracker_number": 0,  "volume_factor": 1, "min_oct": 4, "max_oct": 7},
            "harp1": {"full_name": "harp1", "start": 0, "csound_voice": 8,"time_tracker_number": 0,  "volume_factor": 2, "min_oct": 2, "max_oct": 7},

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

def load_from_midi_file(file_name, quantization = 4):
      logging.info(f'{file_name = }, {quantization = }')
      mid = mido.MidiFile(file_name, clip = True)
      logging.info(f'{mid.length = }') # total playback time in seconds 24.5
      ticks_per_beat = mid.ticks_per_beat
      slots_per_quarter = ticks_per_beat // quantization
      logging.info(f'{ticks_per_beat = }, {slots_per_quarter = }, {ticks_per_beat // slots_per_quarter * quantization * 12 = }')
      logging.debug(f'{mid.length = }')
      chorale = np.zeros((4, ticks_per_beat // slots_per_quarter * quantization * 12), dtype = int)
      mido_keys = [['A', 'A#m', 'Ab', 'Abm', 'Am', 'B', 'Bb', 'Bbm', 'Bm', 'C', 'C#', 'C#m', 'Cb', 'Cm', 'D', 'D#m', 'Db',\
               'Dm', 'E', 'Eb', 'Ebm', 'Em', 'F', 'F#', 'F#m', 'Fm', 'G', 'G#m', 'Gb', 'Gm'],
            [9, 10, 8, 8, 9, 11, 10, 10, 11, 0, 1, 1, 11, 0, 2, 3, 1, 2, 4, 3, 3, 4, 5, 6, 6, 5, 7, 8, 6, 7],
             ['maj', 'min', 'maj', 'min', 'min', 'maj', 'maj', 'min', 'min', 'maj', 'maj', 'min', 'maj', 'min', 'maj', 'min', 'maj',\
             'min', 'maj', 'maj', 'min', 'min', 'maj', 'maj', 'min', 'min', 'maj', 'min', 'maj', 'min']]
      for track_num, track in enumerate(mid.tracks):
            chorale_num = 0
            voice = track_num - 1
            for msg_num, msg in zip(count(0,1), track):
                  if msg.is_meta:
                        if msg.type == 'key_signature':
                              root = msg.key
                              logging.info(f'{msg_num = }, {track_num = }: {root = }')
                        elif msg.type == 'time_signature':
                              time_sig_num = msg.numerator
                              time_sig_den = msg.denominator
                              time_sig_clocks = msg.clocks_per_click
                              ticks_32_per_beat = msg.notated_32nd_notes_per_beat
                              logging.info(f'{msg_num = }, {track_num = }: {time_sig_num = }, {time_sig_den = }, {time_sig_clocks = }, {ticks_32_per_beat = }')
                        elif msg.type == 'set_tempo':
                              tempo = msg.tempo
                              logging.info(f'{msg_num = }, {track_num = }: {tempo = }')
                        elif msg.type == 'end_of_track': pass
                              # end_of_track = msg.time
                              # print(f'{msg_num = }, {track_num = }: {end_of_track = }')
                  else: # not meta
                        if msg.type == 'note_on': pass
                        elif msg.type == 'note_off':
                              slots = msg.time // slots_per_quarter
                              logging.debug(f'note off: {voice = }, {msg.time = }, note info: {msg.note}, {msg.note // 12}, {slots = }, {chorale_num = }')
                              chorale[voice, chorale_num:chorale_num + slots] = msg.note
                              # print(f'chorale[{voice}, {chorale_num}:{chorale_num + slots}], {chorale[voice, chorale_num:chorale_num + slots] = }')
                              chorale_num += slots
                        elif msg.type == 'pitchwheel': pass
                        elif msg.type == 'program_change': pass
                        else: print(f'{msg_num = }, {voice = }: {msg = }')
      chorale = chorale[:voice + 1, :chorale_num]
      logging.info(f'{slots = }, {chorale_num = }, {chorale.shape = }, {quantization = }, {slots_per_quarter = }')
      time_sig = str(time_sig_num) + '/' + str(time_sig_den)
      
      for root_num in np.arange(len(mido_keys[0])):
            if mido_keys[0][root_num] == root:
                  break
      root_note = mido_keys[1][root_num]
      mode = mido_keys[2][root_num]
      return chorale, root_note, mode, time_sig 

def read_from_midi(midi_file_name, quantizer = 4):
      root, mode, s = find_root_mode(midi_file_name)
      # print(f'{len(s) = }')
      music = muspy.from_music21(s, resolution=24) # convert the music21 object to a muspy object
      # print(f'{len(music) = }')
      sample, root, mode, pit_cl_ent, pcu = muspy_to_sample_root_mode(music, quantizer = quantizer)  
      return sample.T, root, mode, s, pit_cl_ent, pcu

def midi_to_music21(midi_file_name, chorale_number):
      root, mode, s = find_root_mode(midi_file_name)
      logging.debug(f'just back from find_root_mode. {root = }')
      # mid = MidiFile(os.path.join(midi_file_name))
      numpy_file = 'chorale' + str(chorale_number) + '.npy'
      chorale = np.load(numpy_file)
      # chorale = np.concatenate((chorale, np.zeros((4,1),dtype=int)),axis = 1) # add a bit at the end so you don't loose the ending
      logging.debug(f'{chorale_number = }, {root = }, {mode = }, {chorale.shape = }')
      return chorale, root, mode, s

# this is passed a muspy music object - optimize quantizer
def muspy_to_sample_root_mode(music, quantizer = 4):
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
    q = music.resolution # quarter note value in this midi file. Default resolution is 24. 
#     beats = music.beats # list of beat times in seconds
    # This means each quarter note consumes 24 time slots. 1/8th note is 12, 1/16th note is 6. 
    # This implies that I could pick up every 6th note and get everything I need. Or compress the result by 6x. 
    q16 = q  // quantizer # 24 / 4 = 6 which equates to catching every 1/16th note. In some cases this is too little, or too much. I'll have to figure out how to determine this more systematically. I just created a dictionary that has the right quantizer value for each chorale. This will cause trouble later. 
    logging.debug(f'time signatures: {numerator}/{denominator}')
    time_steps = int(np.ceil(piano_roll.shape[0] / q16)) # the higher of the number of voices or q16
    logging.debug(f'music.resolution: {q = }. {q16 = }, {time_steps = } 1/16th notes. {piano_roll.shape = }') # q = 24
    # piano_roll.shape = (1537, 128) # 1537 time steps, midi notes from 0 - 127
    pit_cl_ent = muspy.pitch_class_entropy(music) # determine the pitch class entropy of the chorale
    pcu = muspy.n_pitch_classes_used(music)    # how many pitches were used out of the 12 possible
    # This loop is able to load an array of shape N,4 with the notes that are being played in each time step
    sample = np.zeros(shape=(time_steps, 4), dtype = int) # typical chorale has 257 time_steps. Lasso has more.   
    notes_in_chord = 0
    for click in np.arange(0, piano_roll.shape[0], q16): # send every 6th note in the piano roll to be processed
        time_interval = click // q16
        voice = 3 # assign the first to the low voices and decrement voice for the higher voices
        for inx in np.arange(piano_roll.shape[1]): #  check if any notes are non-zero, that will be the one-hot item
            note_in_chord = 0
            if (piano_roll[click][inx]): # if velocity anything but zero - unless you set encode_velocity = False
                  sample[time_interval][voice] = inx 
                  notes_in_chord += 1
                  voice -= 1 # next instrument will get the higher note. 
            if notes_in_chord < 4: logging.debug(f'{click = }, {inx = }, {notes_in_chord = }')
    logging.debug(f'{sample.shape = }') # (257, 4)
    while np.sum(sample[-1:] == 0): # if the last note is all zeros, remove it.
          sample = sample[0:-1,:]
          logging.debug(f'{sample.shape = }') # (256, 4)
    if np.sum(sample[-1:] == 0): # this should never execute
          sample = sample[0:-1,:]
          logging.debug(f'{sample.shape = }') # (256, 4)
    
    return (sample, root, mode, pit_cl_ent, pcu)     

def read_from_corpus(work, quantizer = 4):
      s = m21.corpus.parse(work) # use music21 to pull a chorale from the corpus. For example Herzliebster is 'bwv244.3'
      # then immediately convert it to a muspy object. 
      
      muspy_object = muspy.from_music21(s)
      logging.debug(f'{muspy_object = }')
      sample, root, mode, pit_cl_ent, pcu = muspy_to_sample_root_mode(muspy_object, quantizer = quantizer)
      logging.debug(f'{sample.shape = }, {root = }, {mode = }, {round(pit_cl_ent,2) = }, {pcu = }')
      chorale = sample.T
      logging.debug(f'{chorale.shape = }')
      return chorale, root, mode, s


def read_from_numpy(chorale_number):
      file_name = 'sample' + str(chorale_number) + '.mid' # pull from the set of synthetic chorales
      chorale, root, mode, s = midi_to_music21(file_name, chorale_number)
      return chorale, root, mode, s

# This function goes through the array of cents, octaves and builds a list of slides to deal with cent values that change in the middle of a note.
# In other words, if the composer did not intend to have a new note at the point where the cent value changes, I will alter the chorale_in_cents array as follows:
# 1.    If two notes in a voice have the same 12 TET value, this indicates the composer intend them to be played as one note.
# 2.    If my tuning algorithm made them two different cent values, then this function will make them one note, but with a slide from the first cent value to the next.
# 3.    Downstream functions treat notes with any change in cent value, octave, or glide as a single note. So all with the same values will sound as a single note
# this function should be called once for each chorale processed. 
def build_glides_array(chorale_in_cents_slides, keys):                       
    logging.debug(f'In build_glides_array. {chorale_in_cents_slides.shape = }, {chorale_in_cents_slides.shape[0:2] = }') # , {chorale_in_cents[:,:].shape = }
    # logging.debug('top notes:')
    # logging.debug(*[keys[note] for note in top_notes[0]], sep = '\t')
    # logging.debug(*[cent_value for cent_value in top_notes[1]], sep = '\t')
    t_num = 1500 # this is the number of the first ftable dedicated to slides
    glides = np.zeros(chorale_in_cents_slides.shape[0:2], dtype = int)
    logging.debug(f'{glides.shape = }')
    stored_fn = np.zeros(9, dtype = float)
    stored_gliss = dmu.init_stored_gliss(starting_location = t_num, values_in_ftable = stored_fn.shape[0]) # initialize the stored_gliss array 
    logging.debug(f'{stored_gliss.shape = }')
    
    prev_chord_12 = np.zeros((4,), dtype = int)
    prev_chord_cents = np.zeros((4,), dtype = int)
    max_delta_cents = 0
    min_delta_cents = 0

    for chord_num in np.arange(chorale_in_cents_slides.shape[1]): # 66 chords
        modified_chord = False
        chord_cents = chorale_in_cents_slides[:,chord_num,0] # this is the cent value
        octave = chorale_in_cents_slides[:,chord_num,1] # this is the octave value
        chord_12 = np.array([int(round(note / 100, 0) % 12) for note in chord_cents])
        note_names = np.array([keys[note] for note in chord_12])
        logging.debug(f'chord# {chord_num}, {chord_cents = }, {chord_12 = }, {note_names = }, {octave = }')
        for note_num, note_cents, note_12, prev_note_cents, prev_12 in zip(count(0), chord_cents, chord_12, prev_chord_cents, prev_chord_12):
            if note_12 == prev_12: # if the two notes have the same 12TET note value, then inspect their cent values for differences between adjacent time steps
                if note_cents > 1150: note_cents = note_cents - 1200
                if prev_note_cents > 1150: 
                     temp_prev_note_cents = prev_note_cents - 1200 # how does this affect downstream processing?
                else: temp_prev_note_cents = prev_note_cents
                delta_cents = note_cents - temp_prev_note_cents # calculate the cent value difference # what if one is 1197 and the other is 0?
                if abs(delta_cents) > 1: # if it's more than 1 (should this be a larger slop value?)
                    modified_chord = True
                    logging.debug(f'voice_num = {note_num}, {note_cents = }, {prev_note_cents = }, {temp_prev_note_cents = }, {delta_cents = }')
                    max_delta_cents = np.max([max_delta_cents, delta_cents])
                    min_delta_cents = np.min([min_delta_cents, delta_cents])
                    logging.debug(f'{min_delta_cents = }, {max_delta_cents = }, {delta_cents = }')
                    logging.debug(f'same 12 TET note, {delta_cents = }, chord# {chord_num}, voice# {note_num}, {keys[prev_12]}, {temp_prev_note_cents = }, {note_cents = }')
                    
                    prev_chord_num = chord_num - 1 # set the lookback index to one prior to the current chord number 
                    while prev_note_cents == chorale_in_cents_slides[note_num, prev_chord_num,0] and prev_chord_num >= 0: # if the cent value is the same, keep going back
                        logging.debug(f'{prev_chord_num = }, chorale_in_cents_slides[{note_num}, {prev_chord_num}, 0]: {chorale_in_cents_slides[note_num,prev_chord_num, 0]}')
                        prev_chord_num -= 1
                    first_chord_num = prev_chord_num + 1 # store the first cent value equal to the one at the change
                    logging.debug(f'found first instance of {prev_note_cents = } at voice {note_num} in chord# {first_chord_num}')
                    next_chord_num = chord_num # start searching for all the time slots that have the second cent value 
                    # while note_cents == chorale_in_cents_slides[note_num, next_chord_num, 0] and next_chord_num < chorale_in_cents_slides.shape[1] - 1: 
                    while next_chord_num < chorale_in_cents_slides.shape[1] and note_cents == chorale_in_cents_slides[note_num, next_chord_num, 0]:
                        logging.debug(f'{next_chord_num = }, chorale_in_cents_slides[{note_num}, {next_chord_num}, 0]{chorale_in_cents_slides[note_num,next_chord_num, 0]}')
                        next_chord_num += 1
                    if next_chord_num == chorale_in_cents_slides.shape[1]: # if you are at the end of the array
                        next_chord_num += 1
                    last_chord_num = next_chord_num # store last one in the set equal to the one after the change
                    logging.debug(f'found last instance of {note_cents = } at {note_num} in chord# {last_chord_num - 1}')
                    slide_array = chorale_in_cents_slides[note_num, first_chord_num:last_chord_num, 0] # a list of cents, some at the initial value, others at the target value
                    u, ind = np.unique(slide_array, return_index=True)
                    slide_unique_order_preserved = u[np.argsort(ind)]
                    logging.debug(f'need a slide from voice: {first_chord_num} to voice {last_chord_num} {slide_array = }, {slide_array.shape = }, {slide_unique_order_preserved = }')
                    ratio = round(np.power(2, delta_cents/1200), 6) # how large to make the slide, convert the cents to a decimal ratio. 6 decimal places is probably too many
                    logging.debug(f'{delta_cents = }, {ratio = }')
                    chorale_in_cents_slides[note_num, first_chord_num:last_chord_num, 0] = prev_note_cents # set the cents in all the identified time slots to the initial cent value 
                    logging.debug(f'about to fix the octaves across the slide. {chorale_in_cents_slides[note_num, first_chord_num:last_chord_num, 1] = }, {prev_note_cents = }')
                    if prev_note_cents > 1150: 
                        chorale_in_cents_slides[note_num, first_chord_num:last_chord_num, 1] = chorale_in_cents_slides[note_num, first_chord_num, 1]
                        logging.debug(f'after the fix octaves across the slide. {chorale_in_cents_slides[note_num, first_chord_num:last_chord_num, 1] = }')
                    logging.debug(f'chorale_in_cents_slides[{note_num}, {first_chord_num}:{last_chord_num}: {chorale_in_cents_slides[note_num, first_chord_num:last_chord_num, 0]}')
                    # smoothest array is this: f1504.0 0 256.0 -6 1 128 0.9860465 128 0.972093  
                    fn_array = np.array([t_num, 0, 256, -6, 1, 128, np.average((1, ratio)), 128, ratio]) # 'cubic64_64_128' segments of cubic polynomials,
                    logging.debug(f'{[round(item,3) for item in fn_array[[0,8]]] = }, {fn_array.shape = }')
                    # look in the table of gliss ftables for one that nearly exactly matches the one required here. Strip off the 0th element, that's the table number
                    found = False
                    if stored_gliss.shape[0] > 0:
                        for look_for_fn in stored_gliss:
                            # if this ftable array is in the stored_gliss array, then use it.
                            if np.allclose(fn_array[1:], look_for_fn[1:], rtol = 1e-4): # relative tolerance level is small: 0.0001
                                found = True
                                logging.debug(f'{found = }. Already stored this fn_array: {[round(item,3) for item in fn_array[[0,8]]] = } as ftable {look_for_fn[0] = }') 
                                logging.debug(f'assigning {look_for_fn[0]} ftable to glides[{note_num}, {first_chord_num}:{last_chord_num}]')
                                glides[note_num, first_chord_num:last_chord_num] = look_for_fn[0] # store the existing fn number in all the chords that need it
                    logging.debug(f'{found = }, {stored_gliss.shape = }')
                    if not found: # if you didn't find the array in the stored_gliss array, then store it there 
                        logging.debug(f'did not find the array in {stored_gliss.shape = }. store this array as glide {t_num} at glides[{note_num}, {first_chord_num}:{last_chord_num}]')
                        logging.debug(f'assigning {t_num} ftable to glides[{note_num}, {first_chord_num}:{last_chord_num}]')
                        glides[note_num, first_chord_num:last_chord_num] = t_num
                        stored_gliss = np.vstack((stored_gliss, fn_array))
                        logging.debug(f'In newly found, after vstack. {[round(item,3) for item in fn_array[[0,8]]] = }, {t_num = }, {stored_gliss.shape = }')
                        t_num += 1
        prev_chord_cents = chord_cents
        prev_chord_12 = chord_12   
        if modified_chord: logging.debug(f'chord# {chord_num}, {chord_cents = }, {chord_12 = }, {note_names = }, {octave = }')
    logging.info(f'{min_delta_cents = },{max_delta_cents = }')
    logging.info(f'end of build_glides_array. {chorale_in_cents_slides.shape = }, {glides.shape = }, {stored_gliss.shape = }, {t_num = }')
    return chorale_in_cents_slides, glides, stored_gliss, t_num  


def mismatch_check(chorale_in_cents, chorale):
    mismatch = False
    logging.info(f'In mismatch_check. {chorale_in_cents.shape = }, {chorale.shape = }')
    for chord_num, chord_1200, octaves, midi_notes in zip(count(0,1), chorale_in_cents[:,:,0].T, chorale_in_cents[:,:,1].T, chorale.T):
        # print(f'looking at this chord: {chord_num = }, {chord_1200 = }, {octaves = }, {midi_notes = }')
        #  Convert cent values (0-1199) to MIDI scale values (0-12)
        # don't pay attention to the octave here. It's irrelevant
        chord_12_rounded = np.array([int(round(note / 100, 0) % 12) for (note, octv) in zip(chord_1200, octaves)]) # convert the cent value back into the original MIDI numbers
        logging.debug(f'{chord_num = }, {chord_12_rounded = }, {midi_notes % 12 =}')
        if not np.array_equal(midi_notes % 12, chord_12_rounded % 12): # compare the chord from the MIDI file to the chord in cents, which has been moved a lot. Make sure you have the same 12 TET note.
            delta = np.argmax(np.abs(np.diff(np.array([chord_12_rounded % 12, midi_notes % 12]), n=1, axis=0))) # where is the difference located
            # print(f'{delta = }')
            if octaves[delta] == 0: pass #  0 in the octave in this column means this note will never be played in send_to_csound_file
            else: 
                print(f'mismatch between the original MIDI notes {chord_num % 12 = }, {midi_notes % 12 = }, {chord_12_rounded % 12 =  }')
                print(f'Original scale degrees: {midi_notes % 12 = }\nScale degrees derived from the cent values: {chord_12_rounded % 12 = }')
                print(f'{midi_notes % 12 = }')
                print(f'new note: {chord_12_rounded[delta] = }, original note: {midi_notes[delta] = }')
                mismatch = True
    return mismatch

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
    tonal_diamond_ratios = np.append(tonal_diamond_ratios, [2.0], axis=0) # add 2:1 to the end of the array to make 257.
    tonal_diamond_ratios = np.unique(tonal_diamond_ratios, axis = 0) # reduce from 256 to a sorted list of 214 values
    
    # you now have a list of all the ratios in the tonality diamond to the 31 limit 
    # convert the ratios to cents. 
    tonal_diamond_cents = np.array([int(round(dmu.ratio_to_cents(just_ratio),0)) for just_ratio in tonal_diamond_ratios])
    # You now have a list of cent values that are within the tonality diamond to the 31 limit
    # assemble a list of numerators and denominators for all of the values in the ratio and cent arrays
    tonal_diamond_num_den = np.array([_find_limit(str(Fraction(just_ratio).limit_denominator(50))) for just_ratio in tonal_diamond_ratios])
    # this array will enable you to score based on the numerators and denominators of the ratios to the 31 limit
    # Each array has 214 values
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

# This function is passed a 1 to n note chord in 1200 edo (cents), and returns the score.
# The score is calculated by examining the cent distance between each note and every other note in the chord. 
# For 4 notes, that's 6 compares.
# When it finds the ratio distance of an interval in tonal_diamond_values, it then sums the numerator and denominator of the ratio distance and returns the sum of the two as a score for that interval. 
# I'm still not certain if I should return the max of numerator and denominator or the sum of the same. 
# The latter will make the score difference more pronounced. I originally was going to use the product, but I decided not to.
# It sums the results of those six compares.
# what if the interval distance ratio is not found. With all the rounding I'm doing, it's sometimes has a mismatch. 
# I try one cent higher and one cent lower to see if the interval can be found nearby.
# @cache Can't cache numpy arrays, only hashable types like tuples. TypeError: unhashable type: 'numpy.ndarray'
def score_chord_cents(chord_1200, tonal_diamond_values, tolerance = 1):
      score = 0
      logging.debug(f'in score_chord_cents')
      for notes in combinations(chord_1200, 2): # compare every note in the chord to every other note in the chord two at a time, 6 compares for a 4 note chord
            distance = abs(notes[0] - notes[1])
            # need to search for this distance in the tonal_diamond_cents array
            logging.debug(f'{notes = }, {distance = }')
            found = False
            index_to_limits = 0
            if distance > 0:
                  for gap in np.array([0, -1 * tolerance, tolerance]): # it checks the distance plus or minus tolerance
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
                        logging.debug(f'could not find the interval in the ratio table. {distance = }')
                  # logging.debug(f'{tonal_diamond_values[index_to_limits,2] = }')
                  score +=  tonal_diamond_values[index_to_limits, 2] # 2 is max of num_den for this discovered interval
      logging.debug(f'in score_chord_cents. {round(score,1) = }') # 8/19/23 should I make this division? 8/27/23: no, it's not necessary.
      return round(score,1)

# this function takes in a 4-note chord in cents and returns a optimized chord also in cents
# it picks the best choice for the six intervals in a 4-note chord, optimized by low integer ratios and distance from original.
# this function takes in a 4-note chord in cents and returns a optimized chord also in cents
# it picks the best choice for the six intervals in a 4-note chord, optimized by low integer ratios and distance from original.
def find_intervals(initial_chord, tonal_diamond_values, ratio_factor = 1.0, dist_factor = 1.0, range = 6, tolerance = 1):
      # this function does not use ratio_factor, except to pass it on to the score_chord_cents function.
      # saved_cent_moves = np.empty(0, dtype = int)
      # already_changed = np.array([False, False, False, False]) # keep track of any changes made to each note in the chord
      already_changed = np.repeat(False, initial_chord.shape[0])
      # order_of_compares = np.array([[0,1], [1,2], [2,3], [3,0], [0,2], [0,3], [1,3], [1,0], [2,0], [3,1], [2,1], [3,2]])
      # this one has only 4 compares, and does just as well as the 12 compares above when called from try_permutations.
      a = np.arange(initial_chord.shape[0])
      b = np.arange(initial_chord.shape[0])
      b = np.roll(b, -1)
      ind = np.lexsort((b,a)) # Sort by a, then by b
      order_of_compares = np.array([(a[i],b[i]) for i in ind])
      logging.debug(f'{order_of_compares = }')
      # order_of_compares = np.array(list(combinations(np.arange(initial_chord.shape[0]),2))) # this one didn't do so well
      # order_of_compares = np.concatenate((order_of_compares, np.flip(order_of_compares, axis = 1)),axis = 0) # all the combinations plus their reverse - again, didn't do so well. Intuition said it would, but it didn't.
      # print(f'{order_of_compares = }')
      for inx1, inx2 in order_of_compares:
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
                        prev_score = score_chord_cents(initial_chord, tonal_diamond_values, tolerance = tolerance) # before the second change to this note
                        logging.debug(f'score for the chord before changing {initial_chord = }: score = {prev_score}')
                        prev_chosen_note = initial_chord[inx2] # save what it used to be
                        new_note = (initial_chord[inx1] + cent_moves * tonal_diamond_values[indeciis_to_tonal_diamond[best_choice_overall], 1]) % 1200 
                        logging.debug(f'proposed {new_note = }')
                        initial_chord[inx2] = new_note # stick the new one into the array temporarily 
                        new_score = score_chord_cents(initial_chord, tonal_diamond_values, tolerance = tolerance)
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

def try_permutations(initial_chord, tonal_diamond_values, ratio_factor = 1, dist_factor = 1,  max_score = 70, \
                     original_12 = np.arange(0, 1200, 100), range = 6, already_checked = True, tolerance = 1):
      logging.debug(f'in try_permutations. {initial_chord = }, {original_12 = }')
      chord_in_1200 = np.array(note_to_1200_edo(initial_chord, original_12))
      num_notes = initial_chord.shape[0]
      # print(f'{initial_chord.shape = }, {num_notes = }')
      logging.debug(f'{chord_in_1200 = }')
      best_choice = chord_in_1200
      best_score = 99_999
      for inx, initial_chord in zip(count(0,1),np.array(list(permutations(chord_in_1200.reshape(num_notes,))))):
            if already_checked and inx in np.array([0, 18, 16, 9]): # skip the ones that were already checked in improve_chord_rolls
                 logging.debug(f'skipping {inx = }, already checked')
            #      print(f'skipping {inx = }, already checked')
            else:
                  logging.debug(f'permutation: {inx}. start here {initial_chord = }, midi numbers: {[int(round(note / 100,0)) for note in initial_chord]}')
                  # find_intervals expects one 4-note chord in cents
                  result = find_intervals(initial_chord, tonal_diamond_values, ratio_factor = ratio_factor, dist_factor = dist_factor, range = range) 
                  score = score_chord_cents(result, tonal_diamond_values, tolerance = tolerance)
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
      gap = 0
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
                              if top_cent == 0 and final_result[np.nonzero(found)][0] > 1150: top_cent = 1200 # rounds up to 1200 so the next calculation will be correct
                              gap = top_cent - final_result[np.nonzero(found)][0]
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
     
      return final_result, gap

# this function takes in a midi 4 note chord and returns the best tuned chord it could find in cents
# It is only called if the score is really bad. The roll takes care of the majority.
# I excluded this function from the path of the tuning algorithm on 8/27/23, in favor of always going to the permutation function.
def improve_chord_rolls(initial_chord, top_notes, chord_number, tonal_diamond_values, \
            roll = 4, dist_factor = .2, ratio_factor = .2, stop_when = 25, \
            flats = True, min_score_perm = 100, original_12 = np.arange(0, 1200, 100), range = 6):
      # this uses the variable stop_when to end the rolls looking for a better score
      if roll == 0: roll = 1
      chord_in_1200 = np.array(note_to_1200_edo(initial_chord, original_12)) # assign an initial 1200 edo step to each midi note
      keys = set_accidentals(flats)
      logging.debug(f'{chord_number = }, {initial_chord = }, {keys[initial_chord % 12]}')
      score = 99_999
      best_score = 99_999
      best_choice = chord_in_1200
      for inx in np.arange(roll):
            result = find_intervals(np.roll(best_choice,inx), tonal_diamond_values, ratio_factor = ratio_factor, dist_factor = dist_factor, range = range) 
            score = score_chord_cents(result, tonal_diamond_values)
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
            final_result, best_score = try_permutations(initial_chord, tonal_diamond_values, ratio_factor = ratio_factor, dist_factor = dist_factor, range = range) # this is a permutation, not a roll. It's slower, but more thorough. It also does the rearanging. No need to do it again.
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
      final_result, gap = transpose_top_notes(final_result, top_notes, chord_number, best_score, initial_chord)  # transpose to keep the top notes stable over chord changes
      final_result = final_result % 1200
      logging.debug(f'{chord_number}, improve_chord_rolls after adjustment. {final_result = }, transposed by {gap = }')
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

# This function will inspect MIDI chords and replace any 0's with another note that is not zero. 
# This is to prevent polution of the scores for a chord that includes 0, since 0 means it's silent, not the note C.
# zeros in midi numbers mean the note is silent. 
def remove_zeros_from_midi(initial_chord):
      saved_values = np.array(np.nonzero(initial_chord)) # save the index to the initial_chord of those values that are not zero
      zeros = 0
      # print(f'{saved_values.shape = }')
      if saved_values.shape == (1,0): # if they are all zeros, return an array of zeros
            return np.zeros(4, dtype = int)
      if saved_values.shape[1] < 4: # not all are zeros, but some are. Replace the zeros with the first non-zero value in the chord
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

# this has the same purpose as midi_to_notes_octaves, except it bypasses several of the less effective tuning algorithms and just uses the permutations.
def midi_to_notes_octaves_trimmed(chorale, top_notes, tonal_diamond, ratio_factor = 1, dist_factor = 1, \
            stop_when = 36, flats = True, min_score_perm = 100, original_12 = np.arange(0, 1200, 100), range = 6, tolerance = 1): 
      logging.debug(f'In midi_to_notes_octaves_trimmed. {chorale.shape = }') # In midi_to_notes_octaves. chorale.shape = (4, 256)
      # this function is passed a numpy array of note numbers in midi format, four per time step SATB. input is of the form: voice, midi_note
      # it converts the midi numbers into two features: cents and octaves
      # It returns a numpy array of (voices, notes, features), but only two features
      # logging.debug(f'midi note value frequencies by voice. {[np.unique(voice, return_counts=True) for voice in chorale]}')
      keys = set_accidentals(flats)
      octave = np.array([midi_number // 12 for midi_number in chorale]) # a few of these will need to be reduced if the cents come out just under 1200
      # print(f'in midi_to_notes_octaves_trimmed. {octave.shape = }') # octave.shape = (4, 16)
      # print(f'{octave[:,4:12] = }')
      logging.debug(f'octave values & counts by voice:')
      logging.debug([np.unique(voice, return_counts=True) for voice in octave])
      logging.debug(f'{chorale.T.shape = }')

      scores = np.zeros(chorale.shape[1])
      score_inx = 0
      total_score = 0
      chorale_in_cents = np.zeros((chorale.T.shape), dtype = int)
      prev_chord = np.zeros(4, dtype = int)
      for inx, chord in zip(count(0,1), chorale.T):
            chord = remove_zeros_from_midi(chord) # a zero indicates that the voice is silent. Replace the zero with another note in the chord.
            logging.debug(f'{inx = }, {chord = }, {chord % 12 = }, {prev_chord % 12 = }')
            if np.array_equal(chord, prev_chord):
                  logging.debug(f'same chord as previous. Assign the previous retuning to this chord. {chord = }\n')
                  chorale_in_cents[inx] = chorale_in_cents[inx - 1]
            else:
                  prev_chord = np.copy(chord)
                  logging.debug(f'cost untuned: {score_chord_cents(chord % 12 * 100, tonal_diamond, tolerance = tolerance)}')
                  chord_in_cents, final_cost = try_permutations(chord, tonal_diamond, ratio_factor = ratio_factor, dist_factor = dist_factor, max_score = 70, range = range, already_checked = False, tolerance = tolerance)
                  logging.debug(f'before transposition. {chord_in_cents = }')
                  trans_chord_in_cents, gap = transpose_top_notes(chord_in_cents, top_notes, inx, final_cost, chord)
                  logging.debug(f'{trans_chord_in_cents = }, transposed by {gap = }')                        
                  chorale_in_cents[inx] = trans_chord_in_cents
                  logging.debug(f'after transposing and rearranging: {chorale_in_cents[inx] = }') 
                  logging.debug(f'{[keys[int(round(note / 100, 0) % 12)] for note in chorale_in_cents[inx]]}, {final_cost = }')
                  total_score += final_cost 
                  scores[score_inx] = final_cost
                  score_inx += 1
            for voice_num, note in zip(count(0,1), trans_chord_in_cents):
                  if note > 1150: 
                        logging.debug(f'{octave[voice_num, inx] = }')
                        octave[voice_num, inx] -= 1
                        logging.debug(f'found {note = } greater than 1150, reduce octave for {voice_num = }, chord {inx} octave[{voice_num}, {inx}]')
                        logging.debug(f'{octave[voice_num, inx] = }')
      scores = scores[:score_inx]
      logging.debug(f'{total_score = }, {np.average(scores) = }, {np.min(scores) = }, {np.max(scores) = }, average cent value: {np.average(chorale_in_cents)}') 
      logging.debug(f'{chorale_in_cents.shape = }, {octave.shape = }') # chorale_in_cents.shape = (66, 4), octave.shape = (4, 66)
      return np.stack((chorale_in_cents.T, octave), axis = 2) 

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
      # p1 needs to sum to 1 - for octave_stretch = 5 p1 = [.1, .2, .3, .2, .2]
      # was p1 = [.2, .3, .3, .2] but I needed to make it stretch farther
      while not done:
            # returns a single number 0,1,2,3,4,5 - 2 = -2,-1,0,1,2,3 rarely hitting the largest and smallest values
            some_octave_change = rng.choice(octave_stretch, p = p1) - octave_reduce
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
            some_octave_change = rng.choice(2, p = p1)  # returns a zero or one, mostly zero
            some_repeat_value = (1 + rng.choice(stay, p = p2)) * repeats # pick a number between 1 and 7 inclusive to stay a zero or one
            repeated_octave_mask = np.repeat(some_octave_change, some_repeat_value, axis = 0)
            octave_alteration_mask = np.concatenate((octave_alteration_mask, repeated_octave_mask), axis = 0)
            done = octave_alteration_mask.shape[0] > chorale.shape[1] 
      octave_alteration_mask = octave_alteration_mask[:chorale.shape[1]] # cut off the excess array elements
      octave_alteration_mask = np.array([np.roll(octave_alteration_mask, iteration * repeats, axis = 0) for iteration in np.arange(voices)])
      return octave_alteration_mask

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

# added 9/1/23 to include the glides for the woodwinds_part.
def add_features_glides(notes_octaves, glides, guev_array):
      gls, gls_p, ups, ups_p, env, env_p, vel, vel_p = np.moveaxis(guev_array, 0, 0)
      logging.debug(f'in add_features_glides. {notes_octaves.shape = }, {glides.shape = }, {guev_array.shape = }')
      # notes_octaves shape = (voices, notes, features (note, octave))
      break_point = notes_octaves.shape[1] // env.shape[0] # # of notes divided by the shape of env
      # split the octaves and notes into different array.
      notes = notes_octaves[:,:,0] # the 0th feature is the note # (4, 256)
      octaves = notes_octaves[:,:,1] # the 1th feature is the octave # (4, 256)
      # set the features for each note in the chorale, all voices
      upsample = np.zeros(notes.shape, dtype = int)   
      envelope = np.zeros(notes.shape, dtype = int)
      velocity = np.zeros(notes.shape, dtype = int)  
      
      # move a set of features to the notes based on break points: ups, env, vel
      for voice in np.arange(notes.shape[0]):
            # for every voice in the array
            # logging.debug(f'first note in voice: {voice = } {notes[voice, 0] = }')
            ups_i = 0
            env_i = 0
            vel_i = 0   
            prev_note = notes[voice, 0]
            prev_ups = rng.choice(ups[ups_i], p = ups_p[ups_i])
            prev_env = rng.choice(env[env_i], p = env_p[env_i])
            prev_vel = rng.choice(vel[vel_i], p = vel_p[vel_i])
            for note in np.arange(notes.shape[1]):
                  # for every note in the voice
                  if notes[voice, note] != prev_note:
                        upsample[voice, note] = rng.choice(ups[ups_i], p = ups_p[ups_i])
                        envelope[voice, note] = rng.choice(env[env_i], p = env_p[env_i])
                        velocity[voice, note] = rng.choice(vel[vel_i], p = vel_p[vel_i])
                        prev_note = notes[voice, note]
                        prev_ups = upsample[voice, note]
                        prev_env = envelope[voice, note]
                        prev_vel = velocity[voice, note]
                  else:
                        upsample[voice, note] = prev_ups
                        envelope[voice, note] = prev_env
                        velocity[voice, note] = prev_vel

                  if note % break_point == 0 and note > 0:
                        ups_i = np.min((ups.shape[0] - 1, ups_i + 1))
                        env_i = np.min((env.shape[0] - 1, env_i + 1))
                        vel_i = np.min((vel.shape[0] - 1, vel_i + 1))
              
      return np.stack((notes, octaves, glides, upsample, envelope, velocity), axis = 0) 

# report the results in text form
def print_interval_cent_report(chorale_in_cents, chorale, top_notes, tonal_diamond, keys, ratio_factor, limit_denominator = 42, tolerance = 1):
    print(f'in print_interval_cent_report. {chorale_in_cents.shape = }')
    end_chord = 999
    max_score = 0
    report_over = 0 
    sum_scores = 0
    count_scores = 0
    print(f'report the chords used, with chord scores')
    print(f'#\t\tnames of the notes\tcents of notes\t\tintervals between notes, the cents and ratios of the intervals\t\tchord score')
    previous_chord = np.zeros((4,), dtype = int)

    for chord_num, chord_1200, octaves, midi_notes in zip(count(0,1), chorale_in_cents[:,:end_chord,0].T, chorale_in_cents[:,:end_chord,1].T, chorale.T):
        # chorale_in_cents[:,:end_chord,0].T , chorale_in_cents[:,:end_chord,1].T
        # print(f'{chord_num = }, {chord_1200 = }, {octaves = }, {midi_notes = }')

        chord_12_rounded = np.array([int(round(note / 100, 0) % 12) for (note, octv) in zip(chord_1200, octaves)]) # convert the cent value back into the original MIDI scale degree
        if not np.array_equal(midi_notes % 12, chord_12_rounded): # compare the chord from the MIDI file to the chord in cents, which has been moved a lot. Make sure you have the same 12 TET note.
            delta = np.argmax(np.abs(np.diff(np.array([chord_12_rounded, midi_notes % 12]), n=1, axis=0))) # where is the difference located
            if octaves[delta] == 0: pass #  0 in the octave in this column means this note will never be played in send_to_csound_file
            else: 
                print(f'mismatch between the original MIDI notes {chord_num = }, {midi_notes % 12 = }, {chord_12_rounded =  }')
                print(f'Original scale degrees: {midi_notes % 12 = }, Scale degrees derived from the cent values: {chord_12_rounded = }')
                print(f'{keys[midi_notes % 12] = }')
                print(f'{chord_12_rounded[delta] = }, {midi_notes[delta] = }, {chord_1200 = }')
                
        if not np.array_equal(chord_12_rounded, previous_chord):
            current_score = score_chord_cents(chord_1200, tonal_diamond, tolerance = tolerance) # shouldn't the score include the distance from 12TET? 8/19/23 Future Prent says no. The key decision is not how far from 12TET, it is whether it is still the same 12TET note. The rest is up to taste. 
            max_score = np.max((current_score, max_score))
            sum_scores += current_score
            count_scores += 1
            if current_score > report_over:
                print(chord_num, '\t', end = '\t') # chord_12_rounded % 12, 
                print([keys[int(round(note, 0) % 12)] for note in chord_12_rounded], end = '\t')
                print(chord_1200, end = '\t')
                print(*[(inx1, inx2, abs(chord_1200[inx1] - chord_1200[inx2]), dmu.cents_to_ratio(abs(chord_1200[inx1] - chord_1200[inx2]),limit_denominator = limit_denominator)) for inx1, inx2 in combinations(np.arange(4),2)], end = '\t\t')
                print(f'{current_score}')   
            
        previous_chord = chord_12_rounded

    print(f'{ratio_factor = }, {tolerance = }')
    print(f'Maximum score was: {max_score}')  
    print(f'Total score was {sum_scores}') 
    print(f'Average score was: {round(sum_scores / count_scores,1)}') 
    
    print(f'{keys[top_notes[0]] = }') 
    print(f'in cents: {top_notes[1] = }')
    value, counts = np.unique(chorale_in_cents[:,:,0].T, return_counts = True)
    how_many_notes = 20
    print(f'{how_many_notes} most common cent values, midi note, counts with the most common at the bottom:')
    print(*[(v, int(round(v / 100,0)), c) for v,c in zip(value[np.argsort(counts)[-how_many_notes:]], counts[np.argsort(counts)[-how_many_notes:]])], sep = '\n')
    value = np.unique(chorale_in_cents[:,:,0].T)
    print(f'list of all the cent values in chorale_in_cents: {value = }')
    return max_score, sum_scores, count_scores, len(value)