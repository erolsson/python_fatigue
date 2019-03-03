import os
import sys

try:
    import mesh
    from abaqus import session, Mdb, mdb
    import assembly
    import section
    import step
    import mesh
    import interaction
    import regionToolset
    from abaqus import backwardCompatibility

    from abaqusConstants import OFF, ON, THREE_D, DISCRETE_RIGID_SURFACE, WHOLE_SURFACE, DISTRIBUTING, KINEMATIC
    backwardCompatibility.setValues(reportDeprecated=False)
except ImportError:
    print " ERROR: This script require Abaqus CAE to run"
    raise

from utmis_smooth.utmis_smooth_bending_specimen import SmoothBendingSpecimenClass
from utmis_notched.utmis_notched_bending_specimen import NotchedBendingSpecimenClass

simulation_directory = r'/scratch/users/erik/scania_gear_analysis/abaqus/utmis_specimens/'


specimen_name = sys.argv[-1]
specimen_types = {'notched': NotchedBendingSpecimenClass, 'smooth': SmoothBendingSpecimenClass}

spec = specimen_types[specimen_name]()
spec.modelDB.setValues(noPartsInputFile=OFF)
spec.mesh(analysis_type='Mechanical')
part1 = spec.fatigue_part
part2 = spec.make_part(part_name='mirror', flip=True)
spec.mesh(part=part2, flip=True, analysis_type='Mechanical')

mat = spec.modelDB.Material('Steel')
mat.Elastic(table=((200E3, 0.3), ))
sec = spec.modelDB.HomogeneousSolidSection(name='FatigueSpecimen1',
                                           material='Steel')

part1.SectionAssignment(region=(part1.cells,), sectionName='FatigueSpecimen1')
part2.SectionAssignment(region=(part2.cells,), sectionName='FatigueSpecimen1')

instance_1 = spec.modelDB.rootAssembly.Instance(name='part',   part=part1, dependent=ON)
instance_2 = spec.modelDB.rootAssembly.Instance(name='mirror', part=part2, dependent=ON)

instance_2.rotateAboutAxis(axisPoint=(0, 0, spec.thickness/4),
                           axisDirection=(1, 0, 0),
                           angle=180)

load_nodes = instance_1.sets['Exposed_Nodes'].nodes.getByBoundingBox(xMin=0.999*spec.load_position_x,
                                                                     xMax=1.001*spec.load_position_x,
                                                                     yMin=0.999*spec.height/2)

load_nodeset = spec.modelDB.rootAssembly.Set(name='loadNodes', nodes=load_nodes)

# Creating a "dummy" node for applying the loads
p = spec.modelDB.Part(name='Dummy node', dimensionality=THREE_D,
                      type=DISCRETE_RIGID_SURFACE)
p.ReferencePoint(point=(spec.load_position_x, spec.height, 0.0))
dummy_node_instance = spec.modelDB.rootAssembly.Instance(name='Dummy node', part=p, dependent=OFF)
reference_point = (dummy_node_instance.referencePoints[1],)
spec.load_node = regionToolset.Region(referencePoints=reference_point)
Load_region = regionToolset.Region(nodes=load_nodeset.nodes)
spec.modelDB.Coupling(name='Coupling loadNode',
                      controlPoint=spec.load_node,
                      surface=Load_region,
                      influenceRadius=WHOLE_SURFACE,
                      couplingType=KINEMATIC,
                      u1=OFF,
                      u3=OFF,
                      ur1=OFF,
                      ur2=OFF,
                      ur3=OFF)

spec.modelDB.DisplacementBC(name='load_node',
                            createStepName='Initial',
                            region=spec.load_node,
                            u1=0.0,
                            u3=0.0,
                            ur1=0.,
                            ur2=0,
                            ur3=0)

support_nodes = instance_2.sets['Exposed_Nodes'].nodes.getByBoundingBox(xMin=0.999*(spec.length/2-spec.R1),
                                                                        xMax=1.001*(spec.length/2-spec.R1),
                                                                        yMax=-0.999*spec.height/2)

support_nodeset = spec.modelDB.rootAssembly.Set(name='supportNodes', nodes=support_nodes)
support_region = regionToolset.Region(nodes=support_nodeset.nodes)
spec.modelDB.DisplacementBC(name='support',
                            createStepName='Initial',
                            region=support_region,
                            u2=0.0)

x_symmetry_region = regionToolset.Region(nodes=instance_1.sets['XSym_Nodes'].nodes +
                                         instance_2.sets['XSym_Nodes'].nodes)
spec.modelDB.DisplacementBC(name='XSym',
                            createStepName='Initial',
                            region=x_symmetry_region,
                            u1=0.0)

z_symmetry_region = regionToolset.Region(nodes=instance_1.sets['ZSym_Nodes'].nodes +
                                         instance_2.sets['ZSym_Nodes'].nodes)
spec.modelDB.DisplacementBC(name='ZSym',
                            createStepName='Initial',
                            region=z_symmetry_region,
                            u3=0.0)

spec.modelDB.StaticStep(name='MechanicalLoad',
                        previous='Initial',
                        nlgeom=ON)

# Tie the Ysym surfaces
spec.modelDB.Tie(name='Y0Plane',
                 master=instance_1.surfaces['YSym_Surface'],
                 slave=instance_2.surfaces['YSym_Surface'])

# The load, assuming unit nominal bending stress
wb = spec.notch_height**2*spec.thickness/6
P = wb/(spec.length/2 - spec.R1 - spec.load_position_x)/2
spec.modelDB.ConcentratedForce(name='Force',
                               createStepName='MechanicalLoad',
                               region=spec.load_node,
                               cf2=P)

if not os.path.isdir(simulation_directory):
    os.makedirs(simulation_directory)

os.chdir(simulation_directory)

job = mdb.Job(name='unit_load_' + specimen_name,
              model=spec.modelDB,
              numCpus=7,
              numDomains=7)
job.submit()
job.waitForCompletion()
