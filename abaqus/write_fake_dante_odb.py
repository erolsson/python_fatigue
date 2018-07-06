from odbAccess import *
from abaqusConstants import *

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance


def create_dante_step(results_odb_name, carbon_odb_name, stress_odb_name, results_step_name):
    carbon_odb = openOdb(carbon_odb_name, readOnly=True)
    step = carbon_odb.steps['Carburization-3']
    frame = step.frames[len(step.frames) - 1]
    field = frame.fieldOutputs['NNC11']

    hardness = -1.95704040e+09*field**3 + 1.79113930e+07*field**2 + 5.50685403e+04*field + 2.27359677e+02
    results_odb = openOdb(results_odb_name, readOnly=False)
    new_step = results_odb.Step(name=results_step_name, description='', domain=TIME, timePeriod=1)
    new_frame = new_step.Frame(incrementNumber=0, frameValue=0, description='')

    new_frame.FieldOutput(name='HV', field=hardness)
    carbon_odb.close()

    stress_odb = openOdb(stress_odb_name, readOnly=True)
    step = carbon_odb.steps['Equilibrium']
    frame = step.frames[len(step.frames) - 1]
    field = frame.fieldOutputs['S']
    new_frame.FieldOutput(name='S', field=field)
    stress_odb.close()

    results_odb.close()

if __name__ == '__main__':
    carbon_odb_path = '/scratch/users/erik/python_fatigue/planetary_gear/input_files/resolve_residual_stresses/'
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/'

    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)
    instances = [OdbInstance(name='tooth_right', nodes=nodes_pos, elements=elements_pos)]

    tooth_odb_file_name = dante_odb_path + 'dante_results_fake.odb'
    create_odb(odb_file_name=tooth_odb_file_name, instance_data=instances)

    for cd in ['0_5', '0_8', '1_1', '1_4']:
        create_dante_step(results_odb_name=tooth_odb_file_name,
                          carbon_odb_name=carbon_odb_path + 'Toolbox_Carbon_' + cd + '_quarter.odb',
                          stress_odb_name=dante_odb_path + 'residual_stresses_' + cd + '.odb',
                          results_step_name='dante_results_' + cd)
