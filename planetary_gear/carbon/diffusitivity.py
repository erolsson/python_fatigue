import numpy as np


def LeeChesterTyne(temp, carbon):
    C = 100*carbon
    D0 = 0.146-0.036*C*(1-1.075*0.6)+0.97*-0.0315+0.2*0.0509+0.36*-0.0085+0.7*0.3031+0.27*-0.0520
    E0 = 144.3-15.0*C+0.37*C**2+0.97*-4.3663+0.2*4.0507+0.36*-1.2407+0.7*12.1266+0.27*6.7886+0.6*7.7260
    return D0*np.exp(-E0/8.314E-3/(temp+273))*100


def write_diffusion_file(filename):
    file_lines = ['*Diffusivity']
    carbon = np.arange(0.002, 0.012, 0.0005)
    temperature = np.arange(750, 1150, 10)
    for temp in temperature:
        for carb in carbon:
            file_lines.append('\t' + str(LeeChesterTyne(temp, carb)) + ', ' + str(carb) + ', ' + str(temp))

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
    plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                      'monospace': ['Computer Modern Typewriter']})

    diffusion = []

    for i, data_file in enumerate(['M4_old', 'scaled_085']):
        data = np.genfromtxt('diffusitivity/' + data_file + '.txt', delimiter=',')
        diffusion.append(data[:, 0])
        carbon_levels = np.unique(data[:, 1])
        print carbon_levels
        for carbon_level in carbon_levels:
            plt.figure(i)
            sub_data = data[data[:, 1] == carbon_level]
            D = sub_data[:, 0]
            T = sub_data[:, 2]
            plt.plot(sub_data[:, 2], sub_data[:, 0])

            if i == 1:
                plt.plot(T, LeeChesterTyne(T, carbon_level), '--')

    # writing the file with diffusion data


    plt.show()
