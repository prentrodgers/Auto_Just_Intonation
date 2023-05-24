import numpy as np
import numpy.testing as npt
from importlib import reload
import os
import sys
import time
import logging
from fractions import Fraction
from numpy.random import default_rng
from scipy.interpolate import make_interp_spline
rng = np.random.default_rng()
from itertools import count


def build_all_ratios(limit_value = 31):
      all_ratios = []
      for limit in ([limit_value]): # calculate the size of tonality diamond to the n-limit and create the array all_ratios.
            end_denom = limit + 1
            start_denom = (end_denom) // 2
            o_numerator = np.arange(start_denom, end_denom, 1) # create a list of overtones
            u_denominator = np.arange(start_denom, end_denom, 1) # create a list of undertones
            all_ratios = []
            for oton_root in u_denominator:
                  # logging.debug()
                  for overtone in o_numerator:
                        if overtone < oton_root: oton = overtone * 2
                        else: oton = overtone
                        all_ratios.append(oton / oton_root)
      return all_ratios

def build_ratio_strings(all_ratios):
      ratio_strings = np.array([str(Fraction(ratio).limit_denominator(max_denominator = 100)) for ratio in all_ratios]).reshape(16,16)
      i = 0
      for ratio in ratio_strings:
            j = 0
            for r in ratio:
                  if ratio_strings[i,j] == '1': 
                        ratio_strings[i,j] = '1/1'
                  j += 1
            i += 1
      return ratio_strings


stored_gliss = np.empty((0,70), dtype = float)
current_gliss_table = 1500 # raised on 4/28/23 to make more room for samples. Previously, samples occupied 601 - 798 increased it  to 1500
all_ratios = build_all_ratios()
ratio_strings = build_ratio_strings(all_ratios)
all_ratio_strings = ratio_strings.reshape(256,)

keys = {'oton': {ratio_strings[0, 0]: np.arange(0 * 16, 1 * 16, 1),
                  ratio_strings[1 ,0]: np.arange(1 * 16, 2 * 16, 1),
                  ratio_strings[2 ,0]: np.arange(2 * 16, 3 * 16, 1),
                  ratio_strings[3 ,0]: np.arange(3 * 16, 4 * 16, 1),
                  ratio_strings[4 ,0]: np.arange(4 * 16, 5 * 16, 1),
                  ratio_strings[5 ,0]: np.arange(5 * 16, 6 * 16, 1),
                  ratio_strings[6 ,0]: np.arange(6 * 16, 7 * 16, 1),
                  ratio_strings[7 ,0]: np.arange(7 * 16, 8 * 16, 1),
                  ratio_strings[8 ,0]: np.arange(8 * 16, 9 * 16, 1),
                  ratio_strings[9 ,0]: np.arange(9 * 16, 10 * 16, 1),
                  ratio_strings[10, 0]: np.arange(10 * 16, 11 * 16, 1),
                  ratio_strings[11, 0]: np.arange(11 * 16, 12 * 16, 1),
                  ratio_strings[12, 0]: np.arange(12 * 16, 13 * 16, 1),
                  ratio_strings[13, 0]: np.arange(13 * 16, 14 * 16, 1),
                  ratio_strings[14, 0]: np.arange(14 * 16, 15 * 16, 1),
                  ratio_strings[15, 0]: np.arange(15 * 16, 16 * 16, 1)
                  },
            'uton': {ratio_strings[0, 0]: np.arange(0, 256, 16),
                  ratio_strings[0, 1]: np.arange(1, 256, 16),
                  ratio_strings[0, 2]: np.arange(2, 256, 16),
                  ratio_strings[0, 3]: np.arange(3, 256, 16),
                  ratio_strings[0, 4]: np.arange(4, 256, 16),
                  ratio_strings[0, 5]: np.arange(5, 256, 16),
                  ratio_strings[0, 6]: np.arange(6, 256, 16),
                  ratio_strings[0, 7]: np.arange(7, 256, 16),
                  ratio_strings[0, 8]: np.arange(8, 256, 16),
                  ratio_strings[0, 9]: np.arange(9, 256, 16),
                  ratio_strings[0, 10]: np.arange(10, 256, 16),
                  ratio_strings[0, 11]: np.arange(11, 256, 16),
                  ratio_strings[0, 12]: np.arange(12, 256, 16),
                  ratio_strings[0, 13]: np.arange(13, 256, 16),
                  ratio_strings[0, 14]: np.arange(14, 256, 16),
                  ratio_strings[0, 15]: np.arange(15, 256, 16)                 
                  }
                  }
      # build the 8 note scales for each of the rank A, B, C, D otonal and utonal out of the 16 note scales
#                                                        start, end, step size
# make this dictionary nested: rank, mode
scales = {'A': {'oton': np.array([note % 16 for note in np.arange(0, 16, 2)]),
                      'uton': np.array([note % 16 for note in np.arange(8, -8, -2)])}, # utonal goes down, so that the scale will go up.
                'B': {'oton': np.array([note % 16 for note in np.arange(2, 18, 2)]),
                      'uton': np.array([note % 16 for note in np.arange(14, -2, -2)])},
                'C': {'oton': np.array([note % 16 for note in np.arange(1, 17, 2)]),
                      'uton': np.array([note % 16 for note in np.arange(13, -2, -2)])},
                'D': {'oton': np.array([note % 16 for note in np.arange(3, 19, 2)]),
                      'uton': np.array([note % 16 for note in np.arange(15, 0, -2)])},
          # the next 8 are additional 8 note scales that have good 3:2, and interesting thirds
                'E': {'oton': np.array([ 2,  4,  6,  8, 11, 13, 15,  0]), # 3rd: 11:9 neutral
                      'uton': np.array([ 8,  6,  4,  2,  0, 15, 13, 11])}, # 3rd: 6:5 minor
                'F': {'oton': np.array([ 8, 10, 12, 14,  0,  2,  4,  6]), # 3rd: 7:6 subminor
                      'uton': np.array([ 0, 14, 12, 10,  8,  6,  4,  2])}, # 3rd: 8:7 subminor
                'G': {'oton': np.array([ 4,  6,  8, 10, 14, 15,  0,  2]), # 3rd: 6:5 minor
                      'uton': np.array([14, 10,  8,  6,  4,  2,  0, 15])}, # 3rd: 5:4 major
                'H': {'oton': np.array([12, 14,  0,  2,  5,  7,  9, 11]), # 3rd: 8:7 sub-subminor
                      'uton': np.array([5,  3,   1, 15, 12, 10,  8,  6])} # 3rd: 21/17 neutral
               }
      # this dictionary is helpful in doing a lookup of different inversions of a chord
# choose the notes in scale for each rank (A, B, C, D), mode (oton, uton), & inversion (1, 2, 3, 4)
# access the four note chords by specifying inversions[rank][mode][inv]
# where rank is in (A, B, C, D) mode is in (oton, uton), and inv is in (1, 2, 3, 4)
# use the resulting array as the index into a keys[mode][ratio]

inversions = {'A': {'oton': {1: np.array([0, 4, 8, 12]),
                             2: np.array([4, 8, 12, 0]),
                             3: np.array([8, 12, 0, 4]),
                             4: np.array([12, 0, 4, 8])},
                    'uton': {1: np.flip(np.array([0, 4, 8, 12])),
                             2: np.flip(np.array([4, 8, 12, 0])),
                             3: np.flip(np.array([8, 12, 0, 4])),
                             4: np.flip(np.array([12, 0, 4, 8]))}}, 
              'B': {'oton': {1: np.array([2, 6, 10, 14]),
                             2: np.array([6, 10, 14, 2]),
                             3: np.array([10, 14, 2, 6]),
                             4: np.array([14, 2, 6, 10])},
                    'uton': {1: np.flip(np.array([2, 6, 10, 14])),
                             2: np.flip(np.array([6, 10, 14, 2])),
                             3: np.flip(np.array([10, 14, 2, 6])),
                             4: np.flip(np.array([14, 2, 6, 10]))}}, 
              'C': {'oton': {1: np.array([1, 5, 9, 13]),
                             2: np.array([5, 9, 13, 1]),
                             3: np.array([9, 13, 1, 5]),
                             4: np.array([13, 1, 5, 9])},
                    'uton': {1: np.flip(np.array([2, 6, 10, 14])),
                             2: np.flip(np.array([6, 10, 14, 2])),
                             3: np.flip(np.array([10, 14, 2, 6])),
                             4: np.flip(np.array([14, 2, 6, 10]))}}, 
              'D': {'oton': {1: np.array([3, 7, 11, 15]),
                             2: np.array([7, 11, 15, 3]),
                             3: np.array([11, 15, 3, 7]),
                             4: np.array([15, 3, 7, 11])},
                    'uton': {1: np.flip(np.array([3, 7, 11, 15])),
                             2: np.flip(np.array([7, 11, 15, 3])),
                             3: np.flip(np.array([11, 15, 3, 7])),
                             4: np.flip(np.array([15, 3, 7, 11]))}},
              'E': {'oton': {1: np.array([ 2,  6, 11, 15]),
                             2: np.array([ 6, 11, 15,  2]),
                             3: np.array([11, 15,  2,  6]),
                             4: np.array([15,  2,  6, 11])},
                    'uton': {1: np.array([8,  4,  0, 13]),
                             2: np.array([4,  0, 13,  8]),
                             3: np.array([0, 13,  8,  4]),
                             4: np.array([8,  4,  0, 13])}},
              'F': {'oton': {1: np.array([ 8, 12,  0,  4]),
                             2: np.array([12, 0,  4, 8]),
                             3: np.array([ 0, 4, 8, 12]),
                             4: np.array([ 4, 8, 12,  0])},
                    'uton': {1: np.array([ 0, 12,  8,  2]),
                             2: np.array([12,  8,  2,  0]),
                             3: np.array([ 8,  2,  0, 12]),
                             4: np.array([ 2,  0, 12,  8])}},
              'G': {'oton': {1: np.array([ 4,  8, 14,  0]),
                             2: np.array([ 8, 14,  0,  4]),
                             3: np.array([14,  0,  4,  8]),
                             4: np.array([ 0,  4,  8, 14])},
                    'uton': {1: np.array([14,  8,  4,  0]),
                             2: np.array([ 8,  4,  0, 14]),
                             3: np.array([ 4,  0, 14,  8]),
                             4: np.array([ 0, 14,  8,  4])}},
              'H': {'oton': {1: np.array([12,  0,  5,  9]),
                             2: np.array([ 0,  5,  9, 12]),
                             3: np.array([ 5,  9, 12,  0]),
                             4: np.array([ 9, 12,  0,  5])},
                    'uton': {1: np.array([ 5,  1, 12,  8]),
                             2: np.array([ 1, 12,  8,  5]),
                             3: np.array([12,  8,  5,  1]),
                             4: np.array([ 8,  5,  1, 12])}}}

