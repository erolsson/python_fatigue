import re
import numpy as np


class InputFileReader:
    def __init__(self):
        self.nodal_data = None
        self.elements = None
        self.set_data = {'nset': {}, 'elset': {}}

    def read_input_file(self, model_filename):
        nodes = []
        elements = []
        with open(model_filename) as full_model_file:
            lines = full_model_file.readlines()
        key_word = None
        key_word_data = None
        for line in lines:
            if line.startswith('*') and not line.startswith('**'):
                key_word_line = line.split(',')
                key_word = (key_word_line[0][1:]).lower().rstrip()   # Convert to lower case and remove newlines etc
                key_word_data = key_word_line[1:]
            else:  # We have a data_row
                data = line.split(',')
                data = [item.rstrip() for item in data]
                if key_word == 'node':
                    nodes.append(data)
                elif key_word == 'element':
                    elements.append(data)
                elif key_word[-3:] == 'set':
                    set_name = key_word_data[0].split('=')[1]
                    if set_name not in self.set_data[key_word]:
                        self.set_data[key_word][set_name] = []
                    self.set_data[key_word][set_name] += [int(label) for label in data if label]

        self.nodal_data = np.zeros((len(nodes), 4))

        for i, node in enumerate(nodes):
            self.nodal_data[i, :] = node

        self.elements = np.array(elements, dtype=int)

    def write_geom_include_file(self, filename, simulation_type='Mechanical'):
        element_type = 'DC3D8'
        if simulation_type == 'Mechanical':
            element_type = 'C3D8'

        file_lines = ['*NODE']
        for node in self.nodal_data:
            file_lines.append(
                '\t' + str(int(node[0])) + ', ' + str(node[1]) + ', ' + str(node[2]) + ', ' + str(node[3]))
        file_lines.append('*ELEMENT, TYPE=' + element_type)
        for element in self.elements:
            element_string = [str(e) for e in element]
            element_string = ', '.join(element_string)
            file_lines.append('\t' + element_string)

        with open(filename, 'w') as inc_file:
            for line in file_lines:
                inc_file.write(line + '\n')
            inc_file.write('**EOF')

    def write_sets_file(self, filename, skip_prefix='_', str_to_remove_from_setname=''):
        file_lines = []
        node_sets, element_sets = self.set_data['nset'], self.set_data['elset']

        def write_set_rows(data_to_write):
            data_line = ''
            counter = 0
            for item in data_to_write:
                data_line += str(int(item)) + ', '
                counter += 1
                if counter == 16 or item == data_to_write[-1]:
                    file_lines.append(data_line[:-2])
                    counter = 0
                    data_line = ''

        for key, data in element_sets.iteritems():
            file_lines.append('*Elset, elset=' + key)
            write_set_rows(data)

        for key, data in node_sets.iteritems():
            file_lines.append('*Nset, nset=' + key)
            write_set_rows(data)
        return file_lines


if __name__ == '__main__':
    directory = '../fatigue_specimens/UTMIS_notched/'
    reader = InputFileReader()
    reader.read_input_file(directory + 'utmis_notched_geo.inc')
    reader.write_geom_include_file(directory + 'utmis_notched_geo_carbon.inc', simulation_type='Carbon')
    reader.write_geom_include_file(directory + 'utmis_notched_geo_thermal.inc', simulation_type='Thermal')
    reader.write_geom_include_file(directory + 'utmis_notched_geo_mechanical.inc', simulation_type='Mechanical')
