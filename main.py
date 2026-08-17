# def old():
#     pass
    # print(dir(lsl))
    # muses = list_muses()
    #stream(muses[0]['address'])

# def write_data():
#     os.remove(constants.FILE_NAME)
#     lsl.record(duration=10, filename=constants.FILE_NAME)

# def realtime_stream_pylsl():
#     stream_infos = resolve_streams()
#     inlet = StreamInlet(stream_infos[0])
#     timestamp = time()

#     while True:
#         # if (time() - timestamp) > (1.0/constants.POLLING_RATE):
#         #     timestamp = time()
#         #     print('completing poll')

#         sample, timestamp = inlet.pull_sample()
#         sample.pop() # remove unnecessary channel data

#         print(f"Timestamp: {timestamp:.4f} | Data: {sample}")

#         if (keyboard.is_pressed('q')):
#             print('breaking loop')
#             break

import constants

# import muselsl as lsl
# from pylsl import StreamInlet, resolve_streams
import keyboard

# import mne
import mne_lsl
import os
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from time import time

x_data, y_data = [], []
fig, ax = plt.subplots()
line, = ax.plot([], [], 'r-')

init_time = time()

def init():
    ax.set_xlim(0, 1)
    ax.set_ylim(-256, 256)
    return line,

def update_graph(frame):
    global stream, init_time
    # cuts power lines and gamma
    stream.filter(
        l_freq=0.5,
        h_freq=30.0,
        picks="eeg"
    )

    data = stream.get_data(winsize=1)

    # time_delta = time() - init_time

    x_data = np.arange(256)
    x_data = x_data.astype(float)
    x_data /= 256.0
    y_data = data[0][0]

    # print(x_data)
    # print(y_data)
    
    line.set_data(x_data, y_data)
    return line,

stream = ''

def realtime_stream():
    global stream
    stream = mne_lsl.stream.StreamLSL(
        bufsize=1,
        name="Muse"
    )

    stream.connect()

    ani = FuncAnimation(fig, update_graph, init_func=init, blit=True, interval=100)
    plt.show()

realtime_stream()
print('End program')