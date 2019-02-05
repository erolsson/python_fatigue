import odbAccess

import os
import pickle

from odb_io_functions import add_element_set
from odb_io_functions import read_field_from_odb

from write_nodal_coordinates import get_list_from_set_file

if __name__ == '__main__':
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/stresses/'
    element_set_name = 'tooth_root_volume_elements'
    odb_directory = '/scratch/users/erik/scania_gear_analysis/abaqus/utmis_specimens/'

    if not os.path.isdir(pickle_directory):
        os.makedirs(pickle_directory)

    for specimen in ['smooth', 'notched']:
        mechanical_odb_filename = odb_directory + 'unit_load_' + specimen + '.odb'

        element_labels = get_list_from_set_file('../fatigue_specimens/UTMIS/utmis_' + specimen + '/' +
                                                element_set_name + '_' + specimen + '.inc')
        add_element_set(mechanical_odb_filename, element_set_name, element_labels)

        odb = odbAccess.openOdb(mechanical_odb_filename, readOnly=False)
        step_name = odb.rootAssembly.steps.keys()[-1]
        stress = read_field_from_odb('S', mechanical_odb_filename, element_set_name, step_name, 0,
                                     instance_name='PART')

        pickle_file_name = pickle_directory + 'unit_load_' + specimen + '.pkl'
        with open(pickle_file_name, 'w') as pickle_handle:
            pickle.dump(stress, pickle_handle)
