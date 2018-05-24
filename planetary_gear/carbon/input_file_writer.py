from collections import namedtuple


def write_input_file(sim_data):
    def write_carburization_step(lines, name, t1, t2, carbon):
        lines.append('*STEP,NAME=' + name + ', INC=10000')
        lines.append('\t' + name + ' - Total time: ' + str(t1) + ' - ' + str(t2) + 's, Carbon: ' + str(carbon) + '%')
        lines.append('*MASS DIFFUSION, DCMAX=0.001')
        lines.append('\t0.2,  ' + str(t2-t1) + ', 1e-05,  10000')
        lines.append('*TEMPERATURE, AMPLITUDE=TEMP_AMPLITUDE')
        lines.append('\tAll_Nodes')
        lines.append('*BOUNDARY')
        lines.append('\tEXPOSED_NODES, 11, 11, ' + str(carbon/100))
        lines.append('*MONITOR, NODE=monitor_node, DOF=11, FREQ=1')
        lines.append('*Output, field, frequency=1')
        lines.append('*Node Output')
        lines.append('\tNNC, NT')
        lines.append('*Element Output, directions=YES')
        lines.append('\tCONC')
        lines.append('*Element Output, directions=YES,  POSITION=NODES')
        lines.append('\tCONC')
        lines.append('*End Step')

    file_lines = ['**',
                  'Heading',
                  '\tCarbon diffusion test',
                  '*Preprint, echo=NO, model=NO, history=NO, contact=NO',
                  '*Part, name = tooth_slice',
                  '\t*INCLUDE, INPUT = slice_geo.inc',
                  '\t*Solid Section, elset=All_ELEMS, material=U92506',
                  '\t\t1.',
                  '\t\t*Hourglass Stiffness',
                  '\t\t\t225.0, 0.0, 0.0',
                  '*end part',
                  '*assembly, name=assembly',
                  '\t*instance, name=tooth, part=tooth_slice',
                  '\t *end instance',
                  '\t *INCLUDE, INPUT=planetGear_Sets.inc',
                  '*end assembly',
                  '*INCLUDE, INPUT=SS2506.inc',
                  '*INCLUDE, INPUT=film_properties.inc',
                  '**',
                  '*INITIAL CONDITIONS, TYPE=CONCENTRATION',
                  '\tAll_Nodes, 0.002200',
                  '*INITIAL CONDITIONS, TYPE=TEMPERATURE',
                  '\t All_Nodes, 20.000000',
                  '**',
                  '*AMPLITUDE, NAME = TEMP_AMPLITUDE, TIME = TOTAL TIME, VALUE = ABSOLUTE',
                  '\t 0.0, \t\t 20.0',
                  '\t 1.0, \t\t 780.0',
                  '\t 5400.0, \t 930.0']

    total_time = 5400.
    for t, temp in zip(sim_data.times, sim_data.temperatures):
        file_lines.append('\t ' + str(total_time+1.) + ', \t ' + str(temp))
        total_time += t*60
        file_lines.append('\t ' + str(total_time) + ', \t ' + str(temp))
    file_lines.append('**')

    write_carburization_step(file_lines, 'Heating', 0, 5400, 0.5)
    total_time = 5400.
    step_nr = 1
    for t, carb in zip(sim_data.times, sim_data.carbon):
        write_carburization_step(file_lines, 'Carburization - ' + str(step_nr), total_time, total_time+t*60, carb)
        step_nr += 1
        total_time += t*60

    with open('tooth_slice_' + str(sim_data.CD).replace('.', '_') + '.inp', 'w') as input_file:
        for line in file_lines:
            input_file.write(line + '\n')
        input_file.write('**EOF')

if __name__ == '__main__':
    Simulation = namedtuple('Simulation', ['CD', 'times', 'temperatures', 'carbon'])
    simulations = [Simulation(CD=0.2, times=[105.], temperatures=(840.,), carbon=(0.8,)),
                   Simulation(CD=0.5, times=[75., 5., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8)),
                   Simulation(CD=0.8, times=[135., 30., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8)),
                   Simulation(CD=1.1, times=[370., 70., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8)),
                   Simulation(CD=1.4, times=[545., 130., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8))]
    for sim in simulations:
        write_input_file(sim)
