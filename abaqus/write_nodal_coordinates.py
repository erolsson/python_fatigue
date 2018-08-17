from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import os
import pickle

from odb_io_functions import get_nodal_coordinates_from_node_set
from odb_io_functions import read_field_from_odb
from odb_io_functions import add_node_set
from odb_io_functions import add_element_set


def get_list_from_set_file(filename):
    label_list = []
    with open(filename, 'r') as set_file:
        lines = set_file.readlines()
        for line in lines:
            label_list += line.split(',')
    return [int(l) for l in label_list]


if '__name__' == '__main__':
    mesh = '1x'
    node_set_name = 'tooth_root_volume_nodes'
    element_set_name = 'tooth_root_volume_elements'
    odb_file_name = os.path.expanduser('~/scania_gear_analysis/odb_files/heat_treatment/mesh_' +
                                       mesh + '/dante_results.odb')

    node_labels = get_list_from_set_file('../planetary_gear/input_files/gear_models/planet_gear/mesh_' + mesh + '/'+
                                         node_set_name + '.inc')
    add_node_set(odb_file_name, node_set_name, node_labels, 'tooth_left')
