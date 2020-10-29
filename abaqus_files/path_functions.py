from __future__ import print_function, division
from collections import namedtuple
import numpy as np

from visualization import *
import xyPlot

from abaqusConstants import POINT_LIST, ELEMENT_NODAL, TRUE_DISTANCE, UNDEFORMED, PATH_POINTS, COMPONENT

Path = namedtuple('Path', ['name', 'data', 'normal'])


def create_path(points, path_name, session):
    path_points = []
    for point in points:
        path_points.append((point[0], point[1], point[2]))

    path = session.Path(name=path_name, type=POINT_LIST, expression=path_points)
    return path


def get_stress_tensors_from_path(path, session, output_position=ELEMENT_NODAL):
    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='S',
                                                                   outputPosition=output_position,
                                                                   refinement=[COMPONENT, 'S11'])
    xy = xyPlot.XYDataFromPath(name='Stress profile', path=path,
                               labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                               includeIntersections=False)
    stress_data = np.zeros((max(len(xy), 100), 7))
    print(len(xy))
    comps = ['S11', 'S22', 'S33', 'S12', 'S13', 'S23']
    for i, comp in enumerate(comps):
        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='S',
                                                                       outputPosition=output_position,
                                                                       refinement=[COMPONENT, comp])
        xy = xyPlot.XYDataFromPath(name='Stress profile', path=path,
                                   labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                                   includeIntersections=False)
        print(len(xy))
        for idx, (pos, stress_comp) in enumerate(xy):
            stress_data[idx, 0] = pos
            stress_data[idx, i+1] = stress_comp
    return stress_data


def get_scalar_field_from_path(path, session, variable, output_position=ELEMENT_NODAL):
    data = np.zeros((100, 2))
    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel=variable,
                                                                   outputPosition=output_position)
    xy = xyPlot.XYDataFromPath(name='Stress profile', path=path,
                               labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                               includeIntersections=False)
    for idx, (pos, value) in enumerate(xy):
        data[idx, :] = pos, value
    return data
