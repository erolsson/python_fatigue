from input_file_reader.input_file_reader import InputFileReader
from input_file_reader.input_file_functions import write_set_rows


def create_sets_for_fatigue_evaluation():
    x_pos = {'smooth': 10.0, 'notched': 2.2}

    for specimen in ['smooth', 'notched']:
        input_file_reader = InputFileReader()
        input_file_reader.read_input_file('utmis_' + specimen + '/' + 'utmis_' + specimen + '.inc')

        nodes = input_file_reader.nodal_data[input_file_reader.nodal_data[:, 1] < x_pos[specimen], :]
        nodes = set(nodes[:, 0])

        set_elements = []

        for e in input_file_reader.elements['C3D8']:
            for n in e[1:]:
                if n in nodes:
                    set_elements.append(e[0])

        set_elements = sorted(set(set_elements))
        file_lines = []
        write_set_rows(set_elements, file_lines)

        with open('utmis_' + specimen + '/fatigue_volume_elements_' + specimen + '.inc', 'w') as set_file:
            for line in file_lines:
                set_file.write(line + '\n')


create_sets_for_fatigue_evaluation()
