import constants

import muselsl as lsl
from pylsl import StreamInlet, resolve_streams

import mne
import os

print(dir(lsl))

# muses = list_muses()
# stream(muses[0]['address'])

def write_data():
    os.remove(constants.FILE_NAME)
    lsl.record(duration=10, filename=constants.FILE_NAME)

def realtime_stream():

    while True:
        pass

# realtime_stream()
print('End program')