def build_scales(mode, ratio, rank):
      # logging.debug(f'{mode = }, {ratio = }, {rank = }')
      # if rank in (['A', 'B', 'C', 'D']):
      if ratio in keys[mode]: 
            scale = np.array([keys[mode][ratio][note] for note in (scales[rank][mode])])
      else: 
            logging.error(f'in build_scales. Could not find {ratio = } with {mode} in {keys[mode] = } with {rank = }')
            scale = np.arange(8)
      return scale

def ratio_string_to_float(ratio):
      n, d = ratio.split('/')
      return float(float(n) / float(d))

def ratio_to_cents(ratio):
      if isinstance(ratio, str):
            print(f'this function expects a ratio in floating point form, but we do not care. Here is your answer boss')
            ratio = ratio_string_to_float(ratio)
      return round(1200 * np.log(ratio)/np.log(2),1)

def cents_to_ratio(cents, limit_denominator = 105):
    return str(Fraction(np.power(2, cents/1200)).limit_denominator(limit_denominator))

def cents_to_num_den(cents, limit_denominator = 105):
     f = Fraction(np.power(2, cents/1200)).limit_denominator(limit_denominator)
     return f.numerator, f.denominator


def show_keys():
      return(keys)

def show_scales():
      return(scales)

def show_inversions():
      return(inversions)      
      
# note that this function tries to find the closest end note to the start note.
# It might be up or down, it might cross an octave boundary.
# for example, from 15:8 to 1:1 would ordinarily return 15:8 distance between the two notes, 
# but the closest one is from 15:8 to 2:1, moving up an octave, multiplying the second value by 2
# to accomodate that, the function tests the size of the ratio returned from the normal calculation,
# and multiplies either the start or the end note by 2 before recalculating the ratio.
# this can cause problems if you are looking for that large leap.
# You can override the default behavior by setting find_closest = False
def ratio_distance(start, end, find_closest = True):
      start_ratio = ratio_string_to_float(start)
      end_ratio = ratio_string_to_float(end)
      ratio = end_ratio / start_ratio 
      # logging.debug(f'calculated ratio is {ratio = }')
      if not find_closest: return (ratio)
      min_ratio = 0.75
      max_ratio = 1.50
      if min_ratio <= ratio <= max_ratio:
            return ratio
      else:
            # logging.debug(f'out of range: {round(ratio,2) = }')
            if ratio >= max_ratio: 
                  ratio = end_ratio / (start_ratio * 2)
            elif ratio <= min_ratio: 
                  ratio = end_ratio * 2 / start_ratio
            # logging.debug(f'new {round(ratio,2) = }')
      return ratio

# for each of the keys, build the chords from the scales created above.
# key is a string index into the keys dictionary: e.g. mode, ratio
# inversion is the string index into the inversions dictionary e.g. 'A_oton_1'
# the inversion includes the rank is which of the four tetrachords in each scale, A, B, C, or D
# And it specifies which note is on top

def build_chords(mode, root, rank, inversion):
      if type(inversion) != int: inversion = int(inversion)
      if (root in keys[mode]) and (inversion in inversions[rank][mode]): 
            chord = np.array([keys[mode][root][note] for note in (inversions[rank][mode][inversion])]) 
      else:
            logging.debug(f'in build_chords. Could not find {root = } with {mode = }, in {inversion = } ')
            chord = None
      return chord

# This function takes a table number, glissando type, and ratio and returns an array that can be passed to csound to bend a note
def make_ftable_glissando(t_num, gliss_type, ratio):
#                               +-- table number
#                               |       +-- start at time zero
#                               |       |    +-- size of the table
#                               |       |   |   +-- GEN07 type table, negative = don't normalize
#                               |       |   |   |   +-- start at 1:1, which is the current note
#                               |       |   |   |   |  +-- take this amount of time at 1:1 some portion of the note duration
#                               |       |   |   |   |  |   +-- stay at 1:1
#                               |       |   |   |   |  |   |  +-- take this long to reach the next 
#                               |       |   |   |   |  |   |  |   +-- target ratio, you want to go up or down this amount
#                               |       |   |   |   |  |   |  |   |      +-- stay at 2nd note this long
#                               |       |   |   |   |  |   |  |   |      |    +-- end at the target ratio, or 1 
#                               |       |   |   |   |  |   |  |   |      |    |
      if gliss_type == 'slide':
            fn_array = np.array([t_num, 0, 256, -7, 1, 64, 1, 64, ratio, 128, ratio])
      elif gliss_type == 'cubic16_16_224':
            fn_array = np.array([t_num, 0, 256, -6, 1, 16, np.average((1, ratio)), 16, ratio, 224, ratio])
      elif gliss_type == 'cubic32_32_192':
            fn_array = np.array([t_num, 0, 256, -6, 1, 32, np.average((1, ratio)), 32, ratio, 192, ratio])
      elif gliss_type == 'cubic64_64_128':
            fn_array = np.array([t_num, 0, 256, -6, 1, 64, np.average((1, ratio)), 64, ratio, 128, ratio])
      elif gliss_type == 'cubic96_96_64':
            fn_array = np.array([t_num, 0, 256, -6, 1, 96, np.average((1, ratio)), 96, ratio, 64, ratio])
      elif gliss_type == 'cubic112_112_32':
            fn_array = np.array([t_num, 0, 256, -6, 1, 112, np.average((1, ratio)), 112, ratio, 32, ratio])
      elif gliss_type == 'trill_1_step':
            fn_array = np.array([t_num, 0, 32, -7, 1, 16, 1, 0, ratio, 16, ratio])
      elif gliss_type == 'trill_2_step':
            fn_array = np.array([t_num, 0, 64, -7, 1, 16, 1, 0, ratio, 16, ratio, 0, 1, 16, 1, 0, ratio, 16, ratio])
      elif gliss_type == 'trill_3_step':
            fn_array = np.array([t_num, 0, 64, -7, 1, 13, 1, 0, ratio, 13, ratio, 0, 1, 13, 1, 0, ratio, 13, ratio, 0, 1, 12, 1])
      elif gliss_type == 'trill_4_step':
            fn_array = np.array([t_num, 0, 128, -7, 1, 16, 1, 0, ratio, 16, ratio, 0, 1, 16, 1, 0, ratio, 16, ratio, 0, 1, 16, 1, 0, ratio, 16, ratio, 0, 1, 16, 1, 0, ratio, 16, ratio])
      elif gliss_type == 'trill_6_step':
            fn_array = np.array([t_num, 0, 256, -7, 1, 21, 1, 0, ratio, 21, ratio, 0, 1, 22, 1, 0, ratio, 21, ratio, 0, 1, 21, 1, 0, ratio, 22, ratio, 0, 1, 21, 1, 0, ratio, 21, ratio, 0, 1, 22, 1, 0, ratio, 21, ratio, 0, 1, 21, 1, 0, ratio, 22, ratio]) 
      elif gliss_type == 'trill_8_step':
            fn_array = np.array([t_num, 0, 256, -7, 1, 16, 1, 0, ratio, 16, ratio, 0, 1, 16, 1, 0, ratio, 16, ratio, 0, 1, 16, 1, 0, ratio, 16, ratio, 0, 1, 16, 1, 0, ratio, 16, ratio, 0, 1, 16, 1, 0, ratio, 16, ratio, 0, 1, 16, 1, 0, ratio, 16, ratio, 0, 1, 16, 1, 0, ratio, 16, ratio, 0, 1, 16, 1, 0, ratio, 16, ratio])
      elif gliss_type == 'flat':
            fn_array = np.array([0, 0, 256, -7, 1, 256, 1]) # f0 0 256 -7 1 256 1 ; 
      else: 
           fn_array = np.zeros(10)
           logging.debug(f'invalid gliss type: {gliss_type}')
            
      return fn_array    

# take a scale as indexes and return the ratios as strings
def show_scale_ratios(scale):
      for note in scale:
            return(all_ratio_strings[scale])

