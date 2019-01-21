import numpy as np

from input_file_reader.input_file_reader import InputFileReader

reader = InputFileReader()
reader.read_input_file('../input_files/gear_models/utmis_gear/full_model_file.inp')

tooth_part_nodes = reader.set_data['nset']['tooth_part_nodes']
new_nodal_data = np.zeros((len(tooth_part_nodes), 4))
node_number_dict = {}
for i, node_number in enumerate(tooth_part_nodes):
    node_number_dict[node_number] = i + 1
    new_nodal_data[i, 0] = i + 1
    new_nodal_data[i, 1:] = reader.nodal_data[node_number - 1, 1:]

tooth_part_elements = reader.set_data['elset']['tooth_part_elements']
new_element_data = np.zeros((len(tooth_part_elements), 9), dtype=int)

for i, element_number in enumerate(tooth_part_elements):
    new_element_data[i, 0] = i + 1
    element_idx = np.searchsorted(reader.elements['C3D8R'][:, 0], element_number)
    for j, node_label in enumerate(reader.elements['C3D8R'][element_idx, 1:]):
        new_element_data[i, j+1] = node_number_dict[node_label]

reader.nodal_data = new_nodal_data

reader.elements = {'C3D8': new_element_data}
reader.set_data = {'nset': {}, 'elset': {}}

reader.write_geom_include_file('../input_files/gear_models/utmis_gear/tooth_part_model.inc')
