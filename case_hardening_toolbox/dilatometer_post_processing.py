import odbAccess

import pickle
import sys

import numpy as np


name = sys.argv[-1]
step_names = ['quench']

data_dict = {'Thermal': {'vars': ['NT11', 'SDV_Q_MARTENSITE']},
             'Mechanical': {'vars': ['NT11', 'SDV_Q_MARTENSITE', 'U']}}
for model in data_dict.keys():
    odb = odbAccess.openOdb('Toolbox_' + model + '_' + name + '.odb')
    total_frames = 0
    for step_name in step_names:
        total_frames += len(odb.steps[step_name].frames)
    data = np.zeros((total_frames, len(data_dict[model]['vars']) + 1))  # Time, temp, U3
    j = 0
    for step_name in step_names:
        frames = odb.steps[step_name].frames
        for i in range(0, len(frames)):
            frame = frames[i]
            data[j, 0] = frame.frameValue
            for k, var in enumerate(data_dict[model]['vars'], 1):
                field = frame.fieldOutputs[var].values[6].data
                if var == 'U':
                    field = field[2]
                data[j, k] = field
            j += 1
    data_dict[model]['data'] = data
    odb.close()

with open('data_' + name + '.pkl', 'wb') as pickle_handle:
    pickle.dump(data_dict, pickle_handle)


