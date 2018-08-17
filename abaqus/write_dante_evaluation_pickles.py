from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import os
import pickle

import numpy as np

from materials.gear_materials import SteelData


def write_pickle_for_case_depth(odb_file_name, pickle_file_name, fatigue_set_name, fatigue_set_data):



if __name__ == '__main__':
    dante_odb_filename = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_1x/dante_results.odb'
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/heat_treatment/mesh_1x/'

    # set_file_name  = '../planetary_gear/input_files/gear_models/planet_gear/mesh_1x/tooth_root_volume_elements.inc'
    fatigue_set_data = []
    with open(set_file_name) as set_file:
        for line in set_file.readlines():
            fatigue_set_data += line.split(',')
    fatigue_set_data = [int(e) for e in fatigue_set_data]

    write_pickle_for_case_depth(dante_odb_filename, '', 'tooth_root_volume_elements', fatigue_set_data)

