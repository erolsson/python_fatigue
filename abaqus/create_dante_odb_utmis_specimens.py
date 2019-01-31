from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import glob
import os
import pickle

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance
from odb_io_functions import write_field_to_odb

from materials.hardess_convertion_functions import HRC2HV

if __name__ == '__main__':
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/utmis_specimens/'
    if not os.path.isdir(dante_odb_path):
        os.makedirs(dante_odb_path)
    for specimen in ['smooth', 'notched']:
        input_file_name = '/scratch/users/erik/python_fatigue/fatigue_specimens/UTMIS/utmis_' + specimen +  \
                          '/Toolbox_Mechanical_utmis_' + specimen + '_geo.inc'
        nodes, elements = read_nodes_and_elements(input_file_name)
        instances = [OdbInstance(name='specimen_part', nodes=nodes, elements=elements)]
        odb_file_name = dante_odb_path + 'utmis_' + specimen + '.odb'
        create_odb(odb_file_name=odb_file_name, instance_data=instances)
