#   Interface for MIDI System Exclusive messages used by Behringer FCB1010
#
#   Allows sending and receiving sysex between computer MIDI port and FCB1010
#   Allows loading and saving data using comma separated value file
#
#   Copyright Brian Walton (brian@riban.co.uk) 2021
#   There is no affiliation with Behringer. This is all reverse engineered
#
#   Depends on rtmidi which provides MIDI interface on a range of platforms - only tested on Linux ALSA


#   Class representing the parameters of a FB1010 preset
class fcb1010_preset:
    #   Constructor
    #   pc1_default: MIDI program to send for program change 1
    def __init__(self, pc1_default):
        self.pc1_enabled = True
        self.pc2_enabled = False
        self.pc3_enabled = False
        self.pc4_enabled = False
        self.pc5_enabled = False
        self.cc1_enabled = False
        self.cc2_enabled = False
        self.switch1_enabled = False
        self.switch2_enabled = False
        self.expA_enabled = True
        self.expB_enabled = True
        self.note_enabled = False
        self.pc1_program = pc1_default
        self.pc2_program = 0
        self.pc3_program = 0
        self.pc4_program = 0
        self.pc5_program = 0
        self.cc1_controller = 0
        self.cc1_value = 0
        self.cc2_controller = 0
        self.cc2_value = 0
        self.expA_controller = 27
        self.expA_min = 0
        self.expA_max = 127
        self.expB_controller = 7
        self.expB_min = 0
        self.expB_max = 127
        self.note_value = 60


