import os

from collections import namedtuple
from math import pi, sin, cos, ceil

try:
    import mesh
    from abaqus import *
    import section
    import step
    import mesh
    import interaction
    from abaqusConstants import AXISYM, STANDALONE, THREE_D, ANALYTIC_RIGID_SURFACE, CLOCKWISE, ON, OFF
    from abaqusConstants import DISCRETE_RIGID_SURFACE, WHOLE_SURFACE, KINEMATIC, FRICTIONLESS
    from abaqusConstants import FINITE, NODE_TO_SURFACE
    from abaqus import backwardCompatibility
    backwardCompatibility.setValues(reportDeprecated=False)
    import regionToolset as rT
except ImportError:
    print " ERROR: This script require Abaqus CAE to run"
    raise
from asymmetric_bending_specimen import AsymmetricBendingSpecimen


Roller = namedtuple('Roller', ['name', 'radius', 'x_coord', 'y_coord'])
SpecimenGeometry = namedtuple('SpecimenGeometry', ['L', 'R', 'q', 't', 'h', 'h1', 'CD', 'delta', 'name'])


def create_roller(specimen, roller_data):
    radius = roller_data.radius
    name = roller_data.name
    h = roller_data.y_coord
    b = roller_data.x_coord
    p1 = (0.0, radius)
    p2 = (-radius*sin(0.9*pi/2), radius*(1-cos(0.9*pi/2)))
    p3 = (radius*sin(0.9*pi/2), radius*(1-cos(0.9*pi/2)))

    # Create sketch 
    indenter_sketch = specimen.modelDB.ConstrainedSketch(name=name + '_sketch', sheetSize=800.0)
    indenter_sketch.sketchOptions.setValues(viewStyle=AXISYM)
    indenter_sketch.setPrimaryObject(option=STANDALONE)
    indenter_sketch.ConstructionLine(point1=(0.0, -400.0), point2=(0.0, 400.0))
    indenter_sketch.ArcByCenterEnds(point1=p3, point2=p2, center=p1, direction=CLOCKWISE)

    roller = specimen.modelDB.Part(name=name, dimensionality=THREE_D,
                                   type=ANALYTIC_RIGID_SURFACE)
    roller.AnalyticRigidSurfExtrude(sketch=indenter_sketch, depth=3*specimen.t)
    roller_instance = specimen.assembly.Instance(name=name, part=roller, dependent=ON)
    roller.Surface(side1Faces=roller.faces[0:1], name='surface')

    if h < 0:
        roller_instance.rotateAboutAxis(axisPoint=(0, 0, 0,), axisDirection=(0, 0, 1), angle=180)
    new_pos = (b, h, 0)
    roller_instance.translate(new_pos)
    roller.ReferencePoint((0, radius, 0.))
    ref_pt = roller_instance.referencePoints[roller_instance.referencePoints.keys()[0]]
    specimen.assembly.Set(name='ref_pt_' + name, referencePoints=(ref_pt,))


