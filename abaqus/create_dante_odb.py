from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import os
import pickle

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance
from odb_io_functions import write_field_to_odb
from odb_io_functions import cylindrical_system_z
from odb_io_functions import flip_node_order


def create_dante_step(odb_name, pickle_directory, results_step_name):
    files = os.listdir(pickle_directory)
    print files
    """
    write_field_to_odb(field_data=stress, field_id='S', odb_file_name=odb_name, step_name=results_step_name,
                       instance_name='tooth_right', frame_number=0,
                       invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])

    stress = flip_node_order(stress, axis='z')
    stress[:, 3] *= -1
    write_field_to_odb(field_data=stress, field_id='S', odb_file_name=odb_name, step_name=results_step_name,
                       instance_name='tooth_left', frame_number=0,
                       invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])
    """


if __name__ == '__main__':
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_1x/'
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/heat_treatment/mesh_1x/fem_results/'

    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)
    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xneg.inc'
    nodes_neg, elements_neg = read_nodes_and_elements(input_file_name)

    instances = [OdbInstance(name='tooth_right', nodes=nodes_pos, elements=elements_pos),
                 OdbInstance(name='tooth_left', nodes=nodes_neg, elements=elements_neg)]

    odb_file_name = dante_odb_path + 'dante_results.odb'
    create_odb(odb_file_name=odb_file_name, instance_data=instances)

    for cd in [0.5, 0.8, 1.1, 1.4]:
        create_dante_step(odb_name=odb_file_name,
                          pickle_directory=pickle_directory + 'case_depth_' + str(cd).replace('.', '_'),
                          results_step_name='dante_results_' + str(cd).replace('.', '_'))
