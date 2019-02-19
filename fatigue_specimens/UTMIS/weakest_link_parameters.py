import numpy as np
import matplotlib as mlt
mlt.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.style

from fit_weakest_link_parameters import calc_pf_for_simulation

from weakest_link_functions import evaluated_findley_parameters
from weakest_link_functions import Simulation

from multiprocesser.multiprocesser import multi_processer

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def residual(parameters, simulation_list):
    pf_sim = np.array([calc_pf_for_simulation(simulation, parameters) for simulation in simulation_list])
    return np.sum((pf_sim - experimental_pf)**2)


def likelihood_function(parameters, simulation_list):
    likelihood = 0
    for simulation in simulation_list:
        tol = 1e-6
        pf = calc_pf_for_simulation(simulation, parameters)
        if pf > 1 - tol:
            pf = 1 - tol
        if pf < tol:
            pf = tol

        likelihood -= np.log(pf)*simulation.failures
        likelihood -= np.log(1 - pf)*simulation.run_outs
    return likelihood


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
    experimental_pf = np.array([float(sim.failures)/(sim.failures + sim.run_outs) for sim in simulations])
    n_su = 20
    n_b = 20

    su = np.linspace(1, 1000, n_su)
    b = np.linspace(5, 25, n_b)

    SU, B = np.meshgrid(su, b)

    for fig, findley_parameter in enumerate(evaluated_findley_parameters):
        print 'Analyzing parameter a800 =', findley_parameter
        plt.figure(fig)
        job_list = []
        for b_val in b:
            for su_val in su:
                job_list.append([likelihood_function, ((findley_parameter, su_val, b_val), simulations), {}])
        r_list = multi_processer(jobs=job_list, timeout=1000, delay=0., cpus=8)
        r = np.array(r_list).reshape((n_b, n_su))

        ind_min = np.unravel_index(np.argmin(r, axis=None), r.shape)

        plt.contourf(SU, B, r)
        plt.text(SU[ind_min], B[ind_min], r'\textbf{x}', horizontalalignment='left')
        plt.text(1.1*su[0], 0.9*b[-1], r'$\sigma_u=' + str(SU[ind_min]) + '$ MPa',
                 horizontalalignment='left')
        plt.text(1.1*su[0], 0.8*b[-1], r'$b=' + str(B[ind_min]) + '$',
                 horizontalalignment='left')
        plt.text(1.1*su[0], 0.7*b[-1], r'$r=' + str(r[ind_min]) + '$',
                 horizontalalignment='left')
        plt.xlabel(r'$\sigma_u$ [MPa]')
        plt.ylabel(r'$b$ [-]')
        plt.colorbar()

        plt.savefig('likelihood_a800=' + str(findley_parameter).replace('.', '_') + '.png')
