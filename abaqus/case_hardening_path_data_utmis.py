import os

import numpy as np

from path_functions import Path
from write_heat_treatment_path_data import write_case_hardening_data_along_path

from visualization import *
from abaqusConstants import INTEGRATION_POINT


if __name__ == '__main__':
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/utmis_specimens_U925062/'

    path_points_y = np.ones((100, 3))*1e-3
    path_points_z = np.ones((100, 3))*1e-3
    path_points_y[:, 1] = np.linspace(2. - 1e-3, 0, 100)
    path_points_z[:, 2] = np.linspace(2. - 1e-3, 0, 100)
    for path_points, path_name in zip([path_points_y, path_points_z], ['path_y', 'path_z']):
        path = Path(path_name, path_points, np.array([1, 0, 0]))
        pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/'
        if not os.path.isdir(pickle_directory):
            os.makedirs(pickle_directory)
        for specimen in ['smooth', 'notched']:
            dante_odb_path += 'utmis_' + specimen + '_tempering_2h_200_cooldown_80C/'
            dante_odb_path += 'utmis_' + specimen + '_75min930C11wtC5min840C08wtC30min840C08wtC/'
            odb_file_name = dante_odb_path + 'Toolbox_Mechanical_utmis_' + specimen + '.odb'
            pickle_name = pickle_directory + 'utmis_' + specimen + 'dante_' + path_name + '.pkl'
            step_name = 'Tempering'
            write_case_hardening_data_along_path(odb_file_name, path, pickle_name, step_name=step_name,
                                                 session=session, output_position=INTEGRATION_POINT)
