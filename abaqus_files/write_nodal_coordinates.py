from odbAccess import *

import os
import pickle

import numpy as np

from create_files_for_mechanical_analysis import get_nodal_coordinates_from_node_set
from create_files_for_mechanical_analysis import read_field_from_odb
from create_files_for_mechanical_analysis import add_node_set
from create_files_for_mechanical_analysis import add_element_set


def get_list_from_set_file(filename):
    label_list = []
    with open(filename, 'r') as set_file:
        lines = set_file.readlines()
        for line in lines:
            label_list += line.split(',')
    return [int(l) for l in label_list]


if __name__ == '__main__':
    mesh = '1x'
    node_set_name = 'tooth_root_volume_nodes'
    element_set_name = 'tooth_root_volume_elements'
    odb_file_name = os.path.expanduser('~/scania_gear_analysis/odb_files/heat_treatment/mesh_' +
                                       mesh + '/dante_results.odb')

    coordinate_pickle_file_name = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/'
                                                     'mesh_' + mesh + '/geometry/nodal_positions.pkl')

    node_labels = get_list_from_set_file('../planetary_gear/input_files/gear_models/planet_gear/mesh_' + mesh + '/' +
                                         node_set_name + '.inc')
    element_labels = get_list_from_set_file('../planetary_gear/input_files/gear_models/planet_gear/mesh_' + mesh + '/' +
                                            element_set_name + '.inc')

    add_node_set(odb_file_name, node_set_name, node_labels, 'tooth_right')
    add_element_set(odb_file_name, element_set_name, element_labels, 'tooth_right')

    _, node_labels, _ = read_field_from_odb('HV', odb_file_name, element_set_name, step_name='dante_results_0_5',
                                            frame_number=0, instance_name='tooth_right', get_position_numbers=True)
    nodal_dict = get_nodal_coordinates_from_node_set(odb_file_name, node_set_name, instance_name='tooth_right')

    node_coordinates = np.zeros((len(node_labels), 3))
    for i, node_label in enumerate(node_labels):
        node_coordinates[i, :] = nodal_dict[node_label]

    with open(coordinate_pickle_file_name, 'w') as pickle_handle:
        pickle.dump(node_coordinates, pickle_handle)
