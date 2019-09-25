import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

from weakest_link_functions import Simulation
from weakest_link_functions import calc_pf_for_simulation

from multiprocesser.multiprocesser import multi_processer

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


if __name__ == '__main__':
    figures = {'smooth': 0, 'notched': 1}
    colors = {-1.: 'b', 0.: 'r'}

    k = 1.3
    su = 750.
    m = 15

    experiments = [Simulation(specimen='smooth', R=-1., stress=737., failures=1, run_outs=4),
                   Simulation(specimen='smooth', R=-1., stress=774., failures=4, run_outs=2),
                   Simulation(specimen='smooth', R=-1., stress=820., failures=3, run_outs=1),
                   Simulation(specimen='smooth', R=0., stress=425., failures=2, run_outs=3),
                   Simulation(specimen='smooth', R=0., stress=440., failures=4, run_outs=2),
                   Simulation(specimen='notched', R=-1., stress=427., failures=2, run_outs=4),
                   Simulation(specimen='notched', R=-1., stress=450., failures=5, run_outs=3),
                   Simulation(specimen='notched', R=0., stress=225., failures=2, run_outs=3),
                   Simulation(specimen='notched', R=0., stress=240., failures=2, run_outs=4),
                   Simulation(specimen='notched', R=0., stress=255., failures=4, run_outs=0)]

    for experiment in experiments:
        plt.figure(figures[experiment.specimen])
        plt.plot(experiment.stress, float(experiment.failures) / (experiment.failures + experiment.run_outs),
                 colors[experiment.R] + 'x', ms=12, mew=2)

    simulations = {'smooth': {-1.: np.array([720, 740, 760, 780, 800, 820, 840]),
                              0.0: np.array([380, 400, 420, 440, 460, 480, 500])},
                   'notched': {-1.: np.array([380, 400, 420, 440, 460, 480, 500]),
                               0.0: np.array([200, 220, 240, 260, 280, 300, 310])}}

    for specimen, data in simulations.iteritems():
        print specimen
        for R, load_levels in data.iteritems():
            print R
            job_list = []
            for load_level in load_levels:
                sim = Simulation(specimen=specimen, R=R, stress=load_level, failures=0, run_outs=0)
                job_list.append([calc_pf_for_simulation, (sim, (k, su, m)), {}])
            pf = np.array(multi_processer(jobs=job_list, timeout=1000, delay=0., cpus=1))
            print figures[specimen]
            plt.figure(figures[specimen])
            plt.plot(load_levels, pf, colors[int(R)], lw=2)

    for fig in figures.values():
        plt.figure(fig)
        plt.xlabel('Nominal stress [MPa]')
        plt.ylabel('$p_f$')
        plt.ylim(0, 1)

    plt.show()
