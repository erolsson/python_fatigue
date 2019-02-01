import os

import numpy as np

from path_functions import Path
from write_heat_treatment_path_data import write_case_hardening_data_along_path

from visualization import *


if __name__ == '__main__':
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/utmis_specimens/'
    odb_file_name = dante_odb_path + 'utmis_smooth.odb'
    path_points = np.ones((100, 3))*1e-3
    path_points[:, 1] = np.linspace(2.5-1e-3, 0, 100)
    path = Path('path', path_points, np.array([1, 0, 0]))
    pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/'
    if not os.path.isdir(pickle_directory):
        os.makedirs(pickle_directory)

    write_case_hardening_data_along_path(odb_file_name, path, pickle_directory + '/utmis_smooth_dante_path.pkl',
                                         session=session)
