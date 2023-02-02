import mido
import time
from copy import deepcopy
from random import random
import numpy as np
import math as m

import matplotlib.pyplot as plt

import MIDI_Funcs

arpp_out = mido.open_output('Python A 7')
bass_out = mido.open_output('Python B 8')
alto_out = mido.open_output('Python C 9')
outportSets = [arpp_out, bass_out, alto_out]
MIDI_Funcs.niceMidiExit(outportSets)

scale_set = {
    'Major': [0, 2, 4, 5, 7, 9, 11],
    'Minor': [0, 2, 3, 5, 7, 8, 10],
    'HarmMinor': [0, 2, 3, 5, 7, 8, 11],
    'PentMajor': [0, 2, 4, 7, 9],
    'PentMinor': [0, 2, 3, 7, 9],
    'justFifthLol': [0, 7],
    'No.': [0]
}

sevenNotePriority = [0.99, 0.3, 0.8, 0.7, 0.9, 0.3, 0.4]
pentNotePriority = [0.9, 0.7, 0.8, 0.8, 0.7]
scale_arbitraryPriorities = {
    'Major': sevenNotePriority,
    'Minor': sevenNotePriority,
    'HarmMinor': sevenNotePriority,
    'PentMajor': pentNotePriority,
    'PentMinor': pentNotePriority,
    'justFifthLol': [0.9, 0.8],
    'No.': [0.1],
}

noteRangeMin=24
noteRangeMax=87
def getNoteSet(baseNote, scaleName='Major'):
    intervalSet = scale_set[scaleName]
    arbitraryIntervalPriority = scale_arbitraryPriorities[scaleName]

    while baseNote >= noteRangeMin: baseNote -= 12

    outNotes = []
    outPriority = []
    while baseNote < noteRangeMax:
        for ii in range(len(intervalSet)):
            fooNote = baseNote +intervalSet[ii]
            if fooNote < noteRangeMin: continue 
            if fooNote > noteRangeMax: break
            outNotes.append(fooNote)
            outPriority.append(arbitraryIntervalPriority[ii])

        baseNote += 12

    return(np.array(outNotes), np.array(outPriority))



chordSequence = [
    [50, 'PentMinor'], # Dm
    [55, 'Major'], # G
    [60, 'Major'], # C
    [57, 'HarmMinor'], # Am
    ]



# # I vi ii V
# chordSequence = [
#     [53, 'Major'], # F
#     [50, 'Minor'], # Dm
#     [55, 'Minor'], # Gm
#     [48, 'Major'], # C
#     ]



# # I vi ii V
# chordSequence = [
#     [53, 'Major'], # F
#     [50, 'HarmMinor'], # Dm
#     [55, 'PentMinor'], # Gm
#     [48, 'Major'], # C
#     ]


timeDelay = 0.15


scaleMotionVelocity = 0


chordSequenceDuration = 30
currentChordIndex = 0
notesSinceChordChange = 0

currChord, currPriority = getNoteSet(chordSequence[currentChordIndex][0], chordSequence[currentChordIndex][1])



bass_out.send(mido.Message(
    'note_on', 
    note=chordSequence[currentChordIndex][0]-24,
))

# Define graphing functions
plt.ion()
fig, ax = plt.subplots(1, 2, figsize=(10,5), gridspec_kw={'width_ratios': [1, 2]})
plt.subplots_adjust(top=0.9, left=0.07, right=0.97, bottom=0.1)
# plt.tight_layout()

timeVals = np.arange(chordSequenceDuration*3)

leadHist_notes = np.zeros(chordSequenceDuration*3, np.int16)
leadHist_moves = np.zeros(chordSequenceDuration*3, np.float16)
leadHist_velos = np.full(chordSequenceDuration*3, -2, np.int16)

altoHist_notes = np.zeros(chordSequenceDuration*3, np.int16)
altoHist_moves = np.zeros(chordSequenceDuration*3, np.float16)
altoHist_velos = np.full(chordSequenceDuration*3, -2, np.int16)
altoHist_misc = np.zeros(chordSequenceDuration*3, np.float16)

