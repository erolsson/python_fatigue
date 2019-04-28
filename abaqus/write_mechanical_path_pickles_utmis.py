import os

import numpy as np

from path_functions import Path
from path_functions import create_path
from path_functions import get_stress_tensors_from_path

import odbAccess

if __name__ == '__main__':
    path_points_y = np.ones((100, 3))*1e-3
    path_points_z = np.ones((100, 3))*1e-3
    path_points_y[:, 1] = np.linspace(2. - 1e-3, 0, 100)
    path_points_z[:, 2] = np.linspace(2. - 1e-3, 0, 100)
    for path_points, path_name in zip([path_points_y, path_points_z], ['path_y', 'path_z']):
        path = Path(path_name, path_points, np.array([1, 0, 0]))
        create_path(path.data, path.name, session)
        pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/mechanical_data/'
        if not os.path.isdir(pickle_directory):
            os.makedirs(pickle_directory)
        for specimen in ['smooth', 'notched']:
            mechanical_odb = ('/scratch/users/erik/scania_gear_analysis/abaqus/utmis_specimens/unit_load'
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

            print get_stress_tensors_from_path(path.name, session, output_position=ELEMENT_NODAL)