from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import os
import pickle

import numpy as np

from materials.gear_materials import SteelData

from odb_io_functions import add_element_set
from odb_io_functions import read_field_from_odb
from odb_io_functions import cylindrical_system_z

from write_nodal_coordinates import get_list_from_set_file


def write_pickle_for_case_depth(odb_file_name, case_depth, pickle_file_name, fatigue_set_name):
    field_vars = ['HV']
    dante_dict = {}
    step_name = 'dante_results_' + str(case_depth).replace('.', '_')
    for var in field_vars:
        dante_dict[var] = read_field_from_odb(var, odb_file_name, element_set_name, step_name, frame_number=0,
                                              instance_name='tooth_left')
    steel_data = SteelData(**dante_dict)
    residual_stress = read_field_from_odb('S', odb_file_name, element_set_name, step_name, frame_number=0,
                                          instance_name='tooth_left')
    print np.max(residual_stress)


if __name__ == '__main__':
    mesh = '1x'
    element_set_name = 'tooth_root_volume_elements'
    dante_odb_filename = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_' + \
                         mesh + '/dante_results.odb'
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' \
                       + mesh + '/dante'

    element_labels = get_list_from_set_file('../planetary_gear/input_files/gear_models/planet_gear/mesh_' + mesh + '/' +
                                            element_set_name + '.inc')

    add_element_set(dante_odb_filename, element_set_name, element_labels, 'tooth_right')
    add_element_set(dante_odb_filename, element_set_name, element_labels, 'tooth_left')
    write_pickle_for_case_depth(dante_odb_filename, 0.5, '', 'tooth_root_volume_elements')
