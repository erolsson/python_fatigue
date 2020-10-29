from __future__ import division, print_function
import os

import numpy as np

import matplotlib
import matplotlib.pyplot as plt

from materials.gear_materials import SS2506


matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}", r"\usepackage{gensymb}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def main():
    temperature = np.linspace(20, 920, 100)
    experimental_data = np.genfromtxt(os.path.expanduser('~/phase_transformations/data_tehler/bainite_transformation/'
                                                         'bainite_deformation_02.csv'), delimiter=',')
    plt.plot(experimental_data[:, 0] - 273.15, experimental_data[:, 1]/1e4)
    plt.plot(temperature, SS2506.transformation_strain.Ferrite(temperature, carbon=0.2))
    ferrite = 0.21
    bainite = 1 - ferrite
    e_bf = (ferrite*SS2506.transformation_strain.Ferrite(temperature, 0.002)
            + bainite*SS2506.transformation_strain.Bainite(temperature, 0.002))
    e_af = (ferrite*SS2506.transformation_strain.Ferrite(temperature, 0.002)
            + (1-ferrite)*SS2506.transformation_strain.Austenite(temperature, 0.002))
    plt.plot(temperature, e_af)
    plt.plot(temperature, SS2506.transformation_strain.Austenite(temperature, 0.002))

    experimental_data = np.genfromtxt(os.path.expanduser('~/phase_transformations/data_tehler/expansion_0_2'),
                                      delimiter=',')
    plt.plot(experimental_data[:, 0] - 273.15, experimental_data[:, 1]/1e4)

    plt.show()


if __name__ == '__main__':
    main()
