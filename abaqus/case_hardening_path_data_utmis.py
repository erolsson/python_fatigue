import os

import numpy as np

from path_functions import Path
from write_heat_treatment_path_data import write_case_hardening_data_along_path

from visualization import *


if __name__ == '__main__':
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/utmis_specimens/'

    path_points = np.ones((100, 3))*1e-3
    path_points[:, 1] = np.linspace(2.5-1e-3, 0, 100)
    path = Path('path', path_points, np.array([1, 0, 0]))
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/'
    if not os.path.isdir(pickle_directory):
        os.makedirs(pickle_directory)
    for specimen in ['smooth', 'notched']:
        odb_file_name = dante_odb_path + 'utmis_' + specimen + '.odb'
        for carb in [0.75, 0.8]:
            for temp in [180, 200]:
                pickle_name = 'utmis_' + specimen + 'dante_path_tempering_2h_' + str(temp) + '_' + \
                              str(carb).replace('.', '_') + 'C' + '.pkl'
                step_name = 'dante_results_tempering_2h_' + str(temp) + '_' + str(carb).replace('.', '_') + 'C'
                write_case_hardening_data_along_path(odb_file_name, path, pickle_name, step_name=step_name,
                                                     session=session)
