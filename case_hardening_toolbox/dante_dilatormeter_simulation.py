import os
import pickle

from subprocess import Popen

import numpy as np


class DilatometerSimulation:
    def __init__(self, carbon, material, directory=os.getcwd(), name=None, start_temperature=930, end_temperature=20,
                 cooling_rate=50., heating_rate=20., holding_time=600.):
        self.carbon = float(carbon)
        self.material = material
        self.directory = os.path.expanduser(directory)

        if name is None:
            self.name = 'carbon_' + str(carbon).replace('.', '_')
        else:
            self.name = name
        self.start_temperature = float(start_temperature)
        self.cooling_rate = float(cooling_rate)
        self.end_temperature = float(end_temperature)
        self.quench_time = float(self.start_temperature - self.end_temperature)/self.cooling_rate
        self.heating_time = float(self.start_temperature - 20)/heating_rate
        self.holding_time = float(holding_time)

        self.run_file_name = 'run_dilatometer.sh'
        self.dante_file = '/scratch/users/erik/Dante/Abaqus_Link/DANTE_Library/dante3_7f_pr1/abq2018_linux/' \
                          'dante3_7f_pr1-std.o'

        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

    def _write_thermal_file(self):
        file_lines = ['**',
                      '**',
                      '** Autogenerated input file created by Case Hardening Simulation Toolbox, version 0.8.1',
                      '** Written by Niklas Melin and Erik Olsson',
                      '**',
                      '*Heading',
                      '\t Case Hardening Simulation Toolbox - Thermal - Niklas Melin 2012',
                      '*Preprint, echo=NO, model=NO, history=NO, contact=NO',
                      '**',
                      '** ----------------------------------------------------------------',
                      '** Load required include files',
                      '**',
                      '**   Create Geometry',
                      '*Node, nset=all_nodes',
                      '\t1, \t 0., 0., 0.',
                      '\t2, \t 1., 0., 0.',
                      '\t3, \t 1., 1., 0.',
                      '\t4, \t 0., 1., 0.',
                      '\t5, \t 0., 0., 1.',
                      '\t6, \t 1., 0., 1.',
                      '\t7, \t 1., 1., 1.',
                      '\t8, \t 0., 1., 1.',
                      '*Element, type=DC3D8, elset=all_elements',
                      '\t1, 1, 2, 3, 4, 5, 6, 7, 8',
                      '**',
                      '** ----------------------------------------------------------------',
                      '**',
                      '**   Define material properties',
                      '**',
                      '*Solid Section, elset=All_Elements, material=' + self.material,
                      '\t1.0',
                      '*Hourglass Stiffness',
                      '\t225.0, 0.0, 0.0',
                      '**',
                      '** DEFINE MATERIAL PROPERTIES',
                      '**',
                      '*Material, name=' + self.material,
                      '\t*Density',
                      '\t\t7.83e-06,',
                      '\t*Depvar',
                      '\t\t100,',
                      '\t\t1,  CARBON,       VOLUME FRACTION of CARBON',
                      '\t\t2,  HARDNESS,     Hardness in Rockwell C',
                      '\t\t21, AUSTENITE,    VOLUME FRACTION of AUSTENITE',
                      '\t\t34, FERRITE,      VOLUME FRACTION of FERRITE',
                      '\t\t47, PEARLITE,     VOLUME FRACTION of PEARLITE',
                      '\t\t60, UBAINITE,     VOLUME FRACTION of UPPER BAINITE',
                      '\t\t73, LBAINITE,     VOLUME FRACTION of LOWER BAINITE',
                      '\t\t86, Q_MARTENSITE, VOLUME FRACTION of QUENCHED MARTENSITE',
                      '\t\t99, T_MARTENSITE, VOLUME FRACTION of TEMPERED MARTENSITE',
                      '\t*User Material, constants=8, type=THERMAL',
                      '\t\t7.83e-06, 0, 0.50, 0.50, 0.00, 0.00, 0.00, 0.00',
                      '** Set initial temperature',
                      '*Amplitude, name=amp',
                      '\t0., 1.',
                      '\t' + str(self.quench_time) + ', ' + str(self.end_temperature/self.start_temperature),
                      '*Amplitude, name=heating',
                      '\t0., ' + str(20./self.start_temperature),
                      '\t' + str(self.heating_time) + ', 1.',
                      '\t' + str(self.heating_time + self.holding_time) + ', 1.',
                      '*INITIAL CONDITIONS, TYPE=TEMPERATURE',
                      '\tALL_NODES, 20.',
                      '**',
                      '** Set initial carbon content',
                      '*INITIAL CONDITIONS, TYPE=FIELD, VAR=1',
                      '\tALL_NODES, ' + str(0.2/100),
                      '**',
                      '*INITIAL CONDITIONS, TYPE=FIELD, VAR=2',
                      '\tALL_NODES , 3',
                      '**',
                      '*STEP,NAME=heating , INC=10000, AMP=STEP',
                      '\t Heating a dilatometer experiment',
                      '\t*HEAT TRANSFER, DELTMX=10.0, END=PERIOD',
                      '\t\t0.01,  ' + str(self.heating_time + self.holding_time) + ', 1e-05,  10',
                      '\t*FIELD, OP = NEW, VAR = 2',
                      '\t\tall_nodes, 3',
                      '\t*Boundary, amplitude=heating',
                      '\t\tall_nodes, 11, 11,' + str(self.start_temperature),
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT',
                      '\t\t\tSDV1,SDV2,SDV21,SDV34,SDV47,SDV60,SDV73,SDV86,SDV99,HFL',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*NODE OUTPUT',
                      '\t\t\tNT',
                      '\t\t*EL FILE, FREQUENCY=0',
                      '\t\t*NODE FILE, FREQUENCY=1',
                      '\t\t\tNT',
                      '\t\t*EL PRINT, FREQ=0',
                      '\t\t*NODE PRINT, FREQ=0',
                      '*END STEP',
                      '**',
                      '*STEP,NAME=add_carbon , INC=10000, AMP=RAMP',
                      '\t Quenching a dilatometer experiment',
                      '\t*HEAT TRANSFER, DELTMX=10.0, END=PERIOD',
                      '\t\t0.01,  1., 1e-05,  1.',
                      '\t*FIELD, OP = NEW, VAR = 1',
                      '\t\tall_nodes, ' + str(self.carbon/100),
                      '\t*FIELD, OP = NEW, VAR = 2',
                      '\t\tall_nodes, -2',
                      '\t*Boundary, amplitude=amp',
                      '\t\tall_nodes, 11, 11,' + str(self.start_temperature),
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT',
                      '\t\t\tSDV1,SDV2,SDV21,SDV34,SDV47,SDV60,SDV73,SDV86,SDV99,HFL',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*NODE OUTPUT',
                      '\t\t\tNT',
                      '\t\t*EL FILE, FREQUENCY=0',
                      '\t\t*NODE FILE, FREQUENCY=1',
                      '\t\t\tNT',
                      '\t\t*EL PRINT, FREQ=0',
                      '\t\t*NODE PRINT, FREQ=0',
                      '*END STEP',
                      '**',
                      '*STEP,NAME=quench , INC=10000, AMP=STEP',
                      '\t Quenching a dilatometer experiment',
                      '\t*HEAT TRANSFER, DELTMX=10.0, END=PERIOD',
                      '\t\t1e-5,  ' + str(self.quench_time) + ', 1e-09,  ' + str(self.quench_time/500),
                      '\t*FIELD, OP = NEW, VAR = 2',
                      '\t\tall_nodes, -2',
                      '\t*Boundary, amplitude=amp',
                      '\t\tall_nodes, 11, 11,' + str(self.start_temperature),
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT',
                      '\t\t\tSDV1,SDV2,SDV21,SDV34,SDV47,SDV60,SDV73,SDV86,SDV99,HFL',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*NODE OUTPUT',
                      '\t\t\tNT',
                      '\t\t*EL FILE, FREQUENCY=0',
                      '\t\t*NODE FILE, FREQUENCY=1',
                      '\t\t\tNT',
                      '\t\t*EL PRINT, FREQ=0',
                      '\t\t*NODE PRINT, FREQ=0',
                      '*END STEP',
                      '**']

        with open(self.directory + '/Toolbox_Thermal_' + str(self.name) + '.inp', 'w') as inp_file:
            for line in file_lines:
                inp_file.write(line + '\n')
            inp_file.write('**EOF')

    def _write_mechanical_file(self):
        file_lines = ['**',
                      '**',
                      '** Autogenerated input file created by Case Hardening Simulation Toolbox, version 0.8.1',
                      '** Written by Niklas Melin and Erik Olsson',
                      '**',
                      '*Heading',
                      '\t Case Hardening Simulation Toolbox - Thermal - Niklas Melin 2012',
                      '*Preprint, echo=NO, model=NO, history=NO, contact=NO',
                      '**',
                      '** ----------------------------------------------------------------',
                      '** Load required include files',
                      '**',
                      '**   Create Geometry',
                      '*Node, nset=all_nodes',
                      '\t1, \t 0., 0., 0.',
                      '\t2, \t 1., 0., 0.',
                      '\t3, \t 1., 1., 0.',
                      '\t4, \t 0., 1., 0.',
                      '\t5, \t 0., 0., 1.',
                      '\t6, \t 1., 0., 1.',
                      '\t7, \t 1., 1., 1.',
                      '\t8, \t 0., 1., 1.',
                      '*Element, type=C3D8, elset=all_elements',
                      '\t1, 1, 2, 3, 4, 5, 6, 7, 8',
                      '**',
                      '** ----------------------------------------------------------------',
                      '**',
                      '**   Define material properties',
                      '**',
                      '*Solid Section, elset=all_elements, material=' + self.material,
                      '\t1.0',
                      '**',
                      '** DEFINE MATERIAL PROPERTIES',
                      '**',
                      '*Material, name=' + self.material,
                      '\t*Density',
                      '\t\t7.83e-06,',
                      '\t*Depvar',
                      '\t\t100,',
                      '\t\t1,  CARBON,       VOLUME FRACTION of CARBON',
                      '\t\t2,  HARDNESS,     Hardness in Rockwell C',
                      '\t\t5,  PLASTIC STRAIN, EFFECTIVE PLASTIC STRAIN',
                      '\t\t21, AUSTENITE,    VOLUME FRACTION of AUSTENITE',
                      '\t\t34, FERRITE,      VOLUME FRACTION of FERRITE',
                      '\t\t47, PEARLITE,     VOLUME FRACTION of PEARLITE',
                      '\t\t60, UBAINITE,     VOLUME FRACTION of UPPER BAINITE',
                      '\t\t73, LBAINITE,     VOLUME FRACTION of LOWER BAINITE',
                      '\t\t86, Q_MARTENSITE, VOLUME FRACTION of QUENCHED MARTENSITE',
                      '\t\t99, T_MARTENSITE, VOLUME FRACTION of TEMPERED MARTENSITE',
                      '\t*User Material, constants=8, type=MECHANICAL',
                      '\t\t1, 0, 0.50, 0.50, 0.00, 0.00, 0.00, 0.00',
                      '*Amplitude, name=amp',
                      '\t0., 1.',
                      '\t' + str(self.quench_time) + ', ' + str(self.end_temperature / self.start_temperature),
                      '*Amplitude, name=heating',
                      '\t0., ' + str(20. / self.start_temperature),
                      '\t' + str(10) + ', 1.',
                      '\t' + str(10 + self.holding_time) + ', 1.',
                      '** Set initial temperature',
                      '*INITIAL CONDITIONS, TYPE=TEMPERATURE',
                      '\tALL_NODES , 20.',
                      '**',
                      '** Set initial carbon content',
                      '*INITIAL CONDITIONS, TYPE=FIELD, VAR=1',
                      '\tALL_NODES , ' + str(self.carbon / 100),
                      '**',
                      '*INITIAL CONDITIONS, TYPE=FIELD, VAR=2',
                      '\tALL_NODES , -8',
                      '**',
                      '*Boundary',
                      '\t1, 1, 3',
                      '\t2, 2, 3',
                      '\t3, 3, 3',
                      '\t4, 1, 1',
                      '\t4, 3, 3',
                      '\t5, 1, 2',
                      '\t6, 2, 2',
                      '\t8, 1, 1',
                      '**',
                      '*STEP,NAME=heating , INC=10000, AMP=STEP',
                      '\t Heating a dilatometer experiment',
                      '\t*STATIC',
                      '\t\t0.01,  ' + str(10. + self.holding_time) + ', 1e-05,  10',
                      '\t*FIELD, OP = NEW, VAR = 2',
                      '\t\tall_nodes, 3',
                      '\t*Temperature, amplitude=heating',
                      '\t\tall_nodes, ' + str(self.start_temperature),
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT, directions=YES',
                      '\t\t\tS, E',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT',
                      '\t\t\tSDV1,SDV2,SDV5,SDV21,SDV34,SDV47,SDV60,SDV73,SDV86,SDV99',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*NODE OUTPUT',
                      '\t\t\tNT,U',
                      '*END STEP',
                      '**',
                      '*STEP,NAME=add_carbon1 , INC=10000, AMP=STEP',
                      '\t Quenching a dilatometer experiment',
                      '\t*STATIC',
                      '\t\t0.01,  1., 1e-05,  1.',
                      '\t*FIELD, OP=NEW, VAR = 2',
                      '\t\tall_nodes, 0',
                      '\t*CONTROLS, PARAMETERS=LINE SEARCH',
                      '\t\t6,',
                      '\t*Temperature',
                      '\t\tall_nodes, ' + str(self.start_temperature),
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT, directions=YES',
                      '\t\t\tS, E',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT',
                      '\t\t\tSDV1,SDV2,SDV5,SDV21,SDV34,SDV47,SDV60,SDV73,SDV86,SDV99',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*NODE OUTPUT',
                      '\t\t\tNT,U',
                      '*END STEP',
                      '**',
                      '**',
                      '*STEP,NAME=add_carbon , INC=10000, AMP=RAMP',
                      '\t Quenching a dilatometer experiment',
                      '\t*STATIC',
                      '\t\t0.01,  1., 1e-05,  1.',
                      # '\t*FIELD, VAR = 1',
                      # '\t\tall_nodes, ' + str(self.carbon/100),
                      '\t*CONTROLS, PARAMETERS=LINE SEARCH',
                      '\t\t6,',
                      '\t*Temperature',
                      '\t\tall_nodes, ' + str(self.start_temperature),
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT, directions=YES',
                      '\t\t\tS, E',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT',
                      '\t\t\tSDV1,SDV2,SDV5,SDV21,SDV34,SDV47,SDV60,SDV73,SDV86,SDV99',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*NODE OUTPUT',
                      '\t\t\tNT,U',
                      '*END STEP',
                      '**',
                      '*STEP,NAME=quench , INC=10000, AMP=STEP',
                      '\t Quenching a dilatometer experiment',
                      '\t*STATIC',
                      '\t\t0.01,  ' + str(self.quench_time) + ', 1e-05,  ' + str(self.quench_time/500),
                      '\t*FIELD, OP = NEW, VAR = 2',
                      '\t\tall_nodes, -2',
                      '\t*Temperature, amplitude=amp',
                      '\t\tall_nodes, ' + str(self.start_temperature),
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT, directions=YES',
                      '\t\t\tS, E',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT',
                      '\t\t\tSDV1,SDV2,SDV5,SDV21,SDV34,SDV47,SDV60,SDV73,SDV86,SDV99',
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*NODE OUTPUT',
                      '\t\t\tNT,U',
                      '*END STEP',
                      '**']

        with open(self.directory + '/Toolbox_Mechanical_' + str(self.name) + '.inp', 'w') as inp_file:
            for line in file_lines:
                inp_file.write(line + '\n')
            inp_file.write('**EOF')

    def _write_run_file(self):
        file_lines = ['export LD_PRELOAD=""',
                      'abq=/scratch/users/erik/SIMULIA/CAE/2018/linux_a64/code/bin/ABQLauncher',
                      'usersub_dir=/scratch/users/erik/Dante/Abaqus_Link/DANTE_Library/dante3_7f_pr1/'
                      'abq2018_linux/dante3_7f_pr1-std.o',
                      'export DANTE_PATH=\'/scratch/users/erik/Dante//DANTEDB3_6\'',
                      'sim_name=' + self.name,
                      # '${abq} j=Toolbox_Thermal_${sim_name} interactive double user=${usersub_dir}',
                      '${abq} j=Toolbox_Mechanical_${sim_name} interactive double user=${usersub_dir}',
                      '${abq} python ../dilatometer_post_processing.py ' + self.name]

        with open(self.directory + '/' + self.run_file_name, 'w') as run_file:
            for line in file_lines:
                run_file.write(line + '\n')

    def _write_env_file(self):
        file_lines = ['# Settings for dante',
                      'usub_lib_dir=\'' + os.path.dirname(self.dante_file) + '\'',
                      '',
                      'ask_delete = OFF'
                      '# MPI Configuration',
                      'mp_mode = MPI']

        with open(self.directory + '/abaqus_v6.env', 'w') as env_file:
            for line in file_lines:
                env_file.write(line + '\n')

    def run(self):
        self._write_thermal_file()
        self._write_mechanical_file()
        self._write_env_file()
        self._write_run_file()

        current_directory = os.getcwd()
        os.chdir(self.directory)
        process = Popen(r'chmod u+x ' + self.run_file_name, cwd=os.getcwd(), shell=True)
        process.wait()
        process = Popen(r'./' + self.run_file_name, cwd=os.getcwd(), shell=True)
        process.wait()

        with open('data_' + self.name + '.pkl', 'r') as data_pickle:
            data = pickle.load(data_pickle)
        os.chdir(current_directory)

        return data


