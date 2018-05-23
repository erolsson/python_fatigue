import numpy as np

nodes = []
elements = []
with open('fullTooth.inp') as full_model_file:
    lines = full_model_file.readlines()
    reading_nodes = False
    reading_elements = False

    for line in lines:
        if 'Node' in line.split()[0]:
            reading_nodes = True
            reading_elements = False
        elif 'Element' in line.split()[0]:
            reading_elements = True
            reading_nodes = False
        elif '*' in line.split()[0]:
            reading_nodes = False
            reading_elements = False
        elif reading_nodes:
            nodes.append(line.split(","))
        elif reading_elements:
            elements.append(line.split(","))

nodal_id = np.zeros(len(nodes), dtype=int)
nodal_positions = np.zeros((len(nodes), 3))

for i, node in enumerate(nodes):
    nodal_id[i] = node[0]
    nodal_positions[i, :] = node[1:]

# Just the two first node layers in the middle
z_pos = np.unique(np.abs(nodal_positions[:, 2]))
z_pos = z_pos[:2]

nodal_id = nodal_id[nodal_positions[:, 2] > -1e-6]
nodal_positions = nodal_positions[nodal_positions[:, 2] > -1e-6, :]

nodal_id = nodal_id[nodal_positions[:, 0] > -1e-3]
nodal_positions = nodal_positions[nodal_positions[:, 0] > -1e-3, :]

nodal_id = nodal_id[nodal_positions[:, 2] < z_pos[-1] + 1e-6]
nodal_positions = nodal_positions[nodal_positions[:, 2] < z_pos[-1] + 1e-6, :]
id_set = set(nodal_id)

# Find the elements corresponding to the model nodes
model_elements = []
for element in elements:
    include = True
    for node in element[1:]:
        if int(node) not in id_set:
            include = False
    if include:
        model_elements.append(element)

file_lines = ['*Node\n']
for i in range(nodal_id.shape[0]):
    file_lines.append('\t' + str(nodal_id[i]) + ',\t')
    file_lines.append(str(nodal_positions[i, 0]) + ',\t' + str(nodal_positions[i, 1]) + ',\t' +
                      str(nodal_positions[i, 2]) + '\n')

file_lines.append('*Element, type=C3D8\n')
for element in model_elements:
    line = ''
    for data in element:
        line += '\t' + str(int(data)) + ','
    file_lines.append(line[: -1] + '\n')
file_lines.append('**EOF')

# Write the geometric include file
with open('slice_geo.inc', 'w') as include_file:
    for line in file_lines:
        include_file.write(line)






