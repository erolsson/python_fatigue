from collections import OrderedDict

import numpy as np
import pickle

import odbAccess
from visualization import *
import xyPlot

from abaqusConstants import *

from path_functions import create_path
from path_functions import get_stress_tensors_from_path






if __name__ == '__main__':
    odb_path = '/scratch/users/erik/Abaqus/Gear/planetaryGear/odb/'

    pickle_handle = open('../planetary_gear/pickles/tooth_paths.pkl', 'rb')
    pickle.load(pickle_handle)
    pickle.load(pickle_handle)  # Direction vector of the flank path
    root_data = pickle.load(pickle_handle)
    normal_root = pickle.load(pickle_handle)   # Direction vector perpendicular the root path
    pickle_handle.close()

    normal_root[0] *= -1

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

        root_path = create_path(path_data, 'longitudinal_path')
        stress_tensors = get_stress_tensors_from_path(root_path)

        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='HV',
                                                                       outputPosition=ELEMENT_NODAL)                                                                       
        xy = xyPlot.XYDataFromPath(name='hardness profile', path=root_path,
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
    #Comment
    # Mechanical loading
    mechanical_stresses = np.zeros((100, 2))
    mechanical_stresses[:, 0] = z
    odb = odbAccess.openOdb(odb_path + 'mechanicalLoadsTooth.odb')
    o7 = session.odbs[session.odbs.keys()[0]]
    session.viewports['Viewport: 1'].setValues(displayedObject=o7)

    step_index = odb.steps.keys().index('maxLoad')
    last_frame = len(odb.steps[odb.steps.keys()[-1]].frames)
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_index, frame=last_frame)

    root_path = create_path(path_data, 'longitudinal_path')
    stress_tensors = get_stress_tensors(root_path)
    mechanical_stresses[:, 1] = np.dot(np.dot(normal_root, stress_tensors), normal_root)

    odb.close()

    mechanical_stress_pickle = open('../planetary_gear/pickles/tooth_root_stresses/mechanical_stresses.pkl', 'w')
    pickle.dump(mechanical_stresses, mechanical_stress_pickle)
    mechanical_stress_pickle.close()

    odb = odbAccess.openOdb(odb_path + 'findleyDataSets20170608.odb')
    o7 = session.odbs[session.odbs.keys()[0]]
    session.viewports['Viewport: 1'].setValues(displayedObject=o7)
    root_path = create_path(path_data, 'longitudinal_path')
    findley_data = OrderedDict()
    for case_idx, case_depth in enumerate([0.5, 0.8, 1.1, 1.4]):
        findley_data[case_depth] = OrderedDict()
        for load_idx, load in enumerate(np.arange(29., 40., 1.)):
            findley_data[case_depth][load] = np.zeros(100)
            step_index = odb.steps.keys().index('Pamp=' + str(load).replace('.', '_') + 'kN_DC=' +
                                                str(case_depth).replace('.', '_'))
            last_frame = len(odb.steps[odb.steps.keys()[-1]].frames)
            session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_index, frame=last_frame)

            session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='SF',
                                                                           outputPosition=ELEMENT_NODAL)
            xy = xyPlot.XYDataFromPath(name='stress profile', path=root_path,
                                       labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                                       includeIntersections=False)
            for pos_idx, (_, val) in enumerate(xy):
                findley_data[case_depth][load][pos_idx] = val
    odb.close()

    findley_pickle = open('../planetary_gear/pickles/tooth_root_stresses/findley_stresses.pkl', 'w')
    pickle.dump(findley_data, findley_pickle)
    findley_pickle.close()
