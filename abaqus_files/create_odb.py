from collections import namedtuple

from odbAccess import *
from abaqusConstants import *

import os

from python_fatigue.input_file_reader.input_file_functions import read_nodes_and_elements

OdbInstance = namedtuple('OdbInstance', ['name', 'nodes', 'elements'])


def create_odb(odb_file_name, instance_data):
    if not os.path.isdir(os.path.dirname(odb_file_name)):
        os.makedirs(os.path.dirname(odb_file_name))
    odb = Odb(name=os.path.basename(odb_file_name), path=odb_file_name)

    for instance in instance_data:
        nodal_data = [(int(n[0]), n[1], n[2], n[3]) for n in instance.nodes]
        part = odb.Part(name=instance.name, embeddedSpace=THREE_D, type=DEFORMABLE_BODY)  # Todo Implement 2D models
        part.addNodes(nodeData=nodal_data)
        part.addElements(elementData=instance.elements.tolist(), type='C3D8')
        odb.rootAssembly.Instance(name=instance.name, object=part)

    odb.update()
    odb.save()
    odb.close()


if __name__ == '__main__':
    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)

    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xneg.inc'
    nodes_neg, elements_neg = read_nodes_and_elements(input_file_name)

    instances = [OdbInstance(name='right_part', nodes=nodes_pos, elements=elements_pos),
                 OdbInstance(name='left_part', nodes=nodes_neg, elements=elements_neg)]

    create_odb(odb_file_name=r'/scratch/users/erik/scania_gear_analysis/odb_files/stress.odb',
               instance_data=instances)
