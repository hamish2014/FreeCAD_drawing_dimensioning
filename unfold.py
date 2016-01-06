from dimensioning import *
from dimensioning import __dir__
import previewDimension
from centerLines import _centerLineSVG
import dimensionSvgConstructor
import numpy
from numpy import pi, sin, cos, arctan2, arcsin, arccos, dot
from numpy.linalg import norm
dotProduct = numpy.dot
crossProduct = numpy.cross

d = DimensioningProcessTracker()

def unfold(faces_org):
    faces = map(FaceWrapper, faces_org)
    projection = Projection()
    for ind, working_face in enumerate(faces):
        if projection.empty():
            projection.draw_base( working_face )
            working_face.drawn = True
        if working_face.drawn:
            for f in faces[ind+1:]:
                if not f.drawn:
                    try:
                        projection.unfold( f )
                        f.drawn = True
                    except NoCommonEdge:
                        pass
                    except UnfoldOverlapError:
                        pass
    projection.insert_fold_lines()
    return projection

class FaceWrapper:
    def __init__(self, freeCAD_face_object):
        self.fC_face = freeCAD_face_object
        self.normal = numpy.array( freeCAD_face_object.normalAt(0,0) )
        self.drawn = False

class UnfoldOverlapError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return self.parameter
class NoCommonEdge(UnfoldOverlapError):
    pass



