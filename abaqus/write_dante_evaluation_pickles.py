from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import os
import pickle


def write_pickle_for_case_depth(odb_file_name, pickle_file_name, fatigue_set_name, fatigue_set_data):
    odb = openOdb(odb_file_name)
    if fatigue_set_name not in odb.rootAssembly.elementSets:
        odb.rootAssembly.instances['tooth_left'].ElementSetFromElementLabels(name=fatigue_set_name,
                                                                             element_labels=fatigue_set_data.tolist())
    odb.close()


if __name__ == '__main__':
    dante_odb_filename = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_1x/dante_results.odb'
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/heat_treatment/mesh_1x/'


