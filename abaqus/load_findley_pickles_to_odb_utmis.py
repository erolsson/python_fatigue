import glob
import os
import pickle

from input_file_reader.input_file_functions import read_nodes_and_elements

from odb_io_functions import add_element_set
from odb_io_functions import write_field_to_odb

from create_odb import create_odb
from create_odb import OdbInstance

if __name__ == '__main__':
    odb_file_directory = os.path.expanduser('~/scania_gear_analysis/odb_files/findley/utmis/')
    findley_pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/stresses/findley/'



    if not os.path.isdir(odb_file_directory):
        os.makedirs(odb_file_directory)

    for specimen in ['smooth', 'notched']:
        odb_file_name = odb_file_directory + 'utmis_' + specimen + '.odb'
        input_file_name = '/scratch/users/erik/python_fatigue/fatigue_specimens/UTMIS/utmis_' + specimen + \
                          '/utmis_' + specimen + '.inc'
        nodes, elements = read_nodes_and_elements(input_file_name)
        instances = [OdbInstance(name='specimen_part', nodes=nodes, elements=elements)]

        create_odb(odb_file_name, instances)

        for R in [0, -1]:
            pickle_filenames = glob.glob(findley_pickle_directory + 'findley_' + specimen + '_R=' + str(int(R)) + '_'
                                         + 's=*.pkl')
            print pickle_filenames
            stress_amps = [filename[-7:-4] for filename in pickle_filenames]
            print stress_amps