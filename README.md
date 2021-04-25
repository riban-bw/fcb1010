# fcb1010
Behringer FBC1010 pedalboard sysex interface

This Python code can send and receive MIDI system exclusive messages bewteen a computer and Behringer FCB1010 pedalboard. Global settings for each parameter's MIDI channel are exchanged as well as the parameters for each of the 100 (10 banks of 10) presets. Global data is sent from the FCB1010 and may be viewed in the Python class but only MIDI channel data is set in the FCB1010 when sysex is received.

Data may be printed out with the show_config function. Data may be stored to and recalled from a comma separated variable file using save and load functions. The CSV file is in a specific format which allows simple editing within a spreadsheet. An example is provided in Open Document format which formats the data to allow (reasonably) simple viewing, filtering and editing. This can be saved as CVS then loaded into a Python fcb1010 object.

This project has no affiliation with Behringer and sysex structure has been reverse engineered due to lack of documentation available. (This is unusual - most MIDI device manufacturer's provide sysex structure documentation.)

This code works with standard FCB1010 V2.5 firmware. It has not been tested with other versions of the standard FCB1010 firmware nor any third party firmware.

The main purpose of this software is to allow simple editing, backup and restore of FCB1010 configuration.

In the repository is an Open Office Document format spreadsheet configured to allow filtering and editing of the data. Save spreadsheet as csv to create a file that can be used read and sent to FCB1010.

# Example use:

```
from fcb1010 import fcb1010
import rtmidi
from time import sleep

#   Handle MIDI input (callback)
#   event: Tuple with received MIDI data as list of integers, time since last message (float in seconds)
#   data: fcb1010 object to populate when a valid fcb1010 sysex message received
def on_midi_in(event, data):
    if data.parse_sysex(event[0]):
        print("Parsed FCB1010 sysex")
    else:
        for byte in event[0]:
            print(hex(byte), end=' ')
        print()

#   Send FCB1010 sysex
#   fcb: fcb1010 object
def send_sysex(fcb):
    global midiin
    midiin.cancel_callback()
    midiout.send_message(fcb.get_raw_sysex())
    sleep(2)
    midiin.set_callback(on_midi_in, fcb_rx)

# Create MIDI input and output ports
midiout = rtmidi.MidiOut(rtmidi.API_LINUX_ALSA)
midiin = rtmidi.MidiIn(rtmidi.API_LINUX_ALSA)
# For testing I connect to my second MIDI interface. For production should probably open virtual ports and manually connect
out_port = midiout.open_port(2)
in_port = midiin.open_port(2)
#out_port = midiout.open_virtual_port()
#in_port = midiin.open_virtual_port()

fcb_rx = fcb1010() # fcb1010 object used to receive sysex messages
midiin.ignore_types(sysex=False) # Enable reception of sysex
midiin.set_callback(on_midi_in, fcb_rx) # fcb_rx will be populated with any received sysex
```

Sending sysex fro FCB1010 will populate the fcb1010 object called fcb_rx. Beware that MIDI thru on FCB1010 will mean that sending sysex may result in fcb_rx being updated

Save fcb_rx to file
```
fcb_rx.save()
```

Create a default FCB1010 object and send to device
```
fcb_tx = fcb1010()
send_sysex(fcb_tx)
```

Load fcb_tx from file then send to device
```
fcb_tx = fcb1010()
fcb_tx.load()
send_sysex(fcb_tx)
```
