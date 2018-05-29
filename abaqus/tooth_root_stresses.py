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


def get_stress_tensors():
    stress_data = np.zeros((100, 3, 3))
    comps = ['S11', 'S22', 'S33', 'S12', 'S13', 'S23']
    for (idx1, idx2), comp in zip([(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)], comps):
        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='S',
                                                                       outputPosition=ELEMENT_NODAL,
                                                                       refinement=[COMPONENT, comp])
        xy = xyPlot.XYDataFromPath(name='Stress profile', path=path,
                                   labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                                   includeIntersections=False)

        for idx, (_, stress_comp) in enumerate(xy):
            stress_data[pos_idx, idx1, idx2] = stress_comp
    stress_data[:, 1, 0] = stress_data[:, 0, 1]
    stress_data[:, 2, 0] = stress_data[:, 0, 2]
    stress_data[:, 2, 1] = stress_data[:, 1, 2]
    return stress_data


if __name__ == '__main__':
    odb_path = '/scratch/users/erik/Abaqus/Gear/planetaryGear/odb/'

    pickle_handle = open('../planetary_gear/pickles/tooth_paths.pkl', 'rb')
    pickle.load(pickle_handle)
    pickle.load(pickle_handle)  # Direction vector of the flank path
    root_data = pickle.load(pickle_handle)
    normal_root = pickle.load(pickle_handle)   # Direction vector perpendicular the root path
    pickle_handle.close()

    # Move the path a small distance in the direction of the root direction
    x0 = root_data[0, 0]
    y0 = root_data[0, 1]

    x0 -= 0.05*np.sqrt(3)/2
    y0 -= 0.05/2

    z = np.linspace(1e-3, 18.95, 100)

    path_data = np.zeros((100, 3))
    path_data[:, 0] = -x0     # Left part of the tooth is tensile loaded at bending
    path_data[:, 1] = y0
    path_data[:, 2] = z

    # Reading residual stresses
    residual_stresses = np.zeros((100, 5))
    hardness = np.zeros((100, 5))
    residual_stresses[:, 0] = z
    hardness[:, 0] = z
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
        stress_tensors = get_stress_tensors()

        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='HV',
                                                                       outputPosition=ELEMENT_NODAL)                                                                       
        xy = xyPlot.XYDataFromPath(name='hardness profile', path=path,
                                   labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                                   includeIntersections=False)

        for pos_idx, val in enumerate(xy):
            hardness[pos_idx, case_idx+1] = val[1]
        odb.close()

        normal_stress = np.dot(np.dot(normal_root, stress_tensors), normal_root)
        residual_stresses[:, case_idx+1] = normal_stress

    # Dump stresses to pickle
    residual_stress_pickle = open('../planetary_gear/pickles/tooth_root_stresses/residual_stresses.pkl', 'w')
    pickle.dump(residual_stresses, residual_stress_pickle)
    residual_stress_pickle.close()

    hardness_pickle = open('../planetary_gear/pickles/tooth_root_stresses/hardness.pkl', 'w')
    pickle.dump(hardness, hardness_pickle)
    hardness_pickle.close()

    # Mechanical loading
    mechanical_stresses = np.zeros((100, 2))
    mechanical_stresses[:, 0] = z
    odb = odbAccess.openOdb('mechanicalLoadsTooth.odb')
    o7 = session.odbs[session.odbs.keys()[0]]
    session.viewports['Viewport: 1'].setValues(displayedObject=o7)

    step_index = odb.steps.keys().index('maxLoad')
    last_frame = len(odb.steps[odb.steps.keys()[-1]].frames)
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_index, frame=last_frame)

    path = create_path(path_data, 'longitudinal_path')
    stress_tensors = get_stress_tensors()
    mechanical_stresses[:, 1] = np.dot(np.dot(normal_root, stress_tensors), normal_root)

    mechanical_stress_pickle = open('../planetary_gear/pickles/tooth_root_stresses/mechanical_stresses.pkl', 'w')
    pickle.dump(mechanical_stresses, mechanical_stress_pickle)
    mechanical_stress_pickle.close()
