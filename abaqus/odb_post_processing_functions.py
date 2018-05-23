import odbAccess
from abaqusConstants import *

import os
import pickle
import numpy as np


def create_fatigue_sets(odb, set_data, name='fatigue'):
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


def get_odb_data(odb, variable, element_set_name, step, frame=0, transform=False, node_numbers=None):
    element_set = odb.rootAssembly.instances['PART-1-1'].elementSets[element_set_name]
    field = odb.steps[step].frames[frame].fieldOutputs[variable].getSubset(region=element_set)
    field = field.getSubset(position=ELEMENT_NODAL)
    if transform:
        if 'cylSys2' not in odb.rootAssembly.datumCsyses:
            cylindrical_sys = odb.rootAssembly.DatumCsysByThreePoints(name='cylSys2',
                                                                      coordSysType=CYLINDRICAL,
                                                                      origin=(0., 0., 0.),
                                                                      point1=(0., 1., 0.),
                                                                      point2=(1., 0., 0.))
        else:
            cylindrical_sys = odb.rootAssembly.datumCsyses['cylSys2']
        field = field.getTransformedField(cylindrical_sys)

    field = field.values

    n1 = len(field)
    n2 = 1 if type(field[0].data) is float else len(field[0].data)

    data = np.zeros((n1, n2))
    for i, data_point in enumerate(field):
        data[i, :] = data_point.data
    if node_numbers is not None:
        coords = np.zeros((n1, 3))
        for i, data_point in enumerate(field):
            coords[i, :] = node_numbers[data_point.nodeLabel]
        return data, coords
    return data


def get_node_data_from_set(odb, node_set_name):
    node_set = odb.rootAssembly.instances['PART-1-1'].nodeSets[node_set_name]
    node_dict = {}
    for node in node_set.nodes:
        node_dict[node.label] = node.coordinates
        if node.label == '158441':
            print "found"

    return node_dict


def create_paths(flank_points, root_points):
    def create_path(name, points):
        path_ponts = []
        for point in points:
            path_ponts.append((point[0], point[1], point[2]))

        path = session.Path(name=name, type=POINT_LIST, expression=path_ponts)
        return path

    flank_path = create_path('flank_path', flank_points)
    root_path = create_path('rootPath', root_points)
    return flank_path, root_path

if __name__ == '__main__':
    mechanical_odb = odbAccess.openOdb('/scratch/users/erik/Abaqus/Gear/planetaryGear/odb/mechanicalLoadsTooth.odb')
    pickle_handle = open('/scratch/users/erik/python_fatigue/planetary_gear/rootSetLabels.pkl', 'r')
    root_set_data = []
    for _ in range(4):
        root_set_data.append(pickle.load(pickle_handle))
    pickle_handle.close()

    create_fatigue_sets(mechanical_odb, root_set_data, name='root')

    pickle_dir = '/scratch/users/erik/python_fatigue/planetary_gear/pickles/tooth_root_data'
    if not os.path.exists(pickle_dir):
        os.makedirs(pickle_dir)
        os.mkdir(pickle_dir + '/volume_data')
        os.mkdir(pickle_dir + '/surface_data')
    for eset in ['Volume']:
        nodal_dict = get_node_data_from_set(dante_odb, 'root' + eset + 'Nodes')
        for case_depth in [0.5, 0.8, 1.1, 1.4]:
            dante_odb = odbAccess.openOdb('/scratch/users/erik/Abaqus/Gear/planetaryGear/odb/danteTooth20170220.odb')
            create_fatigue_sets(dante_odb, root_set_data, name='root')
            step_name = 'danteResults_DC' + str(case_depth).replace('.', '_')
            residual_stress = get_odb_data(dante_odb, 'S', 'root' + eset + 'Elements', step_name, 0, transform=True)
            hardness = get_odb_data(dante_odb, 'HV', 'root' + eset + 'Elements', step_name, 0)
            data_dict = {'S': residual_stress, 'HV': hardness}
            pickle_name = pickle_dir + '/' + eset.lower() + '_data/danteCD' + str(case_depth).replace('.', '_') + '.pkl'
            pickle_handle = open(pickle_name, 'w')
            pickle.dump(data_dict, pickle_handle)
            pickle_handle.close()
            dante_odb.close()

        # Maximum load corresponds to Pamp = 32 kN
        min_load, node_coords = get_odb_data(mechanical_odb, 'S', 'root' + eset + 'Elements', 'minLoad', 0,
                                             node_numbers=nodal_dict)
        max_load = get_odb_data(mechanical_odb, 'S', 'root' + eset + 'Elements', 'maxLoad', 0)
        mechanical_dict = {'min': min_load, 'max': max_load, 'force': 32.}
        mechanical_pickle = open(pickle_dir + '/' + eset.lower() + '_data/mechanical_loads.pkl', 'w')
        pickle.dump(mechanical_dict, mechanical_pickle)
        mechanical_pickle.close()

        nodal_pickle = open(pickle_dir + '/' + eset.lower() + '_data/nodal_positions.pkl', 'w')
        pickle.dump(node_coords, nodal_pickle)
        nodal_pickle.close()

    mechanical_odb.close()
