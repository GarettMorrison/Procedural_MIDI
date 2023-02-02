import mido
import signal

# print("MIDI Outputs:")
# midiOutputs = mido.get_output_names()
# for foo in midiOutputs: print(f"   {foo}")

def niceMidiExit(_outportSets):
    outportSets = _outportSets
    
    def gracefulExit(signum, frame):
        print(outportSets)
        for fooOutput in outportSets:
            for ii in range(128): # Kill all notes
                msg = mido.Message('note_off', note=ii, velocity=0)
                fooOutput.send(msg)
            fooOutput.close()
        print('Stopped!')
        exit()
        
    signal.signal(signal.SIGINT, gracefulExit)