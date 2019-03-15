import odbAccess

import pickle
import sys

import numpy as np


name = sys.argv[-1]
odb = odbAccess.openOdb('Toolbox_Mechanical_' + name + '.odb')
frames = odb.steps['quench'].frames
data = np.zeros((len(frames), 3))  # Time, temp, U3

for i in range(0, len(frames)):
    frame = frames[i]
    U = frame.fieldOutputs['U'].values[6]
    NT = frame.fieldOutputs['NT11'].values[6]
    data[i, 0] = frame.frameValue
    data[i, 2] = U.data[2]
    data[i, 1] = NT.data

pickleHandle = open('data_' + name + '.pkl', 'wb')
pickle.dump(data, pickleHandle)
pickleHandle.close()
odb.close()
