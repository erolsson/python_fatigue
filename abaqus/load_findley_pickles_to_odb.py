import os

from odbAccess import *
from abaqusConstants import *

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance


if __name__ == '__main__':

    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)

    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xneg.inc'
    nodes_neg, elements_neg = read_nodes_and_elements(input_file_name)

    instances = [OdbInstance(name='tooth_right', nodes=nodes_pos, elements=elements_pos),
                 OdbInstance(name='tooth_left', nodes=nodes_neg, elements=elements_neg)]

    tooth_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear/mesh_1x/' \
                          'findley_gear_stresses_gearbox.odb'

    create_odb(odb_file_name=tooth_odb_file_name, instance_data=instances)

    tooth_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear/mesh_1x/' \
                          'findley_gear_stresses_pulsator.odb'

    create_odb(odb_file_name=tooth_odb_file_name, instance_data=instances)