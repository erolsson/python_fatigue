from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance
from odb_io_functions import write_field_to_odb
from odb_io_functions import cylindrical_system_z
from odb_io_functions import flip_node_order


if __name__ == '__main__':
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_1x/'
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/heat_treatment/mesh_1x/'

    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)
    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xneg.inc'
    nodes_neg, elements_neg = read_nodes_and_elements(input_file_name)

    instances = [OdbInstance(name='tooth_right', nodes=nodes_pos, elements=elements_pos),
                 OdbInstance(name='tooth_left', nodes=nodes_neg, elements=elements_neg)]

    create_odb(odb_file_name=dante_odb_path + 'dante_results.odb', instance_data=instances)