def start_logger(LOGNAME, log_level = 'info'):
      if os.path.exists(LOGNAME):
            os.remove(LOGNAME) # make sure the log starts over with a fresh log file. Next line starts the logger.
      logger = logging.getLogger()
      fhandler = logging.FileHandler(filename=LOGNAME, mode='w')
      formatter = logging.Formatter('%(msecs)s - %(levelname)s - %(message)s')
      fhandler.setFormatter(formatter)
      logger.addHandler(fhandler)
      if log_level == 'info': logger.setLevel(logging.INFO)
      elif log_level == 'debug': logger.setLevel(logging.DEBUG)
      else: logger.setLevel(logging.WARN)
     
def flushMessages(cs, delay=0):
      s = ""
      if delay > 0:
            time.sleep(delay)
      for i in range(cs.messageCnt()):
            s += cs.firstMessage()
            cs.popFirstMessage()
      return s

def printMessages(cs, delay=0):
    s = flushMessages(cs, delay)
    this_many = 0
    if len(s)>0:
        logging.debug(s)            

# load the orchestra .csd file in to a long string that can be passed to csound
def load_csd(csd_file, strip_f0 = False):
      csd_content = ""
      lines = 0
      empty = False
      with open(csd_file,'r') as csd:
            while not empty:
                  skip = False
                  read_str = csd.readline()
                  empty = not read_str
                  lines += 1
                  if strip_f0:
                        if read_str.startswith('f0') or read_str.startswith('</CsScore') or read_str.startswith('</CsoundS'):
                              skip = True
                  if read_str.startswith('i') or read_str.startswith('t'):
                        skip = True
                  if not skip: csd_content += read_str
      csd.close()        
      return(csd_content, lines)

# start up an instance of csound so that you can pass commands to the started orchestra
# commented out 12/15/22 due to problems loading ctcsound in some environments
# def load_csound(csd_content):
#       cs = ctcsound.Csound()    # create an instance of Csound
#       cs.createMessageBuffer(0)    
#       cs.setOption('-odac') # live performance is the default
#       cs.setOption("-G")  # Postscript output
#       cs.setOption("-W")  # create a WAV format output soundfile
#       printMessages(cs)
#       cs.compileCsdText(csd_content)  # Compile Orchestra from String - already read in from a file 
      
#       # logging.debug(csd_content)    
#       printMessages(cs)
#       cs.start()         # When compiling from strings, this call is necessary before doing any performing
#       flushMessages(cs)

#       pt = ctcsound.CsoundPerformanceThread(cs.csound()) # Create a new CsoundPerformanceThread, passing in the Csound object
#       pt.play()          # starts the thread, which is now running separately from the main thread. This 
#                         # call is asynchronous and will immediately return back here to continue code
#                         # execution.
#       return (cs, pt)

# send in two arrays of note indeciiss and it will build a set of gliss indeciis to move from one to the other
# for example, chord_1 = np.array([36, 40, 44, 32]), chord_2 = np.array([34, 38, 42, 46]), slide='slide'
# will return four slides for the four notes.
# meanwhile it will increment current_gliss_table with the last table number, and concatenate the gliss tables to stored_gliss

def build_slides(chord_1, chord_2, gliss_type = 'slide'):
      global stored_gliss, current_gliss_table
      assert chord_1.shape == chord_2.shape, logging.debug(f'{chord_1.shape = } is not equal to {chord_1.shape = }. Halting.')
      # logging.debug(f'\nIn build_slides. {stored_gliss.shape = }, {current_gliss_table = }')
      # make a glissando table for all the notes in the two chords (should be 4 per chord for a typical usage)
      new_gliss_tables = np.array([make_ftable_glissando(current_gliss_table + i, gliss_type, ratio_distance(all_ratio_strings[a],all_ratio_strings[b])) for i, (a, b) in enumerate(zip(chord_1, chord_2))])
      # logging.debug(f'after making gliss tables. {new_gliss_tables.shape = }, {[gliss[0] for gliss in new_gliss_tables]}') 
      return_table_nums = np.zeros(new_gliss_tables.shape[0]) # array of table numbers for the incoming chords. returned to caller. 
      inx = 0
      for gliss in new_gliss_tables: # for each of the most recently created slides
            found_one = False
            for stored_fn_array in stored_gliss: # check it against all the ones created previously
                  if np.allclose(stored_fn_array[1:gliss.shape[0]], gliss[1:gliss.shape[0]], rtol=1e-4): # pretty close
                        # logging.debug(f'found a match between this new gliss {gliss[0]} and the stored one {stored_fn_array[0]}')
                        found_one = True
                        gliss[0] = stored_fn_array[0] # save the number in the table array of the old table so you can use it later
                        return_table_nums[inx] = gliss[0] # save the position of the old table so you can return it to the caller
                  else: 
                        pass
                        # logging.debug(f'no match between incoming {gliss[0]} and old one {stored_fn_array[0]}')
            if not found_one:
                  return_table_nums[inx] = gliss[0] # if it's a new one, save its number
                  # logging.debug(f'no match found for incoming {gliss[0] = }.')
            # logging.debug(f'{return_table_nums[inx] = }')
            inx += 1
      # logging.debug(f'all the {return_table_nums = }')      
      # only store the tables that are new. If the table number is small, you don't need to store it because it's already stored
      new_gliss_tables = np.array([gliss for gliss in new_gliss_tables if gliss[0] >= current_gliss_table]) # trim to the new ones
      # already_stored = np.array([gliss for gliss in new_gliss_tables if gliss[0] < current_gliss_table]) # point to old ones
      # logging.debug(f'{new_gliss_tables.size = }') # 
      if new_gliss_tables.size > 0: # we have some to store
            new_tables = new_gliss_tables[:,0] # new tables that need to be stored
            # logging.debug(f'new glissandi to be stored: {new_tables.shape = }, {new_tables = }')
            this_call_tables = np.min((chord_1.shape[0], new_tables.shape[0])) # how many new slides are needed to be saved
            # logging.debug(f'storing {this_call_tables = } new tables')
            # we only want to increment this_call_tables by the new tables, not the ones that were found in older gliss tables.
            current_gliss_table += this_call_tables # add the lesser of the number of notes in chord_1 or chord_2
            pad_size = 70 - new_gliss_tables.shape[1] # subtract the length of the array of values in this table
            pad_gliss = np.ones((this_call_tables, pad_size), dtype = float) # padded with ones, not zeros. Zeros cause it to go to 0 Hz.
            new_gliss_tables = np.concatenate((new_gliss_tables, pad_gliss), axis = 1)
            # logging.debug(f'About to store this set of gliss tables in the stored gliss table.')
            # logging.debug(f'before adding new f tables: {stored_gliss.shape = }') 
            stored_gliss = np.concatenate((stored_gliss, new_gliss_tables))
            
            # logging.debug(f'{stored_gliss.shape = }')
            # logging.debug(f'after adding new f tables: {stored_gliss.shape = }')    
      else: # no new tables. All were found in existing f tables collection
            this_call_tables = 0 
      return return_table_nums 

# this is a function call to build an octave boost mask that can be applied to keep scales always moving up.
# scale is an array of (note,) 
# return a mask that indicates by a 1 that the note should be increased an octave, or a zero that it should not.
# this only works for scales going up. 
def build_scale_mask(scale):
      
      boost_octave = 1
      mask = np.zeros(scale.shape, dtype=int) # assume no increase
      prev_note = ratio_string_to_float(all_ratio_strings[scale[0]]) # this assumes shape in (note,) dangerous
      inx = 0
      boost_remaining = False
      
      for note in scale:
            current_note_ratio = ratio_string_to_float(all_ratio_strings[note])
            if current_note_ratio < prev_note or boost_remaining:
                  if current_note_ratio < prev_note and boost_remaining:
                        boost_octave += 1
                  mask[inx] = boost_octave
                  boost_remaining = True
            prev_note = current_note_ratio
            
            inx += 1
      return (mask)

def retrieve_gliss_tables():
      global stored_gliss, current_gliss_table 
      return stored_gliss, current_gliss_table
  
def init_stored_gliss():
      global stored_gliss, current_gliss_table
      stored_gliss = np.empty((0,70), dtype = float) # each slide is made of 11 values
      # #     - size type start         end
      # [800. 0. 256. -7. 1. 16. 1. 128. 1.125 112. 1.125]
      current_gliss_table = 800
      return stored_gliss

def update_gliss_table(gliss_table, current_gl):
      global stored_gliss, current_gliss_table 
      stored_gliss = gliss_table 
      current_gliss_table = current_gl     
      # logging.debug(f'{stored_gliss.shape = }, {current_gliss_table = }')
      return current_gliss_table
# the functions from here to the end were added on 1/7/23 to reduce the clutter in the notebook.
# I think I have to make this a normal python array instead of a numpy array.
best_rank_inversion_combos = [["A", "A", 1, 2],["A", "A", 1, 4],["A", "A", 2, 1],["A", "A", 2, 3],["A", "A", 3, 2],
    ["A", "A", 3, 4],["A", "A", 4, 1],["A", "A", 4, 3],["A", "B", 1, 1],["A", "B", 1, 4],["A", "B", 2, 1],["A", "B", 2, 2],
    ["A", "B", 3, 2],["A", "B", 3, 3],["A", "B", 4, 3],["A", "B", 4, 4],["B", "A", 1, 1],["B", "A", 1, 2],["B", "A", 2, 2],
    ["B", "A", 2, 3],["B", "A", 3, 3],["B", "A", 3, 4],["B", "A", 4, 1],["B", "A", 4, 4],["B", "B", 1, 2],["B", "B", 1, 4],
    ["B", "B", 2, 1],["B", "B", 2, 3],["B", "B", 3, 2],["B", "B", 3, 4],["B", "B", 4, 1],["B", "B", 4, 3]]

