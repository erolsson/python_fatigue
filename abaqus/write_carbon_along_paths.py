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

odb_path = r'C:/Users/erolsson/Post-doc/carbonDiffusion/'

pickle_handle = open('../planetary_gear/pickles/tooth_paths.pkl', 'rb')
flank_data = pickle.load(pickle_handle)
normal_flank = pickle.load(pickle_handle)  # Direction vector of the flank path
root_data = pickle.load(pickle_handle)
normal_root = pickle.load(pickle_handle)   # Direction vector of the root path
pickle_handle.close()

case_depths = [0.5]
carbon_root = {}
carbon_flank = {}

for cd_idx, case_depth in enumerate(case_depths):
    odb = odbAccess.openOdb(odb_path + 'tooth_slice_' + str(case_depth).replace('.', '_') + '.odb')
    session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=309.913116455078,
                     height=230.809509277344)
    session.viewports['Viewport: 1'].makeCurrent()
    session.viewports['Viewport: 1'].maximize()
    o7 = session.odbs[session.odbs.keys()[0]]
    session.viewports['Viewport: 1'].setValues(displayedObject=o7)

    step_index = odb.steps.keys().index(odb.steps.keys()[-1])
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_index, frame=0)
    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='CONC',
                                                                   outputPosition=ELEMENT_NODAL)
    for path_data, name, data_dict in zip([flank_data, root_data], ['flank', 'root'],
                                          [carbon_root, carbon_flank]):
        data_path = create_path(path_data, name + '_path')
        xy = xyPlot.XYDataFromPath(name='Carbon profile', path=data_path,
                                   labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                                   includeIntersections=False)
        data_array = np.zeros((len(xy), 2))
        for i, xy_point in enumerate(xy):
            data_array[i, 0] = xy_point[0]
            data_array[i, 1] = xy_point[1]
        data_dict[case_depth] = data_array

        if cd_idx == len(case_depths) - 1:
            pickle_handle = open('../planetary_gear/pickles/carbon_' + name + '_sim.pkl', 'w')
            pickle.dump(data_dict, pickle_handle)
            pickle_handle.close()

    odb.close()
