import os
import pickle

import numpy as np

from path_functions import Path
from path_functions import create_path
from path_functions import get_stress_tensors_from_path

import odbAccess
from abaqusConstants import INTEGRATION_POINT

if __name__ == '__main__':
    path_points_y = np.ones((100, 3))*1e-3
    path_points_z = np.ones((100, 3))*1e-3
    path_points_y[:, 1] = np.linspace(2.5 - 1e-3, 0, 100)
    path_points_z[:, 2] = np.linspace(0, 2. - 1e-3, 100)
    path_points_z[:, 1] = 2.5 - 1e-3
    for path_points, path_name, axis in zip([path_points_y, path_points_z], ['path_y', 'path_z'], [1, 2]):
        path = Path(path_name, path_points, np.array([1, 0, 0]))
        abq_path = create_path(path.data, path.name, session)
        pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/mechanical_data/'
        if not os.path.isdir(pickle_directory):
            os.makedirs(pickle_directory)
        for specimen in ['smooth', 'notched']:
            mechanical_odb = ('/scratch/users/erik/scania_gear_analysis/abaqus/utmis_specimens/unit_load_'
                              + specimen + '.odb')
            odb = odbAccess.openOdb(mechanical_odb)

            session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=309.913116455078,
                             height=230.809509277344)
            session.viewports['Viewport: 1'].makeCurrent()
            session.viewports['Viewport: 1'].maximize()
            o7 = session.odbs[session.odbs.keys()[0]]
            session.viewports['Viewport: 1'].setValues(displayedObject=o7)

            step_name = odb.steps.keys()[-1]

            step_index = odb.steps.keys().index(step_name)
            frame_number = len(odb.steps[step_name].frames)
            session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_index, frame=frame_number)

            stress = get_stress_tensors_from_path(abq_path, session, output_position=INTEGRATION_POINT)
            data = np.zeros((100, 2))
            data[:, 0] = np.flipud(path_points[:, axis])
            data[:, 1] = stress[0:100, 0, 0]
            with open(pickle_directory + 'unit_load_' + specimen + '_' + path_name + '.pkl', 'w') as pickle_file:
                pickle.dump(data, pickle_file)
