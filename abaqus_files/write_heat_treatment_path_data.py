import os

import odbAccess
from visualization import *

from abaqusConstants import ELEMENT_NODAL

import numpy as np
import pickle

from path_functions import Path
from path_functions import create_path
from path_functions import get_stress_tensors_from_path
from path_functions import get_scalar_field_from_path


def write_case_hardening_data_along_path(data_odb_name, path, pickle_name, session, fields,
                                         step_name=None, frame_number=None, output_position=ELEMENT_NODAL):
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
    data_dict = {}

    for field in fields:
        if field == 'S':
            data = get_stress_tensors_from_path(root_path, session, output_position)
            nx, ny, nz = path.normal
            data_dict['normal_stress'] = ((data[:, 1]*nx + data[:, 4]*ny + data[:, 5]*nz)*nx
                                          + (data[:, 4]*nx + data[:, 2]*ny + data[:, 6]*nz)*ny
                                          + (data[:, 5]*nx + data[:, 6]*ny + data[:, 3]*nz)*nz)

        else:
            data = get_scalar_field_from_path(root_path, session, field, output_position)
        data_dict[field] = data[:, 1:]
        if 'r' not in data_dict:
            data_dict['r'] = data[:, 0]

    with open(pickle_name, 'wb') as result_pickle_handle:
        pickle.dump(data_dict, result_pickle_handle)
    odb.close()


def write_root_pickle(data_odb_name, result_pickle_name, step_name, frame_number=None):
    with open('../planetary_gear/pickles/tooth_paths.pkl', 'rb') as pickle_handle:
        flank_data = pickle.load(pickle_handle)
        normal_flank = pickle.load(pickle_handle)  # Direction vector of the flank path
        root_data = pickle.load(pickle_handle)
        normal_root = pickle.load(pickle_handle)  # Direction vector perpendicular the root path
    paths = [Path(name='flank', data=flank_data, normal=normal_flank),
             Path(name='root', data=root_data, normal=normal_root)]

    for path in paths:
        write_case_hardening_data_along_path(data_odb_name, path, result_pickle_name[:-4] + '_' + path.name + '.pkl',
                                             session, step_name, frame_number)


def main():
    odb_file = os.path.expanduser('~/scania_gear_analysis/odb_files/heat_treatment/mesh_1x/'
                                  'carbon_transfer.odb')
    pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/heat_treatment/mesh_1x/root_data/'
                                     'carbon_transfer_decarburization/')
    if not os.path.isdir(pickle_path):
        os.makedirs(pickle_path)
    for cd in [0.5, 0.8, 1.1, 1.4]:
        with open('../planetary_gear/pickles/tooth_paths.pkl', 'rb') as pickle_handle:
            flank_data = pickle.load(pickle_handle)
            normal_flank = pickle.load(pickle_handle)  # Direction vector of the flank path
            root_data = pickle.load(pickle_handle)
            normal_root = pickle.load(pickle_handle)  # Direction vector perpendicular the root path
        paths = [Path(name='flank', data=flank_data, normal=normal_flank),
                 Path(name='root', data=root_data, normal=normal_root)]
        step_name = 'dante_results_' + str(cd).replace('.', '_')
        fields = ['HV', 'SDV_CARBON', 'S', 'SDV_AUSTENITE', 'SDV_Q_MARTENSITE',
                  'SDV_T_MARTENSITE', 'SDV_UBAINITE', 'SDV_LBAINITE']
        for path in paths:
            write_case_hardening_data_along_path(odb_file, path,
                                                 pickle_path + 'dante_results_' + str(cd).replace('.', '_')
                                                 + '_' + path.name + '.pkl',
                                                 session, fields, step_name, frame_number=0)


if __name__ == '__main__':
    main()
