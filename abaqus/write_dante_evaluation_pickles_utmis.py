import os

from odb_io_functions import read_field_from_odb
from odb_io_functions import add_element_set

from write_dante_evaluation_pickles_gear import write_dante_pickle
from input_file_reader.input_file_reader import InputFileReader

from write_nodal_coordinates import get_list_from_set_file


if __name__ == '__main__':
    element_set_name = 'fatigue_volume_elements'
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/dante/'
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/utmis_specimens/'

    for specimen in ['smooth', 'notched']:

        element_labels = get_list_from_set_file('../fatigue_specimens/UTMIS/utmis_' + specimen + '/' +
                                                element_set_name + '_' + specimen + '.inc')
        dante_odb_filename = dante_odb_path + 'utmis_' + specimen + '.odb'
        add_element_set(dante_odb_filename, element_set_name, element_labels)
        if not os.path.isdir(pickle_directory):
            os.makedirs(pickle_directory)

        pickle_name = pickle_directory + 'data_utmis_' + specimen + '.pkl'
        write_dante_pickle(dante_odb_filename, 'dante_results_0_5', pickle_name, element_set_name)

        # Writes the nodal coordinates
        input_file_reader = InputFileReader()
        input_file_reader.read_input_file('../fatigue_specimens/UTMIS/utmis_' + specimen + '/' + 'utmis_' +
                                          specimen + '.inc')

        # get the node labels by reading HV

        _, node_labels, _ = read_field_from_odb('HV', dante_odb_filename, step_name='dante_results_0_5', frame_number=0,
                                                element_set_name=element_set_name, get_position_numbers=True)

        print node_labels[0]
        print node_labels[-1]

        print input_file_reader.nodal_data.shape
        print input_file_reader.nodal_data[0]
        print input_file_reader.nodal_data[-1]
