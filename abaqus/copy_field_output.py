import odbAccess

from abaqusConstants import *


for cd in ['0_5', '0_8', '1_1']:
    odb = odbAccess.openOdb('/scratch/users/erik/scania_gear_analysis/odb_files/dante_interpolation/'
                            'Toolbox_Carbon_' + cd + '_quarter.odb', readOnly=False)

    step = odb.steps['Carburization-3']
    frame = step.frames[len(step.frames) - 1]
    field = frame.fieldOutputs['NNC11']
    new_step = odb.Step(name='dante_data', description='', domain=TIME, timePeriod=1)
    start_frame = new_step.Frame(incrementNumber=0, frameValue=0, description='')
    end_frame = new_step.Frame(incrementNumber=1, frameValue=1., description='')
    new_field = -2.07934384e+04*field*field + 2.98225944e+02*field-1.60574051e-01
    start_frame.FieldOutput(name='NT11', field=0*field)
    end_frame.FieldOutput(name='NT11', field=new_field)

    odb.save()
    odb.close()
