import constants

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv(constants.FILE_NAME)

arr = df.to_numpy()

rotated_arr = np.rot90(arr, k=-1)

initial_time = rotated_arr[0][-1]

rotated_arr[0] -= initial_time

for i in range (5):
    plt.plot(rotated_arr[0], rotated_arr[i + 1])
plt.show()