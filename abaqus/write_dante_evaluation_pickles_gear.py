import os

import odbAccess

import pickle

from odb_io_functions import add_element_set
from odb_io_functions import read_field_from_odb
from odb_io_functions import cylindrical_system_z

from write_nodal_coordinates import get_list_from_set_file


def write_dante_pickle(odb_file_name, step_name, pickle_file_name, fatigue_set_name=None, instance_name=None,
                       coordinate_system=None):
    field_vars = ['HV']
    dante_dict = {}

    if instance_name is None:
        odb = odbAccess.openOdb(odb_file_name, readOnly=True)
        instance_names = odb.rootAssembly.instances.keys()
        if len(instance_names) == 1:
            instance_name = instance_names[0]
        else:
            raise ValueError('odb has multiple instances, please specify an instance')
    for var in field_vars:
        dante_dict[var] = read_field_from_odb(var, odb_file_name, step_name, frame_number=0,
                                              element_set_name=fatigue_set_name, instance_name=instance_name)
    residual_stress = read_field_from_odb('S', odb_file_name, step_name, frame_number=0,
                                          element_set_name=fatigue_set_name,  instance_name=instance_name,
                                          coordinate_system=coordinate_system)

    dante_dict['S'] = residual_stress
    with open(pickle_file_name, 'w') as pickle_handle:
        pickle.dump(dante_dict, pickle_handle)


if __name__ == '__main__':
    mesh = '1x'
    element_set_name = 'tooth_root_volume_elements'
    dante_odb_filename = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_' + \
                         mesh + '/dante_results_tempering_2h_180C_20190129.odb'
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' \
                       + mesh + '/dante_tempering_2h_180C_20190129/'

    element_labels = get_list_from_set_file('../planetary_gear/input_files/gear_models/planet_gear/mesh_' + mesh + '/' +
                                            element_set_name + '.inc')

    if not os.path.isdir(pickle_directory):
        os.makedirs(pickle_directory)
    for part in ['left', 'right']:
        add_element_set(dante_odb_filename, element_set_name, element_labels, 'tooth_' + part)

        for cd in [0.5, 0.8, 1.1, 1.4]:
            pickle_name = pickle_directory + 'data_' + str(cd).replace('.', '_') + '_' + part + '.pkl'
            step = 'dante_results_' + str(cd).replace('.', '_')
            write_dante_pickle(dante_odb_filename, step, pickle_name, 'tooth_root_volume_elements',
                               instance_name='tooth_' + part, coordinate_system=cylindrical_system_z)
