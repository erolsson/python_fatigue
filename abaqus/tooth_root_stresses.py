import numpy as np
import pickle

import odbAccess
from visualization import *
import xyPlot

from abaqusConstants import *


def create_path(points, path_name):
    path_points = []
    for point in points:
        path_points.append((point[0], point[1], point[2]))

    path = session.Path(name=path_name, type=POINT_LIST, expression=path_points)
    return path

if __name__ == '__main__':
    odb_path = '/scratch/users/erik/Abaqus/Gear/planetaryGear/odb/'

    pickle_handle = open('../planetary_gear/pickles/tooth_paths.pkl', 'rb')
    pickle.load(pickle_handle)
    pickle.load(pickle_handle)  # Direction vector of the flank path
    root_data = pickle.load(pickle_handle)
    normal_root = pickle.load(pickle_handle)   # Direction vector of the root path
    pickle_handle.close()

    # Move the path a small distance in the direction of the root direction
    x0 = root_data[0, 0]
    y0 = root_data[0, 1]

    x0 -= 0.01*normal_root[0]
    y0 -= 0.01*normal_root[1]

    z = np.linspace(0, 18.95, 100)

    path_data = np.zeros((100, 3))
    path_data[:, 0] = x0
    path_data[:, 1] = y0
    path_data[:, 2] = z

    # Reading residual stresses
    for case_idx, (case_depth, odb) in enumerate(zip([0.5, 0.8, 1.1, 1.4], ['', '', '20170220', '20170220'])):
        odb = odbAccess.openOdb(odb_path + 'danteTooth' + odb + '.odb')

        session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=309.913116455078,
                         height=230.809509277344)
        session.viewports['Viewport: 1'].makeCurrent()
        session.viewports['Viewport: 1'].maximize()
        o7 = session.odbs[session.odbs.keys()[0]]
        session.viewports['Viewport: 1'].setValues(displayedObject=o7)

        step_index = odb.steps.keys().index('danteResults_DC' + str(case_depth).replace('.', '_'))
        last_frame = len(odb.steps[odb.steps.keys()[-1]].frames)
        session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_index, frame=last_frame)

        path = create_path(path_data, 'longitudinal_path')

        stress_data = np.zeros((100, 3, 3))
        comps = ['S11', 'S22', 'S33', 'S12', 'S13', 'S23']
        for i, comp in enumerate(comps):
            session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='S',
                                                                           outputPosition=ELEMENT_NODAL,
                                                                           refinement=[COMPONENT, comp])
            xy = xyPlot.XYDataFromPath(name='Stress profile', path=path,
                                       labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                                       includeIntersections=False)

            print len(xy)
        odb.close()

