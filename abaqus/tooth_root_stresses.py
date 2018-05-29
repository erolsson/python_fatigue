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

    x0 = root_data[0, 0]
    y0 = root_data[0, 1]

    z = np.linspace(0, 18.95, 100)

    path_data = np.zeros(100, 3)
    path_data[:, 0] = x0
    path_data[:, 1] = y0
    path_data[:, 2] = Z

    # Reading residual stresses
    for case_depth, odb in zip([0.5, 0.8, 1.1, 1.4], ['', '', '20170220', '20170220']):
        odb = odbAccess.openOdb(odb_path + 'danteTooth' + odb + '.odb')

        session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=309.913116455078,
                         height=230.809509277344)
        session.viewports['Viewport: 1'].makeCurrent()
        session.viewports['Viewport: 1'].maximize()
        o7 = session.odbs[session.odbs.keys()[0]]
        session.viewports['Viewport: 1'].setValues(displayedObject=o7)

        create_path(path_data, 'longitudinal_path')

        odb.close()
    print root_data
