from collections import namedtuple
import sys

CarburizationStep = namedtuple('CarburizationStep', ['time, carbon'])
TemperatureData = namedtuple('TemperatureData', ['time', 'temperature'])
QuenchingData = namedtuple('QuenchingData', ['time', 'temperature', 'oil_name'])


class CaseHardeningToolbox:
    def __init__(self, input_file_name, name, path_to_write=''):
        self.raw_data_file = input_file_name
        self.path_to_write = path_to_write
        self.sets_file_directory = ''
        self.geometry_files_directory = ''
        self.name = name

        self.material = 'U925062'

        self.initial_temperature = 20.
        self.initial_carbon = 0.0022

        self.sets_file = self.name + '_sets.inc'
        self.boundary_condition_file = None
        self.diffusion_file = None
        self.interaction_property_file = None

        self.carburization_steps = []
        self.quenching_data = None
        self.cooldown_data = TemperatureData(time=3600, temperature=80)
        self.tempering_data = None

    def _init_carbon_lines(self):
        if self.diffusion_file is None:
            print ' No diffusion file set, create one or assign a file path'
            sys.exit(1)

        return ['**',
                '**',
                '** Autogenerated input file created by Case Hardening Simulation Toolbox, version 0.8.1',
                '** Written by Niklas Melin and Erik Olsson',
                '**',
                '*Heading',
                '\t Case Hardening Simulation Toolbox - Carburization - Niklas Melin 2012',
                '*Preprint, echo=NO, model=NO, history=NO, contact=NO',
                '**',
                '** ----------------------------------------------------------------',
                '** Load required include files',
                '**',
                '**   Load geometry',
                '*INCLUDE, INPUT = ' + self.geometry_files_directory + ' Toolbox_Carbon_' + self.name + '_geo.inc',
                '** Load geometry set definitions',
                '*INCLUDE, INPUT = ' + self.sets_file,
                '**',
                '** ----------------------------------------------------------------',
                '**',
                '**   Define material properties',
                '**',
                '*Solid Section, elset=All_Elements, material=' + self.material,
                '\t1.0'
                '*Hourglass Stiffness'
                '\t225.0, 0.0, 0.0'
                '**',
                '** DEFINE MATERIAL PROPERTIES',
                '**',
                '*Material, name=' + self.material,
                '\t*Density'
                '\t\t7.83e-06,'
                '\t*INCLUDE, INPUT = ' + self.diffusion_file,
                '\t*Solubility',
                '\t\t1.0',
                '**',
                '**',
                '*INITIAL CONDITIONS, TYPE=CONCENTRATION',
                '\tAll_Nodes , ' + str(self.initial_carbon),
                '*INITIAL CONDITIONS, TYPE=TEMPERATURE',
                '\tAll_Nodes , ' + str(self.initial_temperature),
                '**']

    def _init_thermal_lines(self):
        return ['**',
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
                '**   Load geometry',
                '*INCLUDE, INPUT = ' + self.geometry_files_directory + ' Toolbox_Thermal_' + self.name + '_geo.inc',
                '** Load geometry set definitions',
                '*INCLUDE, INPUT = ' +  self.sets_file,
                '**',
                '** ----------------------------------------------------------------',
                '**',
                '**   Define material properties',
                '**',
                '*Solid Section, elset=All_Elements, material=' + self.material,
                '\t1.0'
                '*Hourglass Stiffness'
                '\t225.0, 0.0, 0.0'
                '**',
                '** DEFINE MATERIAL PROPERTIES',
                '**',
                '*Material, name=' + self.material,
                '\t*Density',
                '\t\t7.83e-06,',
                '\t*Depvar',
                '\t\t100',
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
                '\t\t7.83e-06, 0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00'
                '**',
                '** ----------------------------------------------------------------',
                '*INCLUDE, INPUT = ' + self.interaction_property_file,
                '** ----------------------------------------------------------------',
                '** Set initial temperature',
                '*INITIAL CONDITIONS, TYPE=TEMPERATURE',
                '\tALL_NODES , ' + str(self.initial_temperature),
                '**',
                '** Set initial carbon content',
                '*INITIAL CONDITIONS, TYPE=FIELD, VAR=1',
                '\tALL_NODES , ' + str(self.initial_carbon),
                '**',
                '** Set analysis kinematics type to -8, (2 heating up kinetics, -2 cooling kinetics without tempering',
                '*INITIAL CONDITIONS, TYPE=FIELD, VAR=2',
                '\tALL_NODES , -8',
                '**']

    def _init_mechanical_file(self):
        return ['**',
                '**',
                '** Autogenerated input file created by Case Hardening Simulation Toolbox, version 0.8.1',
                '** Written by Niklas Melin and Erik Olsson',
                '**',
                '*Heading',
                '\t Case Hardening Simulation Toolbox - Mechanical - Niklas Melin 2012',
                '*Preprint, echo=NO, model=NO, history=NO, contact=NO',
                '**',
                '** ----------------------------------------------------------------',
                '** Load required include files',
                '**',
                '**   Load geometry',
                '*INCLUDE, INPUT = ' + self.geometry_files_directory + ' Toolbox_Mechanical_' + self.name + '_geo.inc',
                '** Load geometry set definitions',
                '*INCLUDE, INPUT = ' + self.sets_file,
                '**',
                '** ----------------------------------------------------------------',
                '**',
                '**   Define material properties',
                '**',
                '*Solid Section, elset=All_Elements, material=' + self.material,
                '\t1.0'
                '*Hourglass Stiffness'
                '\t225.0, 0.0, 0.0'
                '**',
                '** DEFINE MATERIAL PROPERTIES',
                '**',
                '*Material, name=' + self.material,
                '\t*Density',
                '\t\t7.83e-06,',
                '\t*Depvar',
                '\t\t100',
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
                '\t*User Material, constants=8, type=THERMAL',
                '\t\t1, 0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00'
                '**',
                '** ----------------------------------------------------------------',
                '*INCLUDE, INPUT = ' + self.interaction_property_file,
                '** ----------------------------------------------------------------',
                '** Set initial temperature',
                '*INITIAL CONDITIONS, TYPE=TEMPERATURE',
                '\tALL_NODES , ' + str(self.initial_temperature),
                '**',
                '** Set initial carbon content',
                '*INITIAL CONDITIONS, TYPE=FIELD, VAR=1',
                '\tALL_NODES , ' + str(self.initial_carbon),
                '**',
                '** Set analysis kinematics type to -8, (2 heating up kinetics, -2 cooling kinetics without tempering',
                '*INITIAL CONDITIONS, TYPE=FIELD, VAR=2',
                '\tALL_NODES , -8',
                '**',
                '*INCLUDE, INPUT = ' + self.boundary_condition_file]

    def write_geometry_files(self):
        pass

    def write_files(self):
        pass