class Projection:
    def __init__(self, bendingRadius=1):
        self.bendingRadius = bendingRadius
        self.graphicObjects = []
        self.points = []
        self.foldingLines = []
    def empty(self):
        return len(self.graphicObjects) == 0
    def _findPoint(self, p):
        if not p in self.points:
            self.points.append(p)
            return p 
        else:
            ind = self.points.index( p )
            return self.points[ind]
    
    def _draw(self, faceWrapper):
        face =  faceWrapper.fC_face
        transform = faceWrapper.transform
        for edge in face.Edges:
            if str(edge.Curve).startswith('<Line'):
                P = [ transform( edge.Curve.StartPoint ), transform( edge.Curve.EndPoint )]
                self.graphicObjects.append( pLine( self._findPoint(P[0]), self._findPoint(P[1]), faceWrapper, edge ) ) #p prefix denoties projection
            elif str(edge.Curve).startswith('Circle '):
                angle1 = edge.FirstParameter
                angle2 = edge.LastParameter 
                assert angle2 > angle1
                arcPoints = []
                c =  numpy.array( edge.Curve.Center )
                r =  edge.Curve.Radius
                xAxis =  numpy.array(edge.Curve.XAxis) 
                yAxis = numpy.array(edge.Curve.YAxis)
                for angle in numpy.linspace(angle1, angle2, 12):
                    pos = c + xAxis*cos(angle)*r + yAxis*sin(angle)*r
                    arcPoints.append( self._findPoint( transform( pos ) ) )
                self.graphicObjects.append( pCircularArc( self._findPoint( transform(c) ), r,  arcPoints, faceWrapper, edge ) )
            else:
                debugPrint(4,"Projection._draw Edge.Curve (%s) type not support: %s" % (edge.Curve, type(edge.Curve)))

    def draw_base(self, faceWrapper ):
        faceWrapper.transform = pTransform1( faceWrapper.normal, numpy.array([0,0,1.0]), 0 )
        self._draw( faceWrapper )

    def unfold( self, faceWrapper ):
        face = faceWrapper.fC_face
        edgeToConnectTo = None
        for edge in face.Edges:
            if edgeToConnectTo == None:
                if str(edge.Curve).startswith('<Line'):
                    for edgeCandidate in self.graphicObjects:
                        if isinstance(edgeCandidate, pLine):
                            if edgeCandidate.colinearWith( edge ):
                                edgeToConnectTo = edgeCandidate
                                cEdge = edge #edge to align with edgeToConnect to
                                break
        if edgeToConnectTo == None:
            raise NoCommonEdge, "%s has no common edge with the current projection" % str(face)
        debugPrint(4,"unfold.commonEdge curve 1 %s , curve 2 %s" % (cEdge.Curve, edgeToConnectTo.edge.Curve))

        faceWrapper.transform = pTransform2(
            faceWrapper.normal, 
            numpy.array([0, 0, 1.0]),
            #edgeToConnectTo.faceW.normal,
            cEdge.Curve.StartPoint,
            edgeToConnectTo.faceW.transform(cEdge.Curve.StartPoint).posProjection,
            cEdge.Curve.EndPoint,
            edgeToConnectTo.faceW.transform(cEdge.Curve.EndPoint).posProjection,
            )
        self._draw( faceWrapper ) 

    def insert_fold_lines(self):
        lines = [ g for g in self.graphicObjects if isinstance(g,pLine) ]
        for i,L1 in enumerate(lines):
            for L2 in lines[i+1:]:
                if L1.colinearWith(L2):
                    #self.foldingLines.append( FoldingLine( L1.startPoint.posProjection, L1.endPoint.posProjection ) )
                    #determining where to draw folding lines.
                    P = numpy.array([ L1.startPoint.posProjection, L1.endPoint.posProjection, L2.startPoint.posProjection, L2.endPoint.posProjection ])
                    v = normalize(P[1] - P[0])
                    T = numpy.unique(numpy.array(sorted([ dotProduct(p-P[0],v) for p in P ])))
                    intersectionSegment = None
                    outsideSegments = []
                    
                    #debugPrint(2,'"insert_fold_lines v %s, T %s"' % (v,T))
                    for t_a, t_b in zip(T[:-1],T[1:]):
                        a = dotProduct(             t_a, v) + P[0]
                        b = dotProduct(             t_b, v) + P[0]
                        c = dotProduct( (t_a + t_b)*0.5, v) + P[0]
                        if L1.pointOnLine(c) and L2.pointOnLine(c):
                            intersectionSegment = [a,b]
                            #debugPrint(2,'"insert_fold_lines adding folding line at a=%s b=%s"' % (a,b))
                        elif L1.pointOnLine(c) or L2.pointOnLine(c):
                            outsideSegments.append([a,b])
                    if intersectionSegment <> None:
                        L1.visible = False
                        L2.visible = False
                        self.foldingLines.append( FoldingLine( *intersectionSegment ) )
                        for a,b in outsideSegments:
                            self.graphicObjects.append( pLine(
                                    self._findPoint(pPoint(a[0],a[1],None)), 
                                    self._findPoint(pPoint(b[0],b[1],None)), 
                                    L1.faceW, L1.edge ) )

    def generateSvg(self, x, y, scale=1.0, rotation=0, strokeWidth=0.5,  lineColor='black', foldLineColor='blue', foldstrokeWidth=0.5, len_dash=3, len_gap=3):
        XML_body = []
        for g in self.graphicObjects:
            if g.visible:
                XML_body.append(  g.svg(strokeWidth/scale, lineColor) )
        for L in self.foldingLines:
            XML_body.append(  L.svg(foldstrokeWidth/scale, foldLineColor, len_dash/scale, len_gap/scale) )
        return '''<g  transform="rotate(%f,%f,%f) translate(%f,%f) scale(%f,%f)" >
%s
</g> ''' % ( rotation, x, y, x, y, scale, scale, "\n".join(XML_body))




class pTransform1:
    def __init__(self, faceNorm, drawingNorm, rotation_drawing_norm):
        axis, angle = rotation_required_to_rotate_a_vector_to_be_aligned_to_another_vector( faceNorm, drawingNorm )
        self.R1 = axis_rotation_matrix( angle, *axis )
        self.R2 = axis_rotation_matrix( rotation_drawing_norm, u_x=0, u_y=0, u_z=1.0 )
        self.R = dotProduct( self.R2, self.R1 )
        self.offset = numpy.zeros(3)
    def __call__(self, p ):
        p_new = dotProduct( self.R, p) + self.offset
        return pPoint( p_new[0], p_new[1], numpy.array(p)) #z dimension ignored


