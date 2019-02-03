import os

from odbAccess import *

import pickle

from odb_io_functions import add_element_set
from odb_io_functions import read_field_from_odb
from odb_io_functions import cylindrical_system_z

from write_nodal_coordinates import get_list_from_set_file


def write_pickle_for_case_depth(odb_file_name, case_depth, pickle_file_name, fatigue_set_name, tooth_half='left'):
    field_vars = ['HV']
    dante_dict = {}
    step_name = 'dante_results_' + str(case_depth).replace('.', '_')
    for var in field_vars:
        dante_dict[var] = read_field_from_odb(var, odb_file_name, step_name, frame_number=0,
                                              element_set_name=fatigue_set_name, instance_name='tooth_' + tooth_half)
    residual_stress = read_field_from_odb('S', odb_file_name, step_name, frame_number=0,
                                          element_set_name=fatigue_set_name,  instance_name='tooth_' + tooth_half,
                                          coordinate_system=cylindrical_system_z)

    dante_dict['S'] = residual_stress
    with open(pickle_file_name, 'w') as pickle_handle:
        pickle.dump(dante_dict, pickle_handle)


if __name__ == '__main__':
    element_set_name = 'fatigue_volume_elements'
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/dante/'
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/utmis_specimens/'

    for specimen in ['smooth', 'notched']:

    element_labels = get_list_from_set_file('../fatigue_specimens/UTMIS/utmis_' + specimen + '/' + element_set_name +
                                            '_' + specimen + '.inc')
    dante_odb_filename =
    add_element_set(dante_odb_filename, element_set_name, element_labels, 'tooth_' + part)
    if not os.path.isdir(pickle_directory):
        os.makedirs(pickle_directory)


            pickle_name = pickle_directory + 'data_' + str(cd).replace('.', '_') + '_' + part + '.pkl'
            write_pickle_for_case_depth(dante_odb_filename, cd, pickle_name, 'tooth_root_volume_elements',
                                        tooth_half=part)
