import os
import pickle
import sys

import numpy as np

if __name__ == '__main__':
    package_directory = os.path.expanduser('~/python_fatigue/')
    sys.path.append(package_directory)
    print sys.path

    from abaqus_files.path_functions import Path
    from abaqus_files.path_functions import create_path
    from abaqus_files.path_functions import get_stress_tensors_from_path

    import odbAccess
    from abaqusConstants import INTEGRATION_POINT

    path_points_y = np.ones((100, 3))*1e-3
    path_points_z1 = np.ones((100, 3))*1e-3
    path_points_y[:, 1] = np.linspace(2.5 - 1e-3, -2.5 + 1e-3, 100)
    path_points_z1[:, 2] = np.linspace(0, 2. - 1e-3, 100)
    path_points_z1[:, 1] = 2.5 - 1e-3

    path_points_z2 = np.copy(path_points_z1)
    path_points_z2[:, 1] *= -1

    specimen_loads = {'smooth': {-1.: [737.], 0.: [425., 440.]},
                      'notched': {-1.: [427., 450.], 0.: [225., 240., 255.]}}
    simulations = []

    for specimen, data in specimen_loads.iteritems():
        if __name__ == '__main__':
            for R, stress_levels in data.iteritems():
                simulations += [(specimen, R, s) for s in stress_levels]
    number_of_steps = 2

    for path_points, path_name, axis in zip([path_points_y, path_points_z1, path_points_z2],
                                            ['path_y', 'path_z1', 'path_z2'], [1, 2, 2]):
        path = Path(path_name, path_points, np.array([1, 0, 0]))
        abq_path = create_path(path.data, path.name, session)
        pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/mechanical_data/'
        if not os.path.isdir(pickle_directory):
            os.makedirs(pickle_directory)
        for specimen, R, stress_level in simulations:
            simulation_name = '/utmis_' + specimen + '_' + str(stress_level).replace('.', '_') + '_R=' + str(int(R))
            mechanical_odb = '/scratch/users/erik/scania_gear_analysis/abaqus/utmis_specimens/utmis_' + specimen \
                             + simulation_name + '.odb'
            print "working with", simulation_name
            odb = odbAccess.openOdb(mechanical_odb)
            session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=309.913116455078,
                             height=230.809509277344)
            session.viewports['Viewport: 1'].makeCurrent()
            session.viewports['Viewport: 1'].maximize()
            o7 = session.odbs[session.odbs.keys()[0]]
            session.viewports['Viewport: 1'].setValues(displayedObject=o7)

            stress_data = {}
            for load_level in ['min_load', 'max_load']:
                step_name = 'step_' + str(number_of_steps) + '_' + load_level

                step_index = odb.steps.keys().index(step_name)
                frame_number = len(odb.steps[step_name].frames)
                session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_index, frame=frame_number)

                stress = get_stress_tensors_from_path(abq_path, session, output_position=INTEGRATION_POINT)
                data = np.zeros((100, 2))
                if axis == 1:
                    data[:, 0] = np.flipud(path_points[:, axis])
                else:
                    data[:, 0] = path_points[:, axis]
                data[:, 1] = stress[0:100, 0, 0]
                stress_data[load_level] = data
            with open(pickle_directory + simulation_name + '_' + path_name + '.pkl', 'w') as pickle_file:
                pickle.dump(stress_data, pickle_file)
            odb.close()
