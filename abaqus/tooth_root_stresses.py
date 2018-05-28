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

pickle_handle = open('../planetary_gear/pickles/tooth_paths.pkl', 'rb')
pickle.load(pickle_handle)
pickle.load(pickle_handle)  # Direction vector of the flank path
root_data = pickle.load(pickle_handle)
normal_root = pickle.load(pickle_handle)   # Direction vector of the root path
pickle_handle.close()

print root_data