bassHist_notes = np.zeros(chordSequenceDuration*3, np.int16)
bassHist_velos = np.full((chordSequenceDuration*3), -2, np.int16)
bassHist_notes[0] = chordSequence[currentChordIndex][0]-24
bassHist_velos[0] = 100



def np_push(np_array, push_val):
    np_array = np.roll(np_array, 1)
    np_array[0] = push_val
    return(np_array)



def plotHistData(fooTimeVals, notes, velos, color, pltAx):
    velosNorm = np.array(velos, np.float16)/127

    noteStarts = np.where(velos>=0)[0]
    if len(noteStarts) > 0:
        pltAx.scatter(fooTimeVals[noteStarts], notes[noteStarts], alpha=velosNorm[noteStarts], c=color)

    ii = 0
    lastNote = 0
    while ii < len(notes):
        if velos[ii] >= 0:
            pltAx.plot(
                [fooTimeVals[ii], fooTimeVals[lastNote]],
                [notes[ii], notes[ii]],
                alpha=velosNorm[ii],
                c=color,
            )
            lastNote = ii

        elif velos[ii] == -2:
            lastNote = ii
        
        ii += 1
    
    # Check last note
    ii -= 1
    if velos[ii] == -1:
        pltAx.plot(
            [fooTimeVals[ii], fooTimeVals[lastNote]],
            [notes[ii], notes[ii]],
            alpha=0.6,
            c=color,
        )


    # if noteHeld > 1:
    #     ii -= 1

    #     pltAx.plot(
    #         [fooTimeVals[ii], fooTimeVals[ii - noteHeld-2] ],
    #         [notes[ii], notes[ii]],
    #         alpha=0.5,
    #         c=color,
    #     )
        



    # noteStarts = np.where(velos>=0)[0]
    # if len(noteStarts) > 0:
    #     plt.scatter(timeVals[noteStarts], notes[noteStarts], alpha=velosNorm[noteStarts], c=color)
    
    
    # noteCons = np.where(velos==-1)[0]
    # print(f"\n{noteStarts}     {noteCons}")
    # for ii in noteCons:
    #     prevNote = noteStarts[ np.where(noteStarts > ii)[0] ]
    #     if len(prevNote) == 0: continue

    #     # print(prevNote)
    #     print(f"{ii} -> {prevNote}")
    #     prevNote = prevNote[0]
    #     plt.plot(
    #         [timeVals[ii+1], timeVals[ii]],
    #         [notes[prevNote], notes[ii]],
    #         # alpha=velosNorm[ii],
    #         c=color,
    #     )


    

gapCount = 0
heldCount = 0
leadVelSum = 100
altoVelSum = 100

vibesLead_repDist = 0.1
vibesLead_sequenceRep = 0.1
vibesLead_noteRep = 0.1
vibesLead_motionRep = 0.1

vibesLead_repDist_hist = np.zeros(chordSequenceDuration*3, np.float16)
vibesLead_sequenceRep_hist = np.zeros(chordSequenceDuration*3, np.float16)
vibesLead_noteRep_hist = np.zeros(chordSequenceDuration*3, np.float16)
vibesLead_motionRep_hist = np.zeros(chordSequenceDuration*3, np.float16)

sigDivCount = 3
altoThreshold = 0.01+0.5*random()*random()
leadLegato = 0.4 + random()*0.4 + random()*0.3

altoSetting = 'pulse'
altoSettingSet = [
    'match', 'match', 'match', 
    'decay', 'decay', 
    'arpeggio', 'arpeggio', 
    'pulse', 
    'random',
]

bassSetting = 'none'
bassSettingSet = [
    'hold','hold','hold',
    'clock',
    'div_2','div_2',
    'div_3',
    'div_4',
    'strike',
    'none',
]



