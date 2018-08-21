import odbAccess

from abaqusConstants import *

odb = odbAccess.openOdb('/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_1x/martensite.odb',
                        readOnly=False)
for cd in ['0_5', '0_8', '1_1']:
    step_name = 'dante_results_' + str(cd).replace('.', '_')
    step = odb.steps[step_name]
    frame = step.frames[0]
    field = frame.fieldOutputs['Q_MARTENSITE']
    new_step = odb.Step(name='martensite_data', description='', domain=TIME, timePeriod=1)
    start_frame = new_step.Frame(incrementNumber=0, frameValue=0, description='')
    end_frame = new_step.Frame(incrementNumber=1, frameValue=1., description='')
    new_field = field
    start_frame.FieldOutput(name='NT11', field=0*field)
    end_frame.FieldOutput(name='NT11', field=new_field)

    odb.save()
    odb.close()