def show_voice_time_short_name(number, voice_time):
    short_name = ''
    voice_num = 0
    for short_name in voice_time:
        if voice_time[short_name]["time_tracker_number"] == number:
            voice_num = voice_time[short_name]["csound_voice"]
            return (short_name, voice_num)

def init_voice_start_times(voice_time):
    for instrument in voice_time:
        voice_time[instrument]["start"] = 0

# This function transforms the note duration field into a start time field. It does this using the voice_time dictionary to keep track of the current time for each voice. In the notebook, it uses a tracking number for the voice number, so in that way it can reuse an instrument several times. Eventually it changes the tracking number in the actual csound voice number in use.

def fix_start_times(note_array, voice_time):
    
    note_num = 0
    start_col = 1
    dur_col = 1
#     hold_col = 2
    voice_col = 6
    for note in note_array: # process the notes one at a time
        voice_name, csound_voice = show_voice_time_short_name(note[voice_col], voice_time) # convert tracker number in the winds array into a 3 letter voice name and csound voice #
        current_time = voice_time[voice_name]["start"] # allows more than one tracking
        voice_time[voice_name]["start"] += note[start_col] # this is the missing piece. must happen even if the note doesn't 
        note_array[note_num, dur_col] = current_time  # overwrite column 1 (duration) with the new start_time
        note_array[note_num, voice_col] = csound_voice # what voice number to use for this tracking number for csound to process.
        note_num += 1 
    return note_array[:note_num,:], voice_time

# build a function table that will create a slide for one voice in a long set of glissandi passing through several different notes
# each ratio distance must compare the desired pitch with the initial pitch, not the previous pitch.
def _build_voice_slide(t_num, one_voice_array, total_slide_size = 2048.0, each_slide_step = 113.0):
    
    start_ratio = 1.0
    slide_steps = one_voice_array.shape[0] 
    logging.debug(f'{one_voice_array.shape = }') # should be 9 notes long
    average_slide_step = total_slide_size // (slide_steps) # 2048 / 9 = 113.5
    assert 0 < each_slide_step < average_slide_step, f'out of range. {each_slide_step = }, {average_slide_step = }'
    each_stay_step = average_slide_step - each_slide_step 
    logging.debug(f'{average_slide_step = }, {each_stay_step = }, {each_slide_step = }')
    # Should be 226, 113, 113, but is actually 
    fn_array = np.array([t_num, 0.0, total_slide_size, -7, start_ratio, each_stay_step, start_ratio])
    sum_of_cents_voice = 0
    initial_note = one_voice_array[0]
    prev_note = initial_note
    max_cents_per_voice = 0.0
    prev_ratio_distance_from_start = 1.0
    ratio_distance_from_start = 1.0
    total_f_steps = 0
    first_note = True
    for current_note in one_voice_array: # for each note one at a time
        if first_note: # we skip the first one, since it is not sliding from anywhere.
            first_note = False
        else:
            ratio_distance_from_start = ratio_distance(all_ratio_strings[initial_note],all_ratio_strings[current_note])
            ratio_distance_from_prev = ratio_distance(all_ratio_strings[prev_note],all_ratio_strings[current_note])
            max_cents_per_voice = np.max((max_cents_per_voice, abs(ratio_to_cents(ratio_distance_from_prev))))
            sum_of_cents_voice += abs(ratio_to_cents(ratio_distance_from_prev))
            # logging.debug(f'{round(prev_ratio_distance_from_start,3) = }, {round(ratio_distance_from_start,3) = }')
            # you need to make sure it doesn't pick the right movement from the initial_note, that is the wrong movement from the prev_note
            # for example, if prev_ratio_distance_from_start = 1.406 and ratio_distance_from_start = 0.75 and the delta is 0.656, that's too far from the previous ratio
            delta_prev_current = abs(prev_ratio_distance_from_start - ratio_distance_from_start)
            if delta_prev_current > .5:
                if prev_ratio_distance_from_start > 1: ratio_distance_from_start *= 2
                else: ratio_distance_from_start /= 2
            # 
            #                        value contour:  ____/⎺⎺\____    ___
            #                                                    \__/
            #                                            120 x.xxx  121 x.xxx
            fn_array = np.append(fn_array, np.array([each_slide_step, ratio_distance_from_start, each_stay_step, ratio_distance_from_start]), axis = None)
            total_f_steps += (each_slide_step + each_stay_step)
            prev_note = current_note
            prev_ratio_distance_from_start = ratio_distance_from_start
    fn_array = np.append(fn_array, np.array([each_stay_step, ratio_distance_from_start]), axis = None)
    # logging.debug(f'{fn_array.shape = }, {[round(item,5) for item in fn_array]}')
    total_f_steps += (each_slide_step + each_stay_step)
    logging.debug(f'{total_f_steps = }')
    # logging.debug(f'{round(sum_of_cents_voice,1) = }, {round(max_cents_per_voice,2) = }')
    return fn_array

# slide bewteen any number of arbitrary chords definded by mode, root, rank, and inversion
def new_multiple_chord_slide(rank, chosen_array, each_slide_step, all_bridge_chords_array):
    global stored_gliss, current_gliss_table
#     stored_gliss_table, current_gliss_table = retrieve_gliss_tables() # retrieve the existing glissando tables from dmu
    rank_num = ord(rank) - 65 # convert "A","B","C","D" into 0,1,2,3 for index into all_bridge_chord_arrays
    array_of_chords = all_bridge_chords_array[rank_num][chosen_array]
    # logging.debug(f'{chosen_array = }, {array_of_chords}') # print the chosen array nine notes and four voices
    voice_count = array_of_chords.shape[0] # should be 4 SATB. This is how many glissandi you are creating
    gliss_f_table = np.array([_build_voice_slide(current_gliss_table + inx, array_of_chords[inx], \
                                     each_slide_step = each_slide_step) for inx in np.arange(voice_count)])
    current_gliss_table = current_gliss_table + voice_count
    pad_size = 70 - gliss_f_table.shape[1] # some zeros needed to pad the gliss table so that all the elements are the same lenth (numpy requirement)
    pad_gliss = np.zeros((4, pad_size), dtype = float)
    gliss_f_table = np.concatenate((gliss_f_table, pad_gliss), axis = 1) 
    stored_gliss = np.concatenate((stored_gliss, gliss_f_table)) # this is a global variable.
    gliss = gliss_f_table[:,0] # these are the four f tables just created
    current_gliss_table = update_gliss_table(stored_gliss, current_gliss_table)
    notes = array_of_chords.T[0,:] # just the first note for each instrument
    return notes, gliss

def masked_notes_by_voice(notes_features, voices, density_function, voice_time):
    voice_num = np.unique(np.array([voice_time[short_name]["csound_voice"] for short_name in voices])) # transform an array of voice short names into unique csound voice number
    logging.debug(f'{voice_num = }, {voices = }, {density_function.shape = }, {notes_features.shape = }')
    vel_col = 5
    oct_col = 5 
    voice_col = 6

    is_voice = 0
    not_voice = 0
    zero_oct = 0

    for inx in np.arange(notes_features.shape[0]):
        if density_function[inx] > 0.99: 
            density_function[inx] = 0.98 # can't allow a probability > 1
        elif density_function[inx] < 0.001: # nor less than zero
            density_function[inx] = 0.001            
        #  current values of density_function are set between 0 and almost 1
        #  choose between 0 and 1, return 1 number, with probability of being zero is 1 - current value, and the probability being one is the current value of the density function
        if notes_features[inx][voice_col] in voice_num: # is this note in this instrument group?
            is_voice += 1
            if rng.choice([True, False], size = None, p = [1 - density_function[inx], density_function[inx]]):  # each note can have it's own probability of being zero
                notes_features[inx][oct_col] = 0 # if the probability is right, zero out the octave.
                zero_oct += 1
        else:
            not_voice += 1
    logging.debug(f'{not_voice = }, {is_voice = }, {zero_oct = }')
    return(notes_features)
     

def masked_notes_features(note_array, density_function):
    assert note_array.shape[0] == density_function.shape[0], logging.debug(f'unequal dimensions between the note_array and the density_function. {note_array.shape = }, {density_function.shape = }')
    # fill an array with zeros and ones, with more of one than the other based on density
    # I want a different probability for every note in the array, based on the percentage chance in density function.
    # density function will be exactly as long as the note array. (same shape[0])
    # I want a mix_mask that has either zero or one, but the choice will favor ones when the density function for that note is high (1.0)
    # and if the density function for the note is low (0.2) then the likelihood is low.
    hold_column = 2
    mix_mask = np.zeros(note_array.shape[0])
    for inx in np.arange(note_array.shape[0]):
        if density_function[inx] > 0.99: density_function[inx] = 0.98 # can't allow a probability > 1
        mix_mask[inx] = rng.choice(np.arange(2), size = 1, p = [1 - density_function[inx], density_function[inx]]) # each note can have it's own probability of being zero
    # once you've built the mask, then apply it to the hold values
    note_array[:,hold_column] = note_array[:,hold_column] * mix_mask # multiply hold values by zeros and ones to erase a percent of the notes
    # logging.debug(f'{note_array.shape = }\n{mix_mask.shape = }, {mix_mask[:5] = }')
    return note_array

