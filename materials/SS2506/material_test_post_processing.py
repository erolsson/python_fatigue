import odbAccess

import pickle
import sys

import numpy as np


name = sys.argv[-1]
step_names = ['material_test']
odb = odbAccess.openOdb(name + '.odb')
total_frames = 0
for step_name in step_names:
    total_frames += len(odb.steps[step_name].frames)

data = np.zeros((total_frames, 13))  # time, 6 strain components, 6 stress components
j = 0
for step_name in step_names:
    frames = odb.steps[step_name].frames
    for i in range(0, len(frames)):
        frame = frames[i]
        data[j, 0] = frame.frameValue
        field = frame.fieldOutputs['E'].values[0].data  # Gauss pt 0
        data[j, 1:7] = frame.fieldOutputs['E'].values[0].data
        data[j, 7:] = frame.fieldOutputs['S'].values[0].data

pickleHandle = open('data_' + name + '.pkl', 'wb')
pickle.dump(data, pickleHandle)
pickleHandle.close()
