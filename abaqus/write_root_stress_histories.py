from visualization import *
from abaqusConstants import *

import sys
from collections import namedtuple

import pickle
import numpy as np

from path_functions import create_path
from path_functions import get_stress_tensors_from_path

Frame = namedtuple('Frame', ['step_name', 'step_idx', 'frame_number', 'frame_value'])
Root = namedtuple('Root', ['name', 'data', 'normal'])
# odb_name = sys.argv[10]
# pickle_name = sys.argv[11]
# number_of_roots = int(sys.argv[12])

odb_name = 'pulsator/pulsator_stresses'
pickle_name = 'pulsator/tooth_root_stresses'
number_of_roots = 1

tooth_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/' + odb_name + '.odb'

with open('../planetary_gear/pickles/tooth_paths.pkl', 'rb') as path_pickle_handle:
    pickle.load(path_pickle_handle)                 # Flank path data
    pickle.load(path_pickle_handle)                 # Direction vector of the flank path
    root_data = pickle.load(path_pickle_handle)     # Root path data
    normal_root = pickle.load(path_pickle_handle)   # Direction vector perpendicular the root path


path_data_pos = np.copy(root_data)
path_data_neg = np.copy(path_data_pos)

path_data_neg[:, 0] *= -1

normal_root_pos = normal_root
normal_root_neg = np.copy(normal_root_pos)
normal_root_neg[0] *= -1

roots = [Root(name='pos', data=path_data_pos, normal=normal_root_pos)]
if number_of_roots == 2:
    roots.append(Root(name='neg', data=path_data_neg, normal=normal_root_neg))

odb = openOdb(tooth_odb_file_name, readOnly=True)
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=309.913116455078,
                 height=230.809509277344)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
o7 = session.odbs[session.odbs.keys()[0]]
session.viewports['Viewport: 1'].setValues(displayedObject=o7)
frames = []
for step_name in odb.steps.keys():
    for i in range(len(odb.steps[step_name].frames)):
        frames.append(Frame(step_name=step_name, step_idx=odb.steps.keys().index(step_name),
                            frame_number=i, frame_value=odb.steps[step_name].frames[i].frameValue))
for root in roots:
    root_path = create_path(root.data, 'root_path_' + root.name, session)
    stress_data = np.zeros((len(frames), 2))
    x, y = root.data[0, 0:2]
    angle = np.pi/2 - np.arctan(x/y)
    print angle
    R = np.array([[np.cos(angle), -np.sin(angle), 0],
                  [np.sin(angle), np.cos(angle),  0],
                  [0,             0,              1]])
    normal_root = np.dot(R, root.normal)
    for i, frame in enumerate(frames):
        session.viewports['Viewport: 1'].odbDisplay.setFrame(step=frame.step_idx, frame=frame.frame_number)
        stress_tensors = get_stress_tensors_from_path(root_path, session)
        stress_data[i, 1] = np.dot(np.dot(normal_root, stress_tensors[0]), normal_root)
        stress_data[i, 0] = frame.frame_value

    stress_pickle_name = '/scratch/users/erik/scania_gear_analysis/pickles/' + pickle_name + '_' + root.name + '.pkl'
    with open(stress_pickle_name, 'w+') as stress_pickle:
        pickle.dump(stress_data, stress_pickle)
odb.close()
