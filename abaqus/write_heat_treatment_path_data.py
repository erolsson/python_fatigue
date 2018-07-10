from collections import namedtuple

import odbAccess
from visualization import *
import xyPlot

from abaqusConstants import *

import numpy as np
import pickle

from path_functions import create_path
from path_functions import get_stress_tensors_from_path


def write_root_pickle(data_odb_name, step_name, result_pickle_name, frame_number=None):
    Path = namedtuple('Path', ['name', 'data', 'normal'])

    with open('../planetary_gear/pickles/tooth_paths.pkl', 'rb') as pickle_handle:
        flank_data = pickle.load(pickle_handle)
        normal_flank = pickle.load(pickle_handle)  # Direction vector of the flank path
        root_data = pickle.load(pickle_handle)
        normal_root = pickle.load(pickle_handle)  # Direction vector perpendicular the root path
    paths = [Path(name='flank', data=flank_data, normal=normal_flank),
             Path(name='root', data=root_data, normal=normal_root)]

    odb = odbAccess.openOdb(data_odb_name)

    session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=309.913116455078,
                     height=230.809509277344)
    session.viewports['Viewport: 1'].makeCurrent()
    session.viewports['Viewport: 1'].maximize()
    o7 = session.odbs[session.odbs.keys()[0]]
    session.viewports['Viewport: 1'].setValues(displayedObject=o7)

    for path in paths:
        step_index = odb.steps.keys().index(step_name)
        if frame_number is None:
            frame_number = len(odb.steps[step_name].frames)
        session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_index, frame=frame_number)

        root_path = create_path(path.data, 'longitudinal_path', session)
        stress_tensors = get_stress_tensors_from_path(root_path, session)
        odb.close()

        data = np.zeros((100, 2))
        data[:, 0] = np.sqrt(np.sum((path.data - path.data[0, :])**2, 1))
        data[:, 1] = np.dot(np.dot(path.normal, stress_tensors), path.normal)

        with open(result_pickle_name[:-4] + '_' + path.name + '.pkl', 'wb') as result_pickle_handle:
            pickle.dump(data, result_pickle_handle)


if __name__ == '__main__':
    for cd in ['0_5', '0_8', '1_1', '1_4']:
        main_path = '/scratch/users/erik/scania_gear_analysis'
        odb_name = main_path + '/odb_files/fake_heat_treatment/residual_stresses_' + cd + '.odb'
        pickle_name = main_path + '/pickles/fake_heat_treatment/residual_stresses_' + cd + '.pkl'
        write_root_pickle(odb_name, step_name='Equilibrium', result_pickle_name=pickle_name)

    odb_name = '/scratch/users/erik/scania_gear_analysis/odb_files/old_heat_treatment/danteTooth.odb'
    pickle_name = '/scratch/users/erik/scania_gear_analysis/pickles/old_heat_treatment/residual_stresses_0_5.pkl'
    write_root_pickle(odb_name, step_name='danteResults_DC0_5', result_pickle_name=pickle_name, frame_number=0)

    odb_name = '/scratch/users/erik/scania_gear_analysis/odb_files/old_heat_treatment/danteTooth.odb'
    pickle_name = '/scratch/users/erik/scania_gear_analysis/pickles/old_heat_treatment/residual_stresses_0_8.pkl'
    write_root_pickle(odb_name, step_name='danteResults_DC0_8', result_pickle_name=pickle_name, frame_number=0)

    odb_name = '/scratch/users/erik/scania_gear_analysis/odb_files/old_heat_treatment/danteTooth20170220.odb'
    pickle_name = '/scratch/users/erik/scania_gear_analysis/pickles/old_heat_treatment/residual_stresses_1_1.pkl'
    write_root_pickle(odb_name, step_name='danteResults_DC1_1', result_pickle_name=pickle_name, frame_number=0)

    odb_name = '/scratch/users/erik/scania_gear_analysis/odb_files/old_heat_treatment/danteTooth20170220.odb'
    pickle_name = '/scratch/users/erik/scania_gear_analysis/pickles/old_heat_treatment/residual_stresses_1_4.pkl'
    write_root_pickle(odb_name, step_name='danteResults_DC1_4', result_pickle_name=pickle_name, frame_number=0)

