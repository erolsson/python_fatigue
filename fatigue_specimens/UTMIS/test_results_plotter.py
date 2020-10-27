import numpy as np

from scipy.optimize import fmin
from scipy.stats import norm

import matplotlib.pyplot as plt
import matplotlib.style

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def fatigue_limit_pf(su, std_dev, load):
    return norm.cdf(load, loc=su, scale=std_dev)


def likelihood(par, data):
    L = 0
    for data_point in data:
        pf = fatigue_limit_pf(par[0], par[1], data_point[0])
        if data_point[1] >= 2e6:
            L += np.log(1 - pf)
        else:
            L += np.log(pf)
    return -L


def main():
    fig = 0
    fatigue_limits = {b'Smooth': {-1.: 760., 0.: 424.}, b'Notched': {-1.: 439, 0.: 237}}

    test_data = np.genfromtxt('test_results_utmis.csv', delimiter=',', usecols=(0, 1, 2))
    specimen_types = np.genfromtxt('test_results_utmis.csv', delimiter=',', usecols=(3,), dtype='S')
    for specimen_type, color in zip([b'Smooth', b'Notched'], ['r', 'b']):
        test_data_type = test_data[specimen_types == specimen_type, :]
        for ratio, symbol in zip([0., -1.], ['x', 'x']):
            plt.figure(fig)
            test_data_set = test_data_type[test_data_type[:, 2] == ratio]
            run_outs = test_data_set[test_data_set[:, 1] >= 2e6]
            failures = test_data_set[test_data_set[:, 1] < 2e6]
            su, std_dev = fmin(likelihood, (1000, 100),
                               args=(test_data_set,),  maxfun=1e6, maxiter=1e6)
            print(su, std_dev)
            plt.semilogx(run_outs[:, 1], run_outs[:, 0],
                         color + 'o', ms=12, mew=2, mfc='w', mec=color)
            plt.semilogx(failures[:, 1], failures[:, 0],
                         color + symbol, ms=12, mew=2, mfc='w', mec=color)
            fig += 1
            plt.semilogx([1e4, 1e7], [su, su], 'k', lw=3)
    plt.show()


if __name__ == '__main__':
    main()
