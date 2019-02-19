import numpy as np
import matplotlib as mlt
mlt.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.style

from weakest_link_functions import evaluated_findley_parameters
from weakest_link_functions import Simulation

if __name__ == '__main__':
    simulations = [Simulation(specimen='smooth', R=-1., stress=737., failures=1, run_outs=4),
                   Simulation(specimen='smooth', R=-1., stress=774., failures=4, run_outs=2),
                   Simulation(specimen='smooth', R=-1., stress=820., failures=3, run_outs=1),
                   Simulation(specimen='smooth', R=0., stress=425., failures=2, run_outs=3),
                   Simulation(specimen='smooth', R=0., stress=440., failures=4, run_outs=2),
                   Simulation(specimen='notched', R=-1., stress=427., failures=2, run_outs=4),
                   Simulation(specimen='notched', R=-1., stress=450., failures=5, run_outs=3),
                   Simulation(specimen='notched', R=0., stress=225., failures=2, run_outs=3),
                   Simulation(specimen='notched', R=0., stress=240., failures=2, run_outs=4),
                   Simulation(specimen='notched', R=0., stress=255., failures=4, run_outs=0)]

    for simulation