class pTransform2(pTransform1):
    def __init__(self, faceNorm, drawingNorm, a_3Dpos, a_2Dproj, b_3Dpos, b_2Dproj):
        axis, angle = rotation_required_to_rotate_a_vector_to_be_aligned_to_another_vector( faceNorm, drawingNorm )
        self.R1 = axis_rotation_matrix( angle, *axis )
        debugPrint(4,"""   R1: %s""" % self.R1 )
        a_R1 = dotProduct( self.R1, a_3Dpos)
        b_R1 = dotProduct( self.R1, b_3Dpos)
        angle_actual = arctan2( b_R1[1] - a_R1[1], b_R1[0] - a_R1[0] )
        angle_desired = arctan2( b_2Dproj[1] - a_2Dproj[1], b_2Dproj[0] - a_2Dproj[0] )
        self.R2 = axis_rotation_matrix( angle_desired - angle_actual, u_x=0, u_y=0, u_z=1.0 ) #R2 maybe unessary...
        self.R = dotProduct( self.R2, self.R1 )
        a_R = dotProduct( self.R, a_3Dpos )
        self.offset = a_2Dproj - a_R
        #debugPrint(4,"""   R: %s""" % self.R )

class pPoint: #p prefix denoties projection
    def __init__(self, x, y, pos3D):
        self.x = x
        self.y = y
        self.posProjection = numpy.array([x,y,0])
        self.pos3D = pos3D
    def __eq__(self, b, tol=10**-6):
        return abs(self.x - b.x) < tol and abs(self.y - b.y) < tol

class pLine:
    def __init__(self, startPoint, endPoint, faceWrapper, edge):
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.faceW = faceWrapper
        self.edge = edge
        self.visible = True
    def colinearWith(self, edge, tol=10**-6):
        a = self.startPoint.pos3D
        b = self.endPoint.pos3D
        if norm( b - a) > 0:
            v = normalize(b - a)
            if hasattr(edge,'Curve'):
                C = [edge.Curve.StartPoint, edge.Curve.EndPoint]
            else:
                C = [edge.startPoint.pos3D, edge.endPoint.pos3D ]
            for c in C:
                d = numpy.array(c) - a
                err = norm(d - dot(d,v)*v)
                if err > tol:
                    return False
            return True
        return False
    def pointOnLine(self, c, tol=10**-3):
        d = norm( self.endPoint.posProjection - self.startPoint.posProjection )
        d1 = norm( self.endPoint.posProjection - c )
        d2 = norm( c - self.startPoint.posProjection )
        return abs(d - (d1+d2)) < tol

    def __str__(self):
        return '<pLine x1="%f" y1="%f" x2="%f" y2="%f">' % (self.startPoint.x, self.startPoint.y, self.endPoint.x,  self.endPoint.y)

    def svg(self, strokeWidth, lineColor):
        return '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (self.startPoint.x, self.startPoint.y, self.endPoint.x,  self.endPoint.y, lineColor, strokeWidth )

    
class FoldingLine:
    def __init__(self, p1, p2 ):
        self.p1 = p1
        self.p2 = p2

    def svg(self, strokeWidth, lineColor, len_dash, len_gap):
        xml = _centerLineSVG(self.p1[0], self.p1[1], self.p2[0],  self.p2[1], len_dash, len_dash, len_gap)
        xml = xml.replace('path ','path style="stroke:%s;stroke-width:%1.2f" ' % (lineColor,strokeWidth))
        #debugPrint(2, xml)
        return xml
                                                     

        #return '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (self.p1[0], self.p1[1], self.p2[0],  self.p2[1], lineColor, strokeWidth )
        

class pCircularArc:
    def __init__(self, center, radius , points, faceWrapper, edge):
        self.center = center
        self.radius = radius
        self.points = points
        self.faceW = faceWrapper
        self.edge = edge
        self.visible = True

    def svg(self, strokeWidth, lineColor):
        if self.points[0] <> self.points[-1]:
            r = self.radius
            largeArc = False #abs(dEnd - dStart) >= pi #given the construction method
            #determine sweep flag
            p1, p2 = self.points[:2]
            angle1 = arctan2( p1.y-self.center.y , p1.x-self.center.x )
            angle2 = arctan2( p2.y-self.center.y , p2.x-self.center.x )
            if abs(angle1 - angle2) < pi/2: # has not crossed pi/2 or -pi/2 mark
                sweep = angle1 < angle2
            else:
                sweep = angle1 < 0
            return ' '.join( ['<path d = "M %f %f A %f %f 0 %i %i %f %f" style="stroke:%s;stroke-width:%1.2f;fill:none" />' % (p1.x, p1.y,r,r,largeArc,sweep, p2.x, p2.y, lineColor, strokeWidth ) for p1,p2 in zip(self.points[:-1], self.points[1:]) ] )
        else:
            return '<circle cx="%f" cy="%f" r="%f" stroke="%s" stroke-width="%1.2f" fill="none" />' % (self.center.x, self.center.y, self.radius, lineColor,  strokeWidth)
        #return '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (self.p1.x, self.p1.y, self.p2.x,  self.p2.y, lineColor, strokeWidth )