altoArpUp = True
altoArpHitEnd = False
prevAltoNote = 0

changeTimeSig = False
timeSplits = [
    (9, 2),
    (16, 8),
    (9, 3),
    (12, 8), 
    (9, 4),
    (8, 3),
    (10, 4),


    (8, 4),
    (9, 3),
    (10, 2),
    (10, 5),
    (12, 3),
    (12, 4),
    (12, 6),
    (14, 7),
    (14, 2),
    (15, 3),
    (15, 5),
    (16, 4),
    (16, 8),
    (18, 3),
    (18, 6),
    (20, 5),
    (20, 4),
    (20, 8),
    (21, 3),



    (24, 3),
    (24, 8),
    (25, 5),
    (27, 9),
    (30, 6),
    (32, 4),
]

# timeDivConstant = 1
timeDivConstant = 2.4

# newSequenceIndex = m.floor(random()*len(timeSplits))
newSequenceIndex = 18
chordSequenceDuration = timeSplits[newSequenceIndex][0]
sigDivCount = timeSplits[newSequenceIndex][1]
timeDelay = timeDivConstant/chordSequenceDuration

if chordSequenceDuration % sigDivCount == 0: timeSigTopStr = str(round(chordSequenceDuration/sigDivCount))
else: timeSigTopStr = str(round(chordSequenceDuration/sigDivCount, 3))

if chordSequenceDuration > 16:
    altoVelAdjust = (altoThreshold*50)/(chordSequenceDuration-12)
    altoVelAdjust = max(0.5, altoVelAdjust)
    altoVelAdjust = min(altoVelAdjust, 1.0)
else: 
    altoVelAdjust = 1.0

if altoVelAdjust < 1.0: print(f"   altoVelAdjust:{round(altoVelAdjust, 3)}")
else: print('')


currentNote = currChord[0]
altoNote = currentNote
currentTick = -1


def printSequence(fullPrint=True):
    if chordSequenceDuration % sigDivCount == 0: timeSigTopStr = str(round(chordSequenceDuration/sigDivCount))
    else: timeSigTopStr = str(round(chordSequenceDuration/sigDivCount, 3))
    
    if fullPrint:
        print(f"\n Sequence: Pattern: {chordSequenceDuration}/{sigDivCount}     ({timeSigTopStr} beats per measure)")
        print(f"     Part Settings:   altoSetting:{altoSetting.ljust(10)}  bassSetting:{bassSetting}")


    print(f"     altoThresh: {str(round(altoThreshold, 3)).ljust(5, ' ')}   leadLegato: {str(round(leadLegato, 3)).ljust(5, ' ')}", end='')


printSequence()

