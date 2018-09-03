import sys
import os
import numpy as np
from math import sqrt, sin, cos, tan, acos, pi
try:
    import mesh
    from abaqus import *
    import assembly
    import section
    import step
    import mesh
    import interaction
    from abaqusConstants import COORDINATE, STANDALONE, ON, DEFORMABLE_BODY, AXISYM, OFF, THREE_D, DELETE, GEOMETRY
    from abaqusConstants import SINGLE, FIXED, SWEEP, MEDIAL_AXIS, DC3D8, DC3D6, C3D8, C3D6, STANDARD, ANALYSIS
    from abaqusConstants import PERCENTAGE, DOMAIN, DEFAULT
    from abaqus import backwardCompatibility
    backwardCompatibility.setValues(reportDeprecated=False)
except ImportError:
    print " ERROR: This script require Abaqus CAE to run"
    raise


class AsymmetricBendingSpecimen:
    def __init__(self, L=100, R=4.5, q=0, t=6, h=24, h1=8, CD=2, delta=0, name='BendingSpecimenPart'):
        """        
        :param L: Length of the specimen
        :param R: Radius of the main notch
        :param R: Radius of the transition between the smooth section and the notch 
        :param t: Thickness of specimen
        :param h: Height of specimen
        :param h1: Height at notch
        :param CD: Case layer, used for controlling mesh
        """

        self.L = float(L)
        self.R = float(R)
        self.t = float(t)
        self.h = float(h)
        self.h1 = float(h1)
        self.CD = float(CD)
        self.q = float(q)*pi/180
        self.delta = float(delta)

        # Create viewport for model creation
        if 'Carbon Toolbox Model' in session.viewports:
            self.viewPort = session.viewports['Carbon Toolbox Model']
        else:
            self.viewPort = session.Viewport(name='Carbon Toolbox Model')
        self.viewPort.makeCurrent()

        # Create new model object
        if 'Model-1' not in mdb.models:
            Mdb()
        self.modelDB = mdb.models['Model-1']
        self.modelDB.setValues(noPartsInputFile=ON)
        self.assembly = self.modelDB.rootAssembly

        session.journalOptions.setValues(replayGeometry=COORDINATE)

        def create_surface_profile(offset, sketch):
            # Creating the main notch
            r = self.R + offset
            p0 = (0+self.delta, self.h1/2 - offset)
            p1 = (r+self.delta, self.h1/2 + r - offset)
            p2 = (-r*cos(self.q)+self.delta, self.h1/2 + r*(1-sin(self.q)) - offset)
            sketch.Arc3Points(point1=p2, point2=p1, point3=p0)

            p3 = (r+self.delta, self.h/2 - offset)
            y = self. h/2 - offset - p2[1]
            p4 = (-y*tan(self.q)+self.delta - r*cos(self.q), self.h/2 - offset)
            sketch.Line(p2, p4)
            sketch.Line(p1, p3)

            p5 = (self.L/2, self.h/2 - offset)
            p6 = (-self.L/2, self.h/2 - offset)
            sketch.Line(p3, p5)
            sketch.Line(p4, p6)
            points = [p6, p4, p2, p0, p1, p3, p5]
            return points

        sketch_inner = self.modelDB.ConstrainedSketch(name='sketch_inner', sheetSize=800.0)
        sketch_inner.setPrimaryObject(option=STANDALONE)
        self.inner_line_points = create_surface_profile(self.CD, sketch_inner)
        sketch_inner.Line((-self.L/2, 0), self.inner_line_points[0])
        sketch_inner.Line((self.L/2, 0), self.inner_line_points[-1])
        sketch_inner.Line((-self.L/2, 0), (self.L/2, 0))

        inner_part = self.modelDB.Part(name='inner_pecimen', dimensionality=THREE_D, type=DEFORMABLE_BODY)
        inner_part.BaseSolidExtrude(sketch=sketch_inner, depth=self.t/2)
        sketch_inner.unsetPrimaryObject()
        sketch_outer = self.modelDB.ConstrainedSketch(name='sketch_outer', sheetSize=800.0)
        sketch_outer.sketchOptions.setValues(viewStyle=AXISYM)
        sketch_outer.setPrimaryObject(option=STANDALONE)

        create_surface_profile(self.CD, sketch_outer)
        self.outer_line_points = create_surface_profile(0., sketch_outer)

        sketch_outer.Line(self.inner_line_points[0], self.outer_line_points[0])
        sketch_outer.Line(self.inner_line_points[-1], self.outer_line_points[-1])

        outer_part = self.modelDB.Part(name='outer_pecimen', dimensionality=THREE_D, type=DEFORMABLE_BODY)
        outer_part.BaseSolidExtrude(sketch=sketch_outer, depth=self.t/2)
        sketch_inner.unsetPrimaryObject()
        # Create assembly and instances
        inner_instance_upper = self.assembly.Instance(name='Inner_specimen_upper', part=inner_part, dependent=OFF)
        outer_instance_upper = self.assembly.Instance(name='Outer_specimen_upper', part=outer_part, dependent=OFF)

        inner_instance_lower = self.assembly.Instance(name='Inner_specimen_lower', part=inner_part, dependent=OFF)
        outer_instance_lower = self.assembly.Instance(name='Outer_specimen_lower', part=outer_part, dependent=OFF)

        inner_instance_lower.rotateAboutAxis(axisPoint=(0., 0., self.t/4), axisDirection=(1, 0, 0), angle=180)
        outer_instance_lower.rotateAboutAxis(axisPoint=(0., 0., self.t/4), axisDirection=(1, 0, 0), angle=180)

        inner_instance_lower.rotateAboutAxis(axisPoint=(0., 0., self.t/4), axisDirection=(0, 1, 0), angle=180)
        outer_instance_lower.rotateAboutAxis(axisPoint=(0., 0., self.t/4), axisDirection=(0, 1, 0), angle=180)

        self.fatigue_part_instance = self.assembly.InstanceFromBooleanMerge(name=name,
                                                                            instances=(inner_instance_upper,
                                                                                       outer_instance_upper,
                                                                                       inner_instance_lower,
                                                                                       outer_instance_lower),
                                                                            keepIntersections=True,
                                                                            originalInstances=DELETE,
                                                                            domain=GEOMETRY)

        self.fatigue_part = self.modelDB.parts[self.fatigue_part_instance.partName]

    def mesh(self, analysis_type='ThermalDiffusion', case_direction_z='positive'):
        def nodes_on(objs):
            nodes = objs[0].getNodes()
            if len(objs) > 1:
                for obj in objs[1:]:
                    nodes = nodes+obj.getNodes()
            return nodes

        def elements_on(objs):
            elements = objs[0].getElements()
            if len(objs) > 1:
                for obj in objs[1:]:
                    elements = elements+obj.getElements()
            return elements

        mesh_parameters = {'N_case': 20, 'bias_case': 5, 'notch_elem_size': 0.15, 'length_elem_size': 2.}
        #  Partitioning the case layer

        def partition_using_points(points):
            faces = self.fatigue_part.faces
            edges = self.fatigue_part.edges
            face = faces.findAt(((points[0][0] + points[1][0])/2, (points[0][1] + points[1][1])/2, 0))
            up_edge = edges.findAt(coordinates=(self.L/2, self.h/2 - 0.00001, 0))
            partition_sketch = self.modelDB.ConstrainedSketch(name='partition1',
                                                              sheetSize=101.27, gridSpacing=2.53)
            # self.fatigue_part.projectReferencesOntoSketch(sketch=partition_sketch, filter=COPLANAR_EDGES)
            edge_pts = []
            for i in range(len(points)-1):
                partition_sketch.Line(points[i], points[i+1])
                edge_pts.append(((points[i][0]+points[i+1][0])/2, (points[i][1]+points[i+1][1])/2, 0.))

            self.fatigue_part.PartitionFaceBySketch(sketchUpEdge=up_edge,
                                                    faces=face, sketch=partition_sketch)
            edges = self.fatigue_part.edges
            sweep_path = edges.findAt((self.L/2, 0, self.t/4))
            cell = self.fatigue_part.cells.findAt((edge_pts[0][0], edge_pts[0][1], self.t/4))
            partition_edges = tuple([edges.findAt((p[0], p[1], 0)) for p in edge_pts])
            self.fatigue_part.PartitionCellBySweepEdge(sweepPath=sweep_path, cells=cell, edges=partition_edges)

        def get_edge_from_points(point1, point2, z_val):
            return self.fatigue_part.edges.findAt(((point1[0] + point2[0])/2, (point1[1] + point2[1])/2, z_val))

        center_line_points = [(-self.L/2, 0),
                              (self.inner_line_points[1][0] - self.inner_line_points[1][1]/sqrt(2), 0),
                              (self.inner_line_points[2][0] - self.inner_line_points[2][1]/sqrt(2), 0),
                              (0, 0),
                              (-self.inner_line_points[2][0] + self.inner_line_points[2][1]/sqrt(2), 0),
                              (-self.inner_line_points[1][0] + self.inner_line_points[1][1]/sqrt(2), 0),
                              (self.L/2, 0)]

        inner_line_lower = [(-p[0], -p[1]) for p in self.inner_line_points[::-1]]
        outer_line_lower = [(-p[0], -p[1]) for p in self.outer_line_points[::-1]]
        for (p1, p2, p3, p4, p5) in zip(self.outer_line_points[1:6], self.inner_line_points[1:6],
                                        center_line_points[1:6], inner_line_lower[1:6], outer_line_lower[1:6]):
            partition_using_points([p1, p2])
            partition_using_points([p2, p3])
            partition_using_points([p3, p4])
            partition_using_points([p4, p5])

        side1_edges, side2_edges = [], []
        length_edges = [[] for _ in range(3)]
        y_edges = []
        for z in [0., self.t / 2]:
            for edge_points in zip(self.inner_line_points+inner_line_lower, self.outer_line_points+outer_line_lower):
                edge = get_edge_from_points(edge_points[0], edge_points[1], z)
                # finding coordinates for the first point of the edge where the mesh should be dense
                outer_coords = self.fatigue_part.vertices[edge.getVertices()[0]].pointOn[0]
                if (outer_coords[0] - edge_points[1][0])**2 + (outer_coords[1] - edge_points[1][1])**2 < 1e-4:
                    side1_edges.append(edge)
                else:
                    side2_edges.append(edge)

            # Seeding the longitudinal edges in the notch
            for notch_r, x, y in zip([self.R, self.R, self.R + self.CD, self.R + self.CD],
                                     [self.delta, self.delta, -self.delta, -self.delta],
                                     [self.h1/2, self.h1/2-self.CD, -self.h1/2, -self.h1/2+self.CD]):
                length_edges[0].append(self.fatigue_part.edges.findAt((-notch_r*sin(1e-4)+x,
                                                                       y+notch_r*(1-cos(1e-4)),
                                                                       z)))
                length_edges[0].append(self.fatigue_part.edges.findAt((notch_r*sin(1e-4)+x,
                                                                       y+notch_r*(1-cos(1e-4)),
                                                                       z)))

            length_edges[0].append(self.fatigue_part.edges.findAt((1e-4, 0, z)))
            length_edges[0].append(self.fatigue_part.edges.findAt((-1e-4, 0, z)))

            for point_list in [self.outer_line_points, self.inner_line_points, center_line_points, inner_line_lower,
                               outer_line_lower]:
                length_edges[1].append(get_edge_from_points(point_list[1], point_list[2], z))
                length_edges[1].append(get_edge_from_points(point_list[4], point_list[5], z))

                length_edges[2].append(get_edge_from_points(point_list[0], point_list[1], z))
                length_edges[2].append(get_edge_from_points(point_list[5], point_list[6], z))

            for p1, p2 in zip(self.inner_line_points, center_line_points):
                y_edges.append(get_edge_from_points(p1, p2, z))
                y_edges.append(get_edge_from_points((p1[0], -p1[1]), (p2[0], -p2[1]), z))

        self.fatigue_part.seedEdgeByBias(biasMethod=SINGLE, end1Edges=tuple(side1_edges), end2Edges=tuple(side2_edges),
                                         number=mesh_parameters['N_case'], ratio=mesh_parameters['bias_case'],
                                         constraint=FIXED)

        sizes = [mesh_parameters['notch_elem_size'], 4*mesh_parameters['notch_elem_size'],
                 mesh_parameters['length_elem_size']]

        for edge_list, size in zip(length_edges, sizes):
            #  use the length of the first edge to calculate the number of elements
            n1 = int(edge_list[0].getSize()/size)
            self.fatigue_part.seedEdgeByNumber(edges=edge_list, number=n1, constraint=FIXED)
        number_elems = int(y_edges[6].getSize()/mesh_parameters['notch_elem_size'])
        self.fatigue_part.seedEdgeByNumber(edges=y_edges, number=number_elems, constraint=FIXED)

        # Seeding edges in the thickness direction
        # A thickness edge is an edge with the same x and y coordinates
        thickness_edges1 = []
        thickness_edges2 = []
        for e in self.fatigue_part.edges:
            idx1, idx2 = e.getVertices()
            p1 = self.fatigue_part.vertices[idx1].pointOn[0]
            p2 = self.fatigue_part.vertices[idx2].pointOn[0]
            if p1[0] == p2[0] and p1[1] == p2[1]:
                if p2[2] == 0:
                    thickness_edges1.append(e)
                else:
                    thickness_edges2.append(e)
        if case_direction_z == 'negative':
            thickness_edges1, thickness_edges2 = thickness_edges2, thickness_edges1
        self.fatigue_part.seedEdgeByBias(biasMethod=SINGLE, end1Edges=tuple(thickness_edges1),
                                         end2Edges=tuple(thickness_edges2),
                                         number=mesh_parameters['N_case'], ratio=mesh_parameters['bias_case'],
                                         constraint=FIXED)
        # Setting mesh controls for the "problematic" cell
        cell = self.fatigue_part.cells.findAt((1.01*self.inner_line_points[1][0], 0.9999*self.inner_line_points[1][1],
                                               self.t/4))
        self.fatigue_part.setMeshControls(regions=(cell,), technique=SWEEP, algorithm=MEDIAL_AXIS)

        if analysis_type == 'ThermalDiffusion':
            elem_type1 = mesh.ElemType(elemCode=DC3D8, elemLibrary=STANDARD)
            elem_type2 = mesh.ElemType(elemCode=DC3D6, elemLibrary=STANDARD)
        elif analysis_type == 'Mechanical':
            elem_type1 = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)
            elem_type2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)
        else:
            print " ERROR: The analysis types supported are: ThermalDiffusion or Mechanical"
            sys.exit(" ERROR: Method mesh of class cylinderSpecimenClass was called using incorrect argument, Exiting")

        self.fatigue_part.setElementType(regions=(self.fatigue_part.cells,), elemTypes=(elem_type1, elem_type2))
        self.fatigue_part.generateMesh()
        self.viewPort.setValues(displayedObject=self.fatigue_part)
        self.viewPort.view.fitView()

        # Creating necessary element sets
        # All Nodes
        self.fatigue_part.Set(nodes=self.fatigue_part.nodes[0:], name='All_Nodes')
        # Create element sets
        self.fatigue_part.Set(elements=self.fatigue_part.elements[0:], name='All_Elements')
        # Surface exposed to carbon
        exposed_face_list = [self.fatigue_part.faces.findAt((self.L/2-0.001, self.h/2, self.t/4)),
                             self.fatigue_part.faces.findAt((self.R*sin(0.01), self.h1/2 + self.R*(1-cos(0.01)),
                                                             self.t/2)),
                             self.fatigue_part.faces.findAt((self.R*sin(0.01), -self.h1/2-self.R * (1-cos(0.01)),
                                                             self.t/2)),
                             self.fatigue_part.faces.findAt((-self.L/2+0.001, self.h/2, self.t/4)),
                             self.fatigue_part.faces.findAt((self.L/2 - 0.001, -self.h / 2, self.t / 4)),
                             self.fatigue_part.faces.findAt((-self.L/2 + 0.001, -self.h / 2, self.t / 4)),
                             self.fatigue_part.faces.findAt((self.L/2, 0.001, self.t/4)),
                             self.fatigue_part.faces.findAt((-self.L/2, 0.001, self.t/4)),
                             self.fatigue_part.faces.findAt((0.001, 0.001, self.t/2))]

        exposed_faces = exposed_face_list[0].getFacesByFaceAngle(89.)
        for f in exposed_face_list[1:]:
            exposed_faces += f.getFacesByFaceAngle(89.)
        exposed_nodes = nodes_on(exposed_faces)
        exposed_elements = elements_on(exposed_faces)

        for x, name_x in zip([-1, 1], ['neg', 'pos']):
            for y, name_y in zip([-1, 1], ['neg', 'pos']):
                face = self.fatigue_part.faces.findAt((x*0.999*self.L/2, y*self.h/2, self.t/4))
                surface_faces = face.getFacesByFaceAngle(0.001)
                surface_name = 'X' + name_x + '_Y' + name_y + '_Surface'
                self.fatigue_part.Surface(side1Faces=surface_faces, name=surface_name)

        self.fatigue_part.Set(nodes=exposed_nodes, name='Exposed_Nodes')
        self.fatigue_part.Set(elements=exposed_elements, name='Exposed_Elements')
        self.fatigue_part.Surface(side1Faces=exposed_faces, name='Exposed_Surface')

        # Creating boundary condition sets
        sym_face = self.fatigue_part.faces.findAt(coordinates=(0.001, 0.001, 0.))
        sym_faces = sym_face.getFacesByFaceAngle(0.001)
        self.fatigue_part.Set(nodes=nodes_on(sym_faces), name='symZ_Nodes')
        self.fatigue_part.Set(elements=elements_on(sym_faces), name='symZ_Elements')
        self.fatigue_part.Surface(side1Faces=sym_faces, name='symZ_Surface')

        # Finding a suitable monitor node, surface node at the notch
        vertex = self.fatigue_part.vertices.findAt((self.delta, self.h1/2, 0))
        node = vertex.getNodes()[0]
        self.fatigue_part.Set(nodes=self.fatigue_part.nodes[node.label-1:node.label], name='Monitor_Node')

    def write_file(self, file_name):
        # Set filename and path
        output_file_name = os.path.basename(file_name)
        output_file_name_no_ext = output_file_name.split('.')[0]
        output_directory = os.path.dirname(file_name)

        # Set path as working directory
        if output_directory:
            os.chdir(output_directory)

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
        os.rename(os.path.join(output_directory, output_file_name_no_ext + '.inp'), file_name)


if __name__ == '__main__':
    specimen = AsymmetricBendingSpecimen()
    specimen.mesh()
    specimen.write_file('../MechanicalAnalysis/shear_bending_specimen.inc')