#   Class representing the complete FCB1010 configuration exposed by MIDI sysex
#   Initialised similar to FCB1010 default
class fcb1010:
    def __init__(self):
        self.preset = [fcb1010_preset(i) for i in range(100)]
        self.pc1_midi_channel = 0
        self.pc2_midi_channel = 0
        self.pc3_midi_channel = 0
        self.pc4_midi_channel = 0
        self.pc5_midi_channel = 0
        self.cc1_midi_channel = 0
        self.cc2_midi_channel = 0
        self.expA_midi_channel = 0
        self.expB_midi_channel = 0
        self.note_midi_channel = 0
        self.direct_select = False
        self.running_status = True
        self.merge = True
        self.switch1 = False
        self.switch2 = False
        self.expA_calibration_min = 0
        self.expA_calibration_max = 127
        self.expB_calibration_min = 0
        self.expB_calibration_max = 127
    
    #   Get the enable state of a preset's parameters
    #   data: Raw sysex data as list of integers
    #   offset: Offset of bitwise flag byte within sysex data
    #   flag: Index of flag bit within byte
    #   invert: True to invert the result
    #   returns: Tuple with boolean value of flag, offset of next flag, index of next flag
    def get_param_enable_states(self, data, offset, flag, invert):
        result = (data[offset] & (1 << flag)) == (1 << flag)
        if invert:
            result = not result
        flag += 1
        if flag > 6:
            flag = 0
            offset += 8
        return (result, offset, flag)
    
    #   Set the enable state of a preset's parameters within raw sysex data
    #   data: Raw sysex data as list of integers
    #   offset: Offset of bitwise flag byte within sysex data
    #   flag: Index of flag bit within byte
    #   value: Boolean value to set flag
    #   returns: Tuple with offset of next flag, index of next flag
    def set_param_enable_states(self, data, offset, flag, value):
        data[offset] |= (value << flag)
        flag += 1
        if flag > 6:
            flag = 0
            offset += 8
        return (offset, flag)
    
    #   Get preset parameter values
    #   data: Raw sysex data as list of integers
    #   offset: Offset of parameter within sysex data
    #   returns: Tuple with parameter value of flag, offset of next parameter
    def get_params(self, data, offset):
        result = data[offset]
        offset += 1
        if ((offset - 6) % 8 == 0):
            offset += 1
        return (result, offset)
    
    #   Set preset parameter values within raw sysex data
    #   data: Raw sysex data as list of integers
    #   offset: Offset of parameter within sysex data
    #   value: Value to set parameter
    #   returns: Offset of next parameter
    def set_params(self, data, offset, value):
        data[offset] = value
        offset += 1
        if ((offset - 6) % 8 == 0):
            offset += 1
        return offset
    
    #   Parse sysex data and populate data structures
    #   data: Raw sysex data as list of integers
    #   returns: True if valid FCB1010 sysex parsed
    def parse_sysex(self, data):
        size = len(data)
        if size != 2352 or data[0] != 240 or data[size - 1] != 247 or data[1] != 0 or data[2] != 32 or data[3] != 50 or data[4] != 1 or data[5] != 12 or data[6] != 15:
            return False
        offset = 14
        flag = 0
        for preset in range(100):
            self.preset[preset].pc1_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, True)
            self.preset[preset].pc2_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, True)
            self.preset[preset].pc3_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, True)
            self.preset[preset].pc4_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, True)
            self.preset[preset].pc5_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, True)
            self.preset[preset].cc1_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, True)
            self.preset[preset].switch1_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, False)
            self.preset[preset].cc2_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, True)
            self.preset[preset].switch2_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, False)
            self.preset[preset].expA_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, True)
            dummy, offset, flag = self.get_param_enable_states(data, offset, flag, False)
            dummy, offset, flag = self.get_param_enable_states(data, offset, flag, False)
            self.preset[preset].expB_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, True)
            dummy, offset, flag = self.get_param_enable_states(data, offset, flag, False)
            dummy, offset, flag = self.get_param_enable_states(data, offset, flag, False)
            self.preset[preset].note_enabled, offset, flag = self.get_param_enable_states(data, offset, flag, True)
        offset = 7
        for preset in range(100):
            self.preset[preset].pc1_program, offset = self.get_params(data, offset)
            self.preset[preset].pc2_program, offset = self.get_params(data, offset)
            self.preset[preset].pc3_program, offset = self.get_params(data, offset)
            self.preset[preset].pc4_program, offset = self.get_params(data, offset)
            self.preset[preset].pc5_program, offset = self.get_params(data, offset)
            self.preset[preset].cc1_controller, offset = self.get_params(data, offset)
            self.preset[preset].cc1_value, offset = self.get_params(data, offset)
            self.preset[preset].cc2_controller, offset = self.get_params(data, offset)
            self.preset[preset].cc2_value, offset = self.get_params(data, offset)
            self.preset[preset].expA_controller, offset = self.get_params(data, offset)
            self.preset[preset].expA_min, offset = self.get_params(data, offset)
            self.preset[preset].expA_max, offset = self.get_params(data, offset)
            self.preset[preset].expB_controller, offset = self.get_params(data, offset)
            self.preset[preset].expB_min, offset = self.get_params(data, offset)
            self.preset[preset].expB_max, offset = self.get_params(data, offset)
            self.preset[preset].note, offset = self.get_params(data, offset)
        self.pc1_midi_channel = data[2311]
        self.pc2_midi_channel = data[2312]
        self.pc3_midi_channel = data[2313]
        self.pc4_midi_channel = data[2314]
        self.pc5_midi_channel = data[2315]
        self.cc1_midi_channel = data[2316]
        self.cc2_midi_channel = data[2317]
        self.expA_midi_channel = data[2319]
        self.expB_midi_channel = data[2320]
        self.note_midi_channel = data[2321]
        self.direct_select = (data[2330] & 2) == 2
        self.running_status = (data[2330] & 4) == 4
        self.merge = (data[2330] & 16) == 16
        self.switch1 = (data[2334] & 4) == 4
        self.switch2 = (data[2329] & 64) == 64
        self.expA_calibration_min = data[2343]
        self.expA_calibration_max = data[2344]
        self.expB_calibration_min = data[2345]
        self.expB_calibration_max = data[2346]
        return True
    
    #   Get raw sysex from data structures
    #   returns: Raw sysex data as list of integers
    def get_raw_sysex(self):
        data = [0 for i in range(2352)]
        data[0] = 240
        data[1] = 0
        data[2] = 32
        data[3] = 50
        data[4] = 1
        data[5] = 12
        data[6] = 15
        preset = 0
        offset = 14
        flag = 0
        for preset in range(100):
            offset, flag = self.set_param_enable_states(data, offset, flag, not self.preset[preset].pc1_enabled)
            offset, flag = self.set_param_enable_states(data, offset, flag, not self.preset[preset].pc2_enabled)
            offset, flag = self.set_param_enable_states(data, offset, flag, not self.preset[preset].pc3_enabled)
            offset, flag = self.set_param_enable_states(data, offset, flag, not self.preset[preset].pc4_enabled)
            offset, flag = self.set_param_enable_states(data, offset, flag, not self.preset[preset].pc5_enabled)
            offset, flag = self.set_param_enable_states(data, offset, flag, not self.preset[preset].cc1_enabled)
            offset, flag = self.set_param_enable_states(data, offset, flag, self.preset[preset].switch1_enabled)
            offset, flag = self.set_param_enable_states(data, offset, flag, not self.preset[preset].cc2_enabled)
            offset, flag = self.set_param_enable_states(data, offset, flag, self.preset[preset].switch2_enabled)
            offset, flag = self.set_param_enable_states(data, offset, flag, not self.preset[preset].expA_enabled)
            offset, flag = self.set_param_enable_states(data, offset, flag, False)
            offset, flag = self.set_param_enable_states(data, offset, flag, False)
            offset, flag = self.set_param_enable_states(data, offset, flag, not self.preset[preset].expB_enabled)
            offset, flag = self.set_param_enable_states(data, offset, flag, False)
            offset, flag = self.set_param_enable_states(data, offset, flag, False)
            offset, flag = self.set_param_enable_states(data, offset, flag, not self.preset[preset].note_enabled)
        offset = 7
        for preset in range(100):
            offset = self.set_params(data, offset, self.preset[preset].pc1_program)
            offset = self.set_params(data, offset, self.preset[preset].pc2_program)
            offset = self.set_params(data, offset, self.preset[preset].pc3_program)
            offset = self.set_params(data, offset, self.preset[preset].pc4_program)
            offset = self.set_params(data, offset, self.preset[preset].pc5_program)
            offset = self.set_params(data, offset, self.preset[preset].cc1_controller)
            offset = self.set_params(data, offset, self.preset[preset].cc1_value)
            offset = self.set_params(data, offset, self.preset[preset].cc2_controller)
            offset = self.set_params(data, offset, self.preset[preset].cc2_value)
            offset = self.set_params(data, offset, self.preset[preset].expA_controller)
            offset = self.set_params(data, offset, self.preset[preset].expA_min)
            offset = self.set_params(data, offset, self.preset[preset].expA_max)
            offset = self.set_params(data, offset, self.preset[preset].expB_controller)
            offset = self.set_params(data, offset, self.preset[preset].expB_min)
            offset = self.set_params(data, offset, self.preset[preset].expB_max)
            offset = self.set_params(data, offset, self.preset[preset].note_value)
        data[2311] = self.pc1_midi_channel
        data[2312] = self.pc2_midi_channel
        data[2313] = self.pc3_midi_channel
        data[2314] = self.pc4_midi_channel
        data[2315] = self.pc5_midi_channel
        data[2316] = self.cc1_midi_channel
        data[2317] = self.cc2_midi_channel
        data[2319] = self.expA_midi_channel
        data[2320] = self.expB_midi_channel
        data[2321] = self.note_midi_channel
        data[2331] = self.pc1_midi_channel
        data[2332] = self.pc2_midi_channel
        data[2333] = self.pc3_midi_channel
        data[2335] = self.pc4_midi_channel
        data[2336] = self.pc5_midi_channel
        data[2337] = self.cc1_midi_channel
        data[2338] = self.cc2_midi_channel
        data[2339] = self.expA_midi_channel
        data[2340] = self.expB_midi_channel
        data[2341] = self.note_midi_channel
        data[2330] = 0
        data[2329] = 0
        data[2334] = 3
        if self.direct_select: data[2330] |= 2
        if self.running_status: data[2330] |= 4
        if self.merge: data[2330] |= 16
        if self.switch1: data[2334] |= 2
        if self.switch2: data[2329] |= 64
        data[2343] = self.expA_calibration_min
        data[2344] = self.expA_calibration_max
        data[2345] = self.expB_calibration_min
        data[2346] = self.expB_calibration_max
        for offset in range(1839, 2311):
            data[offset] = 127
        data[2351] = 247
        return data
    
    #   Print current configuration in human readable form
    def show_config(self):
        for (index, preset) in enumerate(self.preset):
            print("Preset", index)
            print("  PC1: %s %d  PC2: %s %d  PC3: %s %d  PC4: %s %d  PC5: %s %d  CC1: %s %d %d  CC2: %s %d %d" % (
                preset.pc1_enabled, preset.pc1_program, preset.pc2_enabled, preset.pc2_program, preset.pc3_enabled, preset.pc3_program, preset.pc4_enabled, preset.pc4_program, preset.pc5_enabled, preset.pc5_program, preset.cc1_enabled, preset.cc1_controller, preset.cc1_value, preset.cc2_enabled, preset.cc2_controller, preset.cc2_value))
            print("  Switch 1: %s  Switch 2: %s  Expression A: %s %d %d %d  Expression B: %s %d %d %d  Note: %s %d" % (
               preset.switch1_enabled, preset.switch2_enabled, preset.expA_enabled, preset.expA_controller, preset.expA_min, preset.expA_max, preset.expB_enabled, preset.expB_controller, preset.expB_min, preset.expB_max, preset.note_enabled, preset.note_value))
        print()
        print("  MIDI Channels")
        print("  PC1: %d  PC2: %d  PC3: %d  PC4: %d  PC5: %d  CC1: %d  CC2: %d  ExpA: %d  ExpB: %d  Note: %d" %
            (self.pc1_midi_channel, self.pc2_midi_channel, self.pc3_midi_channel, self.pc4_midi_channel, self.pc5_midi_channel, self.cc1_midi_channel, self.cc2_midi_channel, self.expA_midi_channel, self.expB_midi_channel, self.note_midi_channel))
        print("  Direct select: %s  Running status: %s  Merge: %s  Switch 1: %s  Switch 2: %s  Exp A calibration %d %d  Exp B calibration %d %d" % (
            self.direct_select, self.running_status, self.merge, self.switch1, self.switch2, self.expA_calibration_min, self.expA_calibration_max, self.expB_calibration_min, self.expB_calibration_max))
    
    #   Read data from csv file
    #   filename: Absolute or relative path and filename [Default: ./FCB1010.csv]
    #   returns: True on success
    def load(self, filename='FCB1010.csv'):
        try:
            with open(filename) as file:
                csv = file.read().splitlines()
        except:
            print("Failed to read file", filename)
            return False
        if len(csv) < 3:
            print("CSV has insufficient lines. Should be at least 3")
            return False
        if csv[0] != "Global,,Program Change 1,,Program Change 2,,Program Change 3,,Program Change 4,,Program Change 5,,Continuous Controller 1,,,Continuous Controller 2,,,Switch 1,Switch 2,Expression Pedal A,,,,Expression Pedal B,,,,Note,":
            print("First line of CSV should contain headers:")
            print("Global,,Program Change 1,,Program Change 2,,Program Change 3,,Program Change 4,,Program Change 5,,Continuous Controller 1,,,Continuous Controller 2,,,Switch 1,Switch 2,Expression Pedal A,,,,Expression Pedal B,,,,Note,")
            return False
        if csv[2] != "Bank,Preset,Enabled,Program,Enabled,Program,Enabled,Program,Enabled,Program,Enabled,Program,Enabled,Controller,Value,Enabled,Controller,Value,Enabled,Enabled,Enabled,Controller,Minimum,Maximum,Enabled,Controller,Minimum,Maximum,Enabled,Value":
            print("Third line of CSV should contain headers:")
            print("Bank,Preset,Enabled,Program,Enabled,Program,Enabled,Program,Enabled,Program,Enabled,Program,Enabled,Controller,Value,Enabled,Controller,Value,Enabled,Enabled,Enabled,Controller,Minimum,Maximum,Enabled,Controller,Minimum,Maximum,Enabled,Value")
            return False
        midi_channels = csv[1].split(',')
        if len(midi_channels) != 30:
            print("Insufficient MIDI Channel parameters.")
            return False
        self.pc1_midi_channel = int(midi_channels[2])
        self.pc2_midi_channel = int(midi_channels[4])
        self.pc3_midi_channel = int(midi_channels[6])
        self.pc4_midi_channel = int(midi_channels[8])
        self.pc5_midi_channel = int(midi_channels[10])
        self.cc1_midi_channel = int(midi_channels[12])
        self.cc2_midi_channel = int(midi_channels[15])
        self.expA_midi_channel = int(midi_channels[20])
        self.expB_midi_channel = int(midi_channels[24])
        self.note_midi_channel = int(midi_channels[28])
        for i in range(3, len(csv)):
            data = csv[i].split(',')
            if len(data) != 30:
                continue
            bank = int(data[0])
            if bank < 1 or bank > 10:
                continue
            preset = int(data[1])
            if preset < 1 or preset > 10:
                continue
            preset = (bank - 1) * 10 + preset - 1
            self.preset[preset].pc1_enabled = int(data[2]) == 1
            self.preset[preset].pc1_program = int(data[3])
            self.preset[preset].pc2_enabled = int(data[4]) == 1
            self.preset[preset].pc2_program = int(data[5])
            self.preset[preset].pc3_enabled = int(data[6]) == 1
            self.preset[preset].pc3_program = int(data[7])
            self.preset[preset].pc4_enabled = int(data[8]) == 1
            self.preset[preset].pc4_program = int(data[9])
            self.preset[preset].pc5_enabled = int(data[10]) == 1
            self.preset[preset].pc5_program = int(data[11])
            self.preset[preset].cc1_enabled = int(data[12]) == 1
            self.preset[preset].cc1_controller = int(data[13])
            self.preset[preset].cc1_value = int(data[14])
            self.preset[preset].cc1_enabled = int(data[15]) == 1
            self.preset[preset].cc1_controller = int(data[16])
            self.preset[preset].cc1_value = int(data[17])
            self.preset[preset].switch1_enabled = int(data[18]) == 1
            self.preset[preset].switch2_enabled = int(data[19]) == 1
            self.preset[preset].expA_enabled = int(data[20]) == 1
            self.preset[preset].expA_controller = int(data[21])
            self.preset[preset].expA_min = int(data[22])
            self.preset[preset].expA_max = int(data[23])
            self.preset[preset].expB_enabled = int(data[24]) == 1
            self.preset[preset].expB_controller = int(data[25])
            self.preset[preset].expB_min = int(data[26])
            self.preset[preset].expB_max = int(data[27])
            self.preset[preset].note_enabled = int(data[28]) == 1
            self.preset[preset].note_value = int(data[29])
        return True
    
    #   Save data to csv file
    #   filename: Absolute or relative path and filename [Default: ./FCB1010.csv]
    #   returns: True on success
    def save(self, filename='FCB1010.csv'):
        try:
            with open(filename, 'w') as file:
                file.write('Global,,Program Change 1,,Program Change 2,,Program Change 3,,Program Change 4,,Program Change 5,,"Continuous\nController 1",,,"Continuous\nController 2",,,Switch 1,Switch 2,"Expression\nPedal A",,,,"Expression\nPedal B",,,,Note,\n')
                file.write("MIDI Channel,,%d,,%d,,%d,,%d,,%d,,%d,,,%d,,,N/A,N/A,%d,,,,%d,,,,%d,\n" % (
                    self.pc1_midi_channel,
                    self.pc2_midi_channel,
                    self.pc3_midi_channel,
                    self.pc4_midi_channel,
                    self.pc5_midi_channel,
                    self.cc1_midi_channel,
                    self.cc2_midi_channel,
                    self.expA_midi_channel,
                    self.expB_midi_channel,
                    self.note_midi_channel))
                file.write('Bank,Preset,Enabled,Program,Enabled,Program,Enabled,Program,Enabled,Program,Enabled,Program,Enabled,Controller,Value,Enabled,Controller,Value,Enabled,Enabled,Enabled,Controller,Minimum,Maximum,Enabled,Controller,Minimum,Maximum,Enabled,Value\n')
                for bank in range(10):
                    for offset in range(10):
                        preset = (bank - 1) * 10 + offset - 1
                        file.write("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n" % (
                        bank, offset,
                        self.preset[preset].pc1_enabled,
                        self.preset[preset].pc1_program,
                        self.preset[preset].pc2_enabled,
                        self.preset[preset].pc2_program,
                        self.preset[preset].pc3_enabled,
                        self.preset[preset].pc3_program,
                        self.preset[preset].pc4_enabled,
                        self.preset[preset].pc4_program,
                        self.preset[preset].pc5_enabled,
                        self.preset[preset].pc5_program,
                        self.preset[preset].cc1_enabled,
                        self.preset[preset].cc1_controller,
                        self.preset[preset].cc1_value,
                        self.preset[preset].cc1_enabled,
                        self.preset[preset].cc1_controller,
                        self.preset[preset].cc1_value,
                        self.preset[preset].switch1_enabled,
                        self.preset[preset].switch2_enabled,
                        self.preset[preset].expA_enabled,
                        self.preset[preset].expA_controller,
                        self.preset[preset].expA_min,
                        self.preset[preset].expA_max,
                        self.preset[preset].expB_enabled,
                        self.preset[preset].expB_controller,
                        self.preset[preset].expB_min,
                        self.preset[preset].expB_max,
                        self.preset[preset].note_enabled,
                        self.preset[preset].note_value))
        except:
            print("Failed to write file", filename)
            return False
        return True


