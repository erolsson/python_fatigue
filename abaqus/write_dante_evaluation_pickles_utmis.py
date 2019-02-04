import os
from odb_io_functions import add_element_set

from write_dante_evaluation_pickles_gear import write_dante_pickle

from write_nodal_coordinates import get_list_from_set_file


if __name__ == '__main__':
    element_set_name = 'fatigue_volume_elements'
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/dante/'
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/utmis_specimens/'

    for specimen in ['smooth', 'notched']:

        element_labels = get_list_from_set_file('../fatigue_specimens/UTMIS/utmis_' + specimen + '/' +
                                                element_set_name + '_' + specimen + '.inc')
        print element_labels
        dante_odb_filename = dante_odb_path + 'utmis_' + specimen + '.odb'
        add_element_set(dante_odb_filename, element_set_name, element_labels)
        if not os.path.isdir(pickle_directory):
            os.makedirs(pickle_directory)

        pickle_name = pickle_directory + 'data_utmis_' + specimen + '.pkl'
        write_dante_pickle(dante_odb_filename, 'dante_results_0_5', pickle_name, 'tooth_root_volume_elements')
