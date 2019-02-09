import glob
import os
import pickle

from input_file_reader.input_file_functions import read_nodes_and_elements

from odb_io_functions import add_element_set
from odb_io_functions import write_field_to_odb

from create_odb import create_odb
from create_odb import OdbInstance

from write_nodal_coordinates import get_list_from_set_file

if __name__ == '__main__':
    element_set_name = 'fatigue_volume_elements'
    odb_file_directory = os.path.expanduser('~/scania_gear_analysis/odb_files/findley/utmis/')
    findley_pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/stresses/findley/'

    if not os.path.isdir(odb_file_directory):
        os.makedirs(odb_file_directory)

    for specimen in ['notched']:
        odb_file_name = odb_file_directory + 'utmis_' + specimen + '.odb'
        input_file_name = '/scratch/users/erik/python_fatigue/fatigue_specimens/UTMIS/utmis_' + specimen + \
                          '/utmis_' + specimen + '.inc'
        nodes, elements = read_nodes_and_elements(input_file_name)
        instances = [OdbInstance(name='specimen_part', nodes=nodes, elements=elements)]

        create_odb(odb_file_name, instances)
        element_labels = get_list_from_set_file('../fatigue_specimens/UTMIS/utmis_' + specimen + '/' +
                                                element_set_name + '_' + specimen + '.inc')
        add_element_set(odb_file_name, element_set_name, element_labels)

        findley_parameter_directories = glob.glob(findley_pickle_directory + 'a800=*/')
        findley_parameter_directories = [os.path.normpath(directory).split(os.sep)[-1]
                                         for directory in findley_parameter_directories]
        findley_parameters = [directory[5:] for directory in findley_parameter_directories]

        for findley_parameter in findley_parameters:
            for R in [0, -1]:
                pickle_filenames = glob.glob(findley_pickle_directory + 'a800=' + findley_parameter + '/findley_' +
                                             specimen + '_R=' + str(int(R)) + '_' + 's=*.pkl')
                stress_amps = [filename[-10:-7] for filename in pickle_filenames]
                for pickle_file, load in zip(pickle_filenames, stress_amps):
                    print 'loading pickle file', pickle_file
                    with open(pickle_file, 'r') as pickle_handle:
                        findley_stress = pickle.load(pickle_handle)
                    step_name = 'a800=' + findley_parameter + 'R=' + str(int(R)) + '_' + 'samp=' + str(load) + 'MPa'
                    write_field_to_odb(findley_stress, 'SF', odb_file_name, step_name, set_name=element_set_name)
                    print 'Done with step', step_name
