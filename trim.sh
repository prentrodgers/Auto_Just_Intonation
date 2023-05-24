#! /bin/bash
set -v
export SFDIR="../../../Music/sflib"
echo $SFDIR
ls $SFDIR -lth | head -n 10
csound -U sndinfo $SFDIR/"$1".wav
csound "$1"c.csd 
sox $SFDIR/"$1"a-c.wav -p reverse | sox -p -p silence 1 .01 .01 | sox -p -p reverse | sox -p -p silence 1 0.01 0.01 | sox -p $SFDIR/"$1"-t"$2".wav
sox $SFDIR/"$1"-t"$2".wav -C640 $SFDIR/"$1"-t"$2".mp3
csound -U sndinfo $SFDIR/"$1"-t"$2".wav
mv $SFDIR/"$1"-t"$2".mp3 ../../Uploads