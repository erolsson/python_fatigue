import glob
import os

from odbAccess import *
from abaqusConstants import *

from create_odb import create_odb
from create_odb import OdbInstance

from planetary_gear.gear_input_file_functions import create_quarter_model
from planetary_gear.gear_input_file_functions import mirror_quarter_model

from write_nodal_coordinates import get_list_from_set_file
from odb_io_functions import add_element_set


def setup_odb_files(odb_file_name, parts, element_set_name='tooth_root_volume_elements'):
    model_file = '../planetary_gear/input_files/gear_models/planet_gear/mesh_' + mesh + '/mesh_planet.inc'

    quarter_nodes, quarter_elements = create_quarter_model(model_file)
    model_data = [(quarter_nodes, quarter_elements)]

    quarter_nodes, quarter_elements = mirror_quarter_model(quarter_nodes, quarter_elements)
    model_data.append((quarter_nodes, quarter_elements))

    part_names = ['left', 'right']

    instances = []
    for i in range(parts):
        instances.append(OdbInstance(name='tooth_' + part_names[i], nodes=model_data[i][0], elements=model_data[i][1]))
    create_odb(odb_file_name=odb_file_name, instance_data=instances)

    element_labels = get_list_from_set_file('../planetary_gear/input_files/gear_models/planet_gear/mesh_' + mesh +
                                            '/' + element_set_name + '.inc')

    for i in range(parts):
        add_element_set(odb_file_name, element_set_name, element_labels, 'tooth_' + part_names[i])


def load_gearbox_data():
    data_directory = findley_directory + '/gear_box/'
    findley_files = glob.glob(data_directory + 'findley_*.pkl')
    print findley_files

if __name__ == '__main__':
    mesh = '1x'
    findley_directory = os.path.expanduser('~/scania_gear_analysis/pickles/'
                                           'tooth_root_fatigue_analysis/mesh_' + mesh + '/findley')

    gearbox_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear/mesh_' + mesh + '/' +  \
                            'findley_gear_stresses_gearbox.odb'
    setup_odb_files(gearbox_odb_file_name, 2)

    pulsator_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear/mesh_' + mesh + '/' + \
                             'findley_gear_stresses_pulsator.odb'
    setup_odb_files(pulsator_odb_file_name, 1)

