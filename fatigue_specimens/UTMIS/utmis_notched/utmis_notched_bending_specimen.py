from __future__ import print_function, division

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
    from abaqusConstants import PERCENTAGE, DOMAIN, DEFAULT, INDEX, YZPLANE, XYPLANE, LEFT, SIDE1, REVERSE, NUMBER
    from abaqusConstants import HEX_DOMINATED, FORWARD
    from abaqus import backwardCompatibility
    backwardCompatibility.setValues(reportDeprecated=False)
except ImportError:
    print(" ERROR: This script require Abaqus CAE to run")
    raise

import numpy as np


class NotchedBendingSpecimenClass:
    def __init__(self, t=0.8, load_position_x=15):
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
        session.journalOptions.setValues(replayGeometry=COORDINATE)
        self.x = self.R * sqrt(3) / 2
        self.y = self.notch_height / 2 + self.R / 2

        self.make_part()

    def make_part(self, part_name='fatiguePart', analysis_type='ThermalDiffusion'):

        def make_profile(d, profile_name):
            p0 = (0., 0.)
            p1 = (0, self.notch_height/2 - d)
            q = pi/3
            p2 = ((self.R+d)*sin(q), (self.notch_height/2 - d) + (self.R+d)*(1 - cos(q)))

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

        def edge_is_curve(edge):
            try:
                edge.getRadius()
            except AbaqusException:
                return True
            return False

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

        v1 = self.fatigue_part.vertices.findAt((self.R*sqrt(3)/2, self.notch_height/2 + self.R/2, 0))
        v2 = self.fatigue_part.vertices.findAt((self.R*sqrt(3)/2, self.notch_height/2 + self.R/2, self.thickness/2))
        R = self.R + self.case_mesh_thickness
        v3 = self.fatigue_part.vertices.findAt((R*sqrt(3)/2,
                                                (self.notch_height/2 - self.case_mesh_thickness) + R/2,
                                                0.))
        plane1 = self.fatigue_part.DatumPlaneByThreePoints(point1=v1, point2=v2, point3=v3)
        cell_point = (1e-6, self.notch_height/2 - 1e-6, 1e-6)
        self.fatigue_part.PartitionCellByDatumPlane(datumPlane=self.fatigue_part.datum[plane1.id],
                                                    cells=self.fatigue_part.cells.findAt(cell_point))

        faces_to_partition = self.fatigue_part.faces.findAt(((1e-6, 1e-6, 2.),))
        up_edge = self.fatigue_part.edges.findAt((0, 1e-6, 2.))
        t = self.fatigue_part.MakeSketchTransform(sketchPlane=faces_to_partition[0],
                                                  sketchUpEdge=up_edge,
                                                  sketchPlaneSide=SIDE1,
                                                  sketchOrientation=LEFT,
                                                  origin=(0.0, 0.0, 2.0))
        partition_sketch = self.modelDB.ConstrainedSketch(name="partition_sketch_1", sheetSize=800.0, transform=t)
        q = pi/3
        p1 = ((self.R+self.case_mesh_thickness)*sin(q),
              (self.notch_height/2 - self.case_mesh_thickness) + (self.R+self.case_mesh_thickness)*(1 - cos(q)))
        r = p1[1]/sin(pi/3)
        x = p1[1]/tan(pi/3)
        center_point = (p1[0] - x, 0)
        p2 = (center_point[0] + r, 0)
        partition_sketch.ArcByCenterEnds(center=center_point, point1=p2, point2=p1)

        self.fatigue_part.PartitionFaceBySketch(sketchUpEdge=up_edge,
                                                faces=faces_to_partition, sketch=partition_sketch,
                                                sketchOrientation=LEFT)
        picked_edges = self.fatigue_part.edges.findAt(coordinates=(center_point[0] + r*cos(1e-6), r*sin(1e-6), 2.0))
        self.fatigue_part.PartitionCellByExtrudeEdge(line=self.fatigue_part.edges.findAt(coordinates=(0.0, 0.0, 0.5)),
                                                     cells=self.fatigue_part.cells.findAt(((1e-6, 1e-6, 1e-6),)),
                                                     edges=(picked_edges, ), sense=REVERSE)

        # Creating the next partitioning plane in the same way with three points
        # Finding the first point using the diagonal edge from the previous plane
        diagonal_edge = None
        v0 = self.fatigue_part.vertices.findAt((p1[0], p1[1], 0.))
        for edge_idx in v0.getEdges():
            edge = self.fatigue_part.edges[edge_idx]
            if edge.pointOn[0][2] == 0 and edge_is_curve(edge):
                diagonal_edge = edge
        v1 = None
        for v_idx in diagonal_edge.getVertices():
            if v_idx != v0.index:
                v1 = self.fatigue_part.vertices[v_idx]
        v1_coordinates = v1.pointOn[0]

        plane2 = self.fatigue_part.DatumPlaneByOffset(plane=self.fatigue_part.datum[plane1.id], point=v1)
        self.fatigue_part.PartitionCellByDatumPlane(datumPlane=self.fatigue_part.datum[plane2.id],
                                                    cells=self.fatigue_part.cells.findAt(((self.length/4,
                                                                                           self.height/2 - 1e-6,
                                                                                           1e-6), )))

        faces_to_partition = self.fatigue_part.faces.findAt(((self.length/4, 1e-6, 2.),))
        up_edge = self.fatigue_part.edges.findAt((0, 1e-6, 2.))
        t = self.fatigue_part.MakeSketchTransform(sketchPlane=faces_to_partition[0],
                                                  sketchUpEdge=up_edge,
                                                  sketchPlaneSide=SIDE1,
                                                  sketchOrientation=LEFT,
                                                  origin=(0.0, 0.0, 2.0))
        partition_sketch = self.modelDB.ConstrainedSketch(name="partition_sketch_2", sheetSize=800.0, transform=t)
        p1 = (v1_coordinates[0], v1_coordinates[1])
        r = p1[1]/sin(pi/3)
        x = p1[1]/tan(pi/3)
        center_point = (p1[0] - x, 0)
        p2 = (center_point[0] + r, 0)
        partition_sketch.ArcByCenterEnds(center=center_point, point1=p2, point2=p1)

        self.fatigue_part.PartitionFaceBySketch(sketchUpEdge=up_edge,
                                                faces=faces_to_partition, sketch=partition_sketch,
                                                sketchOrientation=LEFT)
        picked_edges = self.fatigue_part.edges.findAt(coordinates=(center_point[0] + r*cos(1e-6), r*sin(1e-6), 2.0))
        direction = self.fatigue_part.edges.findAt(coordinates=(self.length/2 - self.case_mesh_thickness, 0.0, 1.0))
        cell = self.fatigue_part.cells.findAt(((self.length/4, 1e-6, 1e-6),))
        self.fatigue_part.PartitionCellByExtrudeEdge(line=direction,
                                                     cells=cell,
                                                     edges=(picked_edges,), sense=REVERSE)

        # Find the length of the next two outer edges
        # The common face
        face = self.fatigue_part.faces.findAt((self.length/4, self.height/2 - 1e-6, 2.))
        vertices = [self.fatigue_part.vertices[vertex_id] for vertex_id in face.getVertices()]
        vertices.sort(key=lambda v: v.pointOn[0][0])
        edge_length = 0
        x_left = -1e99
        for edge_idx in vertices[1].getEdges():
            edge = self.fatigue_part.edges[edge_idx]
            if edge.pointOn[0][2] == 2.:
                edge_length += edge.getSize(printResults=False)
                x_coords = [self.fatigue_part.vertices[edge.getVertices()[0]].pointOn[0][0],
                            self.fatigue_part.vertices[edge.getVertices()[1]].pointOn[0][0],
                            x_left]
                x_left = max(x_coords)

        x_plane = edge_length + 2*(center_point[0] + r) - x_left
        datum_plane_vertical1 = self.fatigue_part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=x_plane)
        self.fatigue_part.PartitionCellByDatumPlane(datumPlane=self.fatigue_part.datum[datum_plane_vertical1.id],
                                                    cells=self.fatigue_part.cells)

        datum_plane_vertical4 = self.fatigue_part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE,
                                                                             offset=self.length/2 - self.R1)
        self.fatigue_part.PartitionCellByDatumPlane(datumPlane=self.fatigue_part.datum[datum_plane_vertical4.id],
                                                    cells=self.fatigue_part.cells)

        offset = self.thickness/2 - self.case_mesh_thickness
        datum_plane_vertical6 = self.fatigue_part.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,
                                                                             offset=offset)
        self.fatigue_part.PartitionCellByDatumPlane(datumPlane=self.fatigue_part.datum[datum_plane_vertical6.id],
                                                    cells=self.fatigue_part.cells)

        return self.fatigue_part

    def mesh(self, part=None, analysis_type='ThermalDiffusion'):
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

        def edges_direction_part(part_object, edges_to_sort, sort_function):
            case_edges_pos = []
            case_edges_neg = []
            for edge in edges_to_sort:
                v1, v2 = edge.getVertices()
                point_1 = part_object.vertices[v1].pointOn[0]
                point_2 = part_object.vertices[v2].pointOn[0]
                if sort_function(point_1, point_2):
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
            print(" ERROR: The analysis types supported are: ThermalDiffusion or Mechanical")
            sys.exit(" ERROR: Method mesh of class cylinderSpecimenClass was called using incorrect argument, Exiting")

        # Assign element type       
        part.setElementType(regions=(part.cells,), elemTypes=(elem_type1, elem_type2))
        
        # Edges in the hardness gradient
        top_faces = self.fatigue_part.faces.findAt((self.length/2 - 1.01*self.R1, self.height/2, self.thickness/2))
        top_faces = top_faces.getFacesByFaceAngle(89)
        top_vertices_idx = set([idx for face in top_faces for idx in face.getVertices()])
        top_edges_idx = set([idx for face in top_faces for idx in face.getEdges()])
        case_edges = []
        for edge in self.fatigue_part.edges:
            z_point = edge.pointOn[0][2]
            if z_point in [0, self.thickness/2 - self.case_mesh_thickness, self.thickness/2]:
                if edge.index not in top_edges_idx:
                    if edge.getVertices()[0] in top_vertices_idx or edge.getVertices()[1] in top_vertices_idx:
                        case_edges.append(edge)

        def case_edges_sort(p1, p2):
            if p1[1] == p2[1]:
                return p1[0] > p2[0]
            else:
                return p1[1] > p2[1]
        edges1, edges2 = edges_direction_part(self.fatigue_part, case_edges, case_edges_sort)
        part.seedEdgeByBias(biasMethod=SINGLE, 
                            end1Edges=edges1,
                            end2Edges=edges2,
                            number=nr,
                            ratio=20,
                            constraint=FIXED)

        # Edges in the z-direction
        z0 = 0
        z1 = self.thickness/2 - self.case_mesh_thickness
        z2 = self.thickness/2

        z_edges = [edge for edge in self.fatigue_part.edges if z1 < edge.pointOn[0][2] < z2]

        def z_edges_sort(p1, p2):
            return p1[2] > p2[2]
        edges1, edges2 = edges_direction_part(self.fatigue_part, z_edges, z_edges_sort)

        part.seedEdgeByBias(biasMethod=SINGLE, 
                            end1Edges=edges1,
                            end2Edges=edges2,
                            number=25,
                            ratio=20,
                            constraint=FIXED)

        z_edges = [edge for edge in self.fatigue_part.edges if z0 < edge.pointOn[0][2] < z1]
        part.seedEdgeByNumber(edges=z_edges,
                              number=5,
                              constraint=FIXED)

        # Finding points on the upper_line
        # Vertices common to top face and side face
        side_faces = self.fatigue_part.faces.findAt((1e-6, 1e-6, 0)).getFacesByFaceAngle(0)
        bottom_faces = self.fatigue_part.faces.findAt((1e-6, 0, 1e-6)).getFacesByFaceAngle(0)
        side_vertices_idx = set([idx for face in side_faces for idx in face.getVertices()])
        bottom_vertices_idx = set([idx for face in bottom_faces for idx in face.getVertices()])
        top_line_vertices_idx = top_vertices_idx & side_vertices_idx
        bottom_line_vertices_idx = bottom_vertices_idx & side_vertices_idx
        case_line_vertices_idx = side_vertices_idx - top_vertices_idx - bottom_vertices_idx

        def get_xy_from_vertex_list(vertex_list):
            vertices = [self.fatigue_part.vertices[idx] for idx in vertex_list]
            return np.array(sorted([[v.pointOn[0][0], v.pointOn[0][1]] for v in vertices]))
        top_points = get_xy_from_vertex_list(top_line_vertices_idx)
        bottom_points = get_xy_from_vertex_list(bottom_line_vertices_idx)
        case_points = get_xy_from_vertex_list(case_line_vertices_idx)

        # Seeding the notch
        edges_notch_1 = []
        edges_notch_2 = []
        y_edges = []
        mid_section_edges = []
        outer_edges = []
        bottom_transition_edges = []
        for z in [0, self.thickness/2 - self.case_mesh_thickness, self.thickness/2]:
            edges_notch_1.append(part.edges.findAt((1e-6, 0,                            z)))
            y_center = self.notch_height/2 + self.R
            r = self.R + self.case_mesh_thickness
            edges_notch_1.append(part.edges.findAt((r*sin(pi/6), y_center - r*cos(pi/6), z)))
            r = self.R
            edges_notch_1.append(part.edges.findAt((r*sin(pi/6), y_center - r*cos(pi/6), z)))
            for line in [top_points, case_points, bottom_points]:
                mid_p = np.sum(line[1:3, :], axis=0)/2
                edges_notch_2.append(part.edges.findAt((mid_p[0], mid_p[1], z)))

            for i in range(5):
                point = (bottom_points[i, 0], bottom_points[i, 1] + 1e-3, z)
                y_edges.append(part.edges.getClosest((point,))[0][0])
            y_edges.append(part.edges.findAt((bottom_points[-1, 0] - 1e-3, 0, z)))

            for y in [0, self.height/2 - self.case_mesh_thickness, self.height/2]:
                mid_section_edges.append(part.edges.findAt((self.length/4, y, z)))

            x0 = self.length/2 - self.R1
            radius = [self.R1, self.R1 - self.case_mesh_thickness]
            for r in radius:
                outer_edges.append(part.edges.findAt((x0 + r/sqrt(2), r/sqrt(2), z)))
            bottom_transition_edges.append(part.edges.findAt((bottom_points[2, 0] + 1e-3, 0, z)))

        part.seedEdgeByNumber(edges=edges_notch_1, number=nx1)
        part.seedEdgeByNumber(edges=edges_notch_2, number=nx2)
        part.seedEdgeByNumber(edges=y_edges, number=n_height, constraint=FIXED)

        part.seedEdgeBySize(edges=mid_section_edges, size=size_length_direction)

        part.seedEdgeByNumber(edges=outer_edges, number=n_radius, constraint=FIXED)
        part.seedEdgeBySize(edges=bottom_transition_edges, size=size_length_direction/17)

        no_trans_elems = part.getEdgeSeeds(bottom_transition_edges[0], attribute=NUMBER)
        # Finding the length of the two case line edges to mesh
        for z in [0, self.thickness/2 - self.case_mesh_thickness, self.thickness/2]:
            point1 = np.sum(case_points[2:4, :], axis=0)/2
            case_edge_1 = part.edges.getClosest(((point1[0], point1[1], z), ))[0][0]
            case_edge_2 = part.edges.findAt((case_points[3, 0] + 1e-3, self.height/2 - self.case_mesh_thickness, z))
            l1 = case_edge_1.getSize(printResults=False)
            l2 = case_edge_2.getSize(printResults=False)
            n1 = int(round(no_trans_elems*l1/(l1+l2)))
            n2 = int(round(no_trans_elems*l2/(l1+l2)))
            part.seedEdgeByNumber(edges=[case_edge_1], number=n1, constraint=FIXED)
            part.seedEdgeByNumber(edges=[case_edge_2], number=n2, constraint=FIXED)

            top_point_1 = np.sum(top_points[2:4, :], axis=0)/2
            top_edge_1 = part.edges.findAt((top_point_1[0], top_point_1[1], z))

            top_point_2 = np.sum(top_points[3:5, :], axis=0)/2
            top_edge_2 = part.edges.getClosest(((top_point_2[0], top_point_2[1], z),))[0][0]
            top_edge_3 = part.edges.findAt((top_points[4, 0] + 1e-3, self.height/2, z))
            l1 = top_edge_1.getSize(printResults=False)
            l2 = top_edge_2.getSize(printResults=False)
            l3 = top_edge_3.getSize(printResults=False)

            n1 = int(round(no_trans_elems*l1/(l1+l2+l3)))
            n2 = int(round(no_trans_elems*l2/(l1 + l2 + l3)))
            n3 = int(round(no_trans_elems*l3/(l1 + l2 + l3)))

            part.seedEdgeByNumber(edges=[top_edge_1], number=n1, constraint=FIXED)
            part.seedEdgeByNumber(edges=[top_edge_2], number=n2, constraint=FIXED)
            part.seedEdgeByNumber(edges=[top_edge_3], number=n3, constraint=FIXED)

        for z in [1e-3, self.thickness/2 - 1e-3]:
            for y in [1e-3, self.height/2 - 1e-3]:
                cell = self.fatigue_part.cells.findAt((bottom_points[3, 0] - 1e-3, y, z))
                sweep_edge = self.fatigue_part.edges.findAt((bottom_points[3, 0],
                                                             self.height/2 - self.case_mesh_thickness, z))
                self.fatigue_part.setMeshControls(regions=(cell, ), elemShape=HEX_DOMINATED,
                                                  algorithm=MEDIAL_AXIS)
                self.fatigue_part.setSweepPath(region=cell,
                                               edge=sweep_edge, sense=FORWARD)

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

        support_nodes = part.nodes.getByBoundingBox(xMin=self.length/2 - self.R1 - 1e-8,
                                                    xMax=self.length/2 - self.R1 + 1e-8,
                                                    yMin=self.height/2 - 1e-8)
        part.Set(nodes=support_nodes, name='support_nodes')

        session.viewports['Carbon Toolbox Model'].maximize()
        print(" Mesh generation completed")

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
            print(" ERROR: The analysis types supported are: ThermalDiffusion or Mechanical")
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