if __name__ == '__main__':
    import matplotlib
    import matplotlib.pyplot as plt

    matplotlib.style.use('classic')
    plt.rc('text', usetex=True)
    plt.rc('font', serif='Computer Modern Roman')
    plt.rcParams.update({'font.size': 20})
    plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                      'monospace': ['Computer Modern Typewriter']})

    cooling = 30.
    for carbon_level, color in zip([0.2, 0.36, 0.52, 0.65], ['k', 'b', 'm', 'r']):
        dilatometer = DilatometerSimulation(carbon=carbon_level, material='U925063', directory='dilatormeter',
                                            cooling_rate=cooling)
        simulation_data = dilatometer.run()
        plt.plot(simulation_data[:, 1], simulation_data[:, 2], '--' + color, lw=2)

        experimental_data = np.genfromtxt('../phase_transformations/data_tehler/expansion_' +
                                          str(carbon_level).replace('.', '_'), delimiter=',')

        temp = experimental_data[:, 0] - 273.15
        strain = experimental_data[:, 1] / 10000

        plt.plot(temp, strain, color, lw=2)

    dilatometer = DilatometerSimulation(carbon=0.8, material='U925063', directory='dilatormeter', cooling_rate=cooling)
    simulation_data = dilatometer.run()
    plt.plot(simulation_data[:, 1], simulation_data[:, 2], '--y', lw=2)

    plt.show()
