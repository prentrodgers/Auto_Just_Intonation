# Auto_Just_Intonation
This repo contains code that can automaticaly process MIDI files to generate music in just intonation suitable for performance by Csound orchestras. Several examples are shown to illustrate using Music21 corpus of Bach Chorales, as well as synthetic chorales manufactured by TonicNet.

The design of the tuning algorithm is a set of codes that optimize the tuning of each chord, such that the lowest possible numbers are used for the numerator and denominator of each of the six ratios in a four note chord, while trying to stay relatively close to the original 12 tone equal temperament notes in the MIDI file. I trade off between low number ratios and distance from 12-TET using a temperature variable called ratio_factor. The higher ratio_factor gets, the more important low number ratios is compared to distance from 12TET. The lower the ratio_factor, the closer to 12 TET and the higher the acceptable ratios. When two notes in adjacent chords were originally the same 12TET note in the MIDI file, but at different cent values, I create a glissando using a cubic polynomial curve to get from one to the other. For example, if a note in one chord is set to 498 cents, and then to 520 cents in the next chord, I create a glissando of 22 cents to get from one to the other. Some examples are avaliable to listen to on my substack page here: https://microtonalnotes.substack.com/

# Installation 
## required libraries
The following can be installed by pip or anaconda or miniconda:
1.  numpy
2.  music21
3.  muspy
4.  scipy
5.  mido
6.  jupyter

The following should be installed in the operating system using apt-get on Ubuntu or dnf on Fedora/RedHat
1.  musescore
2.  csound-devel 
3.  sox    

The requirements.txt file has lots of other modules, but it's quite possible that none of them are actually required.

# Use
Once you get jupyter installed, open the slide_tuning.ipynb as a notebook. This notebook will use music21 to load one chorale, and send the resulting MIDI file through some code that looks at each chord in the file and does it's best to tune it to low integer ratio just intonation. 

I include suggested anchor points for notes that should always have the same cent values. These are only provide for the J.S.Bach St. Johns Passion Chorales. There's a method to create more described in the notebook.

I've built it using Bach chorales as models, so I can't guarantee it will work with all midi files. Your mileage will vary. When it comes time to run csound, it will complain that the sample files are missing. I'm not comfortable sharing the samples, since half of them are part of the McGill University Master Samples collection, which is copywrite material. I can point you to a CD to purchase that can supply the missing samples. Let me know if you are interested.

If you'd like to listen to some results before deciding if it's worth the trouble, take a listen to some samples here: http://ripnread.com/sample-page/code/fantasias-on-bach-chorales-from-the-st-john-passion-for-large-ensembles/

