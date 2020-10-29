# Import required modules
import os,sys

try:
    import mesh
    from abaqus import *
    import assembly
    import section
    import step
    import mesh
    import interaction
    from abaqusConstants import *
    from abaqus import backwardCompatibility
    backwardCompatibility.setValues(reportDeprecated=False)
except ImportError:
    print " ERROR: This script require Abaqus CAE to run"
    raise

class cylinderSpecimenClassConical():
    """
    =========================================================================
    Version:    0.1.0 - Alpha Development
    Written by: Niklas Melin, 2012
    =========================================================================

    Description:
    -------------------------------------------------------------------------
    This class handles the creation of the specimen used for 
    case hardening simulations, meshing and output of input files.

    Methods:
    -------------------------------------------------------------------------
    .createGeometry             - Add data to the data structure
    .setAnalysisType            - Add data to the fieldOutput object
    .setCarbonAnalysisProp      - Set properties required for the carbon analysis
    .setThermalAnalysisProp     - Set properties required for the carbon analysis    
    .setMechanicalAnalysisProp  - Set properties required for the carbon analysis
    .generateMesh               - Clear all stored values
    .writeInpFile               - Creates output data field

    Internal methods:
    -------------------------------------------------------------------------

    """


    # 3mm 
    def __init__(self,r1=3.0, d1=10,dMax=15.35,h=15.0,t=2.0,angle=10.0,b=2.5, analysisType='ThermalDiffusion'):
        """
        Initiate the class with default values

        Declare specified variables:
        Variable name           Description
        -----------------------------------------------------
        r                       Radius of the specimen
        h                       Height of the specimen
        t                       Thickness of the reinfined region 
                                  in which residual stresses and the
                                  carbon potential is built up.
        analysisType            Parameter used for selecting correct
                                element type, steps and etc.
        
        
        Internal variables
        Variable name           Description
        -----------------------------------------------------

        """        
        def centerOfCircle3Points(Xouter,Youter):
            Xcenter = (Xouter[2]**2 * (Youter[0] - Youter[1]) + (Xouter[0]**2 + (Youter[0] - Youter[1]) * (Youter[0] - Youter[2])) * (Youter[1] - Youter[2]) + Xouter[1]**2 * (-Youter[0] + Youter[2])) / (2 * (Xouter[2] * (Youter[0] - Youter[1]) + Xouter[0] * (Youter[1] - Youter[2]) + Xouter[1] * (-Youter[0] + Youter[2])))
            Ycenter = (Youter[1] + Youter[2]) / 2 - (Xouter[2] - Xouter[1]) / (Youter[2] - Youter[1]) * (Xcenter - (Xouter[1] + Xouter[2]) / 2)
            R = sqrt((Xouter[0] - Xcenter)**2 + (Youter[0] - Ycenter)**2)
            return Xcenter, Ycenter, R

        # Declare vaiables
        self.angle=float(angle) # Number of degrees to revolute
        self.r1=float(r1)
        self.r2=self.r1-t
        self.h=float(h)
        self.t=float(t)
        self.b=float(b)
        self.D1=float(d1)
        self.DMax = float(dMax)
        self.D2=self.D1-self.t
        self.H1=self.h+20
        self.H2=self.h
        self.analysisType=analysisType

        # Create viewport for model creation
        if not session.viewports.has_key('Carbon Toolbox Model'):
            self.viewPort=session.Viewport(name='Carbon Toolbox Model')
        else:    
            self.viewPort=session.viewports['Carbon Toolbox Model']
        self.viewPort.makeCurrent()
        
        # Create new model object
        Mdb()
        self.modelDB=mdb.models['Model-1']
        self.modelDB.setValues(noPartsInputFile=ON)
        
        # Set replay file output format to INDEX for readability
        session.journalOptions.setValues(replayGeometry=INDEX)
        
        # Compute coordinates for all points
        self.r2 = self.r1 - self.t
        self.D2 = self.D1 - self.t
        self.D3 = self.DMax - self.t

        p1  = ( 0.0      ,  0.0     )
        p2  = ( self.r2  ,  0.0     )
        p3  = ( self.r2  ,  self.b  )
        p4  = ( self.D2  ,  self.H2+self.b )
        p5  = ( self.D3  ,self.H1+self.b  )
        p6  = ( 0.0      ,  self.H1+self.b  )
        p7  = ( 0.0      ,  self.H2+self.b  )
        p8  = ( 0.0      ,  self.b  )

        p9  = ( self.r1  ,  0.0     )
        p10 = ( self.r1  ,  self.b  )
        p11 = ( self.D1  ,  self.H2+self.b  )
        p12 = ( self.DMax  ,  self.H1+self.b  )
        
        # Extra points to define arc
        #   Inner arc
        p13 = ( self.D2  , self.b - self.H2  )
        x,y,r = centerOfCircle3Points([ p13[0], p3[0], p4[0] ] , [ p13[1], p3[1], p4[1] ] )
        p14 = ( x, y )
        #   Outer arc
        p15 = ( self.D1  , self.b - self.H2  )
        x,y,self.R = centerOfCircle3Points([ p15[0], p10[0], p11[0] ] , [ p15[1], p10[1], p11[1] ] )
        p16 = ( x, y )

        # Compute the secant angle of the arc
        v1=[ p3[0]-p14[0] , p3[1]-p14[1] ]
        v2=[ p4[0]-p14[0] , p4[1]-p14[1] ]
        norm_v1=(v1[0]**2 + v1[1]**2)**.5
        norm_v2=(v2[0]**2 + v2[1]**2)**.5
        e1=[ v1[0] / norm_v1 , v1[1] / norm_v1 ]
        e2=[ v2[0] / norm_v2 , v2[1] / norm_v2 ]
        self.alpha=acos(e1[0]*e2[0] + e1[1]*e2[1])*180/pi
        
        
        # Create sketch :InnerSpecimen
        mySketch = self.modelDB.ConstrainedSketch(name='__profile__', sheetSize=800.0)
        g, v, d, c = mySketch.geometry, mySketch.vertices, mySketch.dimensions, mySketch.constraints
        mySketch.sketchOptions.setValues(viewStyle=AXISYM)
        mySketch.setPrimaryObject(option=STANDALONE)        
        mySketch.ConstructionLine(point1=(0.0, -400.0), point2=(0.0, 400.0))
        
        # Create component: InnerSpecimen
        mySketch.Line(point1=p1, point2=p2 )
        mySketch.Line(point1=p2, point2=p3 )
        mySketch.ArcByCenterEnds(point1=p3, point2= p4, center= p14, direction=CLOCKWISE)
        mySketch.Line(point1=p4, point2=p5 )
        mySketch.Line(point1=p5, point2=p6 )
        mySketch.Line(point1=p6, point2=p7 )
        mySketch.Line(point1=p7, point2=p8 )
        mySketch.Line(point1=p8, point2=p1 )

        # Creat part: InnerSpecimen
        self.myPartI = mdb.models['Model-1'].Part(name='InnerSpecimen', dimensionality=THREE_D, type=DEFORMABLE_BODY)
        self.myPartI.BaseSolidRevolve(sketch=mySketch, angle=self.angle, flipRevolveDirection=OFF)
        mySketch.unsetPrimaryObject()
        self.viewPort.setValues(displayedObject=self.myPartI)
        

        # Create sketch :OuterSpecimen
        mySketch = self.modelDB.ConstrainedSketch(name='__profile__', sheetSize=800.0)
        g, v, d, c = mySketch.geometry, mySketch.vertices, mySketch.dimensions, mySketch.constraints
        mySketch.sketchOptions.setValues(viewStyle=AXISYM)
        mySketch.setPrimaryObject(option=STANDALONE)        
        mySketch.ConstructionLine(point1=(0.0, -400.0), point2=(0.0, 400.0))
        
        # Create component: OuterSpecimen
        mySketch.Line(point1=p2, point2=p9 )
        mySketch.Line(point1=p9, point2=p10 )
        mySketch.ArcByCenterEnds(point1=p10, point2= p11, center= p16, direction=CLOCKWISE)
        mySketch.Line(point1=p11, point2=p12 )
        mySketch.Line(point1=p12, point2=p5 )
        mySketch.Line(point1=p5, point2=p4 )
        mySketch.ArcByCenterEnds(point1=p3, point2= p4, center= p14, direction=CLOCKWISE)
        mySketch.Line(point1=p3, point2=p2 )

        # Creat part: OuterSpecimen
        self.myPartO = self.modelDB.Part(name='OuterSpecimen', dimensionality=THREE_D, type=DEFORMABLE_BODY)
        self.myPartO.BaseSolidRevolve(sketch=mySketch, angle=self.angle, flipRevolveDirection=OFF)
        mySketch.unsetPrimaryObject()
        self.viewPort.setValues(displayedObject=self.myPartO)

        # Create assembly
        self.myAssembly = self.modelDB.rootAssembly
        self.myAssembly.DatumCsysByThreePoints(coordSysType=CYLINDRICAL, origin=(0.0, 0.0, 0.0), point1=(1.0, 0.0, 0.0), point2=(0.0, 0.0, -1.0))

        self.myInstanceI=self.myAssembly.Instance(name='InnerSpecimen', part=self.myPartI, dependent=OFF)
        self.myInstanceO=self.myAssembly.Instance(name='OuterSpecimen', part=self.myPartO, dependent=OFF)

        # Create instance from merge of parts
        self.fatiguePartInstance=self.myAssembly.InstanceFromBooleanMerge(name='cylinderSpecimenClass', 
            instances=(self.myInstanceI, self.myInstanceO, ),
            keepIntersections=ON, 
            originalInstances=DELETE, domain=GEOMETRY)
        self.fatiguePartInstanceName=self.fatiguePartInstance.name

        # Create reference to new part from the instance.partName
        self.fatiguePart=self.modelDB.parts[self.fatiguePartInstance.partName]


        # Create datum planes
        DatumPlaneVertical=self.fatiguePart.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=self.b)
        DatumPlaneHorizonatal=self.fatiguePart.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=self.H2+self.b )
        
        # Partion faces
        self.fatiguePart.PartitionCellByDatumPlane(datumPlane=self.fatiguePart.datum[DatumPlaneVertical.id], cells=self.fatiguePart.cells)
        self.fatiguePart.PartitionCellByDatumPlane(datumPlane=self.fatiguePart.datum[DatumPlaneHorizonatal.id], cells=self.fatiguePart.cells)

        # Enter mesh module
        self.viewPort.partDisplay.setValues(mesh=ON)
        self.viewPort.partDisplay.meshOptions.setValues(meshTechnique=ON)
        self.viewPort.partDisplay.geometryOptions.setValues(referenceRepresentation=OFF)

    def mesh(self,analysisType='ThermalDiffusion'):
        """
        Method which meshes the part with the appropriate element type
        self.fatiguePart         - Part
        self.fatiguePartInstance - Instance
        """
        #----------------------------------------------------------------        
        def deg2rad(deg):
            return(deg*pi/180)
        #----------------------------------------------------------------
        def EdgeDirectionInstance(modelDB=None,edge=None):
            instances=modelDb.rootAssembly.instances
            #Returnes true if True if positive, else False
            if not str(type(edge)) == "<type 'Edge'>":
               print "Error: The supplied argument is not of Edge type"
               raise
            # Get start and end point of edge
            v1,v2=edge.getVertices()
            instanceName=edge.instanceName
            point_1=instances[instanceName].vertices[v1].pointOn
            point_2=instances[instanceName].vertices[v2].pointOn
            vector=[point_2[0][0]-point_1[0][0],point_2[0][1]-point_1[0][1],point_2[0][2]-point_1[0][2]]
            if (vector[0]<0) or (vector[1]<0) or (vector[2]<0):
                return True
            else:
                return False
        #----------------------------------------------------------------
        def EdgeDirectionPart(partObj=None,edge=None):
            #Returnes true if True if positive, else False
            if not str(type(edge)) == "<type 'Edge'>":
                print "Error: The supplied argument is not of Edge type"
                raise
            # Get start and end point of edge
            v1,v2=edge.getVertices()
            point_1=partObj.vertices[v1].pointOn
            point_2=partObj.vertices[v2].pointOn
            vector=[point_2[0][0]-point_1[0][0],point_2[0][1]-point_1[0][1],point_2[0][2]-point_1[0][2]]
            if (vector[0]<0) or (vector[1]<0) or (vector[2]<0):
                return True
            else:
                return False
        #----------------------------------------------------------------
        def EdgesDirectionPart(partObj=None,edges=None):
            CaseEdgesPos=[]
            CaseEdgesNeg=[]
            for edge in edges:
                #Returnes true if True if positive, else False
                #This check is buggy if the code is run from the terminal
                #if not str(type(edge)) == "<type 'Edge'>":
                #    print "Error: The supplied argument is not of Edge type"
                #    raise
                # Get start and end point of edge
                v1,v2=edge.getVertices()
                point_1=partObj.vertices[v1].pointOn
                point_2=partObj.vertices[v2].pointOn
                vector=[point_2[0][0]-point_1[0][0],point_2[0][1]-point_1[0][1],point_2[0][2]-point_1[0][2]]
                if (vector[0]<0) or (vector[1]<0) or (vector[2]<0):
                    CaseEdgesPos.append(edge)
                else:
                    CaseEdgesNeg.append(edge)
            return CaseEdgesPos, CaseEdgesNeg
        #----------------------------------------------------------------
        def nodesOn(objs):
            nodes=objs[0].getNodes()
            if len(objs) > 1:
                for obj in objs[1:]:
                     nodes=nodes+obj.getNodes()
            return nodes
        #----------------------------------------------------------------
        def elementsOn(objs):
            elements=objs[0].getElements()
            if len(objs) > 1:
                for obj in objs[1:]:
                     elements=elements+obj.getElements()
            return elements
        #----------------------------------------------------------------
        
        # Assign mesh control        Mesh on PART (NOT INSTANCE)
        if analysisType=='ThermalDiffusion':
            elemType1 = mesh.ElemType(elemCode=DC3D8, elemLibrary=STANDARD) # Axisymetric therma and massdiffusion elements
            elemType2 = mesh.ElemType(elemCode=DC3D6, elemLibrary=STANDARD)  # Axisymetric therma and massdiffusion elements
        elif analysisType=='Mechanical':
            elemType1 = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)  # Axisymetric stress elements
            elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)  # Axisymetric stress elements
        else:    
            print " ERROR: The analysis types supported are: ThermalDiffusion or Mechanical"
            sys.exit(" ERROR: Method mesh of class cylinderSpecimenClass was called using incorrect argument, Exiting")

        # Assign element type       
        self.fatiguePart.setElementType(regions=(self.fatiguePart.cells,), elemTypes=(elemType1, elemType2))

        # Sort out all Case edges and other
        CaseEdges=[]
        RadialEdge=[]
        Lengthwise_arc=[]
        Lengthwise_b=[]
        Tangential_arc=[]
        OtherEdges=[]

        #    Compute commonly used quantities
        z_axis=self.fatiguePart.edges.findAt((0.0, self.b/2,0.0))
        tangential_arc_length_r1=self.r1*2*pi*self.angle/360
        tangential_arc_length_D1=self.D1*2*pi*self.angle/360
        fatigue_arc_length=self.R*2*pi*self.alpha/360 # Length of the arc for the waist of the specimen
        
        # Sort edges depending on how to seed. Based on length and direction
        for edge in self.fatiguePart.edges:            
            edge_length=edge.getSize()
            angle=self.fatiguePart.getAngle(line1=z_axis, line2=edge)

            # Case edges, radial direction
            if ( edge_length > float(self.t*0.99) ) and ( edge_length < float(self.t*1.01) ) and ( round(self.fatiguePart.getAngle(line1=z_axis, line2=edge)*100 )/100 == 90.0 ):
                CaseEdges.append(edge)

            # Case edges, tangential direction
            elif ( edge_length < tangential_arc_length_r1*1.01 and edge_length > tangential_arc_length_r1*0.99 ): # Arc length
                Tangential_arc.append(edge)
            elif ( edge_length < tangential_arc_length_D1*1.01 and edge_length > tangential_arc_length_D1*0.99 ): # Arc length
                Tangential_arc.append(edge)

            # Core edges, radial direction
            elif ( angle != None ) and ( abs(round(angle*100)/100 )== 90.0 ):
                RadialEdge.append(edge)

            # Edge at center of specimen with same number of elements as the arc
            elif ( edge_length < self.H2*1.01 and edge_length > self.H2*0.99 ): # Arc length
                Lengthwise_arc.append(edge)

            # Edge at major radii of specimen with same number of elements as the center edge
            elif ( edge_length < fatigue_arc_length*1.01 and edge_length > fatigue_arc_length*0.99 ): # Arc length
                Lengthwise_arc.append(edge)

            # Edge at center of specimen with same number of elements as the arc
            elif ( edge_length < self.b*1.01 and edge_length > self.b*0.99 ): # Arc length
                Lengthwise_b.append(edge)
            else:    
                OtherEdges.append(edge)

        # Assign mesh controls, fixted size
        #    Case region
        caseMin=0.025
        caseMax=0.10
        #    Core region
        coreRadial=int( round(  (self.r2/0.15)   ) )

        # Seed case
        #    Radial case edges
        CaseEdgesPos,CaseEdgesNeg=EdgesDirectionPart(self.fatiguePart,edges=CaseEdges)
        self.fatiguePart.seedEdgeByBias(biasMethod=SINGLE, end1Edges=tuple(CaseEdgesPos), end2Edges=tuple(CaseEdgesNeg), minSize=caseMin, maxSize=caseMax, constraint=FIXED)
        #    Tangential case edges
        print "Seeding Tangential edge %s , %s" %(int(  round(tangential_arc_length_r1/caseMax) ), int(  round(self.b/caseMax*1.4) ) )
        self.fatiguePart.seedEdgeByNumber(edges=Tangential_arc[0:], number=int(  round(tangential_arc_length_r1/caseMax*1.4) ), constraint=FIXED)
        self.fatiguePart.seedEdgeByNumber(edges=Lengthwise_b[0:], number=int(  round(self.b/caseMax*1.4) ), constraint=FIXED)
        
        # Seed core
        #    Seed radial direction
        RadialEdgePos,RadialEdgeNeg=EdgesDirectionPart(self.fatiguePart,edges=RadialEdge)
        print "Seeding radial edge %s , %s" %(int(  round(self.H2/1) ), coreRadial )
        Lengthwise_arc_pos,Lengthwise_arc_neg=EdgesDirectionPart(self.fatiguePart,edges=Lengthwise_arc)
        self.fatiguePart.seedEdgeByBias(biasMethod=SINGLE, end2Edges=tuple(Lengthwise_arc_pos), end1Edges=tuple(Lengthwise_arc_neg), number= int(  round(self.H2*2.0) ), ratio = 6 , constraint=FIXED)
        self.fatiguePart.seedEdgeByBias(biasMethod=SINGLE, end1Edges=tuple(RadialEdgePos), end2Edges=tuple(RadialEdgeNeg), number= coreRadial, ratio = 2)

        # Set general mesh size (Left unset)
        #self.fatiguePart.seedEdgeByBias(biasMethod=SINGLE, end1Edges=tuple(OtherEdgesPos), end2Edges=tuple(OtherEdgesNeg), minSize=coreMin, maxSize=coreMax, constraint=FIXED)
        
        #Fixing for sweep mesh controll for problematic cell -erolsson
        q = deg2rad(self.angle)
        sweepCell = self.fatiguePart.cells.findAt(((self.r2/2*cos(q/2), self.b+self.H2/2, self.r2/2*sin(q/2)),))
        self.fatiguePart.setMeshControls(regions=sweepCell, technique=SWEEP)

        # Mesh assembly
        self.fatiguePart.generateMesh(seedConstraintOverride=OFF)
        self.viewPort.setValues(displayedObject=self.fatiguePart)
        self.viewPort.view.fitView()
        

        # Create sets and surfaces
        #    All_Nodes
        self.fatiguePart.Set(nodes=self.fatiguePart.nodes[0:], name='All_Nodes')
        #    Create element sets
        self.fatiguePart.Set(elements=self.fatiguePart.elements[0:], name='All_Elements')
        
        #       - Exposed Elements and Nodes
        #              Pick surface on arc at failure point
        f1=self.fatiguePart.faces.findAt((cos(deg2rad(self.angle/2))*self.r1, self.b/2, sin(deg2rad(self.angle/2))*self.r1 ))
        fTop = self.fatiguePart.faces.findAt((0.0001*(cos(deg2rad(self.angle/2))), 
                                              self.b+self.H1, 
                                              0.0001*(sin(deg2rad(self.angle/2)))))
        #              Pick connected faces by angle
        print fTop
        exposedFaces=f1.getFacesByFaceAngle(45)+fTop.getFacesByFaceAngle(1)
        #              Get elements and nodes connected to selected faces
        exposedNodes=nodesOn(exposedFaces)
        exposedElements=elementsOn(exposedFaces)
        #              Create sets on part
        self.fatiguePart.Set(nodes=exposedNodes, name='Exposed_Nodes')
        self.fatiguePart.Set(elements=exposedElements, name='Exposed_Elements')
        #              Create surface
        self.fatiguePart.Surface(side1Faces=exposedFaces, name='Exposed_Surface')
        
        #       - Boundary node
        vertice=self.fatiguePart.vertices.findAt((0,0,0),)
        origoNode=vertice.getNodes()
        self.fatiguePart.Set(nodes=origoNode[0:], name='BC_Node')
        
        #       - Boundary face
        face=self.fatiguePart.faces.findAt((self.r1/2, 0.0, sin(deg2rad(self.angle/2))*self.r1 ))
        face=face.getFacesByFaceAngle(0) # Trick to get sequence
        if face == None:
            print "No nodes found for BC_Face"
        else:
            self.fatiguePart.Set(faces=face , name='BC_Face')

        #       - Boundary Cyclic Symmetry 
        masterFaces=self.fatiguePart.faces.findAt((self.r1/2, self.b/2, 0.0))
        masterFaces=masterFaces.getFacesByFaceAngle(20)
        masterElements=elementsOn(masterFaces)
        self.fatiguePart.Set(elements=masterElements, name='master')
        self.fatiguePart.Surface(name = 'masterSurf', side1Faces=masterFaces) #erolsson

        slaveFaces=self.fatiguePart.faces.findAt((cos(deg2rad(self.angle))*self.r1/2, self.b/2 , sin(deg2rad(self.angle))*self.r1/2 ))
        slaveFaces=slaveFaces.getFacesByFaceAngle(20)
        slaveElements=elementsOn(slaveFaces)
        self.fatiguePart.Set(elements=slaveElements, name='slave')
        self.fatiguePart.Surface(name='slaveSurf',side1Faces=slaveFaces) #erolsson

        #       - Element set for the fatigue evaluation -erolsson
        q = deg2rad(self.angle)
        fatigueCells1 = self.fatiguePart.cells.findAt((((self.r2+self.t/2)*cos(q/2), self.b/2, (self.r2+self.t/2)*sin(q/2)),)) 
        fatigueCells2 = self.fatiguePart.cells.findAt(((self.r2/2*cos(q/2), self.b/2, self.r2/2*sin(q/2)),))
        #fatigueCells = self.fatiguePart.cells.findAt(((self.r2/2*cos(q/2), self.b/2, self.r2/2*sin(q/2)),))
        fatigueElems = elementsOn(fatigueCells1 + fatigueCells2)
        self.fatiguePart.Set(elements=fatigueElems, name='fatigueElements')
        #       - Boundary Tension nodes

        fatigueFace1 = self.fatiguePart.faces.findAt((((self.r2+self.t/2)*cos(q/2), 0., (self.r2+self.t/2)*sin(q/2)),)) 
        fatigueFace2 = self.fatiguePart.faces.findAt(((self.r2/2*cos(q/2), 0., self.r2/2*sin(q/2)),))
        fatigueElems = elementsOn(fatigueFace1 + fatigueFace2)
        self.fatiguePart.Set(elements=fatigueElems, name='fatigueElementsSmall')

        #  - element and nodal set for a radial line used for fast fatigue evaluation  -erolsson
        radialEdge1 = self.fatiguePart.edges.findAt(((self.r2+self.t/2, 0,0),))
        radialEdge2 = self.fatiguePart.edges.findAt(((self.r2/2, 0,0),))
        fatigueNodes = nodesOn(radialEdge1+radialEdge2)
        self.fatiguePart.Set(nodes=fatigueNodes, name='radialLine')

        arc1 = self.fatiguePart.edges.findAt(((self.r2+self.t, self.b/2,0),))
        arc2 = self.fatiguePart.edges.findAt(((self.r2+self.t+self.R*(1 - cos(deg2rad(self.alpha/2))), 
                                               self.b+self.R*sin(deg2rad(self.alpha/2)),0),))
        fatigueNodes = nodesOn(arc1+arc2)
        self.fatiguePart.Set(nodes=fatigueNodes, name='arc')

        self.BoundaryLoadFace=self.fatiguePart.faces.findAt((cos(deg2rad(self.angle)/2)*(self.D1+self.DMax)/2, 
                                                             self.H2+(self.H1-self.H2)/2+self.b , 
                                                             sin(deg2rad(self.angle)/2)*(self.D1+self.DMax)/2 ))
        self.BoundaryLoadFaceNodes=nodesOn([self.BoundaryLoadFace])
        self.fatiguePart.Set(nodes=self.BoundaryLoadFaceNodes, name='BoundaryLoadNodes')
        self.BoundaryLoadFace=self.BoundaryLoadFace.getFacesByFaceAngle(0) # Trick to get sequence
        self.fatiguePart.Set(faces=self.BoundaryLoadFace, name='BoundaryLoadFaces') #erolsson
        
        #       - Monitor node
        monitorVertice=self.fatiguePart.vertices.findAt((self.r1,0,0),)
        monitorVerticeNodes=monitorVertice.getNodes()
        monitorNode=monitorVerticeNodes[0].label-1
        self.fatiguePart.Set(nodes=self.fatiguePart.nodes[monitorNode:monitorNode+1], name='Monitor_Node')
        
        session.viewports['Carbon Toolbox Model'].maximize()
        print " Mesh generation completed"

    def changeAnalysisType(self,analysisType='Mechanical'):
        """
        Method to change the analysis type by changing the element type
        """
        # Assign mesh control        Mesh on PART (NOT INSTANCE)
        if analysisType=='ThermalDiffusion':
            elemType1 = mesh.ElemType(elemCode=DC3D8, elemLibrary=STANDARD) # Axisymetric therma and massdiffusion elements
            elemType2 = mesh.ElemType(elemCode=DC3D6, elemLibrary=STANDARD)  # Axisymetric therma and massdiffusion elements
        elif analysisType=='Mechanical':
            elemType1 = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)  # Axisymetric stress elements
            elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)  # Axisymetric stress elements
            
        else: 
            print " ERROR: The analysis types supported are: ThermalDiffusion or Mechanical"
            sys.exit(" ERROR: Method mesh of class cylinderSpecimenClass was called using incorrect argument, Exiting")

        # Assign element type       
        self.myAssembly.setElementType(regions=(self.fatiguePart.cells,), elemTypes=(elemType1, elemType2))
      
    def writeFile(self,fileName):
        
        #Set filename and path
        outputFileName=os.path.basename(fileName)
        outputFileNameNoExt=outputFileName.split('.')[0]
        outputDirectory=os.path.dirname(fileName)
        
        
        # Set path as working directory
        if outputDirectory:
            os.chdir(outputDirectory)
        print outputFileName
        # Create job
        mdb.Job(name=outputFileNameNoExt, model='Model-1', description='', type=ANALYSIS,
            atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
            memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
            explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
            modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
            scratch='', parallelizationMethodExplicit=DOMAIN, numDomains=1, 
            activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=1)        
        
        # Write job to file
        mdb.jobs[outputFileNameNoExt].writeInput(consistencyChecking=OFF)
        
        # Remove job
        del mdb.jobs[outputFileNameNoExt]
        
        # Fix file name
        #print "Renaming from: %s \n           to: %s" %(os.path.join(outputDirectory,outputFileNameNoExt+'.inp'),fileName)
        if os.path.exists(os.path.abspath(fileName)):
            os.remove(os.path.abspath(fileName))
        os.rename(os.path.join(outputDirectory,outputFileNameNoExt+'.inp'),fileName)
        #os.remove(os.path.abspath(os.path.join(outputDirectory,outputFileNameNoExt+'.inp')))
        
    #Function by erolssson
    def mechanicalMaterialAssignment(self):
        mat = self.modelDB.Material('Steel')
        mat.Elastic(table=((200E3, 0.3),))
        sec = self.modelDB.HomogeneousSolidSection(name='FatigueSpecimen-1',
                                                  material = 'steel')
        part = self.fatiguePart
        self.fatiguePart.SectionAssignment(region= (part.elements,), sectionName = 'FatigueSpecimen-1')

    #Function by erolssson
    def applyDisplacementBC(self):
        import regionToolset as rT
        #computing the number of cylindrical symmetric sectors
        numSectors = int(360/self.angle)
        #creating the tie constraint for cylindric symmetry
        #Creating two regions of vertices for the cyclic symmetry and the cylindrical coordinate system
        v1 = self.fatiguePartInstance.vertices.findAt(((0.0,0.0,0.0),),)
        v2 = self.fatiguePartInstance.vertices.findAt(((0.0,self.H1+self.b,0.0),),)
        s1 = self.fatiguePartInstance.surfaces['masterSurf']
        s2 = self.fatiguePartInstance.surfaces['slaveSurf']
        self.modelDB.CyclicSymmetry(name='cyclicSym', createStepName='Initial', 
                                    master = rT.Region(side1Faces = s1.faces),
                                    slave = rT.Region(side1Faces = s2.faces),
                                    repetitiveSectors = numSectors,  
                                    axisPoint1 = rT.Region(vertices = v1),
                                    axisPoint2 = rT.Region(vertices = v2),
                                    positionToleranceMethod=COMPUTED_TOLERANCE, positionTolerance=0.0, 
                                    adjustTie=False, 
                                    extractedNodalDiameter=ALL_NODAL_DIAMETER, excitationNodalDiameter=0)
        

        #Boundary condition for the mirror plane in the center of the specimen
        symPlane = rT.Region(faces = self.fatiguePartInstance.sets['BC_Face'].faces)
        self.modelDB.DisplacementBC(name='mirror',
                                    createStepName = 'Initial',
                                    region = symPlane,
                                    localCsys = self.modelDB.rootAssembly.datums[1],
                                    u2 = 0.0,
                                    u3 = 0.0) 
        
        #Creating a "dummy" node for applying the loads
        p = self.modelDB.Part(name='Dummy node', dimensionality=THREE_D, 
                              type=DISCRETE_RIGID_SURFACE)
        p.ReferencePoint(point=(0.0, 1.2*self.H1, 0.0))
        I = self.modelDB.rootAssembly.Instance(name='Dummy node', part=p, dependent=OFF)
        rP = (I.referencePoints[1],)
        self.loadNode = rT.Region(referencePoints=rP)
        LoadRegion = rT.Region(faces = self.fatiguePartInstance.sets['BoundaryLoadFaces'].faces)
        self.modelDB.Coupling(name = 'Coupling loadNode',
                              controlPoint=self.loadNode,
                              surface=LoadRegion,
                              influenceRadius=WHOLE_SURFACE,
                              couplingType = DISTRIBUTING)

    def applyForceBC(self, Force=1.0):
        #Creating a step for the load if not available
        if not self.modelDB.steps.has_key('MechanicalLoad'):
            self.modelDB.StaticStep(name='MechanicalLoad', previous='Initial')
                
        if self.modelDB.loads.has_key('Force'):
            del self.modelDB.loads['Torque']
        if self.modelDB.loads.has_key('Torque'):
            del self.modelDB.loads['Torque']
        numSectors = int(360/self.angle)
        Force = float(Force)/numSectors
        self.modelDB.ConcentratedForce(name='Force', createStepName ='MechanicalLoad', region=self.loadNode, cf2=Force)

    def applyTorqueBC(self, Torque=1.0):
        #Creating a step for the load if not available
        if not self.modelDB.steps.has_key('MechanicalLoad'):
            self.modelDB.StaticStep(name='MechanicalLoad', previous='Initial')

        if self.modelDB.loads.has_key('Torque'):
            del self.modelDB.loads['Torque']
        if self.modelDB.loads.has_key('Force'):
            del self.modelDB.loads['Force']
        numSectors = int(360/self.angle)
        Torque = float(Torque)/numSectors
        self.modelDB.Moment(name='Torque', createStepName ='MechanicalLoad', region=self.loadNode, cm2=Torque)

##############################
#Test code
if __name__ == "__main__":
    m=cylinderSpecimenClassConical()
    m.mesh(analysisType='Mechanical')
    #Code By EO
    m.mechanicalMaterialAssignment()
    m.applyDisplacementBC()
    m.applyForceBC(1.0)
    m.changeAnalysisType(analysisType='ThermalDiffusion')
    m.writeFile('Test')
    
#import sys
#sys.path.append("H://applications/abaqus_plugins/Plugins/CaseHardeningToolbox/")
#import fatigueSpecimenClass
#spec=fatigueSpecimenClass.cylinderSpecimenClass()
#spec.mesh()
