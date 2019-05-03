import sys
import os
from math import sqrt, sin, cos, pi
try:
    import mesh
    from abaqus import session, Mdb, mdb
    import assembly
    import section
    import step
    import mesh
    import interaction
    from abaqusConstants import COORDINATE, STANDALONE, ON, DEFORMABLE_BODY, AXISYM, OFF, THREE_D, DELETE, GEOMETRY
    from abaqusConstants import SINGLE, FIXED, SWEEP, MEDIAL_AXIS, DC3D8, DC3D6, C3D8, C3D6, STANDARD, ANALYSIS
    from abaqusConstants import PERCENTAGE, DOMAIN, DEFAULT, INDEX, YZPLANE, XYPLANE
    from abaqus import backwardCompatibility
    backwardCompatibility.setValues(reportDeprecated=False)
except ImportError:
    print " ERROR: This script require Abaqus CAE to run"
    raise


class NotchedBendingSpecimenClass:
    def __init__(self, t=1.2, load_position_x=15):
        self.length = float(90)
        self.R = float(0.9)
        self.R1 = float(5.5)
        self.R2 = float(0.5)
        self.notch_height = float(5)
        self.height = float(11.)
        self.thickness = float(4.)
        self.case_mesh_thickness = float(t)
        self.load_position_x = float(load_position_x)
        self.my_part_inner = None
        self.my_part_outer = None
        self.fatigue_part = None

        # Create viewport for model creation
        if 'Carbon Toolbox Model' not in session.viewports:
            self.viewPort = session.Viewport(name='Carbon Toolbox Model')
        else:    
            self.viewPort = session.viewports['Carbon Toolbox Model']
        self.viewPort.makeCurrent()
        
        # Create new model object
        Mdb()
        self.modelDB = mdb.models['Model-1']
        self.modelDB.setValues(noPartsInputFile=ON)
        self.myAssembly = self.modelDB.rootAssembly

        # Set replay file output format to INDEX for readability
        session.journalOptions.setValues(replayGeometry=INDEX)
        self.x = self.R * sqrt(3) / 2
        self.y = self.notch_height / 2 + self.R / 2

        self.make_part()

    def make_part(self, part_name='fatiguePart', flip=False, analysis_type='ThermalDiffusion'):

        def make_profile(d, profile_name):
            p0 = (0., 0.)
            p1 = (0, self.notch_height/2 - d)
            p2 = (self.R*sqrt(3)/2, self.notch_height/2 + self.R/2 - d)

            x2 = p2[0] + 1./sqrt(3)*(self.height/2 - p2[1] - d)
            p3 = (x2, self.height/2 - d)
            p4 = (self.length/2 - self.R1, self.height/2 - d)
            p5 = (self.length/2 - d, 0.)

            # Create sketch :InnerSpecimen
            my_sketch = self.modelDB.ConstrainedSketch(name=profile_name, sheetSize=800.0)
            g, v = my_sketch.geometry, my_sketch.vertices
            my_sketch.Line(point1=p0, point2=p1)
            my_sketch.ArcByStartEndTangent(point1=p1, point2=p2, vector=(1., 0))
            my_sketch.Line(point1=p2, point2=p3)
            my_sketch.Line(point1=p3, point2=p4)

            my_sketch.ArcByStartEndTangent(point1=p4, point2=p5, vector=(1., 0))
            my_sketch.Line(point1=p5, point2=p0)

            # fixing the fillet
            e1 = g.findAt(((p2[0] + p3[0])/2, (p2[1] + p3[1])/2))
            e2 = g.findAt(((p3[0] + p4[0])/2, self.height/2 - d))
            my_sketch.FilletByRadius(radius=self.R2,
                                     curve1=e1,
                                     nearPoint1=e1.pointOn,
                                     curve2=e2,
                                     nearPoint2=e2.pointOn)

            # finding the x-coordinates of the fillet points
            # Warning the points are chosen manually
            self.x2 = v[8].coords[0]
            self.y2 = v[8].coords[1]
            self.x3 = v[12].coords[0]

            part = mdb.models['Model-1'].Part(name=profile_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
            part.BaseSolidExtrude(sketch=my_sketch, depth=self.thickness / 2)
            return part

        self.my_part_inner = make_profile(self.case_mesh_thickness, 'inner')
        instance_inner = self.myAssembly.Instance(name='InnerSpecimen', part=self.my_part_inner, dependent=OFF)
        self.my_part_outer = make_profile(0., 'outer')
        instance_outer = self.myAssembly.Instance(name='OuterSpecimen', part=self.my_part_outer, dependent=OFF)

        # Create instance from merge of parts
        self.fatigue_part = self.modelDB.rootAssembly.PartFromBooleanMerge(name=part_name,
                                                                           instances=(instance_inner, instance_outer),
                                                                           keepIntersections=True)
        del self.modelDB.rootAssembly.features['InnerSpecimen']
        del self.modelDB.rootAssembly.features['OuterSpecimen']
        del self.modelDB.parts['inner']
        del self.modelDB.parts['outer']

        datum_plane_vertical1 = self.fatigue_part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=self.x)
        self.fatigue_part.PartitionCellByDatumPlane(datumPlane=self.fatigue_part.datum[datum_plane_vertical1.id],
                                                    cells=self.fatigue_part.cells)

        datum_plane_vertical2 = self.fatigue_part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=self.x2)
        self.fatigue_part.PartitionCellByDatumPlane(datumPlane=self.fatigue_part.datum[datum_plane_vertical2.id],
                                                    cells=self.fatigue_part.cells)

        datum_plane_vertical3 = self.fatigue_part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=self.x3)
        self.fatigue_part.PartitionCellByDatumPlane(datumPlane=self.fatigue_part.datum[datum_plane_vertical3.id],
                                                    cells=self.fatigue_part.cells)

        datum_plane_vertical4 = self.fatigue_part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE,
                                                                             offset=self.length/2 - self.R1)
        self.fatigue_part.PartitionCellByDatumPlane(datumPlane=self.fatigue_part.datum[datum_plane_vertical4.id],
                                                    cells=self.fatigue_part.cells)

        datum_plane_vertical5 = self.fatigue_part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE,
                                                                             offset=self.load_position_x)
        self.fatigue_part.PartitionCellByDatumPlane(datumPlane=self.fatigue_part.datum[datum_plane_vertical5.id],
                                                    cells=self.fatigue_part.cells)

        offset = 1.3
        if flip:
            offset = self.thickness/2 - 1.3
        datum_plane_vertical6 = self.fatigue_part.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,
                                                                             offset=offset)
        self.fatigue_part.PartitionCellByDatumPlane(datumPlane=self.fatigue_part.datum[datum_plane_vertical6.id],
                                                    cells=self.fatigue_part.cells)

        return self.fatigue_part

    def mesh(self, part=None, flip=False, analysis_type='ThermalDiffusion'):
        if part is None:
            part = self.fatigue_part
        
        nr = 25
        nx1 = 20      # x - dir closest to the notch
        nx2 = 20      # x - dir second to the notch
        n_fillet = 2  # filletRadius
        n_height = 10
        size_length_direction = 2
        n_radius = 10

        # ----------------------------------------------------------------
        def nodes_on(objs):
            nodes = objs[0].getNodes()
            if len(objs) > 1:
                for obj in objs[1:]:
                    nodes = nodes+obj.getNodes()
            return nodes
        # ----------------------------------------------------------------

        def elements_on(objs):
            elements = objs[0].getElements()
            if len(objs) > 1:
                for obj in objs[1:]:
                    elements = elements+obj.getElements()
            return elements
        # ----------------------------------------------------------------

        def edges_direction_part(part_object=None, edges_to_sort=None):
            case_edges_pos = []
            case_edges_neg = []
            for edge in edges_to_sort:
                v1, v2 = edge.getVertices()
                point_1 = part_object.vertices[v1].pointOn
                point_2 = part_object.vertices[v2].pointOn
                vector = [point_2[0][0]-point_1[0][0], point_2[0][1]-point_1[0][1], point_2[0][2]-point_1[0][2]]
                if (vector[0] < 0) or (vector[1] < 0) or (vector[2] < 0):
                    case_edges_pos.append(edge)
                else:
                    case_edges_neg.append(edge)
            return case_edges_pos, case_edges_neg
        # ----------------------------------------------------------------

        if analysis_type == 'ThermalDiffusion':
            elem_type1 = mesh.ElemType(elemCode=DC3D8, elemLibrary=STANDARD)
            elem_type2 = mesh.ElemType(elemCode=DC3D6, elemLibrary=STANDARD)
        elif analysis_type == 'Mechanical':
            elem_type1 = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)
            elem_type2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)
        else:    
            print " ERROR: The analysis types supported are: ThermalDiffusion or Mechanical"
            sys.exit(" ERROR: Method mesh of class cylinderSpecimenClass was called using incorrect argument, Exiting")

        # Assign element type       
        part.setElementType(regions=(part.cells,), elemTypes=(elem_type1, elem_type2))
        
        # Edges in the hardness gradient
        # y-coord key, data x-coords
        xy = {self.notch_height/2 - self.case_mesh_thickness/2:   [0.],
              self.y - self.case_mesh_thickness/2:                [self.x],
              self.y2 - self.case_mesh_thickness/2:               [self.x2],
              self.height/2 - self.case_mesh_thickness/2:         [self.x3, self.load_position_x, self.length / 2 - self.R1],
              0.:                                                 [self.length/2 - self.case_mesh_thickness/2]}
        z_line = 1.3
        if flip:
            z_line = self.thickness/2 - 1.3

        z_coordinates = [0, z_line, self.thickness/2]
        edges = []
        for y, x_coordinates in xy.iteritems():
            for x in x_coordinates:
                for z in z_coordinates:
                    edges.append(part.edges.findAt((x, y, z)))

        edges1, edges2 = edges_direction_part(self.fatigue_part, edges)
        part.seedEdgeByBias(biasMethod=SINGLE, 
                            end1Edges=edges1,
                            end2Edges=edges2,
                            number=nr,
                            ratio=10,
                            constraint=FIXED)

        # Edges in the z-direction
        z = 1.9
        if flip:
            z = 0.1
        x_coordinates = [0, self.x, self.x2, self.x3, self.load_position_x, self.length / 2 - self.R1]
        y_coordinates = [self.notch_height/2, self.y, self.y2, self.height/2, self.height/2, self.height/2]
        edges = []
        for i, x in enumerate(x_coordinates):
            edges.append(part.edges.findAt((x, 0,                                           z)))
            edges.append(part.edges.findAt((x, y_coordinates[i] - self.case_mesh_thickness, z)))
            edges.append(part.edges.findAt((x, y_coordinates[i],                            z)))

        edges.append(part.edges.findAt((self.length / 2, 0, z)))
        edges1, edges2 = edges_direction_part(self.fatigue_part, edges)

        if flip is True:
            edges2, edges1 = edges1, edges2
        part.seedEdgeByBias(biasMethod=SINGLE, 
                            end1Edges=edges1,
                            end2Edges=edges2,
                            number=25,
                            ratio=20,
                            constraint=FIXED)

        # Edges in the z-direction
        z = 0.1
        if flip:
            z = 1.9
        x_coordinates = [0, self.x, self.x2, self.x3, self.load_position_x, self.length / 2 - self.R1]
        y_coordinates = [self.notch_height/2, self.y, self.y2, self.height/2, self.height/2, self.height/2]
        edges = []
        for i, x in enumerate(x_coordinates):
            edges.append(part.edges.findAt((x, 0,                                           z)))
            edges.append(part.edges.findAt((x, y_coordinates[i] - self.case_mesh_thickness, z)))
            edges.append(part.edges.findAt((x, y_coordinates[i],                            z)))

        edges.append(part.edges.findAt((self.length / 2, 0, z)))

        part.seedEdgeByNumber(edges=edges,
                              number=5,
                              constraint=FIXED)

        # Seeding the notch
        num = [nx1, nx2, n_fillet]
        x_coordinates = [self.R*sin(15*pi/180), (self.x2 + self.x)/2, self.x3 - self.R2*sin(1E-3)]
        y_coordinates = [self.notch_height / 2 + self.R*(1 - cos(15*pi/180)),
                         (self.y2 + self.y) / 2,
                         self.height/2 - self.R2 * (1 - cos(1E-3))]
        for x, y, n in zip(x_coordinates, y_coordinates, num):
            edges = []
            for z in z_coordinates:
                edges.append(part.edges.findAt((x, 0,                            z)))
                edges.append(part.edges.findAt((x, y - self.case_mesh_thickness, z)))
                edges.append(part.edges.findAt((x, y,                            z)))

            part.seedEdgeByNumber(edges=edges,
                                  number=n)

        # Mid section
        x_coordinates = [self.load_position_x + (self.length / 2 - self.R1) / 2, (self.x + self.load_position_x) / 2]
        y_coordinates = [0, self.height/2 - self.case_mesh_thickness, self.height/2]
        edges = []
        for x in x_coordinates:
            for y in y_coordinates:
                for z in z_coordinates:
                    edges.append(part.edges.findAt((x, y, z)))

        part.seedEdgeBySize(edges=edges,
                            size=size_length_direction)

        # Vertical edges
        x_coordinates = [0, self.x, self.x2, self.x3, self.load_position_x, self.length / 2 - self.R1]
        y = 0.001*self.height/2
        edges = []
        for x in x_coordinates:
            for z in z_coordinates:
                edges.append(part.edges.findAt((x, y, z)))
        edges.append(part.edges.findAt((self.length/2 - self.R1/2, 0, 0)))
        edges.append(part.edges.findAt((self.length/2 - self.R1/2, 0, self.thickness/2)))
        part.seedEdgeByNumber(edges=edges,
                              number=n_height,
                              constraint=FIXED)

        # Outermost radius
        x0 = self.length / 2 - self.R1
        radius = [self.R1, self.R1 - self.case_mesh_thickness]
        edges = []
        
        for r in radius:
            for z in z_coordinates:
                edges.append(part.edges.findAt((x0+r/sqrt(2), r/sqrt(2), z)))

        part.seedEdgeByNumber(edges=edges,
                              number=n_radius,
                              constraint=FIXED)
        # Mesh assembly
        part.generateMesh(seedConstraintOverride=OFF)
        self.viewPort.setValues(displayedObject=part)
        self.viewPort.view.fitView()

        # Create sets and surfaces
        #    All_Nodes
        part.Set(nodes=part.nodes[0:], name='All_Nodes')
        #    Create element sets
        part.Set(elements=part.elements[0:], name='All_Elements')
        z1 = self.thickness/2
        z2 = 0
        if flip is True:
            z1, z2 = z2, z1
        #       - Exposed Elements and Nodes
        #              Pick surface on arc at failure point
        f1 = part.faces.findAt((1.001*self.x3, self.height/2, self.thickness/4))
        f2 = part.faces.findAt((1.001*self.x3, self.height/4, z1))
        #              Pick connected faces by angle
        exposed_faces = f1.getFacesByFaceAngle(89) + f2.getFacesByFaceAngle(0)
        #              Get elements and nodes connected to selected faces
        exposed_nodes = nodes_on(exposed_faces)
        exposed_elements = elements_on(exposed_faces)
        #              Create sets on part
        part.Set(nodes=exposed_nodes, name='Exposed_Nodes')
        part.Set(elements=exposed_elements, name='Exposed_Elements')
        #              Create surface
        part.Surface(side1Faces=exposed_faces, name='Exposed_Surface')

        # Symmetry planes
        f = part.faces.findAt((0., self.notch_height/4, self.thickness/4))
        x_sym_faces = f.getFacesByFaceAngle(0)
        x_sym_nodes = nodes_on(x_sym_faces)
        x_sym_elements = elements_on(x_sym_faces)
        part.Set(nodes=x_sym_nodes, name='XSym_Nodes')
        part.Set(elements=x_sym_elements, name='XSym_Elements')
        part.Surface(side1Faces=x_sym_faces, name='XSym_Surface')

        f = part.faces.findAt((1.001*self.x3, 0, self.thickness/4))
        y_sym_faces = f.getFacesByFaceAngle(1)
        y_sym_nodes = nodes_on(y_sym_faces)
        y_sym_elements = elements_on(y_sym_faces)
        part.Set(nodes=y_sym_nodes, name='YSym_Nodes')
        part.Set(elements=y_sym_elements, name='YSym_Elements')
        part.Surface(side1Faces=y_sym_faces, name='YSym_Surface')

        f = part.faces.findAt((1.001 * self.x3, self.height/4, z2))
        z_sym_faces = f.getFacesByFaceAngle(0)
        z_sym_nodes = nodes_on(z_sym_faces)
        z_sym_elements = elements_on(z_sym_faces)
        part.Set(nodes=z_sym_nodes, name='ZSym_Nodes')
        part.Set(elements=z_sym_elements, name='ZSym_Elements')
        part.Surface(side1Faces=z_sym_faces, name='ZSym_Surface')

        #       - Monitor node
        monitor_vertex = part.vertices.findAt((0., self.notch_height/2, 0), )
        monitor_vertex_nodes = monitor_vertex.getNodes()
        monitor_node = monitor_vertex_nodes[0].label-1
        part.Set(nodes=part.nodes[monitor_node:monitor_node+1], name='Monitor_Node')

        load_nodes = part.nodes.getByBoundingBox(xMin=self.load_position_x - 1e-8,
                                                 xMax=self.load_position_x + 1e-8,
                                                 yMin=self.height/2 - 1e-8)
        part.Set(nodes=load_nodes, name='load_nodes')

        support_nodes = part.nodes.getByBoundingBox(xMin=self.length/2 - self.R1 - 1e-8,
                                                    xMax=self.length/2 - self.R1 + 1e-8,
                                                    yMin=self.height/2 - 1e-8)
        part.Set(nodes=support_nodes, name='support_nodes')

        session.viewports['Carbon Toolbox Model'].maximize()
        print " Mesh generation completed"

    def change_analysis_type(self, analysis_type='Mechanical'):
        """
        Method to change the analysis type by changing the element type
        """
        # Assign mesh control        Mesh on PART (NOT INSTANCE)
        if analysis_type == 'ThermalDiffusion':
            elem_type1 = mesh.ElemType(elemCode=DC3D8, elemLibrary=STANDARD)
            elem_type2 = mesh.ElemType(elemCode=DC3D6, elemLibrary=STANDARD)
        elif analysis_type == 'Mechanical':
            elem_type1 = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)
            elem_type2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)
            
        else: 
            print " ERROR: The analysis types supported are: ThermalDiffusion or Mechanical"
            sys.exit(" ERROR: Method mesh of class cylinderSpecimenClass was called using incorrect argument, Exiting")

        # Assign element type       
        self.myAssembly.setElementType(regions=(self.fatigue_part.cells,), elemTypes=(elem_type1, elem_type2))
      
    def write_file(self, file_name):
        
        # Set filename and path
        output_file_name = os.path.basename(file_name)
        output_file_name_no_ext = output_file_name.split('.')[0]
        output_directory = os.path.dirname(file_name)

        # Set path as working directory
        if output_directory:
            os.chdir(output_directory)

        self.myAssembly.Instance(name='Specimen', part=self.fatigue_part, dependent=ON)

        # Create job
        mdb.Job(name=output_file_name_no_ext, model=self.modelDB, description='', type=ANALYSIS,
                atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
                memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
                modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                scratch='', parallelizationMethodExplicit=DOMAIN, numDomains=1,
                activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=1)
        
        # Write job to file
        mdb.jobs[output_file_name_no_ext].writeInput(consistencyChecking=OFF)
        # Remove job
        del mdb.jobs[output_file_name_no_ext]
        
        # Fix file name

        if os.path.exists(os.path.abspath(file_name)):
            os.remove(os.path.abspath(file_name))
        os.rename(os.path.join(output_directory, output_file_name_no_ext+'.inp'), file_name)

    # Function by erolssson
    def mechanical_material_assignment(self, part_name='fatiguePart'):
        part = self.modelDB.parts[part_name]
        mat = self.modelDB.Material('Steel')
        mat.Elastic(table=((200E3, 0.3),))
        self.modelDB.HomogeneousSolidSection(name='FatigueSpecimen-1', material='steel')
        part = part
        part.SectionAssignment(region=(part.elements,), sectionName='FatigueSpecimen-1')


if __name__ == "__main__":
    m = NotchedBendingSpecimenClass()
    m.mesh(analysis_type='Mechanical')
    m.mechanical_material_assignment()
    m.write_file('utmis_notched.inc')
