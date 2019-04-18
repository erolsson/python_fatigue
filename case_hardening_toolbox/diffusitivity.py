import numpy as np

from materials.gear_materials import SS2506


def lee_chester_tyne(temp, carbon, material):
    carbon = 100*carbon
    mn = material.composition.get('Mn', 0)
    cr = material.composition.get('Cr', 0)
    si = material.composition.get('Si', 0)
    ni = material.composition.get('Ni', 0)
    mo = material.composition.get('Mo', 0)
    al = material.composition.get('Al', 0)

    D0 = 0.146-0.036*carbon*(1-1.075*cr)+mn*-0.0315+si*0.0509+ni*-0.0085+mo*0.3031+al*-0.0520
    E0 = 144.3-15.0*carbon+0.37*carbon**2+mn*-4.3663+si*4.0507+ni*-1.2407+mo*12.1266+al*-6.7886+cr*7.7260
    return D0*np.exp(-E0/8.314E-3/(temp+273))*100


def write_diffusion_file(filename, material):
    file_lines = []
    carbon = np.arange(0.002, 0.012, 0.0005)
    temperature = np.arange(750, 1150, 10)

    for temp in temperature:
        for carb in carbon:
            file_lines.append('\t' + str(lee_chester_tyne(temp, carb, material)) + ', ' + str(carb) + ', ' + str(temp))

    with open(filename, 'w') as diffusion_file:
        for line in file_lines:
            diffusion_file.write(line + '\n')
        diffusion_file.write('**EOF')


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import matplotlib.style

    matplotlib.style.use('classic')
    plt.rc('text', usetex=True)
    plt.rc('font', serif='Computer Modern Roman')
    plt.rcParams.update({'font.size': 20})
    plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}", r"\usepackage{gensymb}"]
    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                      'monospace': ['Computer Modern Typewriter']})

    carbon_levels = np.array([0.2, 0.4, 0.6, 0.8, 1.0, 1.2])/100
    temperature = np.linspace(800, 1000, 1000)
    for carbon_level in carbon_levels:
        plt.plot(temperature, lee_chester_tyne(temperature, carbon_level, SS2506), lw=2,
                 label=str(carbon_level*100) + r' wt\% C')

    plt.xlabel(r'Temperature [ $\degree$C]')
    plt.ylabel(r'Diffusivity [$\mathrm{mm}^2$/s]')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('diffusivity_2506.png')
    plt.show()
