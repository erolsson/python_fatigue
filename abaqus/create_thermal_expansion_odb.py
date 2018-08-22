import odbAccess
from abaqusConstants import *

import numpy as np

from odb_io_functions import read_field_from_odb


def create_node_field_from_element_field(field, odb_file_name, element_set_name, step_name, frame_number,
                                         instance_name):
    element_field, node_labels, _ = read_field_from_odb(field, odb_file_name, element_set_name=element_set_name,
                                                        step_name=step_name, frame_number=frame_number,
                                                        instance_name=instance_name, get_position_numbers=True)

    nodal_data = {node_label: [] for node_label in node_labels}
    for field_value, node_label in zip(element_field, node_labels):
        nodal_data[node_label].append(field_value[0])
    print nodal_data.items()[5325]


if __name__ == '__main__':
    mesh = '1x'
    dante_odb_filename = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_' + \
                         mesh + '/dante_results.odb'

    for cd in [0.5, 0.8, 1.1, 1.4]:
        create_node_field_from_element_field('SDV_Q_MARTENSITE', dante_odb_filename, None,
                                             'dante_results_' + str(cd).replace('.', '_'), 0, 'tooth_right')