def masked_voices_notes(octave_array, density_function):
    # ensure the notes dimensions of the octave_array and the single dimension of the density_function are identical
    assert octave_array.shape[1] == density_function.shape[0], logging.debug(f'unequal dimensions between the note_array and the density_function. {octave_array.shape = }, {density_function.shape = }')
    mix_mask = np.zeros(octave_array.shape[0]) # create a mask of (voices, notes) shape, but process all the voices with the same element of the density_function array (shape[notes])
    for inx in np.arange(octave_array.shape[0]):
            mix_mask[inx] = rng.choice(np.arange(2), size = None, p = [1 - density_function[inx], density_function[inx]]) # each note can have it's own probability of being zero
    # once you've built the mask of zeros and ones, based on the probabilities in density_function, apply it to the octave values
    octave_array = octave_array * mix_mask # multiply octave values by zeros to erase a percent of the notes
    return octave_array

def send_to_csound_file(notes_features, voice_time, path_to_input, path_to_output = "new_output.csd", \
            limit = 0, tempos = '', print_only = 10, tempo = 60):
      # logging.debug(f'{limit = }, {tempo = }')
      global stored_gliss, current_gliss_table
      if limit == 0: 
           limit = np.max([voice_time[inst]["start"] for inst in voice_time])
           logging.debug('will write all notes to csound file')
      else:
           logging.debug(f'limit to writing to csound file is set at {limit = }')
      logging.debug(f'last note ends: {round(60*limit/tempo,1) = } seconds')
      csd_content, lines = load_csd(path_to_input, strip_f0 = True)
      logging.debug(f'read from {path_to_input}. {lines = }')
      f = open(path_to_output, 'w')
      f.write(csd_content)
      f.write('\n')
      # Write out the accumulated glissando ftables to the csound file after the csd_content string
      # gliss_tables, current_gliss_table = retrieve_gliss_tables() # stored_gliss, current_gliss_table
      # logging.debug(f'{gliss_tables.size = }, {current_gliss_table = }')
      if stored_gliss.size > 0:
            for row in stored_gliss: # pass all the saved f tables for slides and trills to csound
                  f.write('f ')
                  for item in row:
                        f.write(str(item) + ' ')
                  f.write('\n')
      logging.debug(f'before selecting non-zero hold values. {notes_features.shape = }')
      notes_features = np.array([row for row in notes_features if row[2] > 0]) # only include those with a non-zero hold values
      logging.debug(f'In send_to_csound_file after selecting for non-zero hold values. {notes_features.shape = }')
      notes_features = np.array([row for row in notes_features if row[5] > 0]) # only include those with a non-zero octave values      
      logging.debug(f'after selecting for non-zero octave values. {notes_features.shape = }')
      perturb = tempo / 6000
      logging.debug(f'{perturb = }')
      z_range = np.linspace(-perturb, perturb, 50)
      max_z = 0
      min_z = 0
      start_time_col = 1
      for row in notes_features: # add a perturbation time to each note.
            z = rng.choice(z_range) 
            max_z = np.max((z, max_z))
            min_z = np.min((z, min_z))
            duration = row[start_time_col] + z
            if duration < 0: duration = abs(duration)
            row[start_time_col] = duration
      
      # sort the array by start time
      notes_features = notes_features.tolist() # I hate the numpy sort function. It fails to keep the rows together. 
      notes_features.sort(key = lambda x: x[start_time_col]) # python list sort is what I want. by column # 1 start time.
      notes_features = np.array(notes_features)
      logging.debug(f'after sorting by start time. {notes_features.shape = }')
      logging.debug(f'{print_only = }')
      logging.debug(f' 1\t2\t3\t4\t5\t6\t7\t8\t9\t0\t11\t12\t13\t14')
      logging.debug(f'Sta\tHold\tVel\tTon\tOct\tVoi\tSte\tEn1\tGls\tUps\tRen\t2gl\t3gl\tVol')
      #  0        1      2    3     4     5     6     7     8     9     10    11    12    13    14
      # ;Inst	Sta	Hold	Vel	Ton	Oct	Voi	Ste	En1	Gls	Ups	Ren	2gl	3gl	Vol
      for notes in notes_features[:print_only]:
            logging.debug(f'{round(notes[1],2)}\t{round(notes[2],2)}\t{round(notes[3],2)}\t{notes[4]}\t{notes[5]}\t{notes[6]}\t{notes[7]}\t{notes[8]}\t{notes[9]}\t{notes[10]}\t{notes[11]}\t{notes[12]}\t{notes[13]}\t{round(notes[14],3)}')
      f.write(f';Inst\tSta\tHold\tVel\tTon\tOct\tVoi\tSte\tEn1\tGls\tUps\tRen\t2gl\t3gl\tVol\n')
      rows_written = 0
      for notes in notes_features:
            if notes[1] < limit:
                  f.write('i ')
                  for inx, feature in zip(count(0,1), notes):
                        if inx in ([1,2,14]): 
                             f.write(str(feature) + f'\t') # floating point values for start, hold, volume only
                        else: 
                             f.write(str(int(round(feature,0))) + f'\t')
                  f.write('\n')
            rows_written += 1
      if tempos != '':
            f.write(tempos)
            f.write('\n')
      f.write('</CsScore>\n')
      f.write('</CsoundSynthesizer>\n')
      f.write('\n')
      f.close()
      logging.debug(f'{rows_written = }')
      logging.debug(f'{round(min_z,5) = }, {round(max_z,5) = }')  
      return(notes_features)

def build_density_function(y, points):
    x = np.arange(y.shape[0])
    spline = make_interp_spline(x, y)
    X_ = np.linspace(x.min(), x.max(), points)
    return spline(X_)

def format_seconds_to_minutes(sec, n_msec=3):
      # Convert seconds to D days, HH:MM:SS.FFF
      # if hasattr(sec,'__len__'): return [sec2time(s) for s in sec]
      # logging.debug(f'in format_seconds_to_minutes. {sec = }, {n_msec = }')
      m, s = divmod(sec, 60)
      h, m = divmod(m, 60)
      d, h = divmod(h, 24)
      if n_msec > 0:
            pattern = '%%02d:%%02d:%%0%d.%df' % (n_msec+3, n_msec)
      else:
            pattern = r'%02d:%02d:%02d'
      if d == 0:
            return pattern % (d, m, s)
      return (pattern) % (m, s)

# pass a set of parameters and get back an array of notes
def root_chord_slide(mode, root, combo, gliss_type):
    # Build two chords and slide from the first to the second. Return the initial chord and the slide to reach the second chord                                                    
    tones_1 = build_chords(mode, root, combo[0], combo[2]) # get four notes
    tones_2 = build_chords(mode, root, combo[1], combo[3])
    gliss = build_slides(tones_1, tones_2, gliss_type = gliss_type) 
    # logging.debug(f'{tones_1 = }, {tones_2 = }, {gliss = }')
    return (tones_1, gliss)

