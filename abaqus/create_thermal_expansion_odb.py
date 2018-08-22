import odbAccess
from abaqusConstants import *

import numpy as np

from odb_io_functions import read_field_from_odb


def create_node_field_from_element_field(fields, odb_file_name, element_set_name, step_name, frame_number,
                                         instance_name):
    for i, field in enumerate(fields):
        element_field, node_labels, _ = read_field_from_odb(field, odb_file_name, element_set_name=element_set_name,
                                                            step_name=step_name, frame_number=frame_number,
                                                            instance_name=instance_name, get_position_numbers=True)

        if i == 0:
            nodal_data = {node_label: {f: [] for f in fields} for node_label in node_labels}
        for field_value, node_label in zip(element_field, node_labels):
            nodal_data[node_label][field].append(field_value[0])
        print nodal_data.items()[5325]


if __name__ == '__main__':
    mesh = '1x'
    dante_odb_filename = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_' + \
                         mesh + '/dante_results.odb'

    fields_to_process = ['SDV_Q_MARTENSITE']
    for cd in [0.5, 0.8, 1.1, 1.4]:
        create_node_field_from_element_field(fields_to_process, dante_odb_filename, None,
                                             'dante_results_' + str(cd).replace('.', '_'), 0, 'tooth_right')
