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

