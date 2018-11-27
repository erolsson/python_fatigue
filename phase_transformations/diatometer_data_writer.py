import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

from dilatometer_simulations import expansion_austenite
from dilatometer_simulations import expansion_martensite

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def write_dilatometer_file(carbon, cooling_rate, start_temp=400, end_temp=22, file_name=None, figure=None):
    pass


def write_transformation_strain_file():


if __name__ == '__main__':
    print expansion_martensite(700, 0.004) - expansion_austenite(700, 0.004)

