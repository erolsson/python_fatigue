import os
from subprocess import Popen
import sys

try:
    import distro
except ImportError:
    import platform as distro

from input_file_reader.input_file_reader import InputFileReader
from materials.SS2506.stress_strain_evaluation import SS2506


def write_mechanical_input_files(geom_include_file, directory, loads, no_steps=1, initial_inc=1e-2):
    input_file_reader = InputFileReader()
    input_file_reader.read_input_file(geom_include_file)
    input_file_reader.write_geom_include_file(directory + '/include_files/geom_pos.inc')
    input_file_reader.nodal_data[:, 2] *= -1
    load_nodes = input_file_reader.set_data['nset']['Specimen_load_nodes']
    support_nodes = input_file_reader.set_data['nset']['Specimen_support_nodes']
    x_sym_nodes = input_file_reader.set_data['nset']['Specimen_XSym_Nodes']
    y = -min([input_file_reader.nodal_data[n-1, 2] for n in x_sym_nodes])
    z = max([input_file_reader.nodal_data[n - 1, 3] for n in x_sym_nodes])

