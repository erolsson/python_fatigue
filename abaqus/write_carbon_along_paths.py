import numpy as np
import pickle 

import odbAccess
from visualization import *
import xyPlot

from abaqusConstants import *


def create_path(points, name):
    path_points = []
    for point in points:
        path_points.append((point[0], point[1], point[2]))

    path = session.Path(name=name, type=POINT_LIST, expression=path_points)
    return path

odb_path = r'C:/Users/erolsson/Post-doc/carbonDiffusion/'

pickle_handle = open('../planetary_gear/pickles/tooth_paths.pkl', 'rb')
flank_data = pickle.load(pickle_handle)
normal_flank = pickle.load(pickle_handle)  # Direction vector of the flank path
root_data = pickle.load(pickle_handle)
normal_root = pickle.load(pickle_handle)   # Direction vector of the root path
pickle_handle.close()

case_depths = [0.5]
carbon_root = np.zeros((root_data.shape[0], len(case_depths)+1))
carbon_flank = np.zeros((flank_data.shape[0], len(case_depths)+1))

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
    for path_data, name, data_array in zip([flank_data, root_data], ['flank_path', 'root_path'],
                                           [carbon_root, carbon_flank]):
        data_path = create_path(path_data, name)
        xy = xyPlot.XYDataFromPath(name='Carbon profile', path=data_path,
                                   labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                                   includeIntersections=False)

        for i, xy_point in enumerate(xy):
            if cd_idx == 0:
                data_array[i, 0] = xy_point[0]
            data_array[i, cd_idx+1] = xy_point[1]
    print carbon_flank
    print carbon_root
    odb.close()

"""
def writeDataAlongPath(path, n,step, dataToWrite):
    session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=309.913116455078,
                     height=230.809509277344)
    session.viewports['Viewport: 1'].makeCurrent()
    session.viewports['Viewport: 1'].maximize()
    o7 = session.odbs[session.odbs.keys()[0]]
    session.viewports['Viewport: 1'].setValues(displayedObject=o7)
    
    stepI = odb.steps.keys().index(step)  
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=stepI, frame=0)
    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='SDV_CARBON', outputPosition=ELEMENT_NODAL)
    xy = xyPlot.XYDataFromPath(name = 'Carbon profile', path=path, 
                              labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                              includeIntersections=False)
    
    data = np.zeros((len(xy),4))
    if dataToWrite['Carbon']:
        for i,xyp in enumerate(xy):
            data[i,0:2] = xyp[0], xyp[1]

    if dataToWrite['Hardness']:
        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='SDV_HARDNESS', outputPosition=ELEMENT_NODAL)
        xy = xyPlot.XYDataFromPath(name = 'Hardness profile', path=path, 
                              labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                              includeIntersections=False)
        for i,xyp in enumerate(xy):
            data[i,2] = HRC2HV(xyp[1])



    if dataToWrite['ResidualStress']:
        stresses = np.zeros((len(xy),6))
        comps = ['S11','S22','S33','S12','S13','S23']
        for i, comp in enumerate(comps):
            session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='S', outputPosition=ELEMENT_NODAL, 
                                                                           refinement=[COMPONENT, comp])
            xy = xyPlot.XYDataFromPath(name = 'Stress profile', path=path, 
                                       labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                                       includeIntersections=False)
            if len(xy) > data.shape[0]:
                xy = xy[-len(xy):-1]
            for j,xyp in enumerate(xy):
                stresses[j,i] = xyp[1]
        S = np.zeros((3,3))
        for i,s in enumerate(stresses):
            S[0,0], S[1,1], S[2,2] = s[0:3]    
            S[1,0], S[0,1] = s[3],s[3]
            S[2,0], S[0,2] = s[4],s[4]
            S[2,1], S[1,2] = s[5],s[5]
            data[i,3] = np.dot(n, np.dot(S,n))
    return data
     

pickleHandle = open('hardnessPaths.pkl', 'rb')
flank = pickle.load(pickleHandle)
nFlank = pickle.load(pickleHandle)
root = pickle.load(pickleHandle)
nRoot = pickle.load(pickleHandle)
pickleHandle.close()    


pickleHandleFlank = open('flankData.pkl', 'wb')
pickleHandleRoot = open('rootData.pkl', 'wb')

flank_path, rootPath = create_paths(flank, root)
data = writeDataAlongPath(flank_path, nFlank, stepName, dataToWrite)
pickle.dump(data, pickleHandleFlank)
data = writeDataAlongPath(rootPath, nRoot, stepName, dataToWrite)
pickle.dump(data, pickleHandleRoot)
    
pickleHandleFlank.close()
pickleHandleRoot.close()

odb.close()
"""
