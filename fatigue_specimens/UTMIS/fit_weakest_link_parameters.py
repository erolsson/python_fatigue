import numpy as np
from scipy.optimize import fmin

from weakest_link_functions import Simulation

from weakest_link_functions import likelihood_function_fit
from weakest_link_functions import residual_fit

if __name__ == '__main__':
    par = np.array([1.4, 1000, 15])

    simulations = [Simulation(specimen='smooth', R=-1., stress=737., failures=1, run_outs=4),
                   Simulation(specimen='smooth', R=-1., stress=774., failures=4, run_outs=2),
                   Simulation(specimen='smooth', R=-1., stress=820., failures=3, run_outs=1),
                   Simulation(specimen='smooth', R=0., stress=425., failures=2, run_outs=3),
                   Simulation(specimen='smooth', R=0., stress=440., failures=4, run_outs=2)]
                   #Simulation(specimen='notched', R=-1., stress=427., failures=2, run_outs=4),
                   #Simulation(specimen='notched', R=-1., stress=450., failures=5, run_outs=3),
                   #Simulation(specimen='notched', R=0., stress=225., failures=2, run_outs=3),
                   #Simulation(specimen='notched', R=0., stress=240., failures=2, run_outs=4),
                   #Simulation(specimen='notched', R=0., stress=255., failures=4, run_outs=0)]

    print fmin(residual_fit, par, (simulations, [1.3, 300, 15], [1.3, 2000, 15]))
