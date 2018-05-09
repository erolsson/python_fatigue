import odbAccess
from abaqusConstants import *

import numpy as np


def create_fatigue_sets(odb, set_data, name='fatigue'):
    if name + 'VolumeNodes' not in odb.rootAssembly.instances['PART-1-1'].nodeSets:
        odb.rootAssembly.instances['PART-1-1'].NodeSetFromNodeLabels(name=name + 'VolumeNodes', nodeLabels=set_data[0])
    if name + 'VolumeElements' not in odb.rootAssembly.instances['PART-1-1'].elementSets:
        odb.rootAssembly.instances['PART-1-1'].ElementSetFromElementLabels(name=name + 'VolumeElements',
                                                                           elementLabels=set_data[1])
    if name + 'SurfNodes' not in odb.rootAssembly.instances['PART-1-1'].nodeSets:
        odb.rootAssembly.instances['PART-1-1'].NodeSetFromNodeLabels(name=name + 'SurfNodes', nodeLabels=set_data[2])
    if name + 'SurfElements' not in odb.rootAssembly.instances['PART-1-1'].elementSets:
        odb.rootAssembly.instances['PART-1-1'].ElementSetFromElementLabels(name=name + 'SurfElements',
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
    field = field.getSubset(position=ELEMENT_NODAL).values

    n1 = len(field)
    n2 = 1
    if type(field[0]) != float:
        n2 = len(field[0].data)
    data = np.zeros((n1, n2))

    for i, data_point in enumerate(field):
        data[i, :] = data_point.data
    print n1, n2


def get_node_data_from_set(odb, node_set_name):
    node_set = odb.rootAssembly.instances['PART-1-1'].nodeSets[node_set_name]
    node_dict = {}
    for node in node_set.nodes:
        node_dict[node.label] = node.coordinates

    return node_dict

if __name__ == '__main__':
    dante_odb = odbAccess.openOdb('/scratch/users/erik/Abaqus/Gear/planetaryGear/odb/danteTooth20170220.odb')
    get_odb_data(dante_odb, 'S', 'fatigueVolumeElements', step='danteResults_DC0_5')
    get_odb_data(dante_odb, 'HV', 'fatigueVolumeElements', step='danteResults_DC0_5')
    dante_odb.close()
    print "Odb closed "
