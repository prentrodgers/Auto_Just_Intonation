<CsoundSynthesizer>
; modified 07/12/12 10:55am - removed option -+y - not compatible with Csound 5
; created 10/6/00 3:28pm - first used for shuffle9.wav - Omar & Los Bandelero's
<CsOptions>
-W -m2 -G -o ../../../Music/sflib/ball9a-c.wav -3
; -o dac -W -G -m0 
</CsOptions>

<CsInstruments>
 sr = 44100 
 ksmps = 1 ; any higher than 10 and I hear clicks - can this line be eliminated?
 nchnls = 2

  instr 1

    imix = p4 ; Wet/dry mix. long reverb needs mix=.005, to make it wetter, try .007
    idel = p5 ; Required delay to align dry audio with output of convolve. length of convolv input file

    adryl,adryr  soundin "../../../Music/sflib/ball9.wav"      ; input (dry) audio (both channels?)
    ; convolv with the impulse response from Teatro Alcorcon in Madrid from Angelo Farina
    awetlr,awetll convolve adryl,"../../csound/Impulse/alcorcon.cv" ; stereo convolved (wet) audio
    awetrr,awetrl convolve adryr,"../../csound/Impulse/alcorcon.cv" ; stereo convolved (wet) audio

    adrydell     delay   (1-imix)*adryl,idel  ; Delay dry signal, to align it with convolved one
    adrydelr     delay   (1-imix)*adryr,idel  ; Delay dry signal, to align it with convolved one

    outs adrydell+imix*awetll+imix*awetrl, adrydelr+imix*awetrr+imix*awetlr ; mix dry and wet for both channels

  endin

</CsInstruments>

<CsScore>
; start dur wet/dry-mix  delaydry
;    + length in seconds plus length of impulse response file
;    |     + percentage of reverb vs live sound .0075 is pretty wet now
;    |     |       + Length of impulse response file Teatro Alcorcon in Madrid is 1.811247175532879818replaceme430839
;    |     |       |
i1 0 replaceme .0085   1.81124716553287981859410430839
</CsScore>
</CsoundSynthesizer>

