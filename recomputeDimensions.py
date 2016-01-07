from dimensioning import *
from XMLlib import SvgXMLTreeNode
from svgLib_dd import SvgPath

class DrawingViewInfo:
    def __init__(self, drawingView, calculateBounds=False ):
        self.name = drawingView.Name
        #self.scale =  drawingView.Scale #not always correct for center line objects.
        self.drawing_x = drawingView.X
        self.drawing_y = drawingView.Y
        self.viewResult_length = len(drawingView.ViewResult)
        self.viewResult_hash = hash(drawingView.ViewResult)
        if calculateBounds:
            XML_tree = SvgXMLTreeNode(drawingView.ViewResult, 0)
            scaling = XML_tree.scaling()
            self.scale = scaling
            for element in XML_tree.getAllElements():
                if element.tag == 'circle':
                    x, y = element.applyTransforms( float( element.parms['cx'] ), float( element.parms['cy'] ) )
                    r =  float( element.parms['r'] )* scaling
                    self.updateBounds_ellipse( x, y, r, r )
                if element.tag == 'ellipse':
                    cx, cy = element.applyTransforms( float( element.parms['cx'] ), float( element.parms['cy'] ) )
                    rx, ry = float( element.parms['rx'] )* scaling, float( element.parms['ry'] )* scaling
                    self.updateBounds_ellipse( cx, cy, rx, ry )
                if element.tag == 'path': 
                    path = SvgPath( element )
                    for p in path.points:
                        self.updateBounds( p.x, p.y )
                if element.tag == 'line':
                    x1, y1 = element.applyTransforms( float( element.parms['x1'] ), float( element.parms['y1'] ) )
                    x2, y2 = element.applyTransforms( float( element.parms['x2'] ), float( element.parms['y2'] ) )
                    self.updateBounds( x1, y1 )
                    self.updateBounds( x1, y2 )


    def updateBounds( self, x, y): #svg bounds ...
        if not hasattr( self, 'x_min'):
            self.x_min = x
            self.x_max = x
            self.y_min = y
            self.y_max = y
        else:
            self.x_min = min( self.x_min, x)
            self.x_max = max( self.x_max, x)
            self.y_min = min( self.y_min, y)
            self.y_max = max( self.y_max, y)

    def updateBounds_ellipse( self, cx, cy, rx, ry):
        if not hasattr( self, 'x_min'):
            self.x_min = cx - rx
            self.x_max = cx + rx
            self.y_min = cy - ry
            self.y_max = cy + ry
        else:
            self.x_min = min( self.x_min, cx - rx)
            self.x_max = max( self.x_max, cx + rx)
            self.y_min = min( self.y_min, cy - ry)
            self.y_max = max( self.y_max, cy + ry)

    def normalize_position(self, x, y):
        if self.x_max > self.x_min:
            x_n = (x - self.x_min) / (self.x_max - self.x_min)
        else:
            x_n = 0
        if self.y_max > self.y_min:
            y_n = (y - self.y_min) / (self.y_max - self.y_min)
        else:
            y_n = 0
        return numpy.array( [ x_n, y_n ] )

    def unnormalize_position(self, x_n, y_n):
        return numpy.array( [ 
                self.x_min + x_n * (self.x_max - self.x_min), 
                self.y_min + y_n * (self.y_max - self.y_min)
                ] )

    def changed( self, doc ):
        drawingView = doc.getObject( self.name )
        if drawingView == None:
            return False
        return not ( self.viewResult_length == len(drawingView.ViewResult) and self.viewResult_hash == hash(drawingView.ViewResult) ) #hash should change with drawingView.X Y scale changes, i hope...

    def get_up_to_date_version( self, doc ):
        drawingView = doc.getObject( self.name )
        if DrawingInfo_cache.has_key( self.name ):
            v = DrawingInfo_cache[ self.name ]
            recalculate = not ( v.viewResult_length == len(drawingView.ViewResult) and v.viewResult_hash == hash(drawingView.ViewResult) )
        else:
            recalculate = True
        if recalculate:
            DrawingInfo_cache[ self.name ] = DrawingViewInfo( drawingView, calculateBounds=True )
        return DrawingInfo_cache[ self.name ]
DrawingInfo_cache = {}

