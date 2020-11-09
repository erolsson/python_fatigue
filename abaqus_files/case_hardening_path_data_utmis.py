import os

import numpy as np

from path_functions import Path
from write_heat_treatment_path_data import write_case_hardening_data_along_path

from visualization import *
from abaqusConstants import INTEGRATION_POINT


if __name__ == '__main__':
    fields = ['SDV_HARDNESS', 'SDV_CARBON', 'S', 'SDV_AUSTENITE', 'SDV_T_MARTENSITE', 'SDV_UBAINITE', 'SDV_LBAINITE']

    path_points_y = np.ones((100, 3))*1e-3
    path_points_z = np.ones((100, 3))*1e-3
    path_points_y[:, 1] = np.linspace(2.5 - 1e-3, 0, 100)
    path_points_z[:, 2] = np.linspace(0, 2. - 1e-3, 100)
    path_points_z[:, 1] = 2.5 - 1e-3
    for path_points, path_name in zip([path_points_y, path_points_z], ['path_y', 'path_z']):
        path = Path(path_name, path_points, np.array([1, 0, 0]))

        for specimen in ['smooth']:
            pickle_directory = os.path.expanduser('~/utmis_specimens/' + specimen + '/heat_treatment_data/')
            if not os.path.isdir(pickle_directory):
                os.makedirs(pickle_directory)
            dante_odb_path = os.path.expanduser('~/utmis_specimens/' + specimen
                                                + '/t=9_min_cooltemp=40C/')
            odb_file_name = dante_odb_path + 'Toolbox_Cooling_utmis_' + specimen + '.odb'
            pickle_name = pickle_directory + 'utmis_' + specimen + '_dante_' + path_name + '.pkl'
            step_name = 'cooling'
            write_case_hardening_data_along_path(odb_file_name, path, pickle_name, step_name=step_name,
                                                 fields=fields, session=session, output_position=INTEGRATION_POINT)
