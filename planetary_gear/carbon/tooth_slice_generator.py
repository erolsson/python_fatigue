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

print nodal_id
print nodal_positions
