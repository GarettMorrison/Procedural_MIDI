## Procedurally Generate Live Music

Generates MIDI for music in real time

Uses Python to generate MIDI, VCV Rack to simulate the synths, and LoopMidi to connect the two. 

### Demo Video

[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/tAtjBQ3fOFA/0.jpg)](http://www.youtube.com/watch?v=tAtjBQ3fOFA)

I'd been thinking about making something like this for ages but never had time, I decided to start simple and see what I could make over a weekend. I blinked and it was a week later. It's a single file with ~900 lines of barely documented Python. It's remarkably poorly structured and hard to follow. At this point, if I wanted to add a new mechanism, I'd probably just rewrite the whole thing from scratch. This repo is primarily just a backup. 

The system is entirely probabalistic. Every decision is made by weighted randomization. It's not AI, theres no training data or feedback. I entirely worked by listening to the random beeps and boops, guessing and checking different ways to tweak the weights. 

The chord progression is pre-programmed, as I was mostly interested in melody generation. Each beat the lead melody has a chance to start playing any note in the current scale. There's a ton a math for the odds of playing each note, as technically every note has some chance of playing. The weighting primarily makes the melody more likely to move on downbeats, play notes which don't clash, and follow a similar structure to the last measure. When a lead note is played, the probability of each potential note is displayed on the left hand plot.

Every 8 measures, a number of configuration variables are modified. This creates a more comprehensible structure, as different patterns can be observed within each configuration. First, the beat pattern is tweaked. Each chord is split into beats, which are grouped into notes. This creates a similar pattern to tuplets in traditional music. 

The bass and alto voices also randomly cycle through several different settings . These specify the algorithm for note pitch and timing, reading the beat division, chord position, and lead voice to select notes. Finally, two threshold values are tweaked for the lead and alto voices. These change the threshold required for a note to play, varying how frequently notes play and move. 
