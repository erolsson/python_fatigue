from abaqusConstants import *

import odbAccess

import os
import pickle
import numpy as np

from odb_io_functions import read_field_from_odb
from odb_io_functions import cylindrical_system_z


def create_fatigue_sets(odb_file_name, set_data, name='fatigue'):
    odb = odbAccess.openOdb(odb_file_name, readOnly=False)
    if name + 'VolumeNodes' not in odb.rootAssembly.instances['PART-1-1'].nodeSets:
        odb.rootAssembly.instances['PART-1-1'].NodeSetFromNodeLabels(name=name + 'VolumeNodes', nodeLabels=set_data[0])
    if name + 'VolumeElements' not in odb.rootAssembly.instances['PART-1-1'].elementSets:
        odb.rootAssembly.instances['PART-1-1'].ElementSetFromElementLabels(name=name + 'VolumeElements',
                                                                           elementLabels=set_data[1])
    if name + 'SurfaceNodes' not in odb.rootAssembly.instances['PART-1-1'].nodeSets:
        odb.rootAssembly.instances['PART-1-1'].NodeSetFromNodeLabels(name=name + 'SurfaceNodes', nodeLabels=set_data[2])
    if name + 'SurfaceElements' not in odb.rootAssembly.instances['PART-1-1'].elementSets:
        odb.rootAssembly.instances['PART-1-1'].ElementSetFromElementLabels(name=name + 'SurfaceElements',
                                                                           elementLabels=set_data[3])
    odb.close()
# ToDo: Rewrite get odb data


def get_node_data_from_set(odb_file_name, node_set_name):
    odb = odbAccess.openOdb(odb_file_name, readOnly=True)
    node_set = odb.rootAssembly.instances['PART-1-1'].nodeSets[node_set_name]
    node_dict = {}
    for node in node_set.nodes:
        node_dict[node.label] = node.coordinates
    odb.close()
    return node_dict


def create_path(points, name):
    path_points = []
    for point in points:
        path_points.append((point[0], point[1], point[2]))

    data_path = session.Path(name=name, type=POINT_LIST, expression=path_points)
    return data_path

if __name__ == '__main__':
    mechanical_odb_name = '/scratch/users/erik/Abaqus/Gear/planetaryGear/odb/mechanicalLoadsTooth.odb'
    dante_odb_name = '/scratch/users/erik/Abaqus/Gear/planetaryGear/odb/danteTooth20170220.odb'
    pickle_handle = open('/scratch/users/erik/python_fatigue/planetary_gear/rootSetLabels.pkl', 'r')
    root_set_data = []
    for _ in range(4):
        root_set_data.append(pickle.load(pickle_handle))
    pickle_handle.close()

    create_fatigue_sets(mechanical_odb_name, root_set_data, name='root')

    pickle_dir = '/scratch/users/erik/python_fatigue/planetary_gear/pickles/tooth_root_data'
    if not os.path.exists(pickle_dir):
        os.makedirs(pickle_dir)
        os.mkdir(pickle_dir + '/volume_data')
        os.mkdir(pickle_dir + '/surface_data')
    for element_set in ['Volume']:
        element_set_name = 'root' + element_set + 'Elements'
        nodal_dict = get_node_data_from_set(mechanical_odb_name, 'root' + element_set + 'Nodes')
        for case_depth in [0.5, 0.8, 1.1, 1.4]:
            dante_odb = odbAccess.openOdb('/scratch/users/erik/Abaqus/Gear/planetaryGear/odb/danteTooth20170220.odb')
            create_fatigue_sets(dante_odb_name, root_set_data, name='root')
            step_name = 'danteResults_DC' + str(case_depth).replace('.', '_')
            residual_stress = read_field_from_odb(field_id='S', odb_file_name=dante_odb_name,
                                                  element_set_name=element_set_name,
                                                  step_name=step_name, frame_number=0,
                                                  coordinate_system=cylindrical_system_z)

            hardness = read_field_from_odb(field_id='HV', odb_file_name=dante_odb_name,
                                           element_set_name=element_set_name,
                                           step_name=step_name, frame_number=0)
            data_dict = {'S': residual_stress, 'HV': hardness}
            pickle_name = pickle_dir + '/' + element_set.lower() + '_data/danteCD' + \
                str(case_depth).replace('.', '_') + '.pkl'

            pickle_handle = open(pickle_name, 'w')
            pickle.dump(data_dict, pickle_handle)
            pickle_handle.close()

        # Maximum load corresponds to Pamp = 32 kN
        min_load, node_labels, _ = read_field_from_odb('S', odb_file_name=mechanical_odb_name,
                                                       element_set_name=element_set_name,
                                                       step_name='minLoad', frame_number=0,
                                                       position_numbers=True)

        max_load = read_field_from_odb('S', odb_file_name=mechanical_odb_name,
                                       element_set_name=element_set_name,
                                       step_name='maxLoad', frame_number=0,
                                       position_numbers=True)

        mechanical_dict = {'min': min_load, 'max': max_load, 'force': 32.}
        mechanical_pickle = open(pickle_dir + '/' + element_set.lower() + '_data/mechanical_loads.pkl', 'w')
        pickle.dump(mechanical_dict, mechanical_pickle)
        mechanical_pickle.close()

        node_coordinates = np.zeros((min_load.shape[0], 3))
        for i, node_label in enumerate(node_labels):
            node_coordinates[i, :] = nodal_dict[node_label]

        nodal_pickle = open(pickle_dir + '/' + element_set.lower() + '_data/nodal_positions.pkl', 'w')
        pickle.dump(node_coordinates, nodal_pickle)
        nodal_pickle.close()
