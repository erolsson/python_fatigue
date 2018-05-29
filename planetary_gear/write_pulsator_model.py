from write_input_for_dante import create_quarter_model
from write_input_for_dante import write_geom_include_file

quarter_nodes, quarter_elements = create_quarter_model()
write_geom_include_file(quarter_elements, quarter_elements,
                        filename='input_files/pulsator_model/dense_geom_xpos.inc')

quarter_nodes
