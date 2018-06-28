from collections import namedtuple

from odbAccess import *
from abaqusConstants import *

import os

from input_file_reader.input_file_functions import read_nodes_and_elements

OdbInstance = namedtuple('OdbInstance', ['name', 'nodes', 'elements'])


def create_odb(odb_file_name, instance_data):
    print os.path.basename(odb_file_name), os.path.dirname(odb_file_name)
    odb = Odb(name=os.path.basename(odb_file_name), path=odb_file_name)

    for instance in instance_data:

        part = odb.Part(name=instance.name, embeddedSpace=THREE_D, type=DEFORMABLE_BODY)  # Todo Implement 2D models
        odb.rootAssembly.Instance(name=instance.name, object=part)

    odb.update()
    odb.save()
    odb.close()

if __name__ == '__main__':
    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)
    print nodes_pos, elements_pos
    model_data = 0
    instances = [OdbInstance(name='right_part', nodes=nodes_pos, elements=elements_pos)]
    create_odb(odb_file_name=r'/scratch/users/erik/scania_gear_analysis/odb_files/stress.odb',
               instance_data=instances)