def perform_mechanical_analysis(specimen_geometry, delta, run_directory):
    Mdb()

    roller_radius = 10.
    overlap = 0.
    b2 = 48

    specimen = AsymmetricBendingSpecimen(**specimen_geometry)
    b1 = ceil(-specimen.outer_line_points[1][0])
    specimen.mesh('Mechanical')
    specimen_part = specimen.fatigue_part

    assembly = specimen.assembly
    model_db = specimen.modelDB

    # Creating two instances upper and lower for the mechanical analysis
    # Saving the previous instance name to delete it later

    # Assigning material
    mat = model_db.Material('Steel')
    mat.Elastic(table=((200E3, 0.3),))
    model_db.HomogeneousSolidSection(name='FatigueSpecimen1',
                                     material='Steel')
    specimen_part.SectionAssignment(region=(specimen_part.cells,), sectionName='FatigueSpecimen1')

    # Boundary condition for the symmetry plane
    model_db.DisplacementBC(name='sym_Z_BC', createStepName='Initial',
                            region=specimen.fatigue_part_instance.sets['symZ_Nodes'],
                            u3=0.0)
    center_node = specimen.fatigue_part.nodes.getByBoundingBox(xMin=-1e-3, xMax=1e-3,
                                                               yMin=-1e-3, yMax=1e-3,
                                                               zMin=-1e-3, zMax=1e-3)
    specimen.fatigue_part.Set(name='center_Node', nodes=center_node)
    model_db.DisplacementBC(name='center_point', createStepName='Initial',
                            region=specimen.fatigue_part_instance.sets['center_Node'],
                            u1=0.0)

    r1 = Roller(name='roller1_right', radius=roller_radius, x_coord=b1, y_coord=-specimen.h/2 + overlap)
    r2 = Roller(name='roller2_right', radius=roller_radius, x_coord=b2, y_coord=specimen.h/2 + overlap)
    r3 = Roller(name='roller1_left', radius=roller_radius, x_coord=-b1, y_coord=specimen.h/2 + overlap)
    r4 = Roller(name='roller2_left', radius=roller_radius, x_coord=-b2, y_coord=-specimen.h/2 + overlap)
    create_roller(specimen, r1)
    create_roller(specimen, r2)
    create_roller(specimen, r3)
    create_roller(specimen, r4)

    # Adding support boundary condition on the leftmost roller
    ref_points1_right = assembly.instances['roller1_right'].referencePoints
    ref_point1_right = ref_points1_right[ref_points1_right.keys()[0]]
    ref_points2_left = assembly.instances['roller2_left'].referencePoints
    ref_point2_left = ref_points2_left[ref_points2_left.keys()[0]]

    ref_points1_left = assembly.instances['roller1_left'].referencePoints
    ref_point1_left = ref_points1_left[ref_points1_left.keys()[0]]
    ref_points2_right = assembly.instances['roller2_right'].referencePoints
    ref_point2_right = ref_points2_right[ref_points2_right.keys()[0]]

    rT.Region(referencePoints=(ref_point1_right, ref_point2_left))

    assembly.Set(name='r1_right', referencePoints=(ref_point1_right,))
    assembly.Set(name='r2_left', referencePoints=(ref_point2_left,))

    assembly.Set(name='r1_left', referencePoints=(ref_point1_left,))
    assembly.Set(name='r2_right', referencePoints=(ref_point2_right,))

    # specimen.modelDB.Equation(name='inner_rollers', terms=((1., 'r1_right', 2), (1., 'r1_left', 2)))
    # specimen.modelDB.Equation(name='outer_rollers', terms=((1., 'r2_left', 2), (1., 'r2_right', 2)))
    # modelDB.DisplacementBC(name='support', createStepName='Initial', region=support_reg,
    #                       u1=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0)

    # load_reg1 = rT.Region(referencePoints=(ref_point1_left,))
    # load_reg2 = rT.Region(referencePoints=(ref_point2_right,))

    load_step = model_db.StaticStep(name='load', previous='Initial', initialInc=1e-2, minInc=1e-12, nlgeom=OFF)

    load_step.control.setValues(allowPropagation=OFF,
                                lineSearch=(40.0, 1.0, 0.0001, 0.25, 0.1),
                                resetDefaultValues=OFF)
    # Creating a "dummy" node for applying the loads
    p = model_db.Part(name='DummyNodeU', dimensionality=THREE_D,
                      type=DISCRETE_RIGID_SURFACE)
    p.ReferencePoint(point=(0.0, specimen.h/2 + roller_radius, 0.0))
    dummy_instance = model_db.rootAssembly.Instance(name='DummyNodeUpper', part=p, dependent=OFF)
    rp_upper = (dummy_instance.referencePoints[1],)

    p = model_db.Part(name='DummyNodeL', dimensionality=THREE_D,
                      type=DISCRETE_RIGID_SURFACE)
    p.ReferencePoint(point=(0.0, -specimen.h/2 - roller_radius, 0.0))
    dummy_instance = model_db.rootAssembly.Instance(name='DummyNodeLower', part=p, dependent=OFF)
    rp_lower = (dummy_instance.referencePoints[1],)

    control_region_upper = model_db.rootAssembly.Set(referencePoints=rp_upper, name='upperControlNode')
    control_region_lower = model_db.rootAssembly.Set(referencePoints=rp_lower, name='lowerControlNode')

    coupled_region_upper = model_db.rootAssembly.Set(referencePoints=(ref_point1_left, ref_point2_right),
                                                     name='upperCoupledRegion')
    coupled_region_lower = model_db.rootAssembly.Set(referencePoints=(ref_point2_left, ref_point1_right),
                                                     name='lowerCoupledRegion')
    model_db.Coupling(name='couplingUpper', controlPoint=control_region_upper,
                      surface=coupled_region_upper, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC,
                      u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

    model_db.Coupling(name='couplingLower', controlPoint=control_region_lower,
                      surface=coupled_region_lower, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC,
                      u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

    model_db.DisplacementBC(name='lower_support', createStepName='Initial', region=control_region_lower,
                            u1=0.0, u2=0, u3=0.0, ur1=0.0, ur2=0.0)

    model_db.DisplacementBC(name='upper_support', createStepName='Initial', region=control_region_upper,
                            u1=0.0, u3=0.0, ur1=0.0, ur2=0.0)

    model_db.DisplacementBC(name='upper_load', createStepName='load', region=control_region_upper,
                            u2=-delta)

    # modelDB.ConcentratedForce(name='upper_load', createStepName='load', region=control_region_upper, cf2=-load)
    # Contact between the rollers and the exposed surface
    comp = model_db.ContactProperty('cProp')
    comp.TangentialBehavior(formulation=FRICTIONLESS)
    model_db.SurfaceToSurfaceContactStd(name='c1',
                                        createStepName='Initial',
                                        master=assembly.instances['roller1_right'].surfaces['surface'],
                                        slave=specimen.fatigue_part_instance.surfaces['Xpos_Yneg_Surface'],
                                        sliding=FINITE,
                                        interactionProperty='cProp',
                                        enforcement=NODE_TO_SURFACE)

    model_db.SurfaceToSurfaceContactStd(name='c2',
                                        createStepName='Initial',
                                        master=assembly.instances['roller2_right'].surfaces['surface'],
                                        slave=specimen.fatigue_part_instance.surfaces['Xpos_Ypos_Surface'],
                                        sliding=FINITE,
                                        interactionProperty='cProp',
                                        enforcement=NODE_TO_SURFACE)

    model_db.SurfaceToSurfaceContactStd(name='c3',
                                        createStepName='Initial',
                                        master=assembly.instances['roller1_left'].surfaces['surface'],
                                        slave=specimen.fatigue_part_instance.surfaces['Xneg_Ypos_Surface'],
                                        sliding=FINITE,
                                        interactionProperty='cProp',
                                        enforcement=NODE_TO_SURFACE)

    model_db.SurfaceToSurfaceContactStd(name='c4',
                                        createStepName='Initial',
                                        master=assembly.instances['roller2_left'].surfaces['surface'],
                                        slave=specimen.fatigue_part_instance.surfaces['Xneg_Yneg_Surface'],
                                        sliding=FINITE,
                                        interactionProperty='cProp',
                                        enforcement=NODE_TO_SURFACE)
    if not os.path.isdir(run_directory):
        os.makedirs(run_directory)
    os.chdir(run_directory)
    job = mdb.Job(name='mechanical_analysis',
                  model=model_db,
                  numCpus=8,
                  numDomains=8)

    job.submit()
    job.waitForCompletion()