def projectionSvg(x,y):
    return d.projection.generateSvg(
        x, y,
        strokeWidth= d.strokeWidth, #0.5
        lineColor= d.lineColor, #'black', 
        foldLineColor= d.foldColor, #'green', 
        foldstrokeWidth= d.foldstrokeWidth, #0.3
        len_dash= d.fold_len_gap, 
        len_gap= d.fold_len_dash,
        scale= d.svgScale, 
        rotation= d.svgRotation,
        )

def clickHandler( x, y ):
    d.placement_x = x
    d.placement_y = y
    FreeCADGui.Control.closeDialog()
    return 'createDimension:%s' % findUnusedObjectName('unfold')


class Proxy_unfold( Proxy_DimensionObject_prototype ):
    def __init__(self, obj, selections, svgFun):
        self.selections = [] #to be compdabile with Proxy_DimensionObject_prototype
        self.svgFun = None
        obj.X = d.placement_x
        obj.Y = d.placement_y
        obj.Scale = d.svgScale
        obj.Rotation = d.svgRotation
        obj.Proxy = self

    def execute( self, obj ):
        origSvg = obj.ViewResult
        newTransform = 'transform="rotate(%f,%f,%f) translate(%f,%f) scale(%f,%f)" ' %  (obj.Rotation, obj.X, obj.Y, obj.X,  obj.Y, obj.Scale, obj.Scale)
        p1 = origSvg.find('transform')
        p2 = origSvg.find('>')
        obj.ViewResult = origSvg[:p1] + newTransform +  origSvg[p2:]
        
d.ProxyClass = Proxy_unfold

class UnfoldCommand:
    def Activated(self):
        selection = FreeCADGui.Selection.getSelectionEx()
        if len(selection) == 1 and all( isinstance(s, Part.Face) for s in selection[0].SubObjects )  :
            V = getDrawingPageGUIVars() #needs to be done before dialog show, else Qt active is dialog and not freecads
            d.activate(V) #to do, implement defaults preferences, ['centerLine_width','centerLine_len_gap','centerLine_len_dash','centerLine_len_dot'], ['centerLine_color'])
            d.dialogIconPath = ':/dd/icons/unfold.svg' #nessary since dialog is none
            d.projection = unfold( selection[0].SubObjects )
            d.taskPanelDialog =  UnfoldTaskPanel()
            FreeCADGui.Control.showDialog( d.taskPanelDialog )
            previewDimension.initializePreview( d, projectionSvg, clickHandler )
        else:
            QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Info", 'Please select touching faces from the same shape')
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/unfold.svg', 
            'MenuText': 'Unfold faces', 
            'ToolTip': 'Unfold faces'
            } 
FreeCADGui.addCommand('dd_unfold', UnfoldCommand())


