from collections import namedtuple
import numpy as np

Models = namedtuple('Model', ['fatigue_limit', 'fatigue_life', 'haiback'])
_k = 200


def _weibull_fatigue_limit(stress, steel_properties, material):
    stress[stress < 0] = 0.
    return (stress/material.weibull_sw(steel_properties))**material.weibull_m(steel_properties)


def _weibull_life_limit(stress, cycles, steel_properties, material):
    stress[stress < 0] = 0.
    if np.log(cycles) > material.ne:
        return _weibull_fatigue_limit(stress, steel_properties, material)
    # m = (material.ne - material.ns)/(np.log(cycles)-material.ns)*material.weibull_m(steel_properties)
    m = material.weibull_m(steel_properties)*(cycles/np.exp(material.ne))**(-1/material.b)
    return ((stress/material.weibull_sw(steel_properties))*(cycles/np.exp(material.ne))**(1./material.b))**m


def _weibull_life_haiback(stress, cycles, steel_properties, material):
    stress[stress < 0] = 0.
    if np.log(cycles) > material.ne:
        ne = np.log(2E6)
        sw = material.weibull_sw(steel_properties)
        k = _k
        m = material.weibull_m(steel_properties)*(cycles/np.exp(ne))**(-1./_k)

    else:
        k = material.b
        ne = material.ne
        sw = material.weibull_sw(steel_properties)*(1E5/2E6)**(1/_k)
        m = material.weibull_m(steel_properties) * (cycles / np.exp(ne))**(-1. / k)*(1E5/2E6)**(-1./_k)
    return ((stress/sw)*(cycles/np.exp(ne))**(1./k))**m


weibull = Models(fatigue_limit=_weibull_fatigue_limit,
                 fatigue_life=_weibull_life_limit,
                 haiback=_weibull_life_haiback)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    N = np.exp(np.linspace(np.log(0.1), np.log(1e7), 1000))

    mA = 20*(np.log(1e5) - np.log(0.1))/(np.log(N) - np.log(0.1))
    plt.semilogx(N, mA)

    mB = 20*(N/2e6)**(-1./_k)

    plt.semilogx(N, mB)

    mC = mB
    mC[N <= 1e5] = 20*(1e5/2e6)**(-1./_k)*(N[N <= 1e5]/1e5)**(-0.2)
    plt.semilogx(N, mC)
    plt.show()