"""    
## Example usage ##
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
midiout = rtmidi.MidiOut(rtmidi.API_LINUX_ALSA, "riban")
midiin = rtmidi.MidiIn(rtmidi.API_LINUX_ALSA, "riban")
# For testing I connect to my second MIDI interface. For production should probably open virtual ports and manually connect
out_port = midiout.open_port(2)
in_port = midiin.open_port(2)
#out_port = midiout.open_virtual_port()
#in_port = midiin.open_virtual_port()

fcb_rx = fcb1010() # fcb1010 object used to receive sysex messages
midiin.ignore_types(sysex=False) # Enable reception of sysex
midiin.set_callback(on_midi_in, fcb_rx) # fcb_rx will be populated with any received sysex

# Beware that MIDI thru on FCB1010 will mean that sending sysex may result in fcb_rx being updated
"""

"""
# Create a default FCB1010 object and send to device
result = input("Do you want to send default configuration to device Y/n?")
if len(result) > 0 and result.lower[0] != 'n':
    fcb_tx = fcb1010()
    send_sysex(fcb_tx)

# Save fcb_rx to file
result = input("Do you want to save received sysex to file Y/n?")
if len(result) > 0 and result.lower[0] != 'n':
    fcb_rx.save()

# Load fcb_tx from file then send to device
result = input("Do you want to load configuration from file then send to device Y/n?")
if len(result) > 0 and result.lower[0] != 'n':
    fcb_tx = fcb1010()
    fcb_tx.load()
    send_sysex(fcb_tx)
"""
