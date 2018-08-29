from odbAccess import *

import glob

import pickle

from odb_io_functions import add_element_set
from odb_io_functions import read_field_from_odb

from write_nodal_coordinates import get_list_from_set_file

if __name__ == '__main__':
    mesh = '1x'
    element_set_name = 'tooth_root_volume_elements'
    gear_odb_directory = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear/mesh_' + mesh + '/'

    print glob.glob(gear_odb_directory + 'planet_gear_stresses_*.odb')

    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' \
                       + mesh + '/planet_gear_stresses/'

    element_labels = get_list_from_set_file('../planetary_gear/input_files/gear_models/planet_gear/mesh_' + mesh + '/' +
                                            element_set_name + '.inc')

    # add_element_set(pulsator_odb_filename, element_set_name, element_labels, 'tooth_left')

    # pulsator_odb = openOdb(pulsator_odb_filename)
    # step_names = pulsator_odb.steps.keys()
    # pulsator_odb.close()
    # stress_dict = {'min_load': {}, 'max_load': {}}