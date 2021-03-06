import odbAccess

import os
import pickle

from odb_io_functions import add_element_set
from odb_io_functions import read_field_from_odb

from write_nodal_coordinates import get_list_from_set_file

if __name__ == '__main__':
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/stresses/'
    element_set_name = 'fatigue_volume_elements'
    odb_directory = '/scratch/users/erik/scania_gear_analysis/abaqus/utmis_specimens/'

    if not os.path.isdir(pickle_directory):
        os.makedirs(pickle_directory)

    for specimen in ['smooth', 'notched']:
        mechanical_odb_filename = odb_directory + 'unit_load_' + specimen + '.odb'

        element_labels = get_list_from_set_file('../fatigue_specimens/UTMIS/utmis_' + specimen + '/' +
                                                element_set_name + '_' + specimen + '.inc')
        print "The element set", element_set_name, "has ", len(element_labels), "elements"
        add_element_set(mechanical_odb_filename, element_set_name, element_labels, instance_name='PART')

        odb = odbAccess.openOdb(mechanical_odb_filename, readOnly=False)
        step_name = odb.steps.keys()[-1]
        odb.close()
        stress = read_field_from_odb('S', mechanical_odb_filename, step_name, frame_number=-1,
                                     element_set_name=element_set_name, instance_name='PART')

        print "The stress matrix has shape ", stress.shape, "for specimen", specimen
        pickle_file_name = pickle_directory + 'unit_load_' + specimen + '.pkl'
        with open(pickle_file_name, 'w') as pickle_handle:
            pickle.dump(stress, pickle_handle)
