from odbAccess import *

import glob
import os
import pickle

import numpy as np

from create_files_for_mechanical_analysis import add_element_set
from create_files_for_mechanical_analysis import read_field_from_odb

from write_nodal_coordinates import get_list_from_set_file

if __name__ == '__main__':
    mesh = '1x'
    element_set_name = 'tooth_root_volume_elements'
    gear_odb_directory = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear/mesh_' + mesh + '/'

    odb_files = glob.glob(gear_odb_directory + 'planet_gear_stresses_*.odb')

    simulated_loads = [float(os.path.basename(file_name).replace('planet_gear_stresses_', '').replace('_Nm.odb', ''))
                       for file_name in odb_files]
    print simulated_loads

    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' \
                       + mesh + '/planet_gear_stresses/'

    element_labels = get_list_from_set_file('../planetary_gear/input_files/gear_models/planet_gear/mesh_' + mesh + '/' +
                                            element_set_name + '.inc')

    for odb_file in odb_files:
        add_element_set(odb_file, element_set_name, element_labels, 'tooth_left')
        add_element_set(odb_file, element_set_name, element_labels, 'tooth_right')

    stress_dict = {'tooth_left': {'min_load': {}, 'max_load': {}},
                   'tooth_right': {'min_load': {}, 'max_load': {}}}
    root_path_names = {'tooth_left': 'neg', 'tooth_right': 'pos'}

    for load in simulated_loads:
        for tooth_part in ['tooth_left', 'tooth_right']:
            tooth_stress_pickle_dir = '/scratch/users/erik/scania_gear_analysis/pickles/tooth_root_stresses/'
            tooth_root_pickle_name = 'stresses_' + str(int(load)) + '_Nm_' + root_path_names[tooth_part] + '.pkl'
            with open(tooth_stress_pickle_dir + tooth_root_pickle_name) as pickle_handle:
                tooth_root_stresses = pickle.load(pickle_handle)
            idx_max = np.argmax(tooth_root_stresses[:, 1])
            idx_min = np.argmin(tooth_root_stresses[:, 1])

            odb_file_name = gear_odb_directory + 'planet_gear_stresses_' + str(int(load)) + '_Nm.odb'
            min_load = read_field_from_odb('S', odb_file_name=odb_file_name, element_set_name=element_set_name,
                                           step_name='mechanical_stresses', frame_number=idx_min,
                                           instance_name=tooth_part)
            max_load = read_field_from_odb('S', odb_file_name=odb_file_name, element_set_name=element_set_name,
                                           step_name='mechanical_stresses', frame_number=idx_max,
                                           instance_name=tooth_part)

            stress_dict[tooth_part]['max_load'][load] = max_load
            stress_dict[tooth_part]['min_load'][load] = min_load

    with open(pickle_directory + 'gear_stresses.pkl', 'w') as pickle_handle:
        pickle.dump(stress_dict, pickle_handle)
