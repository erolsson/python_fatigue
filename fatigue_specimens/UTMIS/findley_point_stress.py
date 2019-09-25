import os
import pickle

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

if __name__ == '__main__':
    sm = np.linspace(-400, 200, 1000)
    fig = 0
    plt.figure(fig)

    s_res_smooth = -302

    plt.plot([s_res_smooth, s_res_smooth+430*1.03], [760*1.03, 430*1.03], '-gx', ms=12)

    s_res_notched = -396

    plt.plot([s_res_notched, s_res_notched+250*1.89], [440*1.89, 250*1.89], '-rx', ms=12)
    fig += 1
    print s_res_smooth, s_res_notched

    k = 1.3
    sF = 580 * (k + np.sqrt(1 + k ** 2)) / 2
    print sF
    sa = 2 * (-k * sF + np.sqrt(sF ** 2 + k ** 2 * sF ** 2 - k * sF * sm))
    plt.plot(sm, sa)

    k = 1.3
    sF = 560 * (k + np.sqrt(1 + k ** 2)) / 2
    print sF
    sa = 2 * (-k * sF + np.sqrt(sF ** 2 + k ** 2 * sF ** 2 - k * sF * sm))
    plt.plot(sm, sa)

    plt.show()
