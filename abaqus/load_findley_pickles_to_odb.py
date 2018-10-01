import os

from odbAccess import *
from abaqusConstants import *

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance


def setup_odb_files(odb_file_name, parts):
    input_file_names = ['/scratch/users/erik/python_fatigue/planetary_gear/'
                        'input_files/planet_sun/planet_dense_geom_xneg.inc',
                        '/scratch/users/erik/python_fatigue/planetary_gear/'
                        'input_files/planet_sun/planet_dense_geom_xpos.inc']

    part_names = ['left', 'right']

    instances = []
    for i in range(parts):
        nodes, elements = read_nodes_and_elements(input_file_names[i])
        instances.append(OdbInstance(name='tooth_' + part_names[i], nodes=nodes, elements=elements))
    create_odb(odb_file_name=odb_file_name, instance_data=instances)


if __name__ == '__main__':
    findley_directory = os.path.expanduser('~/scania_gear_analysis/pickles/'
                                           'tooth_root_fatigue_analysis/mesh_1x/findley')

    gearbox_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear/mesh_1x/' \
                            'findley_gear_stresses_gearbox.odb'
    setup_odb_files(gearbox_odb_file_name, 2)

    pulsator_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear/mesh_1x/' \
                             'findley_gear_stresses_pulsator.odb'
    setup_odb_files(pulsator_odb_file_name, 1)