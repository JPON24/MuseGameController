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

# from pylsl import StreamInlet, resolve_streams
import keyboard

# import mne
import mne_lsl
import os
import numpy as np
import pandas as pd

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

    # gets only delta and theta freq bands
    stream.filter(
        l_freq=constants.LOWER_FREQ,
        h_freq=constants.UPPER_FREQ,
        picks="eeg"
    )

    # filter for low frequency 
    # stream.filter(
    #         l_freq=1.0,
    #         h_freq=10.0,
    #         method='iir', 
    #         iir_params=dict(order=4, ftype="butter")
    # )

    data = stream.get_data(winsize=1)

    # time_delta = time() - init_time

    x_data = np.arange(256)
    x_data = x_data.astype(float)
    x_data /= 256.0
    y_data = data[0][0] # af7 data

    # print(x_data)
    # print(y_data)
    
    line.set_data(x_data, y_data)
    return line,

stream = ''

def realtime_stream(animating=True):
    global stream
    stream = mne_lsl.stream.StreamLSL(
        bufsize=1,
        name="Muse"
    )

    stream.connect()

    if (animating):
        ani = FuncAnimation(fig, update_graph, init_func=init, blit=True, interval=100)
        plt.show()

from sklearn.svm import SVC
import muselsl as lsl

all_data = []
all_timestamps = []

def collect_data():
    isBlinking = False
    global stream, init_time, all_data, all_timestamps    

    stream = mne_lsl.stream.StreamLSL(
        bufsize=1,
        name="Muse"
    )

    stream.connect()

    # gets only delta and theta freq bands
    stream.filter(
        l_freq=constants.LOWER_FREQ,
        h_freq=constants.UPPER_FREQ,
        picks="eeg"
    )

    # filter for low frequency 
    # stream.filter(
    #         l_freq=1.0,
    #         h_freq=10.0,
    #         method='iir', 
    #         iir_params=dict(order=4, ftype="butter")
    # )
    starting_time = time()
    batch_start_time = time()
    batch_length = 1.0

    while True:
        data = stream.get_data(winsize=1)

        delta_time = time() - starting_time
        batch_delta = time() - batch_start_time
        

        # batch data collection
        if (batch_delta) > batch_length:
            x_data = np.arange(256)
            x_data = x_data.astype(float)
            x_data /= 256.0
            x_data += (delta_time - 1.0)
            y_data = data[0][0] # af7 data

            batch_start_time = time()

            if data:
                all_data.append(y_data)
                all_timestamps.append(x_data)

        # concatenate data and send it off!
        if (delta_time) > constants.RECORDING_TIME + 0.05:
            print('done')

            x_out = np.concat(all_timestamps)
            y_out = np.concat(all_data)

            # print(x_out)
            # print(y_out)

            df = pd.DataFrame({
                'Time': x_out,
                'AF7': y_out,
                'Blinking': True   
            })

            # print(x_out.shape)
            # print(y_out.shape)
            
            df.to_csv('blink.csv', index=False, sep=',', na_rep='REMOVE')
            break

max_blink = 0

def inference(model):
    global stream, max_blink

    if (stream):
        stream.filter(
            l_freq=constants.LOWER_FREQ,
            h_freq=constants.UPPER_FREQ,
            picks="eeg"
        )
    
        data = stream.get_data(winsize=1)

        x_new = data[0][0] # af7 data

        x_new = x_new.reshape(-1,1)

        print(x_new)

        prediction = model.predict(x_new)

        pred_np = np.zeros(256)
        pred_np *= prediction

        np_sum = np.sum(pred_np)

        if np_sum > max_blink:
            max_blink = np_sum
        
        print(np_sum)

    
    if (keyboard.is_pressed('q')):
        print('breaking loop')

        print(f'max blink: {max_blink}')
        return True

def supervised_learning():
    # (Features X, Target y)
    # detection will be single feature from delta/theta power, may swap to being delta power AND theta power later using two different features from same data
    
    df1 = pd.read_csv('noblink.csv')
    df2 = pd.read_csv('blink.csv')

    result = pd.concat([df1, df2], axis=0)

    x = np.array(result['AF7'])
    x = x.reshape(-1,1)
    y = np.array(result['Blinking'])  

    model = SVC(kernel='rbf')

    model.fit(x,y) # train

    realtime_stream(False)

    while True:
        output = inference(model)
        if output:
            break

# realtime_stream()
# collect_data()
supervised_learning()
print('Program closed.')
exit()