def masked_by_pattern(octave_array, pattern):
    # ensure the notes dimensions of the octave_array and the single dimension of the density_function are compatible
    # old method:
    pattern = pattern[:octave_array.shape[0],:] # make the pattern smaller to match the number of voices in the input chorale
    skip = 1
    for i in range(0, octave_array.shape[1] // pattern.shape[1], skip): # 0,notes // mask slots by skip
        start = i * pattern.shape[1] 
        end = (i + 1) * pattern.shape[1] 
        logging.debug(f'{start = }, {end = }')
        octave_array[:,start:end] = pattern * octave_array[:,start:end] # so here is where the mask is broadcasting all voices in the mask
    return octave_array

def piano_roll_to_notes_features(note_array, volume_array, instruments, time_per_note, voice_time): 
      # this function identifies identical adjacent notes and replaces them with one note with duration equal to the sum of the duration value of the identical adjacent notes.
      # Assign duration, hold, instruments, envelopes, and volumes to notes.
      # Starts with a piano_roll type structure of (initial 6 features (noguev), voices, notes). 
      # the number of voices must equal the instruments.shape[0]
      # the number of notes is variable
      num_inst = instruments.shape[0]
      logging.debug(f'in piano_roll_to_notes_features. {volume_array.shape = }, {volume_array[:20] = }')
      num_notes = note_array.shape[1] * note_array.shape[2]
      logging.debug(f'in piano_roll_to_notes_voices. Total notes to process: {note_array.shape = }, {num_notes = }')
      prev_note = np.zeros((7), dtype = int)
      max_dur = 0
      max_hold = 0
      notes_features = np.zeros((num_notes, 15), dtype = float) 
      output_inx = 0 # index to the output (notes, features) 
      input_voice_inx = 0
      for verse_array, octave_array, gliss_array, upsample_array, env_array, velocity_array in list(zip(*note_array)):
            input_note_inx = 0
            # logging.debug(f'{input_note_inx = }, {output_inx = }')
            voice_name = instruments[input_voice_inx % num_inst] # three letter voice name
            voice_num = voice_time[voice_name]["time_tracker_number"] # the fake number used to keep track of the start times. Later changed to the csound voice number
            duration = time_per_note
            hold = time_per_note
            first = True
            for note, octv, glx, upx, envx, velx, volx in zip(verse_array, octave_array, gliss_array, upsample_array, env_array, velocity_array, volume_array):
                  if first:
                        prev_note = (note, octv, glx, upx, envx, velx, volx)
                        first = False
                  elif (note, octv, glx, upx, envx, velx, volx) == prev_note:
                        duration += time_per_note  
                        hold += time_per_note 
                  else: # send the note to the (notes, features) array
                        stereo = rng.integers(low = 1, high = 17) # locate in stereo field randomly
                        if duration < 0: 
                             duration = abs(duration)
                        notes_features[output_inx] = np.array((1, duration, hold * 1.01, prev_note[5], prev_note[0], prev_note[1], voice_num, stereo, prev_note[4], prev_note[2], prev_note[3], prev_note[4], 0, 0, prev_note[6]))
                        output_inx += 1
                        max_dur = np.max((max_dur, duration))
                        max_hold = np.max((max_hold, hold))
                        duration = time_per_note 
                        hold = time_per_note
                        #       0      1    2    3    4     5     6
                  prev_note = (note, octv, glx, upx, envx, velx, volx)
                  input_note_inx += 1 
                  # logging.debug(f'{input_note_inx = }, {output_inx = }')
                  
            # send the last note in the voice to the output array
            stereo = rng.integers(low = 1, high = 17) # locate in stereo field randomly
            #                                      1, dur,           hol, vel,            note,             octv,  voice,      stereo
            notes_features[output_inx] = np.array((1, duration, hold * 1.01, prev_note[5], prev_note[0], prev_note[1], voice_num, stereo, \
                                    # env        gls1         upsample     r env     2nd   3rdgl volume
                              prev_note[4], prev_note[2], prev_note[3], prev_note[4], 0, 0, prev_note[6]))
            output_inx += 1
            input_voice_inx += 1
            # logging.debug(f'{input_voice_inx = }, {output_inx = }')
      return (notes_features[:output_inx])

def _parse(word, prev_note, prev_oct, prev_gls, prev_ups, prev_env, prev_vel, prev_dur):
    if word.find("n") == -1: note_value = prev_note # if it's not found python returns -1
    else: 
        digit_len = 1
        for inx in np.arange(1, len(word)):
            if word.find("n") + inx >= len(word): pass
            elif word[word.find("n") + inx].isdigit(): digit_len += 1
            else: break
        note_value = word[word.find("n") + 1:  word.find("n") + digit_len]
        
    if word.find("o") == -1: oct_value = prev_oct
    else: 
        digit_len = 1
        for inx in np.arange(1, len(word)):
            if word.find("o") + inx >= len(word): pass
            elif word[word.find("o") + inx].isdigit(): digit_len += 1
            else: break
        oct_value = word[word.find("o") + 1:  word.find("o") + digit_len]
        
    if word.find("d") == -1: dur_value = prev_dur
    else: 
        digit_len = 1
        for inx in np.arange(1, len(word)):
            if word.find("d") + inx >= len(word): pass
            elif word[word.find("d") + inx].isdigit(): digit_len += 1
            else: break
        dur_value = word[word.find("d") + 1:  word.find("d") + digit_len]
        
    if word.find("e") == -1: env_value = prev_env
    else: 
        digit_len = 1
        for inx in np.arange(1, len(word)):
            if word.find("e") + inx >= len(word): pass
            elif word[word.find("e") + inx].isdigit(): digit_len += 1
            else: break
        env_value = word[word.find("e") + 1:  word.find("e") + digit_len]
    
    if word.find("v") == -1: vel_value = prev_vel
    else: 
        digit_len = 1
        for inx in np.arange(1, len(word)):
            if word.find("v") + inx >= len(word): pass
            elif word[word.find("v") + inx].isdigit(): digit_len += 1
            else: break
        vel_value = word[word.find("v") + 1:  word.find("v") + digit_len]
      
    if word.find("u") == -1: ups_value = prev_ups
    else: 
        digit_len = 1
        for inx in np.arange(1, len(word)):
            if word.find("u") + inx >= len(word): pass
            elif word[word.find("u") + inx].isdigit(): digit_len += 1
            else: break
        ups_value = word[word.find("u") + 1:  word.find("u") + digit_len]

    if word.find("g") == -1: gls_value = prev_gls
    else: 
        digit_len = 1
        for inx in np.arange(1, len(word)):
            if word.find("g") + inx >= len(word): pass
            elif word[word.find("g") + inx].isdigit(): digit_len += 1
            else: break
        gls_value = word[word.find("g") + 1:  word.find("g") + digit_len]
    
    return(note_value, oct_value, gls_value, ups_value, env_value, vel_value, dur_value)
    
def _arrays_from_text(input, prev_note = 0, prev_oct = 4, prev_gls = 0, prev_ups = 0, prev_env = 1, prev_vel = 75, prev_dur = 4, shuffle = False):
      input_list = np.array(np.char.split(input,sep=" ").tolist()) # convert a text string to a set of space separated tokens
      notes = np.empty(0, dtype = int)
      octv = np.empty(0, dtype = int)
      gls = np.empty(0, dtype = int)
      ups = np.empty(0, dtype = int)
      env = np.empty(0, dtype = int)
      vel = np.empty(0, dtype = int)
      if shuffle: 
          logging.debug(f'{shuffle = }')
          len_list = len(input_list)
          order = rng.choice(np.arange(len_list), size = len_list, replace = False)
          input_list = input_list[order]
      for word in input_list:
            prev_note, prev_oct, prev_gls, prev_ups, prev_env, prev_vel, prev_dur  = \
                  _parse(word, prev_note, prev_oct, prev_gls, prev_ups, prev_env, prev_vel, prev_dur)
            for value in [prev_note, prev_oct, prev_gls, prev_ups, prev_env, prev_vel, prev_dur]:
                  assert value != '', f'{word = }. There is a missing value for one of the fields'
            for note in np.arange(int(prev_dur)): # once for every time step in the voices, notes array
                  notes = np.append(notes, int(prev_note))
                  octv = np.append(octv, int(prev_oct))
                  gls = np.append(gls, int(prev_gls))
                  ups = np.append(ups, int(prev_ups))
                  env = np.append(env, int(prev_env))
                  vel = np.append(vel, int(prev_vel))
      input_reconstructed = ""
      current_dur = 0
      prev_features = (notes[0], octv[0], env[0], vel[0], ups[0], gls[0])
      for features in zip(notes, octv, gls, ups, env, vel):
            if features != prev_features:
                  input_reconstructed = input_reconstructed +\
                        "n" + str(prev_features[0]) + "o" + str(prev_features[1]) + "g" + str(prev_features[2]) + "u" + str(prev_features[3]) + "e" + str(prev_features[4]) + "v" + str(prev_features[5]) + "d" + str(current_dur) + " "
                  prev_features = features
                  current_dur = 1
            else: current_dur += 1
      input_reconstructed = input_reconstructed +\
                        "n" + str(prev_features[0]) + "o" + str(prev_features[1]) + "g" + str(prev_features[2]) + "u" + str(prev_features[3]) + "e" + str(prev_features[4]) + "v" + str(prev_features[5]) + "d" + str(current_dur) + " "
                  
      return notes, octv, gls, ups, env, vel, input_reconstructed[:-1] # return all but the last space in the string

# These are helper functions that allow the calling of arrays_from_text without getting unnecessary results back.
def fill_out_text(input):
      _, _, _, _, _, _, input_reconstructed = _arrays_from_text(input)
      # logging.debug(f'{input_reconstructed = }')
      return input_reconstructed
            
def text_to_features(input, shuffle = False):
      notes, octv, gls, ups, env, vel, _ = _arrays_from_text(input, shuffle = shuffle)	
      if shuffle: logging.debug(f'after shuffle: {notes = }')
      return notes, octv, gls, ups, env, vel

def choose_trill_type(repeat_notes):
    # valid repeat_each_note values are [2,3,4,5,6,7,8,9,10,12,14,16]
    # select if random number is greater than:
    prefer_flat = .75
    prefer_trill = .60 # repeat_each_note
    logging.debug(f'in choose_trill_type. {repeat_notes = }')
    if rng.random() > prefer_flat:
        trill_type = 'flat'
    if repeat_notes in [6,12,18]:
        if rng.random() > prefer_trill:
            trill_type = "trill_6_step"
        else: trill_type = 'cubic64_64_128'
    elif repeat_notes in [16,24]:
        if rng.random() > prefer_trill:
            trill_type = "trill_8_step"
        else: trill_type = 'cubic64_64_128'
    elif repeat_notes in [3,9,15,21]:
        if rng.random() > prefer_trill:
            trill_type = "trill_3_step"
        else: trill_type = 'cubic64_64_128'
    elif repeat_notes in [2,10,14,20,22]:
        if rng.random() > prefer_trill:
            trill_type = "trill_2_step"
        else: trill_type = 'cubic64_64_128'
    elif repeat_notes in [4, 8]:
        if rng.random() > prefer_trill:
            trill_type = "trill_4_step"
        else: trill_type = 'cubic64_64_128'
    else: trill_type = "trill_1_step"
    logging.debug(f'{trill_type}')
#     logging.debug(" ")
    return trill_type

# find the largest number evenly divisible into the array_size, starting a max number and moving down until you find one.
def largest_evenly_divisible(array_size, max_number): 
    for inx in np.arange(max_number, 0, -1):
        if array_size // inx == array_size / inx:
            return inx

def mask_array(octave_array, mask):
    # logging.debug(f'In mask array. {mask.shape = }, {octave_array.shape = }')
    mask = np.tile(mask, (octave_array.shape[0] // mask.shape[0], octave_array.shape[1] // mask.shape[1])) # make the mask the same size as the octave_array
    # logging.debug(f'{mask.shape = }')
    return octave_array * mask

def build_bass_line(repeat_section, notes, octave_array, gls, ups_array, envelope_array, vel_array,\
                  mask, voices, mode = "oton", root = "16/9", rank = "A"):
    
    scale = build_scales(mode, root, rank)
    note_array = np.array([scale[note] for note in notes]) # convert from positions int eh scale to positions in the total array of 256 notes.

    note_array = np.tile(note_array, (voices, 1)) # make more voices by repeating by voices
    octave_array = np.tile(octave_array, (voices, 1)) # make more voices
    gliss_array = np.tile(gls, (voices, 1)) # make more voices
    ups_array = np.tile(ups_array, (voices, 1)) # make more voices
    envelope_array = np.tile(envelope_array, (voices, 1))
    vel_array = np.tile(vel_array, (voices, 1)) # make more voices by repeating by voices
    logging.debug(f'{np.max(vel_array) = }')

    # [2:4] is the voice for the baritone guitar, which might be an octave above the finger piano bass
    bar_guitar_voices = np.arange(3,4) # was (2,4)
    octave_array[bar_guitar_voices] += rng.choice([0, 1], size = None, p = [0.7, 0.3])  # <-- changed from [0.1, 0.9] to [0.6, 0.4] tp [0.8, 0.2]
    octave_array = mask_array(octave_array, mask)  # set some octaves to zero to make them silent
    note_array = np.stack((note_array, octave_array, gliss_array, ups_array, envelope_array, vel_array), axis = 0)
    logging.debug(f'after stacking in build_bass_line. {note_array.shape = }')
    note_array = np.array([np.roll(note_array, rng.choice([-16, -8, 0, 8, 16], size = None), axis = 2)\
                  for _ in np.arange(repeat_section)])
    logging.debug(f'after roll by {repeat_section = }: {note_array.shape = }')
    # logging.debug(f'after rolls. {note_array.shape}')
    #
    #
    # 
    logging.debug('in build_bass_line')
    concat_array = np.empty((6, voices, 0), dtype = int)  
    for inx in np.arange(repeat_section): 
        logging.debug(f'{note_array[inx].shape = }')
        concat_array = np.concatenate((concat_array, note_array[inx]), axis = 2)
    #
    #
    #
    
    logging.debug(f'{concat_array.shape = }')
    return concat_array

def thin(arr):
      # this function is designed to convert a list of notes into just the notes that are different
      # for example, if we want to slide across several notes, such as 1,1,2,2,5,3,3,3 this will convert that to 1,2,5,3
      # so that I can calculated a slide across those notes.
      #     logging.debug(f'in thin. {type(arr) = }')
      #     logging.debug(f'{arr.shape = }')
    
    target = np.zeros(arr.shape, dtype = int)
    prev = arr[0]
    inx = 0
    for element in arr:
        if element != prev:
            target[inx] = prev
            inx += 1
        prev = element
    target[inx] = prev
    inx += 1
    return target[:inx]

def build_horn_from_text(repeat_section, note_array, octave_array, gliss_array, ups_array, envelope_array, vel_array,\
                        voices, mode = "oton", root = "16/9", rank = "A",\
                        roll_low = -3, roll_high = 4, likelihood = .65, octave_shift = 0, vel_echo_max = 7, each_slide_step = 240): 
      logging.debug(f'{roll_low = }, {roll_high = }, {likelihood = }, {octave_shift = }, {vel_echo_max = }, {each_slide_step = } ')
      # current_gliss_table: what the next table number created should be
      # stored_gliss: collection of all the slides asked for so far
      global stored_gliss, current_gliss_table
      logging.debug(f'in build_horn_from_text. variable shapes: {voices = }')
      #                             [(8, 48),    (8, 48),     (8, 48),        (8, 48),   (8, 48),    (4, 48)
      logging.debug([var.shape for var in [note_array, octave_array, envelope_array, vel_array, ups_array, gliss_array]])
      # control to volume decrease on every repeat_section
      vel_col = 5
      oct_col = 1
      # Major alteration 1/19/23 - 2/2/23 to process the glissandi in the text input strings and fix a bunch of bugs

      scale = build_scales(mode, root, rank)
      notes_in_scale = scale[note_array] # these will change for those notes that are gliding by f table
      original_scale = scale[note_array] # these will be saved to send to _build_voice_slide
      logging.debug(f'{notes_in_scale.shape = }, {original_scale.shape = }')
      voice = 0
      # process each voice in the array.
      for notes, org_notes, octv, env, vel, ups, gls in \
            zip(notes_in_scale, original_scale, octave_array, envelope_array, vel_array, ups_array, gliss_array):
            # if np.max(gls) > 0:
            #       stored_gliss_table, current_gliss_table = retrieve_gliss_tables()
            logging.debug(f'{np.max(gls) = }, {stored_gliss.shape = }, {current_gliss_table = }')
            logging.debug(f'processing a stream: {[var.shape for var in [notes, org_notes, octv, env, vel, ups, gls]]}')
            inx = 0
            slide_sections = 0
            slide_locations = np.zeros(notes.shape, dtype = int) # we don't know how many different slide slots there will be in this set
            while inx < notes.shape[0]:
                  if gls[inx] > 0: # we need to calculate a slide for this slot
                        notes[inx:inx + gls[inx]] = notes[inx] # assign the value of the first note to all of the notes in this slide
                        slide_locations[slide_sections] = inx
                        slide_sections += 1
                        inx += gls[inx] # skip over the remaining slots
                  else: inx += 1
            logging.debug(f'{slide_sections = }')
            logging.debug(f'{slide_locations[:slide_sections] = }')
            end = 0
            for loc in np.arange(slide_sections): # count of the slide sections discovered earlier
                  start = slide_locations[loc] # the start of the slide set
                  length = gls[slide_locations[loc]] # the length of the slide set
                  logging.debug(f'{start = }, {end = }')
                  if start > end: # you need to process the first part that doesn't include a slide
                        # logging.debug(f'keep this section discrete: {notes[end:start] = }')
                        # notes_in_scale[end:start] already has the correct notes
                        pass
                  end = start + length
                  logging.debug(f'{start = }, {end = }')
                  logging.debug(f'build a glide over this section: {thin(org_notes[start:end]) = }')
                  gliss_f_table = _build_voice_slide(current_gliss_table + 1, thin(org_notes[start:end]), each_slide_step = each_slide_step)
                  logging.debug(f'{gliss_f_table.shape = }')
                  if gliss_f_table.shape[0] > 17:
                       check_slide_points = [4,8,12,16,20]
                  elif gliss_f_table.shape[0] > 13:
                       check_slide_points = [4,8,12,16]
                  elif gliss_f_table.shape[0] > 9:
                       check_slide_points = [4,8,12]
                  else: check_slide_points = [4,8]
                  logging.debug(f'{check_slide_points = }')
                  notes_in_scale[start:end] = org_notes[start] # for a slide you only need the initial note but it needs to populate from [start:end]
                  #
                  # here is where you need to check if this exact slide has already been created.
                  #
                  found_one = False
                  for stored_fn_array in stored_gliss: # check it against all the ones created previously
                        if np.allclose(stored_fn_array[1:gliss_f_table.shape[0]], gliss_f_table[1:gliss_f_table.shape[0]], rtol=1e-4): # pretty close
                             logging.debug(f'Found a match. {gliss_f_table[check_slide_points] = }')
                             logging.debug(f'matches {stored_fn_array[check_slide_points] = }')
                             found_one = True
                             gls[start:end] = stored_fn_array[0] # point to the existing ftable number
                        if found_one: break # don't look at the remaining ones
                  if not found_one: # if it doesn't exist you must create it
                        current_gliss_table += 1
                        gls[start:end] = gliss_f_table[0] # the number of the f table stored in all the slots that are in the set
                        # logging.debug(f'after moving the f table number to the slots in {gls = }')
                        # dur = length # how long should the note be held - for how many ticks
                        pad_size = 70 - gliss_f_table.shape[0]
                        pad_gliss = np.zeros((pad_size), dtype = float)
                        # assign different values to the ups array based on the direction and magnitude of the slide.
                        gliss_f_table = np.concatenate((gliss_f_table, pad_gliss), axis = 0) 
                        logging.debug(f'{gliss_f_table[[0,4,8,12,16]] = }')
                        if gliss_f_table[4] > 1.1 or gliss_f_table[8] > 1.1 or gliss_f_table[12] > 1.1:
                              ups[start:end] += 1
                              if np.all(ups[start:end] > 255): ups[start:end] = 0
                              if gliss_f_table[4] > 1.2 or gliss_f_table[8] > 1.2 or gliss_f_table[12] > 1.2:
                                    ups[start:end] += 1
                                    if np.all(ups[start:end] > 255): ups[start:end] = 0
                        if gliss_f_table[4] < 0.9 or gliss_f_table[8] < 0.9 or gliss_f_table[12] < 0.9:
                              ups[start:end] = 255
                              if gliss_f_table[4] < 0.8 or gliss_f_table[8] < 0.8 or gliss_f_table[12] < 0.8:
                                    ups[start:end] -= 1
                                    if np.all(ups[start:end] < 0): ups[start:end] = 255
                        gliss_f_table = np.reshape(gliss_f_table, (1, 70))
                        logging.debug(f'prior to updating the stored_gliss variable. {gliss_f_table.shape = }, {stored_gliss.shape = }')
                        # only do this is the slide is novel
                        stored_gliss = np.concatenate((stored_gliss, gliss_f_table), axis = 0) 
                        logging.debug(f'after updating the stored_gliss variable. {current_gliss_table = }, {stored_gliss.shape = }')
            if end < notes.shape[0]: 
                   pass
            logging.debug(f'process last part of the stream: {[var.shape for var in [notes, original_scale, octv, env, vel, ups, gls]]}')
            logging.debug(f'{notes_in_scale.shape = }, {voice = }, {notes.shape = }')
            gliss_array[voice] = gls
            logging.debug(f'{gliss_array.shape = }')
            ups_array[voice] = ups
            voice += 1
            logging.debug(f'{voice = }')

      # something happens to the gliss numbers between here and the end of this function to make them into 
      logging.debug(f'Make sure these are all the same shape: {[var.shape for var in [notes_in_scale, octave_array, gliss_array, ups_array, envelope_array, vel_array]]}')
      note_array = np.stack((notes_in_scale, octave_array, gliss_array, ups_array, envelope_array, vel_array), axis = 0)
      logging.debug(f'after stacking. {note_array.shape = }') # (6, 4, 64)
      rolls = np.array([rng.integers(low = roll_low, high = roll_high, size = None) for inx in np.arange(repeat_section)])
      note_array = np.array([np.roll(note_array, r, axis = 2) for r in rolls]) # this adds a dimension of repeat_section onto the start of the array
      logging.debug(f'after rolls. {rolls = }, {note_array.shape = }, {repeat_section = }, {octave_shift = }')  # note_array.shape = (3, 6, 4, 64)
      concat_array = np.empty((6, voices, 0), dtype = int)  
      logging.debug(f'gliss values after roll: {np.max(note_array[:,2,:,:]) = }') # they are the expected values of either 0 or 800+
      for inx in np.arange(repeat_section): 
            note_array[inx, vel_col] -= inx * rng.integers(4, high = vel_echo_max) # decrease the velocity with each repetition. 
            logging.debug(f'repeats, features, voices, notes. {note_array.shape = }') 
            if octave_shift > 0: 
                  # for octave_shift = 2, returns -1, 0, 1, 2
                  new_octave = rng.integers((-1 * octave_shift + 1), high = octave_shift, endpoint = True) 
            else: 
                  new_octave = 0
            for inx2 in np.arange(note_array.shape[3]):
                  if note_array[inx, oct_col, 0, inx2] > 0: # don't alter octave if you've already masked it to zero in the text input.
                        note_array[inx, oct_col, :, inx2] += new_octave
                        if rng.random() < 1 - likelihood: # if likelihood = .99, is random() less than 0.01, then mask to zero
                              note_array[inx, oct_col, :, inx2] = 0
            logging.debug(f'{inx = }, {concat_array.shape = }, {note_array[inx].shape = }') 
            concat_array = np.concatenate((concat_array, note_array[inx]), axis = 2)
      logging.debug(f'after concatenation: {concat_array.shape = }') # (6, 8, 96)
      logging.debug(f'gliss values after concatenation: {np.max(concat_array[2,:,:]) = }') # they are the expected values of either 0 or 800+
      return concat_array

def build_arpeggio_part(repeat_section, repeat_notes, repeat_all, octave_array, envelope_array, mask, voices, mode = "oton", root = "16/9", rank = "A"):
    logging.debug(f'in build_arpeggio_part. {mode = }, {root = }, {rank = }')
    combo_set = rng.choice(np.arange(8, 8 + repeat_section, 1), size = repeat_section, replace = False) # create repeat_section pairs of chords 
    note_array = np.array([(build_chords(mode, root, best_rank_inversion_combos[combo][0], best_rank_inversion_combos[combo][2]), \
                            build_chords(mode, root, best_rank_inversion_combos[combo][1], best_rank_inversion_combos[combo][3])) \
                            for combo in combo_set])
    note_array = note_array.reshape(2 * repeat_section, -1).T
#     logging.debug(f'created original with {repeat_section = }. {note_array.shape = }')
    note_array = np.repeat(note_array, repeat_notes, axis = 1)
    # logging.debug(f'repeated notes by {repeat_notes = }. {note_array.shape = }')
    if voices > 4: 
        note_array = np.tile(note_array, (voices // 4, 1))
   
    octave_array = mask_array(octave_array, mask)  # set some octaves to zero to make them silent
    envelope_array = np.tile(envelope_array, (voices, 1))
    gliss_array = np.full(note_array.shape, 0, dtype = int)
    ups_array = np.full(note_array.shape, 1, dtype = int)
    vel_array = np.full(note_array.shape, 70, dtype = int)
    # logging.debug('About to stack features. shapes:')
    shapes = [arr.shape for arr in [note_array, octave_array, envelope_array, gliss_array, ups_array, vel_array]]
    logging.debug(f'shapes of arpeggio section: {shapes = }')
    note_array = np.stack((note_array, octave_array, gliss_array, ups_array, envelope_array, vel_array), axis = 0)
    # logging.debug(f'prior to tile. {note_array.shape = }')
    note_array = np.tile(note_array, (repeat_all,1))
    logging.debug(f'after tile. {note_array.shape = }')
    return note_array

def build_bass_flute_part(repeat_section, repeat_notes, repeat_all, octave_array, envelope_array, voices, mode = "oton", root = "16/9", rank = "A"):
    
    combo_set = rng.choice(np.arange(8, 8 + repeat_section, 1), size = repeat_section, replace = False) # create repeat_section pairs of chords (
    note_gliss_array = np.array([root_chord_slide(mode, root, best_rank_inversion_combos[combo], choose_trill_type(repeat_notes))\
                            for combo in combo_set])
    
    logging.debug(" ")
    note_array = note_gliss_array[:,0,:]
    gliss_array = note_gliss_array[:,1,:] 
    note_array = note_array.T
    gliss_array = gliss_array.T
    note_array = np.repeat(note_array, repeat_notes, axis = 1) # repeat_notes = 8 yields (4,16)
    gliss_array = np.repeat(gliss_array, repeat_notes, axis = 1) # repeat_notes = 8 yields (4,16)
    
    if voices > 4: 
        logging.debug(f'{voices = }, {voices // 4 = }')
        note_array = np.tile(note_array, (voices // 4, 1))
        gliss_array = np.tile(gliss_array, (voices // 4, 1))
        logging.debug(f'created more voices. {note_array.shape = }')
    
    ups_array = np.full(note_array.shape, 1, dtype = int)
    vel_array = np.full(note_array.shape, 71, dtype = int)
    note_array = np.stack((note_array, octave_array, gliss_array, ups_array, envelope_array, vel_array), axis = 0)
    note_array = np.tile(note_array, (repeat_all ,1))
    
    return note_array

def log_notes(notes, octv, gls, ups, env, vel, limit = 200):
    d = 0
    sum_d = 0
    pn = -1
    po = -1
    pg = -1
    pu = -1
    pe = -1
    pv = -1
  
    logging.debug(f'inx\tn\to\tg\tu\te\tv\td')
    first = True
    inx = 0
    for n, o, g, u, e, v in zip(notes, octv, gls, ups, env, vel):
        if first: 
            d += 1
            first = False
        elif n == pn and o == po and g == pg and u == pu and e == pe and v == pv:
            d += 1
        else:
            logging.debug(f' {inx}\t{pn}\t{po}\t{pg}\t{pu}\t{pe}\t{pv}\t{d}')
            sum_d += d
            d = 1
            inx += 1
        pn = n
        po = o
        pg = g
        pu = u
        pe = e
        pv = v
        if inx > limit: break
    logging.debug(f' {inx}\t{pn}\t{po}\t{pg}\t{pu}\t{pe}\t{pv}\t{d}')
    sum_d += d
    logging.debug(f'{sum_d = }')

def log_notes_features(notes_features, limit = 200):
    logging.debug(f'{limit = }')
    logging.debug(f' 1\t2\t3\t4\t5\t6\t7\t8\t9\t0\t11\t12\t13\t14')
    logging.debug(f'Sta\tHold\tVel\tTon\tOct\tVoi\tSte\tEn1\tGls\tUps\tRen\t2gl\t3gl\tVol')
    #  0        1      2    3     4     5     6     7     8     9     10    11    12    13    14
    # ;Inst	Sta	Hold	Vel	Ton	Oct	Voi	Ste	En1	Gls	Ups	Ren	2gl	3gl	Vol
    for notes in notes_features[:limit]:
          logging.debug(f'{round(notes[1],2)}\t{round(notes[2],2)}\t{round(notes[3],2)}\t{notes[4]}\t{notes[5]}\t{notes[6]}\t{notes[7]}\t{notes[8]}\t{notes[9]}\t{notes[10]}\t{notes[11]}\t{notes[12]}\t{notes[13]}\t{round(notes[14],3)}')    