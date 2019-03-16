import odbAccess

import pickle
import sys

import numpy as np


name = sys.argv[-1]
odb = odbAccess.openOdb('Toolbox_Mechanical_' + name + '.odb')
step_names = ['heating', 'add_carbon', 'quench']
total_frames = 0
for step_name in step_names:
    total_frames += len(odb.steps[step_name].frames)
data = np.zeros((total_frames, 3))  # Time, temp, U3

j = 0
for step_name in step_names:
    frames = odb.steps[step_name].frames
    for i in range(0, len(frames)):
        frame = frames[i]
        U = frame.fieldOutputs['U'].values[6]
        NT = frame.fieldOutputs['NT11'].values[6]
        data[j, 0] = frame.frameValue
        data[j, 2] = U.data[2]
        data[j, 1] = NT.data
        j += 1
pickleHandle = open('data_' + name + '.pkl', 'wb')
pickle.dump(data, pickleHandle)
pickleHandle.close()
odb.close()
