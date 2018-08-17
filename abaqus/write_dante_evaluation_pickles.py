from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import os
import pickle

import numpy as np


def write_pickle_for_case_depth(odb_file_name, pickle_file_name, fatigue_set_name, fatigue_set_data):
    odb = openOdb(odb_file_name)
    for instance_name in ['left', 'right']:
        if fatigue_set_name not in odb.rootAssembly.elementSets:
            instance = odb.rootAssembly.instances['tooth_' + instance_name]
            instance.ElementSetFromElementLabels(name=fatigue_set_name,
                                                 element_labels=fatigue_set_data)
    odb.close()


if __name__ == '__main__':
    dante_odb_filename = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_1x/dante_results.odb'
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/heat_treatment/mesh_1x/'

    set_file_name  = '../planetary_gear/input_files/gear_models/planet_gear/tooth_root_set_volume_dense_mesh.inc'
    fatigue_set_data = []
    with open(set_file_name) as set_file:
        for line in set_file.readlines():
            fatigue_set_data += line.split()
    print fatigue_set_data