class SvgElements:
    def __init__(self, SvgXML, element_tag_of_interest, doFittedCircles=False):
        'parses a SVG and returns a FreeCAD_Object.Shape styled data structure'
        self.points = []
        self.lines = []
        self.circles = []
        self.ellipses = []
        self.arcs = []
        self.texts = []
        XML_tree =  SvgXMLTreeNode( SvgXML, 0 )
        scaling = XML_tree.scaling()
        for element in XML_tree.getAllElements():
            if element.tag != element_tag_of_interest:
                continue
            if element.tag == 'circle':
                x, y = element.applyTransforms( float( element.parms['cx'] ), float( element.parms['cy'] ) )
                r =  float( element.parms['r'] )* scaling
                self.circles.append( [ x, y, r] )
                self.ellipse_points( x, y, r, r )
            if element.tag == 'ellipse': #no angle parm?
                cx, cy = element.applyTransforms( float( element.parms['cx'] ), float( element.parms['cy'] ) )
                rx, ry = float( element.parms['rx'] )* scaling, float( element.parms['ry'] )* scaling
                self.ellipses.append( [ cx, cy, rx, ry] )
                self.ellipse_points( cx, cy, rx, ry )
            if element.tag == 'text' and element.parms.has_key('x'):
                x, y = element.applyTransforms( float( element.parms['x'] ), float( element.parms['y'] ) )
                self.texts.append( [x, y, element] )
            if element.tag == 'path': 
                path = SvgPath( element )
                for p in path.points:
                    self.points.append( [p.x, p.y] )
                for line in path.lines:
                    self.lines.append([ line.x1, line.y1, line.x2, line.y2 ])
                    self.points.append( line.midPoint() )
                for arc in path.arcs:
                    if arc.circular:
                        self.circles.append( [arc.center[0], arc.center[1], arc.r*scaling] )
                    else:
                        self.ellipses.append( [arc.center[0], arc.center[1], arc.rX*scaling, arc.rY*scaling ] )
                    self.points.append( [arc.center[0], arc.center[1]] )
                if doFittedCircles:
                    for bezierCurve in path.bezierCurves:
                        x, y, r, r_error = bezierCurve.fitCircle()
                        if r_error < 10**-4:
                            self.circles.append( [ x, y, r] )
            if element.tag == 'line':
                x1, y1 = element.applyTransforms( float( element.parms['x1'] ), float( element.parms['y1'] ) )
                x2, y2 = element.applyTransforms( float( element.parms['x2'] ), float( element.parms['y2'] ) )
                self.points.append( [x1, y1] )
                self.points.append( [x2, y2] )
                self.points.append( [(x1+x2)/2, (y1+y2)/2] )
                self.lines.append(  [x1, y1, x2, y2 ] )
    def ellipse_points( self, x, y, rx, ry ):
        self.points.append( [x, y] )
        self.points.append( [x - rx, y     ] )
        self.points.append( [x     , y - ry] )
        self.points.append( [x + rx, y     ] )
        self.points.append( [x     , y + ry] )


class RecomputeDimensions:
    "Defines the RecomputeDimensions command"
    
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/recomputeDimensions.svg' , 
            'MenuText': 'recompute dimensions', 
            'ToolTip':  'recompute dimensions'
            } 
            
    def Activated(self):
        doc = FreeCAD.ActiveDocument
        changed = False
        for obj in doc.Objects:
            if hasattr(obj, 'Proxy'):
                if isinstance( obj.Proxy, Proxy_DimensionObject_prototype ):
                    changed = False
                    for s_ind, s in enumerate( obj.Proxy.selections ):
                        if hasattr(s, 'updateValues'):
                            if s_ind == 0:
                                old_vi = s.viewInfo #used to update placement clicks later
                            changeOccured = s.updateValues( doc )
                            changed = changed or changeOccured
                    if changed:
                        #updating placement clicks using view as reference or anche
                        if hasattr( obj.Proxy.selections[0], 'viewInfo' ):
                            new_vi = obj.Proxy.selections[0].viewInfo
                            for s in obj.Proxy.selections:
                                if isinstance(s, PlacementClick):
                                    ref = old_vi.normalize_position ( s.x, s.y )
                                    s.updatePosition( obj, *new_vi.unnormalize_position(*ref) )
                                    obj.purgeTouched()
                        obj.Proxy.execute( obj ) #updating straight away since other dimensions may be based upon this.
                    else: #delete check for deleting dimensions based on deleted views
                        for s in obj.Proxy.selections: 
                            if hasattr( s, 'viewInfo'):
                                if doc.getObject( s.viewInfo.name ) == None:
                                    debugPrint(2, 'deleting dimension %s since it refers to a deleted object (%s)' % (obj.Name, s.viewInfo.name))
                                    doc.removeObject( obj.Name )
                                    break
                        
        FreeCAD.ActiveDocument.recompute()
        

FreeCADGui.addCommand('dd_recomputeDimensions', RecomputeDimensions())
