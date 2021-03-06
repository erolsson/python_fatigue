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
odb_name = sys.argv[10]
pickle_name = sys.argv[11]
root1 = sys.argv[12]
root2 = None
if len(sys.argv) > 13:
    root2 = sys.argv[13]

tooth_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear/' + odb_name + '.odb'

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
root_data_dict = {'pos': Root(name='pos', data=path_data_pos, normal=normal_root_pos),
                  'neg': Root(name='neg', data=path_data_neg, normal=normal_root_neg)}

roots = [root_data_dict[root1]]
if root2:
    roots.append(root_data_dict[root2])

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

    R = np.array([[np.cos(angle), -np.sin(angle), 0],
                  [np.sin(angle), np.cos(angle),  0],
                  [0,             0,              1]])
    normal_root = np.dot(R, root.normal)

    for i, frame in enumerate(frames):
        session.viewports['Viewport: 1'].odbDisplay.setFrame(step=frame.step_idx, frame=frame.frame_number)
        stress_tensors = get_stress_tensors_from_path(root_path, session)
        stress_data[i, 1] = np.dot(np.dot(normal_root, stress_tensors[0]), normal_root)
        stress_data[i, 0] = frame.frame_value

    stress_pickle_name = '/scratch/users/erik/scania_gear_analysis/pickles/tooth_root_stresses/' + \
        pickle_name + '_' + root.name + '.pkl'
    with open(stress_pickle_name, 'w+') as stress_pickle:
        pickle.dump(stress_data, stress_pickle)
odb.close()