while(True):
    startTime = time.time()
    currentTick += 1

    # Move to next chord maybe
    notesSinceChordChange += 1
    if notesSinceChordChange >= chordSequenceDuration:
        notesSinceChordChange = 0
        
        currChord, currPriority = getNoteSet(chordSequence[currentChordIndex][0], chordSequence[currentChordIndex][1])

        bass_out.send(mido.Message(
            'note_off', 
            note=chordSequence[currentChordIndex][0] -24,
        ))

        currentChordIndex += 1

        if currentChordIndex >= len(chordSequence):
            currentChordIndex = 0
            
            if changeTimeSig:
                # Limit new time signature to +/- 5 beats per measure of the previous signature
                timeSplitDurs = np.array(list(zip(*timeSplits))[0])
                possibleNewIndices = np.where(abs(timeSplitDurs-chordSequenceDuration) < 6)[0]
                newSequenceIndex = possibleNewIndices[ m.floor(random()*len(possibleNewIndices)) ]
                
                chordSequenceDuration = timeSplits[newSequenceIndex][0]
                sigDivCount = timeSplits[newSequenceIndex][1]
                timeDelay = timeDivConstant/chordSequenceDuration

                # Change setting for alto
                altoSetting = altoSettingSet[m.floor(random()*len(altoSettingSet))]
                
                # Change setting for bass
                bassSetting = bassSettingSet[m.floor(random()*(len(bassSettingSet) -1))]
                
                
                altoThreshold = 0.01+0.5*random()*random()
                leadLegato = 0.4 + random()*0.4 + random()*0.3

                printSequence()
                
                changeTimeSig = False
            else:
                altoThreshold += 0.15*(random()-0.5)
                leadLegato += 0.6*(random()-0.5)
                
                printSequence(False)
                
                changeTimeSig = True
            
            
            if chordSequenceDuration > 16:
                altoVelAdjust = (altoThreshold*50)/(chordSequenceDuration-12)
                altoVelAdjust = max(0.5, altoVelAdjust)
                altoVelAdjust = min(altoVelAdjust, 1.0)
            else: 
                altoVelAdjust = 1.0

            if altoVelAdjust < 1.0: print(f"   altoVelAdjust:{round(altoVelAdjust, 3)}")
            else: print('')
            # print('')
            

    # Do bass
    bassVel = -1
    if bassSetting == "hold":
        if notesSinceChordChange == 0:
            bassVel = 100

    elif bassSetting == "clock":
        if notesSinceChordChange == 0:
            bassVel = 100
        elif notesSinceChordChange % sigDivCount == 0:
            bassVel = 60

    elif bassSetting == "strike":
        if notesSinceChordChange == 0:
            bassVel = 120
        elif notesSinceChordChange % sigDivCount == 0:
            bassVel = -2

    elif bassSetting == "div_2":
        if notesSinceChordChange == 0:
            bassVel = 100
        elif notesSinceChordChange % sigDivCount*2 == 0:
            bassVel = 70

    elif bassSetting == "div_3":
        if notesSinceChordChange == 0:
            bassVel = 100
        elif notesSinceChordChange % sigDivCount*3 == 0:
            bassVel = 70

    elif bassSetting == "div_4":
        if notesSinceChordChange == 0:
            bassVel = 100
        elif notesSinceChordChange % sigDivCount*3 == 0:
            bassVel = 70
    elif bassSetting == "none":
        bassVel = -2

    if bassVel >= 0:
        bass_out.send(mido.Message(
            'note_off', 
            note=chordSequence[currentChordIndex][0] -24,
        ))

    if bassVel > 0:
        bass_out.send(mido.Message(
            'note_on', 
            note=chordSequence[currentChordIndex][0] -24,
            velocity=100,
        ))

    bassHist_velos = np_push(bassHist_velos, bassVel)
    bassHist_notes = np_push(bassHist_notes, chordSequence[currentChordIndex][0] -24)
        




    # print('\n')
    # for foo in bassHist_velos: print(str(foo).ljust(4, ' '), end='')
    # print('')
    # for foo in bassHist_notes: print(str(foo).ljust(4, ' '), end='')
    
    previousNote = currentNote
    
    # Odds of playing next note
    playNoteOdds = random()
    if notesSinceChordChange == 0:
        playNoteOdds *= 20
    elif notesSinceChordChange % sigDivCount == 0:
        playNoteOdds *= 5
    
    if gapCount > 10:
        playNoteOdds *= gapCount -8
    elif gapCount > 0 and gapCount < 4:
        playNoteOdds /= 2
    elif gapCount > 4 and gapCount < 8:
        playNoteOdds /= 1.5
    
    if gapCount == 0:
        playNoteOdds *= 1.0 - pow(0.95, heldCount+1)
        # playNoteOdds *= max(2, 5, abs(abs(scaleMotionVelocity)-6))/2

    if leadHist_velos[chordSequenceDuration -1]>0:
        playNoteOdds *= 20*vibesLead_sequenceRep
    
    # if leadHist_velos[chordSequenceDuration -1]>0:
    #     playNoteOdds *= 25 *(1.0-vibesLead_repDist) *vibesLead_sequenceRep
    # if leadHist_velos[chordSequenceDuration*2 -1]>0:
    #     playNoteOdds *= 10 *(vibesLead_repDist) *vibesLead_sequenceRep

    if playNoteOdds > 0.3 +(leadLegato-0.4)/4:
        doPlayNote = True
    else:
        doPlayNote = False



    # Calculate odds adjustments base on history for generally all notes
    noteRangeOdds = np.full(noteRangeMax - noteRangeMin, 1.0, np.float16)
    noteRangeSet = np.arange(noteRangeMin, noteRangeMax)
    
    # Note was played this iteration last cycle
    if leadHist_velos[chordSequenceDuration -1] > 0:
        # Add adjustments for previous sequence
        compareIndex = chordSequenceDuration-1

        # Boost same note at octave offset from last iteration
        noteMatch = np.where((noteRangeSet - leadHist_notes[compareIndex])%12 == 0)[0]
        if len(noteMatch)>0: 
            for ii in noteMatch: 
                noteRangeOdds[ii] *= 2*vibesLead_noteRep +2

        # Boost exact note value from last iteration
        noteMatch = np.where((noteRangeSet - leadHist_notes[compareIndex])%12 == 0)[0]
        if len(noteMatch)>0: 
            for ii in noteMatch: 
                noteRangeOdds[ii] *= 3*vibesLead_noteRep +2

        noteRangeOdds = noteRangeOdds * pow(1.0 -vibesLead_motionRep/5, abs(noteRangeSet - previousNote - (leadHist_moves[compareIndex])))
        
        # noteRangeOdds = noteRangeOdds * pow(1.0, abs(noteRangeSet - previousNote + (leadHist_moves[compareIndex])))
        
        if leadHist_moves[compareIndex] > 0: 
            noteRangeOdds[np.where(noteRangeSet > previousNote)] *= 5
        if leadHist_moves[compareIndex] < 0:
            noteRangeOdds[np.where(noteRangeSet < previousNote)] *= 5
        
        # print(f"leadHist_notes[compareIndex]:{leadHist_notes[compareIndex]}")
        # print(f"previousNote:{previousNote}")
        # print(f"previousNote + (leadHist_moves[compareIndex]):{previousNote + (leadHist_moves[compareIndex])}")
        # print(f"vibesLead_motionRep:{vibesLead_motionRep}")

        # ax[0].cla()
        # ax[0].plot(noteRangeSet, noteRangeOdds, alpha=0.5)
        # plt.pause(1000.0)
        # exit()



    fooPriority = deepcopy(currPriority)
    for ii in range(len(fooPriority)):
        matchIndex = np.where(currChord[ii] == noteRangeSet)[0][0]
        fooPriority[ii] *= noteRangeOdds[matchIndex]


    for ii in range(len(currChord)):
        if notesSinceChordChange != 0: fooPriority[ii] *= pow(0.9, abs(currChord[ii] - (scaleMotionVelocity+previousNote)))

        fooPriority[ii] /= pow(abs(len(fooPriority)/2 -ii) + len(fooPriority), 2)


    prioritySum = sum(fooPriority)
    for ii in range(len(currChord)):
        fooPriority[ii] /= prioritySum


    if doPlayNote:
        ax[0].clear()
        if chordSequenceDuration < 20:
            ax[0].plot(fooPriority, currChord)
            ax[0].set_title("Odds of Note Selection\nLead (Blue)")
            ax[0].set_xlabel("Relative Probability of selection")
            ax[0].set_ylabel("Notes (MIDI)")
            ax[0].set_ylim(12, noteRangeMax+1)
        else:
            ax[0].set_title("Paused to Prevent Desync\n(For Fast Sequences)")

    # Randomize velocity occasionally
    if random() > 0.95:
        leadVelSum = random()*127
        altoVelSum = leadVelSum


    if doPlayNote:
        prioritySumSoFar = 0
        randomValue = random()
        selectedPos = 0
        for ii in range(len(currChord)):
            prioritySumSoFar += fooPriority[ii]
            if randomValue < prioritySumSoFar:
                selectedPos = ii
                break
        
        currentNote = currChord[selectedPos]
        noteVel = int((currPriority[selectedPos]>0.5)*leadVelSum/4 +30*random() +30*(notesSinceChordChange%sigDivCount == 0) +30)
        leadVelSum = (noteVel + leadVelSum*3)/4





    # Play alto note if it's time
    altoMiscDataPt = 0.0
    
    playAltoOdds = random()
    if notesSinceChordChange == 0:
        playAltoOdds *= 10
    elif notesSinceChordChange % sigDivCount == 0:
        playAltoOdds *= 3

    if altoHist_velos[chordSequenceDuration -1] > 0: 
        playAltoOdds *= 10
    
    if altoHist_velos[0] > 0: 
        playAltoOdds *= 2
        
    if playNoteOdds > altoThreshold:
        # altoPriority= deepcopy(currPriority)
        selectedAltoPos = 0
        prevAltoNote = altoNote
        noteVelAlto = int(altoVelAdjust * ((random()/2 +0.5)*(altoVelSum/2*(currPriority[selectedAltoPos]>0.5) + 30 ) + 30))

        # altoSettingSet = ['match', 'match', 'decay', 'arpeggio', 'pulse', 'random']

        # Play notes according to 
        if altoSetting == 'match':
            prioritySumSoFar = 0
            randomValue = random()
            for ii in range(len(currChord)):
                prioritySumSoFar += fooPriority[ii]
                if randomValue < prioritySumSoFar:
                    selectedAltoPos = ii
                    break

            altoNote = currChord[selectedAltoPos] -12
                

        elif altoSetting == 'random':
            potentialMatches = np.where(currPriority > 0.6)[0]
            selectedAltoPos = m.floor(random()*len(potentialMatches))
            altoNote = currChord[potentialMatches[selectedAltoPos]] -12
                

        elif altoSetting == 'pulse':
            if notesSinceChordChange == 0:
                potentialMatches = np.where(currPriority >= 0.8)[0]
                if len(potentialMatches) >= 7: selectedAltoPos = m.floor(random()*10)
                else: selectedAltoPos = m.floor(random()*len(potentialMatches))
                altoNote = currChord[potentialMatches[selectedAltoPos]]

            if notesSinceChordChange == 0:
                noteVelAlto = 120
            elif notesSinceChordChange % sigDivCount == 0:
                noteVelAlto = 90
            else:
                noteVelAlto = 60
                

        elif altoSetting == 'decay':
            randomValue = random()

            potentialMatches = np.where(currPriority > 0.6)[0]
            potentialMatchIndices = np.where(currChord[potentialMatches] < altoNote)[0]
        
        
            if notesSinceChordChange == 0: randomValue *= 2
            elif notesSinceChordChange % sigDivCount == 0: randomValue *= 6/5

            if altoHist_misc[chordSequenceDuration -1] == 1.0: randomValue *= 4/3

            if len(potentialMatchIndices) > 3 and randomValue < 1/12:
                altoNote = currChord[potentialMatches[potentialMatchIndices[-3]]]

            elif len(potentialMatchIndices) > 2 and randomValue < 3/12:
                altoNote = currChord[potentialMatches[potentialMatchIndices[-2]]]

            elif len(potentialMatchIndices) > 1 and randomValue < 1:
                altoNote = currChord[potentialMatches[potentialMatchIndices[-1]]]
            else:
                altoMiscDataPt = 1.0
                altoNote = currentNote

        elif altoSetting == 'arpeggio':
            # Change direction at chordChange
            if notesSinceChordChange == 0:
                if altoArpHitEnd:
                    altoArpHitEnd = not altoArpHitEnd
                else:
                    altoArpUp = not altoArpUp
                    if altoArpUp: altoMiscDataPt = 4.0
                    else: altoMiscDataPt = -4.0
            

            # Change to repeat direction change
            if altoMiscDataPt == -4.0:
                if altoArpUp and random()<0.8: 
                    altoArpHitEnd = True
                    altoArpUp = False
                    altoMiscDataPt = -4.0
                elif random() < 0.5: 
                    altoArpHitEnd = True
                    altoArpUp = True
                    altoMiscDataPt = -4.0
            elif altoMiscDataPt == 4.0:
                if altoArpUp and random()<0.8: 
                    altoArpHitEnd = True
                    altoArpUp = True
                    altoMiscDataPt = 4.0
                elif random() < 0.5: 
                    altoArpHitEnd = True
                    altoArpUp = False
                    altoMiscDataPt = 4.0
            elif (notesSinceChordChange%sigDivCount == 0 and random()<0.15) or random() < 0.05:
                altoArpHitEnd = True
                if altoArpUp:
                    altoArpUp = False
                    altoMiscDataPt = -4.0
                else:
                    altoArpUp = True
                    altoMiscDataPt = 4.0

            potentialNoteIndices = np.where(currPriority > 0.7)[0]
            potentialMatches = currChord[potentialNoteIndices]

            # Arpeggio is ascending
            if altoArpUp:
                potentialNoteInds = np.where(potentialMatches > prevAltoNote)[0]
                if len(potentialNoteInds) > 0: # In range, go to next value
                    selectedAltoPos = potentialNoteInds[0]
                else: # Top of range reached
                    altoArpHitEnd = True
                    altoArpUp = False
                    altoMiscDataPt = -4.0
                    potentialNoteInds = np.where(potentialMatches < prevAltoNote)[0]
                    selectedAltoPos = potentialNoteInds[-1]
               
            # Arpeggio is descending     
            else:
                potentialNoteInds = np.where(potentialMatches < prevAltoNote)[0]
                if len(potentialNoteInds) > 0: # In range, go to next value
                    selectedAltoPos = potentialNoteInds[-1]
                else: # Top of range reached
                    altoArpHitEnd = True
                    altoArpUp = True
                    altoMiscDataPt = -4.0
                    potentialNoteInds = np.where(potentialMatches > prevAltoNote)[0]
                    selectedAltoPos = potentialNoteInds[0]

            altoNote = potentialMatches[selectedAltoPos]
            
        
        altoVelSum = (noteVelAlto + altoVelSum*3)/4

        alto_out.send(  mido.Message(
            'note_off', 
            note=prevAltoNote,
        ))
        alto_out.send(mido.Message(
            'note_on', 
            note=altoNote,
            velocity=noteVelAlto
        ))
    else:
        noteVelAlto = -2

    altoHist_misc = np_push(altoHist_misc, altoMiscDataPt)


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

        scaleMotionVelocity = 1.0*(currentNote - previousNote)
    else:
        scaleMotionVelocity /= 1.5



    if doPlayNote:
        gapCount = 0
        heldCount = 0
    else:
        # Potentially end note
        if random() > leadLegato -0.05*gapCount -0.5*((currentNote-noteRangeMin)/(noteRangeMax-noteRangeMin) > 0.8):
            arpp_out.send(  mido.Message(
                'note_off', 
                note=previousNote,
            ))

            gapCount += 1
        else:
            if gapCount > 0:
                gapCount += 1
            else: 
                heldCount += 1
    

    # If note played, adjust vibes
    if doPlayNote:
        vibesLead_repDist = 0.0
        comparePosition = chordSequenceDuration -1

        
        motionAccuracy = abs(leadHist_moves[comparePosition] - scaleMotionVelocity)
        motionAccuracy = 1.0 - motionAccuracy/12
        motionAccuracy = max(motionAccuracy, 0.0)
        vibesLead_motionRep = (motionAccuracy + 15*vibesLead_motionRep)/16
            
        # Check if note was actually played last time
        if leadHist_velos[comparePosition] > 0:
            # Check if notes line up
            if (leadHist_notes[comparePosition] - currentNote)%12 == 0: vibesLead_noteRep = (1.0 + 7*vibesLead_noteRep)/8
            else: vibesLead_noteRep = (0.0 + 7*vibesLead_noteRep)/8

            # Check if sequence lines up
            vibesLead_sequenceRep = (1.0 + 15*vibesLead_sequenceRep)/16
        else:
            vibesLead_sequenceRep = (0.0 + 15*vibesLead_sequenceRep)/16 

        
        
    if gapCount>0: noteVel = -2 # Track is not playing
    elif heldCount>0: noteVel = -1  # Track is holding note

    leadHist_notes = np_push(leadHist_notes, currentNote)
    leadHist_moves = np_push(leadHist_moves, scaleMotionVelocity)
    leadHist_velos = np_push(leadHist_velos, noteVel)

    altoHist_notes = np_push(altoHist_notes, altoNote)
    # altoHist_moves = np_push(altoHist_moves, scaleMotionVelocity)
    altoHist_velos = np_push(altoHist_velos, noteVelAlto)
    

    ax[1].set_xlabel("Time")
    ax[1].set_ylabel("Note")
    ax[1].set_title("Notes vs Time\nLead (B) Alto (G) Bass (O)")
    ax[1].set_xlim(0, chordSequenceDuration*3)
    ax[1].set_ylim(12, noteRangeMax+1)
    plotHistData(timeVals, bassHist_notes, bassHist_velos, 'orange', ax[1])
    plotHistData(timeVals, altoHist_notes, altoHist_velos, 'green', ax[1])
    plotHistData(timeVals, leadHist_notes, leadHist_velos, 'blue', ax[1])



    # ax[0].set_xlabel("Time")
    # ax[0].set_ylabel("Note")
    # ax[0].set_xlim(0, chordSequenceDuration)
    # ax[0].set_ylim(12, noteRangeMax+1)
    # plotHistData(timeVals[:chordSequenceDuration], bassHist_notes[:chordSequenceDuration], bassHist_velos[:chordSequenceDuration], 'orange', ax[0])
    # plotHistData(timeVals[:chordSequenceDuration], leadHist_notes[:chordSequenceDuration], leadHist_velos[:chordSequenceDuration]/2, 'blue', ax[0])
    # plotHistData(timeVals[:chordSequenceDuration], leadHist_notes[chordSequenceDuration:chordSequenceDuration*2], leadHist_velos[chordSequenceDuration:chordSequenceDuration*2]/2, 'purple', ax[0])

    # ax[1].set_ylim(0, 1)

    # vibesLead_repDist_hist = np_push(vibesLead_repDist_hist, vibesLead_repDist)
    vibesLead_sequenceRep_hist = np_push(vibesLead_sequenceRep_hist, vibesLead_sequenceRep)
    vibesLead_noteRep_hist = np_push(vibesLead_noteRep_hist, vibesLead_noteRep)
    vibesLead_motionRep_hist = np_push(vibesLead_motionRep_hist, vibesLead_motionRep)

    # ax[1].plot(timeVals[:chordSequenceDuration*2], vibesLead_sequenceRep_hist[:chordSequenceDuration*2], color='green', alpha=0.5, label='sequenceRep')
    # ax[1].plot(timeVals[:chordSequenceDuration*2], vibesLead_noteRep_hist[:chordSequenceDuration*2], color='blue', alpha=0.5, label='noteRep')
    # ax[1].plot(timeVals[:chordSequenceDuration*2], vibesLead_motionRep_hist[:chordSequenceDuration*2], color='purple', alpha=0.5, label='motionRep')
    # ax[1].legend()
    
    
    
    

    # time.sleep(timeDelay)




    endTime = time.time()

    # Delay for remainder of time
    if timeDelay -(endTime-startTime) > 0: 
        plt.show()
        plt.pause(timeDelay -(endTime-startTime))
        ax[1].clear()
        # ax[1].clear()
    else:
        print("TIMING ERROR!!! Not enough time to process generation between ticks")


        