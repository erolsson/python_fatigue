import os

import odbAccess
from visualization import *

from abaqusConstants import *

import numpy as np
import pickle

from path_functions import Path
from path_functions import create_path
from path_functions import get_stress_tensors_from_path
from path_functions import get_scalar_field_from_path


def write_case_hardening_data_along_path(data_odb_name, path, pickle_name, step_name=None, frame_number=None):
    odb = odbAccess.openOdb(data_odb_name)

    session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=309.913116455078,
                     height=230.809509277344)
    session.viewports['Viewport: 1'].makeCurrent()
    session.viewports['Viewport: 1'].maximize()
    o7 = session.odbs[session.odbs.keys()[0]]
    session.viewports['Viewport: 1'].setValues(displayedObject=o7)

    if step_name is None:
        step_name = odb.steps.keys()[-1]

    step_index = odb.steps.keys().index(step_name)
    if frame_number is None:
        frame_number = len(odb.steps[step_name].frames)
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_index, frame=frame_number)
    path.data[:, 0:2] -= 1e-4
    root_path = create_path(path.data, 'longitudinal_path', session)
    stress_tensors = get_stress_tensors_from_path(root_path, session)
    hardness = get_scalar_field_from_path(root_path, session, 'HV')
    qenched_martensite = get_scalar_field_from_path(root_path, session, 'SDV_Q_MARTENSITE')
    tempered_martensite = get_scalar_field_from_path(root_path, session, 'SDV_T_MARTENSITE')
    austenite = get_scalar_field_from_path(root_path, session, 'SDV_AUSTENITE')
    carbon = get_scalar_field_from_path(root_path, session, 'SDV_CARBON')

    data = {'r': np.sqrt(np.sum((path.data - path.data[0, :]) ** 2, 1)),
            'S': np.dot(np.dot(path.normal, stress_tensors), path.normal),
            'HV': hardness,
            'T-Martensite': tempered_martensite,
            'Q-Martensite': qenched_martensite,
            'Austenite': austenite,
            'Carbon': carbon}

    with open(pickle_name, 'wb') as result_pickle_handle:
        pickle.dump(data, result_pickle_handle)


def write_root_pickle(data_odb_name, result_pickle_name, step_name, frame_number=None):
    with open('../planetary_gear/pickles/tooth_paths.pkl', 'rb') as pickle_handle:
        flank_data = pickle.load(pickle_handle)
        normal_flank = pickle.load(pickle_handle)  # Direction vector of the flank path
        root_data = pickle.load(pickle_handle)
        normal_root = pickle.load(pickle_handle)  # Direction vector perpendicular the root path
    paths = [Path(name='flank', data=flank_data, normal=normal_flank),
             Path(name='root', data=root_data, normal=normal_root)]

    for path in paths:
        result_pickle_name = result_pickle_name[:-4] + '_' + path.name + '.pkl'
        write_case_hardening_data_along_path(data_odb_name, path, result_pickle_name, step_name, frame_number)


if __name__ == '__main__':
    for cd in ['0_5', '0_8', '1_1', '1_4']:
        main_path = '/scratch/users/erik/scania_gear_analysis'
        odb_name = main_path + '/odb_files/heat_treatment/mesh_1x/dante_results_tempering_2h_180C_20190129.odb'
        pickle_name = main_path + '/pickles/heat_treatment/mesh_1x/root_data/tempering_2h_180C_20190129/' \
                                  'dante_results_' + cd + '.pkl'
        pickle_directory = os.path.dirname(pickle_name)
        if not os.path.isdir(pickle_directory):
            os.makedirs(pickle_directory)
        write_root_pickle(odb_name, step_name='dante_results_' + str(cd), result_pickle_name=pickle_name)


