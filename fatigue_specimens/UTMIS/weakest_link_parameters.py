import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style

from fit_weakest_link_parameters import Simulation
from fit_weakest_link_parameters import calc_pf_for_simulation

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

simulations = [Simulation(specimen='smooth', R=-1., stress=760.),
               Simulation(specimen='smooth', R=0., stress=424.),
               Simulation(specimen='notched', R=-1., stress=439.),
               Simulation(specimen='notched', R=0., stress=237.)]

su = np.linspace(800, 1500, 1000)
parameters = (1.1, su, 22)

pf = calc_pf_for_simulation(simulations[0], parameters)