from odbAccess import *

import pickle

from odb_io_functions import add_element_set
from odb_io_functions import read_field_from_odb

from write_nodal_coordinates import get_list_from_set_file


if __name__ == '__main__':
    mesh = '1x'
    element_set_name = 'tooth_root_volume_elements'
    pulsator_odb_filename = '/scratch/users/erik/scania_gear_analysis/odb_files/pulsator/mesh_' + \
                            mesh + '/pulsator_stresses.odb'

    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' \
                       + mesh + '/pulsator_stresses/'

    element_labels = get_list_from_set_file('../planetary_gear/input_files/gear_models/planet_gear/mesh_' + mesh + '/' +
                                            element_set_name + '.inc')

    add_element_set(pulsator_odb_filename, element_set_name, element_labels, 'tooth_left')

    pulsator_odb = openOdb(pulsator_odb_filename)
    step_names = pulsator_odb.steps.keys()
    pulsator_odb.close()
    stress_dict = {'min_load': {}, 'max_load': {}}
    for step_name in step_names:
        min_load = read_field_from_odb('S', pulsator_odb_filename, step_name, 0,
                                       element_set_name=element_set_name, instance_name='tooth_left')
        max_load = read_field_from_odb('S', pulsator_odb_filename, step_name, 1,
                                       element_set_name=element_set_name, instance_name='tooth_left')

        load = float(step_name[5:9].replace('_', '.'))
        stress_dict['min_load'][load] = min_load
        stress_dict['max_load'][load] = max_load

    pickle_file_name = 'pulsator_stresses.pkl'
    with open(pickle_directory + pickle_file_name, 'w') as pickle_handle:
        pickle.dump(stress_dict, pickle_handle)
