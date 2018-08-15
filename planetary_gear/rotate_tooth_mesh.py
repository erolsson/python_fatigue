from math import pi
import numpy as np

from input_file_reader.input_file_functions import read_nodes_and_elements
from write_input_for_dante import write_geom_include_file

center_node = 13033

nodes, elements = read_nodes_and_elements('input_files/gear_models/planet_gear/dense_mesh_x3_planet.inc')

point = nodes[nodes[:, 0] == center_node, 1:3][0]

q = -np.arctan(point[0]/point[1]) + pi
rot = np.array([[np.cos(q), -np.sin(q), 0],
                [np.sin(q), np.cos(q), 0],
                [0, 0, 1]])

for n in nodes:
    n[1:] = np.dot(n[1:], rot)

nodes[np.abs(nodes[:, 1]) < 1e-9, 1] = 0.
print nodes[:, 1]
write_geom_include_file(nodes, elements, 'input_files/gear_models/planet_gear/dense_mesh_x3_planet.inc')
