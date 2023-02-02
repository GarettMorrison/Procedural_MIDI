import mido
import time
from copy import deepcopy
from random import random

import MIDI_Funcs

arpp_out = mido.open_output('Python A 7')
bass_out = mido.open_output('Python B 8')
alto_out = mido.open_output('Python C 9')
outportSets = [arpp_out, bass_out, alto_out]
MIDI_Funcs.niceMidiExit(outportSets)

majorIntervals = [0, 2, 4, 5, 7, 9, 11]
minorIntervals = [0, 2, 3, 5, 7, 8, 10]
arbitraryIntervalPriority = [0.99, 0.2, 0.8, 0.7, 0.9, 0.2, 0.3]
noteRangeMin=36
noteRangeMax=84
def getNoteSet(baseNote, majorNotMinor=True):
    intervalSet = majorIntervals
    if not majorNotMinor: intervalSet = minorIntervals

    while baseNote >= noteRangeMin: baseNote -= 12

    outNotes = []
    outPriority = []
    while baseNote <= noteRangeMax:
        for ii in range(len(intervalSet)):
            fooNote = baseNote +intervalSet[ii]
            if fooNote < noteRangeMin: continue 
            if fooNote > noteRangeMax: break
            outNotes.append(fooNote)
            outPriority.append(arbitraryIntervalPriority[ii])

        baseNote += 12

    return(outNotes, outPriority)



chordSequence = [
    [50, False], # Dm
    [55, True], # G
    [60, True], # C
    [57, False], # Am
    ]

timeDelay = 0.1


scaleMotionVelocity = 0


chordSequenceDuration = 16
currentChordIndex = 0
notesSinceChordChange = 0

currChord, currPriority = getNoteSet(chordSequence[currentChordIndex][0], chordSequence[currentChordIndex][1])
bass_out.send(mido.Message(
    'note_on', 
    note=chordSequence[currentChordIndex][0],
))

gapCount = 0

currentNote = currChord[0]
altoNote = currentNote
while(True):
    previousNote = currentNote
    
    playNoteOdds = random()
    if notesSinceChordChange == 0:
        playNoteOdds *= 6
    elif notesSinceChordChange % 4 == 0:
        playNoteOdds *= 3
    
    if gapCount > 10:
        playNoteOdds *= gapCount -8
    elif gapCount > 0 and gapCount < 4:
        playNoteOdds /= 4
    elif gapCount > 4 and gapCount < 8:
        playNoteOdds /= 2
    


    if playNoteOdds > 0.25:
        doPlayNote = True
    else:
        doPlayNote = False


    if doPlayNote: gapCount = 0
    else: gapCount += 1


    fooPriority = deepcopy(currPriority)
    for ii in range(len(currChord)):
        # fooPriority[ii] = pow(fooPriority[ii], 1.0 + abs(currChord[ii] - (scaleMotionVelocity+previousNote)))
        fooPriority[ii] *= pow(0.8, abs(currChord[ii] - (scaleMotionVelocity+previousNote)))
        fooPriority[ii] *= 0.5 - abs(len(fooPriority)/2 -ii)/len(fooPriority)

    #     print(0.6 - abs(len(fooPriority)/2 -ii)/len(fooPriority))
    # exit()
    
    prioritySum = sum(fooPriority)
    for ii in range(len(currChord)):
        fooPriority[ii] /= prioritySum

    prioritySumSoFar = 0
    randomValue = random()
    selectedPos = 0
    for ii in range(len(currChord)):
        prioritySumSoFar += fooPriority[ii]
        if randomValue < prioritySumSoFar:
            selectedPos = ii
            break
        
    prioritySumSoFar = 0
    randomValue = random()
    selectedAltoPos = 0
    for ii in range(len(currChord)):
        prioritySumSoFar += fooPriority[ii]
        if randomValue < prioritySumSoFar:
            selectedAltoPos = ii
            break


    if doPlayNote:
        currentNote = currChord[selectedPos]
        noteVel = int(random()*(50*(currPriority[selectedPos]>0.5) + 30 ) + 30)

    if playNoteOdds > 0.1:
        prevAltoNote = altoNote
        altoNote = currChord[selectedAltoPos]
        noteVelAlto = int(random()*(50*(currPriority[selectedAltoPos]>0.5) + 30 ) + 30)


    
        alto_out.send(  mido.Message(
            'note_off', 
            note=prevAltoNote,
        ))
        alto_out.send(mido.Message(
            'note_on', 
            note=altoNote,
            velocity=noteVelAlto
        ))


    if doPlayNote:
        arpp_out.send(  mido.Message(
            'note_off', 
            note=previousNote,
        )) 



        arpp_out.send(mido.Message(
            'note_on', 
            note=currentNote,
            velocity=noteVel
        ))


        time.sleep(timeDelay)
        

        scaleMotionVelocity = currentNote - previousNote
    else:
        scaleMotionVelocity /= 3
        time.sleep(timeDelay)

    if random() > 0.75 -0.5*(gapCount>0):
        arpp_out.send(  mido.Message(
            'note_off', 
            note=previousNote,
        ))
        
    time.sleep(timeDelay)




    # print(f"{str(previousNote).ljust(5, ' ')}{str(round(scaleMotionVelocity, 2)).ljust(6, ' ')}", end='')
    for foo in currChord:
        if foo >= currentNote: break 
        print('   ', end='')
    if doPlayNote: print(currentNote)
    else: print('')




    # scaleMotionVelocity /= 2.0
    # scaleMotionVelocity += currentNote - previousNote
    



    notesSinceChordChange += 1
    if notesSinceChordChange >= chordSequenceDuration:
        notesSinceChordChange = 0

        currentChordIndex += 1
        if currentChordIndex >= len(chordSequence):
            currentChordIndex = 0
        
        
        bass_out.send(mido.Message(
            'note_off', 
            note=chordSequence[currentChordIndex][0],
        ))

        currChord, currPriority = getNoteSet( chordSequence[currentChordIndex][0], chordSequence[currentChordIndex][1]  )

        bass_out.send(mido.Message(
            'note_on', 
            note=chordSequence[currentChordIndex][0],
        ))

