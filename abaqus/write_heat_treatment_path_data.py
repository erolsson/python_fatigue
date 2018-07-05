import odbAccess
from visualization import *
import xyPlot

from abaqusConstants import *

import numpy as np
import pickle

from path_functions import create_path
from path_functions import get_stress_tensors_from_path


def write_root_pickle(data_odb_name, step_name, result_pickle_name, frame_number=0):
    with open('../planetary_gear/pickles/tooth_paths.pkl', 'rb') as pickle_handle:
        pickle.load(pickle_handle)
        pickle.load(pickle_handle)  # Direction vector of the flank path
        root_data = pickle.load(pickle_handle)
        normal_root = pickle.load(pickle_handle)  # Direction vector perpendicular the root path

    odb = odbAccess.openOdb(data_odb_name)

    session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=309.913116455078,
                     height=230.809509277344)
    session.viewports['Viewport: 1'].makeCurrent()
    session.viewports['Viewport: 1'].maximize()
    o7 = session.odbs[session.odbs.keys()[0]]
    session.viewports['Viewport: 1'].setValues(displayedObject=o7)

    step_index = odb.steps.keys().index(step_name)
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_index, frame=frame_number)
    root_data[:, 2] += 1e-2
    root_path = create_path(root_data, 'longitudinal_path', session)
    stress_tensors = get_stress_tensors_from_path(root_path, session)
    normal_stress = np.dot(np.dot(normal_root, stress_tensors), normal_root)

    distance = np.sqrt(np.sum((root_data - root_data[0, :])**2, 1))
    print normal_stress, distance
    odb.close()

if __name__ == '__main__':
    odb_name = '/scratch/users/erik/scania_gear_analysis/odb_files/fake_heat_treatment/residual_stresses_1_4.odb'
    pickle_name = '/scratch/users/erik/scania_gear_analysis/pickles/fake_heat_treatment/residual_stresses_1_4.pkl'
    write_root_pickle(odb_name, step_name='Equilibrium', result_pickle_name=pickle_name, frame_number=11)
