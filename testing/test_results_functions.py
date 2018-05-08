from math import sqrt

import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import fmin
from scipy.special import erf
from scipy.stats import norm


def calculate_fatigue_limit(test_serie):
    # Likelihood function assuming that the fatigue limit of a specimen is normal distributed
    def likelihood_function(parameters, *data):
        mu, nu = parameters
        results, = data
        
        def pf(val, mean, std):
            return 1./2*(1+erf((val-mean)/std*sqrt(2)))
        l = 0
        for amp in results.keys():
            l -= results[amp]['failures'].shape[0]*np.log(pf(amp, mu, nu))
            l -= results[amp]['survivors'].shape[0]*np.log(1-pf(amp, mu, nu))
        return l
    s0 = 30
    par = fmin(likelihood_function, [s0, 0.1*s0], (test_serie,), disp=False)
    return par[0]


def calculate_basquin_params(test_serie):
    amps = test_serie.keys()
    s = np.array([])
    n = np.array([])
    for amp in amps:
        n = np.hstack((n, test_serie[amp]['failures']))
        s = np.hstack((s, amp*np.ones(test_serie[amp]['failures'].shape[0])))
    par = np.polyfit(np.log(n), np.log(s), 1)
    c = np.exp(par[1])
    b = -par[0]
    return c, b


def fatigue_line(sa, c, b, n_inf=1E8):
    ne = (sa/c)**(1./-b)
    n = np.exp(np.linspace(0., np.log(ne), 1000))
    if b > 0:
        return np.hstack([n, n_inf]), np.hstack([c*n**-b, sa])
    else:
        return np.hstack([n, n_inf]), np.hstack([sa+0*n, sa])


def create_arrow_for_runout(amp, number, axis, ns=2E6, text=True):
    l = 0.05
    v = l*(axis[3] - axis[2])
    h = (l*(np.log(axis[1]) - np.log(axis[0])))
    plt.annotate("", xy=(np.exp(np.log(ns)+h), amp+v), xytext=(ns, amp),
                 arrowprops=dict(arrowstyle='->'))
    if text:
        plt.text(np.exp(np.log(ns)+1.5*h), amp+v,
                 r'\textbf{' + str(number) + '}', va='center', ha='center')


def draw_fatigue_limit_probabilities(se, m, fig, axis):
    plt.figure(fig)
    plt.semilogx([axis[0], axis[1]], [se, se], '--k', lw=2)
    s25 = norm.ppf(0.25, se, m**2)
    s75 = norm.ppf(0.75, se, m**2)
    plt.semilogx([axis[0], axis[1]], [s25, s25], ':k', lw=2)
    plt.semilogx([axis[0], axis[1]], [s75, s75], ':k', lw=2)
    h = axis[3]-axis[2]
    d = 0.05
    plt.text(2*axis[0], s25 - d*h, r'$p_f=25 \%$', va='center', ha='center')
    plt.text(2*axis[0], s75 + d*h, r'$p_f=75 \%$', va='center', ha='center')


def draw_fatigue_life_probabilities(distr, fig, axis):
    plt.figure(fig)
    cycles = np.exp(np.linspace(np.log(axis[0]), np.log(axis[1]), 10000))
    s50 = distr.ppf_s(0.5, cycles)
    plt.semilogx(cycles, s50, '--k', lw=2)
    s25 = distr.ppf_s(0.25, cycles)
    plt.semilogx(cycles, s25, ':k', lw=2)
    s75 = distr.ppf_s(0.75, cycles)
    plt.semilogx(cycles, s75, ':k', lw=2)


def plot_test_results(results, fig, c, axis, labels=('Failure', 'Run-out'), ylab=r'$\tau_a$',
                      plot_fatigue_line=False, title='', leg_pos=1.034, fig_name=None):
    fig = plt.figure(fig)
    amps = results.keys()
    plt.xlim(axis[0], axis[1])
    plt.ylim(axis[2], axis[3])
    plt.xlabel('$N$')
    plt.ylabel(ylab)
    plt.grid(True)
    leg_h = []
    for i, amp in enumerate(amps):
        nf = results[amp]['failures']
        ns = results[amp]['survivors']
        if i == 0:
            l, = plt.semilogx(nf, amp * np.ones(nf.shape), c + 'x', ms=12, mew=2,
                              label=labels[0])
            leg_h.append(l)
            l, = plt.semilogx(ns, amp * np.ones(ns.shape), c + 'o', ms=12, mew=2,
                              label=labels[1])
            leg_h.append(l)
        else:
            plt.semilogx(nf, amp * np.ones(nf.shape), c + 'x', ms=12, mew=2)
            plt.semilogx(ns, amp * np.ones(ns.shape), c + 'o', ms=12, mew=2)

        # Creating arrows for the run-outs
        if ns.shape[0] > 0:
            create_arrow_for_runout(amp, ns.shape[0], axis, text=False)

    se = calculate_fatigue_limit(results)
    c, b = calculate_basquin_params(results)
    print "The fatigue limit is ", se, " MPa and the exponent is ", b
    if plot_fatigue_line:
        cycles, load = fatigue_line(se, c, b)
        plt.semilogx(cycles, load, c + '--', lw=2)
    ax = plt.subplot(111)
    leg = ax.legend(handles=leg_h, title=title,
                    numpoints=1, loc='upper left', bbox_to_anchor=(1, leg_pos))
    plt.gca().add_artist(leg)
    fig.set_size_inches(11, 6, forward=True)
    box = ax.get_position()

    ax.set_position([box.x0, box.y0, 0.6, box.height])
    if fig_name is not None:
        plt.savefig(fig_name)
