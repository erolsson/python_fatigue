import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

from materials.gear_materials import SS2506
from materials.gear_materials import SteelData

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


if __name__ == '__main__':
    hardness = 800.
    steel_data = SteelData(HV=hardness)
    k = SS2506.findley_k(steel_data)
    sf = SS2506.weibull_sw(steel_data)

    sm_max = sf/k
    sm = np.linspace(-1000, sm_max, 1000)

    sa = -2*k*sf + 2*np.sqrt(sf*(sf+k**2*sf - k*sm))

    su = -2*k*sf + 2*np.sqrt(sf*(sf+k**2*sf))

    sw = 1.98*hardness - 0.0011*hardness**2/(1+20.7/hardness)
    mm = hardness/1000
    print mm
    plt.plot(sm, sw - mm*sm, 'r', lw=3)
    plt.plot(sm, su - mm*sm, '--r', lw=3)

    plt.plot(sm, sa, lw=3)
    plt.xlabel('$\sigma_{m}$ [MPa]')
    plt.ylabel('$\sigma_{a}$ [MPa]')
    plt.ylim(0, 2500)
    plt.show()
