from odbAccess import *

import glob
import os

import pickle

from odb_io_functions import add_element_set
from odb_io_functions import read_field_from_odb

from write_nodal_coordinates import get_list_from_set_file

if __name__ == '__main__':
    mesh = '1x'
    element_set_name = 'tooth_root_volume_elements'
    gear_odb_directory = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear/mesh_' + mesh + '/'

    obb_files = glob.glob(gear_odb_directory + 'planet_gear_stresses_*.odb')
    print obb_files

    simulated_loads = [float(os.path.basename(file_name).replace('planet_gear_stresses_', '').replace('_Nm.odb', ''))
                       for file_name in obb_files]
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
