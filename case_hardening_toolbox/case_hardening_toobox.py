import os

from input_file_reader.input_file_reader import InputFileReader


class CarburizationData:
    def __init__(self, time, temperature, carbon):
        self.time = time
        self.temperature = temperature
        self.carbon = carbon


class TemperatureData:
    def __init__(self, time, temperature, interaction_property_name):
        self.time = time
        self.temperature = temperature
        self.interaction_property_name = interaction_property_name


class QuenchingData:
    def __init__(self, time, temperature, oil_name):
        self.time = time
        self.temperature = temperature
        self.oil_name = oil_name


class CaseHardeningToolbox:
    def __init__(self, name, include_file_name, include_file_directory):
        """
        :param name:  All input files will get the name Toolbox_Simulation_name.inp
                      where simulation is 'Carbon',
        :param include_file_name:
        """
        self._include_file_directory = include_file_directory + '/'

        self.name = name
        self.include_file_name = include_file_name

        self.input_file_reader = InputFileReader()

        self.material = 'U925062'

        self.initial_temperature = 20.
        self.initial_carbon = 0.0022

        self.diffusion_file = None
        self.interaction_property_file = None

        self.heating_data = CarburizationData(time=None, temperature=self.initial_temperature,
                                              carbon=self.initial_carbon)
        self.carburization_steps = []
        self.furnace_interaction_property = 'FURNACE'
        self.hot_air_interaction_property = 'HOT_AIR'
        self.cool_air_interaction_property = 'AIR_COOL'
        self.transfer_data = TemperatureData(time=60., temperature=650., interaction_property_name=None)
        self.quenching_data = QuenchingData(time=None, temperature=None, oil_name='QUENCHWAY125B_Used_0mps')
        self.cooldown_data = TemperatureData(time=600, temperature=80., interaction_property_name=None)
        self.tempering_data = TemperatureData(time=None, temperature=None, interaction_property_name=None)

        self.carbon_file_lines = None
        self.thermal_file_lines = None
        self.mechanical_file_lines = None

        self.total_time = 0.
        self.thermal_step_counter = 1

        self.dante_file = '/scratch/users/erik/Dante/Abaqus_Link/DANTE_Library/dante3_7f_pr1/abq2018_linux/' \
                          'dante3_7f_pr1-std.o'
        self.abaqus_path = '/scratch/users/erik/SIMULIA/CAE/2018/linux_a64/code/bin/ABQLauncher'
        self.dante_path = '/scratch/users/erik/Dante/'

        self.write_env_file = True
        self.write_run_file = True

    def _init_carbon_file_lines(self):
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
                '*INCLUDE, INPUT = ' + self._include_file_directory + '/Toolbox_Carbon_' +
                self.include_file_name + '_geo.inc',
                '** Load geometry set definitions',
                '*INCLUDE, INPUT = ' + self._include_file_directory + self.include_file_name + '_sets.inc',
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
                '\t*Diffusivity',
                '\t\t*INCLUDE, INPUT = ' + self._include_file_directory + self.diffusion_file,
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
                '*INCLUDE, INPUT = ' + self._include_file_directory +
                'Toolbox_Thermal_' + self.include_file_name + '_geo.inc',
                '** Load geometry set definitions',
                '*INCLUDE, INPUT = ' + self._include_file_directory + self.include_file_name + '_sets.inc',
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
                '**',
                '** ----------------------------------------------------------------',
                '*INCLUDE, INPUT = ' + self._include_file_directory + self.interaction_property_file,
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

    def _init_mechanical_lines(self):
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
                '*INCLUDE, INPUT = ' + self._include_file_directory + 'Toolbox_Mechanical_'
                + self.include_file_name + '_geo.inc',
                '** Load geometry set definitions',
                '*INCLUDE, INPUT = ' + self._include_file_directory + self.include_file_name + '_sets.inc',
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
                '**',
                '** Set initial temperature',
                '*INITIAL CONDITIONS, TYPE=TEMPERATURE',
                '\tALL_NODES , ' + str(20.),
                '**',
                '** Set initial carbon content',
                '*INITIAL CONDITIONS, TYPE=FIELD, VAR=1',
                '\tALL_NODES , ' + str(self.initial_carbon),
                '**',
                '** Set analysis kinematics type to -8, (2 heating up kinetics, -2 cooling kinetics without tempering',
                '*INITIAL CONDITIONS, TYPE=FIELD, VAR=2',
                '\tALL_NODES , -8',
                '**',
                '*INCLUDE, INPUT = ' + self._include_file_directory + self.include_file_name + '_BC.inc']

    def _write_carburization_step(self, step_name, t1, t2, carbon):
        self.carbon_file_lines.append('*STEP,NAME=' + step_name + ', INC=10000')
        self.carbon_file_lines.append('\t' + step_name + ' - Total time: ' + str(t1) + ' - ' +
                                      str(t2) + 's, Carbon: ' + str(carbon) + '%')
        self.carbon_file_lines.append('\t*MASS DIFFUSION, DCMAX=0.001')
        self.carbon_file_lines.append('\t\t0.2,  ' + str(t2 - t1) + ', 1e-05,  10000')
        self.carbon_file_lines.append('\t*TEMPERATURE, AMPLITUDE=TEMP_AMPLITUDE')
        self.carbon_file_lines.append('\t\tAll_Nodes')
        self.carbon_file_lines.append('\t*BOUNDARY')
        self.carbon_file_lines.append('\t\tEXPOSED_NODES, 11, 11, ' + str(carbon / 100))
        self.carbon_file_lines.append('\t*MONITOR, NODE=monitor_node, DOF=11, FREQ=1')
        self.carbon_file_lines.append('\t*Output, field, frequency=1')
        self.carbon_file_lines.append('\t\t*Node Output')
        self.carbon_file_lines.append('\t\t\tNNC, NT')
        self.carbon_file_lines.append('\t\t*Element Output, directions=YES')
        self.carbon_file_lines.append('\t\t\tCONC')
        self.carbon_file_lines.append('\t\t*Element Output, directions=YES,  POSITION=NODES')
        self.carbon_file_lines.append('\t\t\tCONC')
        self.carbon_file_lines.append('*END STEP')
        self.carbon_file_lines.append('**')

        self.thermal_file_lines.append('*STEP,NAME=' + step_name + ', INC=10000')
        self.thermal_file_lines.append('\t*HEAT TRANSFER, DELTMX=10.0, END=PERIOD')
        self.thermal_file_lines.append('\t\t0.01,  ' + str(t2 - t1) + ', 1e-05,  10000')
        self.thermal_file_lines.append('\t*CONTROLS, PARAMETERS = LINE SEARCH')
        self.thermal_file_lines.append('\t\t6,')
        self.thermal_file_lines.append('\t*CONTROLS, PARAMETERS = TIME INCREMENTATION')
        self.thermal_file_lines.append('\t\t20, 30')
        self.thermal_file_lines.append('\t*CONTROLS, FIELD = TEMPERATURE, PARAMETERS = FIELD')
        self.thermal_file_lines.append('\t\t0.05, 0.05')
        self.thermal_file_lines.append('\t*SFILM, OP = NEW, AMPLITUDE=TEMP_AMPLITUDE')
        self.thermal_file_lines.append('\t\tEXPOSED_SURFACE, F, 1.000000, ' + self.furnace_interaction_property)
        self.thermal_file_lines.append('\t*MONITOR, NODE = MONITOR_NODE, DOF=11, FREQ=1')
        self.thermal_file_lines.append('\t*RESTART, WRITE, FREQ=1000')
        self.thermal_file_lines.append('\t*OUTPUT, FIELD, FREQ=1')
        self.thermal_file_lines.append('\t\t*ELEMENT OUTPUT')
        self.thermal_file_lines.append('\t\t\tSDV1, SDV21, SDV34, SDV47, SDV60, SDV73, SDV86, HFL')
        self.thermal_file_lines.append('\t*OUTPUT, FIELD, FREQ=1')
        self.thermal_file_lines.append('\t\t*NODE OUTPUT')
        self.thermal_file_lines.append('\t\t\tNT')
        self.thermal_file_lines.append('\t*EL FILE, FREQUENCY=0')
        self.thermal_file_lines.append('\t*NODE FILE, FREQUENCY=1')
        self.thermal_file_lines.append('\t\tNT')
        self.thermal_file_lines.append('\t*EL PRINT, FREQ=0')
        self.thermal_file_lines.append('\t*NODE PRINT, FREQ=0')
        self.thermal_file_lines.append('*END STEP')
        self.thermal_file_lines.append('**')

        self.mechanical_file_lines.append('*STEP,NAME=' + step_name + ', INC=10000')
        self.mechanical_file_lines.append('\tMechanical simulation')
        self.mechanical_file_lines.append('\t*STATIC')
        self.mechanical_file_lines.append('\t\t0.01,  ' + str(t2 - t1) + ', 1e-05,  10000')
        self.mechanical_file_lines.append('\t*TEMPERATURE, FILE=Toolbox_Thermal_' + self.name + '.odb, '
                                          'BSTEP=' + str(self.thermal_step_counter) + ', ESTEP=' +
                                          str(self.thermal_step_counter))
        self.mechanical_file_lines.append('\t** Add convergence control parameters')
        self.mechanical_file_lines.append('\t*CONTROLS, PARAMETERS = LINE  SEARCH')
        self.mechanical_file_lines.append('\t\t6,')
        self.mechanical_file_lines.append('\t*CONTROLS, PARAMETERS = TIME INCREMENTATION')
        self.mechanical_file_lines.append('\t\t20, 30')
        self.mechanical_file_lines.append('\t*CONTROLS, FIELD = DISPLACEMENT, PARAMETERS = FIELD')
        self.mechanical_file_lines.append('\t\t0.05, 0.05')
        self.mechanical_file_lines.append('\t** Add output variables')
        self.mechanical_file_lines.append('\t*RESTART, WRITE, FREQ = 1000')
        self.mechanical_file_lines.append('\t*MONITOR, NODE = MONITOR_NODE, DOF = 1, FREQ = 1')
        self.mechanical_file_lines.append('\t*OUTPUT, FIELD, FREQ = 10')
        self.mechanical_file_lines.append('\t\t*ELEMENT OUTPUT, directions = YES')
        self.mechanical_file_lines.append('\t\t\tS, E')
        self.mechanical_file_lines.append('\t*OUTPUT, FIELD, FREQ = 10')
        self.mechanical_file_lines.append('\t\t*ELEMENT OUTPUT')
        self.mechanical_file_lines.append('\t\t\tSDV1, SDV2, SDV5, SDV21, SDV34, SDV47, SDV60, SDV73, SDV86, SDV99')
        self.mechanical_file_lines.append('\t*OUTPUT, FIELD, FREQ = 10')
        self.mechanical_file_lines.append('\t\t*NODE OUTPUT')
        self.mechanical_file_lines.append('\t\t\tNT, U')
        self.mechanical_file_lines.append('*END  STEP')
        self.mechanical_file_lines.append('**')
        self.thermal_step_counter += 1

    def add_carburization_steps(self, times, temperatures, carbon_levels):
        for t, temp, carbon in zip(times, temperatures, carbon_levels):
            self.carburization_steps.append(CarburizationData(time=t*60, temperature=temp, carbon=carbon))

    @staticmethod
    def _thermal_step_data(step_name, step_description, step_time, surface_temperature, interaction_property,
                           kinematic_mode, output_frequency=5, step_amp='STEP'):
        return ['*STEP,NAME=' + step_name + ' , INC=10000, AMP=' + step_amp,
                '\t' + step_description,
                '\t*HEAT TRANSFER, DELTMX=10.0, END=PERIOD',
                '\t\t0.01,  ' + str(step_time) + ', 1e-09,  1000.',
                '\t*FIELD, OP=NEW, VAR = 2',
                '\t\tAll_Nodes, ' + str(kinematic_mode),
                '\t*SFILM, OP=NEW',
                '\t\tEXPOSED_SURFACE,F, ' + str(surface_temperature) + ', ' + interaction_property,
                '\t*MONITOR, NODE=MONITOR_NODE, DOF=11, FREQ=1',
                '\t*CONTROLS, PARAMETERS=LINE SEARCH',
                '\t\t 6,',
                '\t*CONTROLS, PARAMETERS=TIME INCREMENTATION',
                '\t\t20, 30, 9, 16, 10, 4, 12, 20',
                '\t*RESTART, WRITE, FREQ=1000',
                '\t*OUTPUT, FIELD, FREQ=' + str(output_frequency),
                '\t\t*ELEMENT OUTPUT',
                '\t\t\tSDV1,SDV2,SDV21,SDV34,SDV47,SDV60,SDV73,SDV86,SDV99,HFL',
                '\t*OUTPUT, FIELD, FREQ=' + str(output_frequency),
                '\t\t*NODE OUTPUT',
                '\t\t\tNT',
                '\t\t*EL FILE, FREQUENCY=0',
                '\t\t*NODE FILE, FREQUENCY=1',
                '\t\t\tNT',
                '\t\t*EL PRINT, FREQ=0',
                '\t\t*NODE PRINT, FREQ=0',
                '*END STEP',
                '**']

    def _mechanical_step_data(self, step_name, step_description, step_time, kinematic_mode, output_frequency=5,
                              max_increment=1000., step_amp='STEP'):
        return ['*STEP, NAME=' + step_name + ', inc=10000, AMP=' + step_amp,
                '\t' + step_description,
                '\t*STATIC',
                '\t\t0.01,  ' + str(step_time) + ', 1e-05,  ' + str(max_increment),
                '\t*FIELD, OP=NEW, VAR=2',
                '\t\tAll_Nodes,  ' + str(kinematic_mode),
                '\t*TEMPERATURE, FILE=Toolbox_Thermal_' + self.name + '.odb, BSTEP = ' +
                str(self.thermal_step_counter) + ', ESTEP = ' + str(self.thermal_step_counter),
                '\t*CONTROLS, PARAMETERS=LINE SEARCH',
                '\t\t 6,',
                '\t*CONTROLS, PARAMETERS=TIME INCREMENTATION',
                '\t\t20, 30',
                '\t*CONTROLS, FIELD=DISPLACEMENT, PARAMETERS=FIELD',
                '\t\t0.05,0.05',
                '\t*RESTART, WRITE, FREQ=1000',
                '\t*MONITOR, NODE=MONITOR_NODE, DOF=1, FREQ=1',
                '\t*OUTPUT, FIELD, FREQ=' + str(output_frequency),
                '\t\t*ELEMENT OUTPUT, directions=YES',
                '\t\t\tS, E',
                '\t*OUTPUT, FIELD, FREQ=' + str(output_frequency),
                '\t\t*ELEMENT OUTPUT',
                '\t\t\tSDV1,SDV2,SDV5,SDV21,SDV34,SDV47,SDV60,SDV73,SDV86,SDV99',
                '\t*OUTPUT, FIELD, FREQ=' + str(output_frequency),
                '\t\t*NODE OUTPUT',
                '\t\t\tNT,U',
                '*END STEP',
                '**']

    def _add_add_carbon_step(self):
        step_lines = self._mechanical_step_data(step_name='Add carbon',
                                                step_description='Import carbon content from mass diffusion simulation',
                                                step_time=1.0,
                                                kinematic_mode=-8,
                                                output_frequency=1, step_amp='RAMP')

        step_lines[6] = '\t*FIELD, VAR=1,  INPUT=Toolbox_Carbon_' + self.name + '.nod'
        self.mechanical_file_lines += step_lines

    def _add_transfer_step(self):
        step_name = 'Transfer'
        step_description = 'Transfer from furnace to quench tank in air'
        interaction_property = self.hot_air_interaction_property
        if self.transfer_data.interaction_property_name is not None:
            interaction_property = self.transfer_data.interaction_property_name

        step_lines = self._thermal_step_data(step_name=step_name,
                                             step_description=step_description,
                                             step_time=self.transfer_data.time,
                                             surface_temperature=self.transfer_data.temperature,
                                             interaction_property=interaction_property,
                                             kinematic_mode=-8,
                                             output_frequency=1)

        step_lines.insert(4, '\t*FIELD, VAR=1,  INPUT=Toolbox_Carbon_' + self.name + '.nod')

        self.thermal_file_lines += step_lines

        self.mechanical_file_lines += self._mechanical_step_data(step_name=step_name,
                                                                 step_description=step_description,
                                                                 step_time=self.transfer_data.time,
                                                                 kinematic_mode=-8,
                                                                 output_frequency=10)
        self.thermal_step_counter += 1

    def _add_quenching_step(self):
        step_name = 'Quenching'
        step_description = 'Quenching in oil ' + self.quenching_data.oil_name
        self.thermal_file_lines += self._thermal_step_data(step_name=step_name,
                                                           step_description=step_description,
                                                           step_time=self.quenching_data.time,
                                                           surface_temperature=self.quenching_data.temperature,
                                                           interaction_property=self.quenching_data.oil_name,
                                                           kinematic_mode=-8,
                                                           output_frequency=1)

        self.mechanical_file_lines += self._mechanical_step_data(step_name=step_name,
                                                                 step_description=step_description,
                                                                 step_time=self.quenching_data.time,
                                                                 kinematic_mode=-8,
                                                                 output_frequency=1)

        self.thermal_step_counter += 1

    def _add_cooldown_step(self, step_name, kinematic_mode, time, temperature):
        step_description = 'Cooling'
        interaction_property = self.cool_air_interaction_property
        if self.cooldown_data.interaction_property_name is not None:
            interaction_property = self.cooldown_data.interaction_property_name

        self.thermal_file_lines += self._thermal_step_data(step_name=step_name,
                                                           step_description=step_description,
                                                           step_time=time,
                                                           surface_temperature=temperature,
                                                           interaction_property=interaction_property,
                                                           kinematic_mode=kinematic_mode,
                                                           output_frequency=1)

        self.mechanical_file_lines += self._mechanical_step_data(step_name=step_name,
                                                                 step_description=step_description,
                                                                 step_time=time,
                                                                 kinematic_mode=kinematic_mode,
                                                                 output_frequency=1)

        self.thermal_step_counter += 1

    def _add_tempering_step(self):
        step_name = 'Tempering'
        step_description = 'Tempering'
        interaction_property = self.cool_air_interaction_property
        if self.tempering_data.interaction_property_name is not None:
            interaction_property = self.tempering_data.interaction_property_name

        self.thermal_file_lines += self._thermal_step_data(step_name=step_name,
                                                           step_description=step_description,
                                                           step_time=self.tempering_data.time,
                                                           surface_temperature=self.tempering_data.temperature,
                                                           interaction_property=interaction_property,
                                                           kinematic_mode=-3,
                                                           output_frequency=1)

        self.mechanical_file_lines += self._mechanical_step_data(step_name=step_name,
                                                                 step_description=step_description,
                                                                 step_time=self.tempering_data.time,
                                                                 kinematic_mode=-3,
                                                                 output_frequency=1,
                                                                 max_increment=50)
        self.thermal_step_counter += 1

    def write_files(self):
        self.carbon_file_lines = self._init_carbon_file_lines()
        self.thermal_file_lines = self._init_thermal_lines()
        self.mechanical_file_lines = self._init_mechanical_lines()

        for line_set in [self.carbon_file_lines, self.thermal_file_lines]:
            line_set.append('*AMPLITUDE, NAME=TEMP_AMPLITUDE, TIME=TOTAL TIME, VALUE=ABSOLUTE')
            line_set.append('\t ' + str(0.) + ', \t ' + str(self.initial_temperature))
            total_time = 0.
            if self.heating_data.time is not None:
                line_set.append('\t ' + str(60.) + ', \t ' + str(self.heating_data.temperature))
                line_set.append('\t ' + str(self.heating_data.time*60) + ', \t ' +
                                str(self.heating_data.temperature))
                total_time = self.heating_data.time*60

            for carb_step in self.carburization_steps:
                line_set.append('\t ' + str(total_time + 60.) + ', \t ' + str(carb_step.temperature))
                line_set.append('\t ' + str(total_time + carb_step.time) + ', \t ' + str(carb_step.temperature))
                total_time += carb_step.time
            line_set.append('**')

        # Add a heating step
        if self.heating_data.time is not None:
            self._write_carburization_step('Heating', self.total_time, self.total_time + self.heating_data.time*60,
                                           self.heating_data.carbon)
            self.total_time += self.heating_data.time*60

        # Add the carburization steps
        for i, carburization_step in enumerate(self.carburization_steps):
            step_name = 'Carburization - ' + str(i+1)
            self._write_carburization_step(step_name, self.total_time, self.total_time + carburization_step.time,
                                           carburization_step.carbon)
            self.total_time += carburization_step.time

        # Add the add carbon step to the mechanical input file
        self._add_add_carbon_step()

        # Add step for transfer from oven to quench bath
        if self.transfer_data.time is not None and self.transfer_data.time > 0.:
            self._add_transfer_step()

        if self.quenching_data.time is not None and self.quenching_data.time > 0.:
            self._add_quenching_step()

        if self.cooldown_data.time is not None and self.cooldown_data.time > 0.:
            self._add_cooldown_step('Cooldown_1', kinematic_mode=-8, time=self.cooldown_data.time,
                                    temperature=self.cooldown_data.temperature)
            self._add_cooldown_step('Cooldown_2', kinematic_mode=1, time=self.cooldown_data.time,
                                    temperature=20)

        if self.tempering_data.time is not None and self.tempering_data.time > 0:
            self._add_tempering_step()

        self._add_cooldown_step('Cooldown_3', kinematic_mode=1, time=3600, temperature=self.initial_temperature)

        for name, lines in zip(['Carbon', 'Thermal', 'Mechanical'],
                               [self.carbon_file_lines, self.thermal_file_lines, self.mechanical_file_lines]):
            with open('Toolbox_' + name + '_' + self.name + '.inp', 'w+') as inp_file:
                for line in lines:
                    inp_file.write(line + '\n')
                inp_file.write('**EOF')

        if self.write_env_file:
            self._write_env_file()

        if self.write_run_file:
            self._write_run_file()

    def _write_env_file(self):
        file_lines = ['# Settings for dante',
                      'usub_lib_dir=\'' + os.path.dirname(self.dante_file) + '\'',
                      '',
                      'ask_delete = OFF'
                      '# MPI Configuration',
                      'mp_mode = MPI']

        with open('abaqus_v6.env', 'w') as env_file:
            for line in file_lines:
                env_file.write(line + '\n')

    def _write_run_file(self):
        file_lines = ['#!/bin/bash',
                      '#PBS -V',
                      '#PBS -z',
                      '#PBS -l select=1:ncpus=8',
                      'cd $PBS_O_WORKDIR',
                      'export LD_PRELOAD=\"\"',
                      'abq=' + self.abaqus_path,
                      'usersub_dir=' + self.dante_file,
                      'export DANTE_PATH=\'' + self.dante_path + '/DANTEDB3_6\'',
                      '',
                      'sim_name=' + self.name,
                      'carbon_exp_script=' + self.dante_path + '/python/carbonFieldExport.py',
                      '${abq} j=Toolbox_Carbon_${sim_name} cpus=8 interactive',
                      '${abq} python ${carbon_exp_script} odbFileName=Toolbox_Carbon_${sim_name}.odb '
                      'carbonFileName=Toolbox_Carbon_${sim_name}.nod',
                      '${abq} j=Toolbox_Thermal_${sim_name} cpus=8 interactive user=${usersub_dir}',
                      '${abq} j=Toolbox_Mechanical_${sim_name} cpus=8 interactive user=${usersub_dir}']

        with open('run_heat_treatment_sim.sh', 'w') as shell_file:
            for line in file_lines:
                shell_file.write(line + '\n')


def write_geometry_files_for_dante(geometry_data_file, directory_to_write, dante_include_file_name,
                                   str_to_remove_from_set_names=''):
    input_file_reader = InputFileReader()
    input_file_reader.read_input_file(geometry_data_file)
    if not os.path.isdir(directory_to_write):
        os.makedirs(directory_to_write)

    input_file_reader.write_geom_include_file(directory_to_write + '/Toolbox_Carbon_' +
                                              dante_include_file_name + '_geo.inc',
                                              simulation_type='Carbon')

    input_file_reader.write_geom_include_file(directory_to_write + '/Toolbox_Thermal_' +
                                              dante_include_file_name + '_geo.inc',
                                              simulation_type='Thermal')

    input_file_reader.write_geom_include_file(directory_to_write + '/Toolbox_Mechanical_' +
                                              dante_include_file_name + '_geo.inc',
                                              simulation_type='Mechanical')

    surfaces = [('EXPOSED_SURFACE', 'EXPOSED_ELEMENTS')]
    input_file_reader.write_sets_file(directory_to_write + dante_include_file_name + '_sets.inc',
                                      str_to_remove_from_setname=str_to_remove_from_set_names,
                                      surfaces_from_element_sets=surfaces)
