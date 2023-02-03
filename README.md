## Procedurally Generated Live MIDI

Generates MIDI for music in real time

Uses Python to generate MIDI, VCV Rack to simulate the synths, and LoopMidi to connect the two. 

### Demo Video

[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/tAtjBQ3fOFA/0.jpg)](http://www.youtube.com/watch?v=tAtjBQ3fOFA)

I'd been thinking about making something like this for ages but never had time, I decided to start simple and see what I could make over a weekend. I blinked and it was a week later. It's a single file with ~900 lines of barely documented Python. It's remarkably poorly structured and hard to follow. At this point, if I wanted to add a new mechanism, I'd probably just rewrite the whole thing from scratch. This repo is primarily just a backup. 

The system is entirely probabalistic. Every decision is made by weighted randomization. It's not AI, theres no training data or feedback. I entirely worked by listening to the random beeps and boops, guessing and checking different ways to tweak the weights. 

### [Link to Full Write-Up](https://www.garettmorrison.net/posts/proceduralmidi/)
