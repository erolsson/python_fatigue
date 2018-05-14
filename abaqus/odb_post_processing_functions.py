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


def get_odb_data(odb, variable, element_set_name, step, frame=0, transform=False):
    element_set = odb.rootAssembly.instances['PART-1-1'].elementSets[element_set_name]
    if transform is True and 'cylSys2' not in odb.rootAssembly.datumCsyses:
        cylindrical_sys = odb.rootAssembly.DatumCsysByThreePoints(name='cylSys2',
                                                                  coordSysType=CYLINDRICAL,
                                                                  origin=(0., 0., 0.),
                                                                  point1=(0., 1., 0.),
                                                                  point2=(1., 0., 0.))
    else:
        cylindrical_sys = odb.rootAssembly.datumCsyses['cylSys2']

    field = odb.steps[step].frames[frame].fieldOutputs[variable].getSubset(region=element_set)
    if transform:
        field = field.getTransformedField(cylindrical_sys).values
    field = field.getSubset(position=ELEMENT_NODAL).values

    n1 = len(field)
    n2 = 1
    if type(field[0].data) != float:
        n2 = len(field[0].data)
    data = np.zeros((n1, n2))

    for i, data_point in enumerate(field):
        data[i, :] = data_point.data
    return data


def get_node_data_from_set(odb, node_set_name):
    node_set = odb.rootAssembly.instances['PART-1-1'].nodeSets[node_set_name]
    node_dict = {}
    for node in node_set.nodes:
        node_dict[node.label] = node.coordinates

    return node_dict

if __name__ == '__main__':
    dante_odb = odbAccess.openOdb('/scratch/users/erik/Abaqus/Gear/planetaryGear/odb/danteTooth20170220.odb')
    mechanical_odb = odbAccess.openOdb('/scratch/users/erik/Abaqus/Gear/planetaryGear/odb/mechanicalLoadsTooth.odb')
    pickle_handle = open('/scratch/users/erik/python_fatigue/planetary_gear/rootSetLabels.pkl', 'r')
    root_set_data = []
    for _ in range(4):
        root_set_data.append(pickle.load(pickle_handle))
    pickle_handle.close()
    create_fatigue_sets(dante_odb, root_set_data, name='root')
    create_fatigue_sets(mechanical_odb, root_set_data, name='root')

    pickle_dir = '/scratch/users/erik/python_fatigue/planetary_gear/pickles/tooth_root_data'
    if not os.path.exists(pickle_dir):
        os.mkdirs(pickle_dir)
        os.mkdir(pickle_dir + '/volume_data')
        os.mkdir(pickle_dir + '/surface_data')
    for eset in ['Volume', 'Surface']:
        for case_depth in [0.5, 0.8, 1.1, 1.4]:
            step_name = 'danteResults_DC' + str(case_depth).replace('.', '_')
            residual_stress = get_odb_data(dante_odb, 'S', eset + 'Elements', step_name, 0, transform=True)
            hardness = get_odb_data(dante_odb, 'HV', eset + 'Elements', step_name, 0)
            data_dict = {'S': residual_stress, 'HV': hardness}
            pickle_name = pickle_dir + '/' + eset.lower() + '_data/danteCD' + str(case_depth).replace('.', '_') + '.pkl'
            pickle_handle = open(pickle_name, 'w')
            pickle.dump(data_dict, pickle_handle)
            pickle_handle.close()

        # Maximum load corresponds to Pamp = 32 kN
        min_load = get_odb_data(mechanical_odb, 'S', eset + 'Elements', 'minLoad', 0)
        max_load = get_odb_data(mechanical_odb, 'S', eset + 'Elements', 'maxLoad', 0)
        mechanical_dict = {'min': min_load, 'max': max_load, 'force': 32.}
        pickle_handle = open(pickle_dir + '/' + eset.lower() + '_data/mechanical_loads.pkl', 'w')
        pickle.dump(mechanical_dict)
        pickle_handle.close()

    dante_odb.close()
    mechanical_odb.close()

