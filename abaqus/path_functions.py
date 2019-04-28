from collections import namedtuple
import numpy as np

from visualization import *
import xyPlot

from abaqusConstants import *

Path = namedtuple('Path', ['name', 'data', 'normal'])


def create_path(points, path_name, session):
    path_points = []
    for point in points:
        path_points.append((point[0], point[1], point[2]))

    path = session.Path(name=path_name, type=POINT_LIST, expression=path_points)
    return path


def get_stress_tensors_from_path(path, session, output_position=ELEMENT_NODAL):

    xy = xyPlot.XYDataFromPath(name='Stress profile', path=path,
                               labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                               includeIntersections=False)
    stress_data = np.zeros((len(xy), 3, 3))
    comps = ['S11', 'S22', 'S33', 'S12', 'S13', 'S23']
    for (idx1, idx2), comp in zip([(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)], comps):
        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='S',
                                                                       outputPosition=output_position,
                                                                       refinement=[COMPONENT, comp])
        xy = xyPlot.XYDataFromPath(name='Stress profile', path=path,
                                   labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                                   includeIntersections=False)

        for idx, (_, stress_comp) in enumerate(xy):
            stress_data[idx, idx1, idx2] = stress_comp
    stress_data[:, 1, 0] = stress_data[:, 0, 1]
    stress_data[:, 2, 0] = stress_data[:, 0, 2]
    stress_data[:, 2, 1] = stress_data[:, 1, 2]
    return stress_data


def get_scalar_field_from_path(path, session, variable, output_position=ELEMENT_NODAL):
    data = np.zeros(100)
    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel=variable,
                                                                   outputPosition=output_position)
    xy = xyPlot.XYDataFromPath(name='Stress profile', path=path,
                               labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                               includeIntersections=False)
    for idx, (_, value) in enumerate(xy):
        data[idx] = value
    return data
