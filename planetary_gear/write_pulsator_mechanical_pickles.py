import sys

from odbAccess import openOdb

import pickle

import numpy as np

from gear_input_file_functions import create_quarter_model
from gear_input_file_functions import mirror_quarter_model

from abaqus_files.odb_io_functions import add_element_set
from abaqus_files.odb_io_functions import read_field_from_odb

from abaqus_files.write_nodal_coordinates import get_list_from_set_file

if __name__ == '__main__':
    mesh = '1x'
    element_set_name = sys.argv[-1]
    pulsator_odb_filename = '/scratch/users/erik/scania_gear_analysis/odb_files/pulsator/mesh_' + \
                            mesh + '/pulsator_stresses.odb'

    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' \
                       + mesh + '/pulsator_stresses/'
    pulsator_odb = openOdb(pulsator_odb_filename)
    step_names = pulsator_odb.steps.keys()
    if element_set_name.lower() != 'all_elements':
        if element_set_name not in pulsator_odb.rootAssembly.instances['tooth_left'].elementSets:
            element_labels = get_list_from_set_file(
                'input_files/gear_models/planet_gear/mesh_' + mesh + '/' +
                element_set_name + '.inc')
            add_element_set(pulsator_odb_filename, element_set_name, element_labels, 'tooth_left')
        e_set_name = element_set_name
    else:
        e_set_name = None
    pulsator_odb.close()

    stress_dict = {'min_load': {}, 'max_load': {}}
    positions_written = False

    for step_name in step_names:
        if not positions_written:
            min_load, node_labels, _ = read_field_from_odb('S', pulsator_odb_filename, step_name, 0,
                                                           element_set_name=e_set_name, instance_name='tooth_left',
                                                           get_position_numbers=True)
            nodes, elements = create_quarter_model('input_files/gear_models/planet_gear/mesh_' + mesh
                                                   + '/mesh_planet.inc')
            nodes, elements = mirror_quarter_model(nodes, elements)
            nodal_data = np.zeros((min_load.shape[0], 3))
            nodal_coordinates = {}
            for i in range(nodes.shape[0]):
                nodal_coordinates[nodes[i, 0]] = nodes[i, 1:]
            for i, label in enumerate(node_labels):
                nodal_data[i, :] = nodal_coordinates[label]
            stress_dict['pos'] = nodal_data
            positions_written = True
        else:
            min_load = read_field_from_odb('S', pulsator_odb_filename, step_name, 0,
                                           element_set_name=e_set_name, instance_name='tooth_left')
        max_load = read_field_from_odb('S', pulsator_odb_filename, step_name, 1,
                                       element_set_name=e_set_name, instance_name='tooth_left')

        load = float(step_name[5:9].replace('_', '.'))
        stress_dict['min_load'][load] = min_load
        stress_dict['max_load'][load] = max_load

    pickle_file_name = 'pulsator_stresses_' + element_set_name + '.pkl'
    with open(pickle_directory + pickle_file_name, 'w') as pickle_handle:
        pickle.dump(stress_dict, pickle_handle)
