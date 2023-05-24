# Auto_Just_Intonation
This repo contains code that can automaticaly process MIDI files to generate music in just intonation suitable for performance by Csound orchestras. Several examples are shown to illustrate using Music21 corpus of Bach Chorales, as well as synthetic chorales manufactured by TonicNet.
# Installation 
## required libraries
The following can be installed by pip or anaconda or miniconda:
1.  numpy
2.  music21
3.  muspy
4.  scipy
5.  mido
6.  jupyterlab or jupyter

The following should be installed in the operating system using apt-get on Ubuntu or dnf on Fedora/RedHat
1.  musescore
2.  csound-devel 
3.  sox    

The requirements.txt file has lots of other modules, but it's quite possible that none of them are actually required.

# Use
Once you get jupyter installed, open the TonicNet_Csound_adaptive_big_ensemble_strings.ipynb as a notebook. This notebook will use music21 to load one chorale, and send the resulting MIDI file through some code that looks at each chord in the file and does it's best to tune it to low integer ratio just intonation. I've built it using Bach chorales as models, so I can't guarantee it will work with all midi files. Your mileage will vary. When it comes time to run csound, it will complain that the sample files are missing. I'm not comfortable sharing the samples, since half of them are part of the McGill University Master Samples collection, which is copywrite material. I can point you to a CD to purchase that can supply the missing samples. Let me know if you are interested.


