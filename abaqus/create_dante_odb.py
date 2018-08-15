from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import pickle

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance
from odb_io_functions import write_field_to_odb
from odb_io_functions import cylindrical_system_z
from odb_io_functions import flip_node_order

"""
def create_dante_step(odb_name, results_step_name):


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

    create_odb(odb_file_name=dante_odb_path + 'dante_results.odb', instance_data=instances)
    pickle_file = pickle_directory + 'case_depth_0_5/Toolbox_Mechanical_0_5_quarter_S.pkl'
    with open(pickle_file, 'r') as pickle_handle:
        data = pickle.load(pickle_handle)
        print data
