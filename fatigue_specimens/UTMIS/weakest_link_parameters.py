import numpy as np
import matplotlib as mlt
mlt.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.style

from fit_weakest_link_parameters import Simulation
from fit_weakest_link_parameters import calc_pf_for_simulation

from weakest_link_functions import evaluated_findley_parameters

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


if __name__ == '__main__':
    simulations = [Simulation(specimen='smooth', R=-1., stress=737., pf_exp=0.25),
                   Simulation(specimen='smooth', R=-1., stress=774., pf_exp=0.67),
                   Simulation(specimen='smooth', R=-1., stress=820., pf_exp=0.75),
                   Simulation(specimen='smooth', R=0., stress=425., pf_exp=0.50),
                   Simulation(specimen='smooth', R=0., stress=440., pf_exp=0.67),
                   Simulation(specimen='notched', R=-1., stress=427., pf_exp=0.33),
                   Simulation(specimen='notched', R=-1., stress=450., pf_exp=0.50),
                   Simulation(specimen='notched', R=0., stress=225., pf_exp=0.40),
                   Simulation(specimen='notched', R=0., stress=240., pf_exp=0.20),
                   Simulation(specimen='notched', R=0., stress=255., pf_exp=0.90)]
    experimental_pf = np.array([sim.pf_exp for sim in simulations])
    n_su = 20
    n_b = 20

    su = np.linspace(500, 1500, n_su)
    b = np.linspace(10, 50, n_b)
    su_norm = (su - su[0])/(su[-1] - su[0])
    b_norm = (b - b[0]) / (b[-1] - b[0])

    SU, B = np.meshgrid(su, b)

    for fig, findley_parameter in enumerate(evaluated_findley_parameters):
        plt.figure(fig)
        job_list = []
        for b_val in b_norm:
            for su_val in su_norm:
                job_list.append([residual, ((findley_parameter, su_val, b_val), simulations), {}])
        r_list = multi_processer(jobs=job_list, timeout=1000, delay=0., cpus=8)
        r = np.array(r_list).reshape((n_b, n_su))

        ind_min = np.unravel_index(np.argmin(r, axis=None), r.shape)

        plt.contourf(SU, B, r)
        plt.text(SU[ind_min], B[ind_min], r'\textbf{x}  $r=' + str(r[ind_min]) + '$', horizontalalignment='left')
        plt.text(1.1*su[0], 0.9*b[-1], r'$\sigma_u=' + str(SU[ind_min]) + '$ MPa',
                 horizontalalignment='left')
        plt.text(1.1*su[0], 0.8*b[-1], r'$b=' + str(B[ind_min]) + '$',
                 horizontalalignment='left')
        plt.xlabel(r'$\sigma_u$ [MPa]')
        plt.ylabel(r'$b$ [-]')
        plt.colorbar()

        plt.savefig('residual_a800=' + str(findley_parameter).replace('.', '_') + '.png')
