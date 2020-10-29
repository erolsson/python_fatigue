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
    T0 = 700
    for filename in ['3_1K.csv', 'expansion_0_2']:
        experimental_data = np.genfromtxt(os.path.expanduser('~/phase_transformations/data_tehler/'
                                                             + filename), delimiter=',')

        experimental_data = experimental_data[np.argsort(experimental_data[:, 0]), :]
        print(experimental_data)
        temperature = experimental_data[:, 0] - 273.15
        d0 = np.interp(T0, temperature, experimental_data[:, 1])
        e = (experimental_data[:, 1] - d0)/1e4
        plt.plot(temperature, e)
    plt.show()


if __name__ == '__main__':
    main()
