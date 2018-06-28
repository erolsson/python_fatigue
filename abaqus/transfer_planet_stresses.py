from odbAccess import *

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance


def transfer_gear_stresses(from_odb_name, to_odb_name):
    # inspect odb to find steps in frames
    simulation_odb = openOdb(from_odb_name, readOny=True)
    step_names = [name for name in simulation_odb.steps.keys() if 'Loading_tooth' in name]
    print step_names
    simulation_odb.close()

if __name__ == '__main__':
    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)

    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xneg.inc'
    nodes_neg, elements_neg = read_nodes_and_elements(input_file_name)

    instances = [OdbInstance(name='right_part', nodes=nodes_pos, elements=elements_pos),
                 OdbInstance(name='left_part', nodes=nodes_neg, elements=elements_neg)]

    tooth_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear_stresses.odb'

    create_odb(odb_file_name=tooth_odb_file_name,
               instance_data=instances)

# Importing stress history from the planet-sun simulations
simulation_odb_name = '/scratch/users/erik/python_fatigue/planetary_gear/input_files/planet_sun/planet_sun_400Nm.odb'

