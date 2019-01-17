import numpy as np

from input_file_reader.input_file_reader import InputFileReader

reader = InputFileReader()
reader.read_input_file('../input_files/gear_models/utmis_gear/full_model_file.inp')

tooth_part_nodes = reader.set_data['nset']['tooth_part_nodes']
new_nodal_data = np.zeros(len(tooth_part_nodes), 4)


