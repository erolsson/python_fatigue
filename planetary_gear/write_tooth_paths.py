from math import pi
import numpy as np

from input_file_reader.input_file_reader import InputFileReader


def compute_tooth_paths(geometry_file):
    reader = InputFileReader()
    reader.read_input_file(geometry_file)

    all_nodes = reader.nodal_data

    z0_nodes = set(reader.set_data['nset']['z0_nodes'])
    exposed_nodes = set(reader.set_data['nset']['exposed_nodes'])

    profile_nodes_idx = np.array(sorted(z0_nodes & exposed_nodes)) - 1

    profile_points = all_nodes[profile_nodes_idx, 1:3]
    profile_points = profile_points[profile_points[:, 1] > 1.2*np.min(profile_points[:, 1])]

    tooth_height = np.max(profile_points[:, 1]) - np.min(profile_points[:, 1])

    idx = np.argsort(np.arctan2(profile_points[:, 0], profile_points[:, 1]))
    profile_points = profile_points[idx]

    root_points = profile_points[profile_points[:, 1] < np.min(profile_points[:, 1]) + 0.5*tooth_height, :]
    diff = np.diff(root_points, axis=0)
    tangent = 180 - np.arctan2(diff[:, 0], diff[:, 1])*180/pi

    idx = np.argmin(np.abs(tangent-30))
    tangent_point = np.mean(root_points[idx-1:idx+1], axis=0)

    x = np.linspace(0, tangent_point[0]-1e-3, 100)
    y = -np.arctan(-30*pi/180)*x
    y += np.arctan(-30*pi/180)*tangent_point[0] + tangent_point[1]

    diff = profile_points[:, 1] - np.min(profile_points[:, 1]) - tooth_height/2
    p1 = profile_points[diff < 0, :][0]
    p2 = profile_points[diff > 0, :][-1]

    k = (p2[1] - p1[1])/(p2[0] - p1[0])
    y = np.min(profile_points[:, 1]) + tooth_height/2
    tangent_point = np.array([p1[0] + (y - p1[1])/k, y])

    x = np.linspace(0, tangent_point[0]-1e-3, 100)
    y = -x/k + tangent_point[0]/k + tangent_point[1]


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import matplotlib.style

    matplotlib.style.use('classic')
    plt.rc('text', usetex=True)
    plt.rc('font', serif='Computer Modern Roman')
    plt.rcParams.update({'font.size': 20})
    plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                      'monospace': ['Computer Modern Typewriter']})

    compute_tooth_paths('input_files/gear_models/utmis_gear/tooth_part_model_file.inp')