class UnfoldTaskPanel:
    'based on FreeCAD_sf_master/src/Mod/PartDesign/InvoluteGearFeature.py'
    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi( ':/dd/ui/unfold.ui' )
        self.form.setWindowIcon( QtGui.QIcon( ':/dd/icons/unfold.svg' ) )

        #self.form.doubleSpinBox_scale.setValue(d.svgScale)
        #self.form.doubleSpinBox_rotation.setValue(d.svgRotation)
        self.getValuesFromDialog()
        
        for groupBox in self.form.children():
            for w in groupBox.children():
                if hasattr(w, 'valueChanged'):
                    w.valueChanged.connect( self.getValuesFromDialog )
                if isinstance(w, QtGui.QLineEdit):
                    #debugPrint(2, 'QtGui.QLineEdit')
                    w.textChanged.connect( self.getValuesFromDialog )
                #if isinstance(w, QtGui.QDoubleSpinBox):
                    #QtCore.QObject.connect(w, QtCore.SIGNAL("valueChanged(double)"), self.getValuesFromDialog)


    def getValuesFromDialog(self, notUsed=None):
        d.svgScale = self.form.doubleSpinBox_scale.value()
        d.svgRotation = self.form.doubleSpinBox_rotation.value()
        d.strokeWidth = self.form.doubleSpinBox_lineWidth.value()
        d.lineColor = self.form.lineEdit_lineColor.text()
        d.foldstrokeWidth = self.form.doubleSpinBox_foldWidth.value()
        d.foldColor = self.form.lineEdit_foldColor.text()
        d.fold_len_gap = self.form.doubleSpinBox_foldDash.value()
        d.fold_len_dash = self.form.doubleSpinBox_foldGap.value()
        
    def scaledChanged(self, newScale):
        d.svgScale = newScale
    def rotationChanged(self, v):
        d.svgRotation = v

    def getStandardButtons(self): #http://forum.freecadweb.org/viewtopic.php?f=10&t=11801
        return 0x00400000
    
    def reject(self):
        previewDimension.removePreviewGraphicItems( recomputeActiveDocument = True )
        FreeCADGui.Control.closeDialog()


        
#copied from assembly2/lib3D.py

def arccos2( v, allowableNumericalError=10**-1 ):
    if -1 <= v and v <= 1:
        return arccos(v)
    elif abs(v) -1 < allowableNumericalError:
        return 0 if v > 0 else pi
    else:
        raise ValueError,"arccos2 called with invalid input of %s" % v

def normalize( v ):
    return v / norm(v)


def axis_rotation_matrix( theta, u_x, u_y, u_z ):
    ''' http://en.wikipedia.org/wiki/Rotation_matrix '''
    return numpy.array( [
            [ cos(theta) + u_x**2 * ( 1 - cos(theta)) , u_x*u_y*(1-cos(theta)) - u_z*sin(theta) ,  u_x*u_z*(1-cos(theta)) + u_y*sin(theta) ] ,
            [ u_y*u_x*(1-cos(theta)) + u_z*sin(theta) , cos(theta) + u_y**2 * (1-cos(theta))    ,  u_y*u_z*(1-cos(theta)) - u_x*sin(theta )] ,
            [ u_z*u_x*(1-cos(theta)) - u_y*sin(theta) , u_z*u_y*(1-cos(theta)) + u_x*sin(theta) ,              cos(theta) + u_z**2*(1-cos(theta))   ]
            ])

def rotation_required_to_rotate_a_vector_to_be_aligned_to_another_vector( v, v_ref ):
    c = crossProduct( v, v_ref)
    if norm(c) > 0:
        axis = normalize(c)
        angle = arccos2( dotProduct( v, v_ref ))
        return axis, angle
    else: #no rotation required OR vector needs to be flipped ...
        debugPrint(3,"rotation_required_to_rotate_a_vector_to_be_aligned_to_another_vector,  norm(c)==0")
        if numpy.array_equal( v, v_ref ):
            return numpy.array([1.0, 0, 0]), 0.0
        else:
            a, e = axis_to_azimuth_and_elevation_angles(*v_ref)
            axis = azimuth_and_elevation_angles_to_axis(a, e + pi/2)
            return axis, pi
            

def azimuth_and_elevation_angles_to_axis( a, e):
    u_z = sin(e)
    u_x = cos(e)*cos(a)
    u_y = cos(e)*sin(a)
    return numpy.array([ u_x, u_y, u_z ])
def axis_to_azimuth_and_elevation_angles( u_x, u_y, u_z ):
    return arctan2( u_y, u_x), arcsin2(u_z)

def arcsin2( v, allowableNumericalError=10**-1 ):
    if -1 <= v and v <= 1:
        return arcsin(v)
    elif abs(v) -1 < allowableNumericalError:
        return pi/2 if v > 0 else -pi/2
    else:
        raise ValueError,"arcsin2 called with invalid input of %s" % v
