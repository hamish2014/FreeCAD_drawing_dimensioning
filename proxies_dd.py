import pickle
from svgLib_dd import SvgTextParser
from numpy.linalg import norm
from numpy import log

class Proxy_DimensionObject_prototype:
    def __init__(self, obj, selections, svgFun):
        self.selections = selections
        self.svgFun = svgFun
        #setup_dimension_objects_properties
        for prop in ['Rotation', 'Scale', 'X', 'Y']:  #not used so hide
            obj.setEditorMode(prop, 2)
        d = self.dimensionProcess()
        for w in d.dialogWidgets + d.preferences + selections:
            if hasattr(w, 'add_properties_to_dimension_object'):
                w.add_properties_to_dimension_object( obj )
        obj.Proxy = self

    def __getstate__(self):
        D = self.__dict__.copy() 
        D['selections_dumps'] = pickle.dumps( self.selections )
        del D['selections']
        D['svgFun_dumps'] = pickle.dumps( self.svgFun )
        del D['svgFun']
        return D

    def __setstate__(self, D):
        self.__dict__.update(D) 
        self.selections = pickle.loads( D['selections_dumps'] )
        self.svgFun =  pickle.loads( D['svgFun_dumps'] )

    def dimensionProcess( self ):
        raise ValueError,"override  dimensionProcess to return the dimensionProcessTracker"

    def execute( self, obj ):
        KWs = {}
        d = self.dimensionProcess()
        for w in d.dialogWidgets + d.preferences + self.selections:
            if hasattr(w, 'get_values_from_dimension_object'):
                w.get_values_from_dimension_object( obj, KWs )
        if KWs.has_key('unit_scaling_factor'):
            KWs['scale'] = 1.0/self.selections[0].viewInfo.scale*KWs['unit_scaling_factor']
            del KWs['unit_scaling_factor']
        if d.add_viewScale_KW: #for centerLines
             KWs['viewScale'] = self.selections[0].viewInfo.scale
        obj.ViewResult = self.generate_viewResult( KWs )
    def generate_viewResult( self, KWs ): #overriden by linear stack dimension proxy
        return self.svgFun(*selections_to_svg_fun_args(self.selections), **KWs)

def selections_to_svg_fun_args( selections ):
    args = []
    for s in selections:
        s.svg_fun_args( args )
    return args


class Dimensioning_Selection_prototype:
    'these selection classes are for purposes of recording a drawing view selection for later updates'
    def __init__( self, svg_KWs, svg_element, viewInfo, **extraKWs ):
        self.init_for_svg_KWs( svg_KWs, svg_element, **extraKWs )
        #info for updating selection after its drawing view has been updated
        self.svg_element_tag = svg_element.tag
        self.viewInfo = viewInfo #view bounds etc ...
    def init_for_svg_KWs( self, svg_KWs, svg_element ):
        raise NotImplementedError,'needs to overwritten depending upon the selection type'
    def svg_fun_args( self, args ):
        raise NotImplementedError,'needs to overwritten depending upon the selection type'


class PointSelection( Dimensioning_Selection_prototype ):
    def init_for_svg_KWs( self, svg_KWs, svg_element, condensed_args = False  ):
        self.x = svg_KWs['x']
        self.y = svg_KWs['y']
        self.condensed_args = condensed_args
    def xy(self):
        return self.x, self.y
    def svg_fun_args( self, args ):
        if self.condensed_args:
            args.append( [self.x, self.y] )
        else:
            args.extend( [self.x, self.y] )
    def updateValues( self, doc ):
        if not self.viewInfo.changed( doc ):
            return False
        from recomputeDimensions import SvgElements
        from dimensioning import debugPrint
        debugPrint(3,'PointSelection: drawing %s has changed, updating values' % self.viewInfo.name )
        new_vi = self.viewInfo.get_up_to_date_version( doc )
        old_vi = self.viewInfo
        pos_ref = old_vi.normalize_position ( self.x, self.y )
        svg = SvgElements( doc.getObject( self.viewInfo.name ).ViewResult, self.svg_element_tag)
        min_error = None
        for point in svg.points:
            error = norm( pos_ref - new_vi.normalize_position ( *point ) )
            if min_error == None or error < min_error:
                min_error = error
                self.x, self.y = point
        self.viewInfo = new_vi
        return True

class LineSelection(  Dimensioning_Selection_prototype ):
    def init_for_svg_KWs( self, svg_KWs, svg_element ):
        self.x1 = svg_KWs['x1']
        self.y1 = svg_KWs['y1']
        self.x2 = svg_KWs['x2']
        self.y2 = svg_KWs['y2']
        self.condensed_args = True
    def drawing_coordinates( self ):
        return self.x1, self.y1, self.x2, self.y2
    def svg_fun_args( self, args ):
        if self.condensed_args:
            args.append( [self.x1, self.y1, self.x2, self.y2] )
        else:
            args.extend( [self.x1, self.y1, self.x2, self.y2] )
    def updateValues( self, doc ):
        if not self.viewInfo.changed( doc ):
            return False
        from recomputeDimensions import SvgElements
        from dimensioning import debugPrint
        debugPrint(3,'LineSelection: drawing %s has changed, updating values' % self.viewInfo.name )
        new_vi = self.viewInfo.get_up_to_date_version( doc )
        old_vi = self.viewInfo
        ref1 = old_vi.normalize_position ( self.x1, self.y1 )
        ref2 = old_vi.normalize_position ( self.x2, self.y2 )
        svg = SvgElements( doc.getObject( self.viewInfo.name ).ViewResult, self.svg_element_tag)
        min_error = None
        for x1,y1,x2,y2 in svg.lines:
            error1 = min( 
                norm( ref1 - new_vi.normalize_position ( x1, y1 )), 
                norm( ref2 - new_vi.normalize_position ( x1, y1 ) ) 
                )
            error2 = min( 
                norm( ref1 - new_vi.normalize_position ( x2, y2 )), 
                norm( ref2 - new_vi.normalize_position ( x2, y2 ) ) 
                )
            error = error2 + error1
            if min_error == None or error < min_error:
                min_error = error
                self.x1, self.y1, self.x2, self.y2 = x1,y1,x2,y2
        self.viewInfo = new_vi
        return True



class CircularArcSelection(  Dimensioning_Selection_prototype ):
    def init_for_svg_KWs( self, svg_KWs, svg_element, output_mode='xyr' ):
        self.x = svg_KWs['x']
        self.y = svg_KWs['y']
        self.r = svg_KWs['r']
        self.output_mode =  output_mode
    def svg_fun_args( self, args ):
        if self.output_mode == 'xyr':
            args.extend( [self.x, self.y, self.r] )
        elif self.output_mode == 'xy':
            args.append( [self.x, self.y] )
        else:
            raise NotImplementedError, "output_mode %s not implemented" % self.output_mode
    def updateValues( self, doc ):
        if not self.viewInfo.changed( doc ):
            return False
        from recomputeDimensions import SvgElements
        from dimensioning import debugPrint
        debugPrint(3,'CircularArcSelection: drawing %s has changed, updating values' % self.viewInfo.name )
        new_vi = self.viewInfo.get_up_to_date_version( doc )
        old_vi = self.viewInfo
        pos_ref = old_vi.normalize_position ( self.x, self.y )
        r_ref = self.r / old_vi.scale
        svg = SvgElements( doc.getObject( self.viewInfo.name ).ViewResult, self.svg_element_tag)
        min_error = None
        for x,y,r in svg.circles:
            error1 = norm( pos_ref - new_vi.normalize_position ( x,y ) )
            error2 = abs( log( r_ref / (r/new_vi.scale) ) )
            error = error2 + error1 #giving radius and center position equal priority ...
            if min_error == None or error < min_error:
                self.x, self.y, self.r = x,y,r
        self.viewInfo = new_vi
        return True



class TextSelection( Dimensioning_Selection_prototype ):
    def init_for_svg_KWs( self, svg_KWs, svg_element ):
        self.svgText = SvgTextParser( svg_element.XML[svg_element.pStart:svg_element.pEnd])
    def svg_fun_args( self, args ):
        t = self.svgText
        args.extend([t.x, t.y, t.text, t.font_size, t.rotation, t.font_family, t.fill])
    def updateValues( self, doc ):
        if not self.viewInfo.changed( doc ):
            return False
        from recomputeDimensions import SvgElements
        from dimensioning import debugPrint
        debugPrint(3,'textSelection: drawing %s has changed, updating values' % self.viewInfo.name )
        new_vi = self.viewInfo.get_up_to_date_version( doc )
        old_vi = self.viewInfo
        pos_ref = old_vi.normalize_position ( self.svgText.x, self.svgText.y )
        drawingObj = doc.getObject( self.viewInfo.name )
        svg = SvgElements( drawingObj.ViewResult, self.svg_element_tag)
        min_error = None
        for x,y,element in svg.texts:
            error = norm( pos_ref - new_vi.normalize_position ( x,y ) )
            if min_error == None or error < min_error:
                self.svgText = SvgTextParser( element.XML[element.pStart:element.pEnd] )
        self.viewInfo = new_vi
        return True


class ThreePointAngleSelection( Dimensioning_Selection_prototype ):
    def __init__(self):
        self.points = []
    def addPoint( self, svg_KWs, svg_element, viewInfo ):
        self.points.append( PointSelection( svg_KWs, svg_element, viewInfo ) )
        self.viewInfo = viewInfo
    def svg_fun_args( self, args ):
        x1, y1 =   self.points[0].xy()
        x_c, y_c = self.points[1].xy()
        x2, y2 =   self.points[2].xy()
        args.extend( [[x_c, y_c, x1, y1], [x_c, y_c, x2, y2]] )
    def updateValues( self, doc ):
        changed = any([ p.updateValues( doc ) for p in self.points ])
        self.viewInfo = self.points[0].viewInfo
        return changed
    
class PointLinePertubationSelection( Dimensioning_Selection_prototype ):
    'these selection classes are for purposes of recording a drawing view selection for later updates'
    def __init__( self, svg_KWs, svg_element, viewInfo, parellel_line ):
        self.point = PointSelection( svg_KWs, svg_element, viewInfo )
        self.parellel_line = parellel_line
        self.viewInfo = viewInfo 
    def svg_fun_args( self, args ):
        x1,y1,x2,y2 = self.parellel_line.drawing_coordinates()
        dx = (x2-x1)*10**-6
        dy = (y2-y1)*10**-6
        x = self.point.x
        y = self.point.y
        args.append( [ x-dx,y-dy,x+dx,y+dy ] )
    def updateValues( self, doc ):
        changed = self.point.updateValues( doc ) or self.parellel_line.updateValues( doc )  
        self.viewInfo = self.point.viewInfo
        return changed


class TwoLineSelection( Dimensioning_Selection_prototype ):
    def __init__(self, output_mode='combined_center'):
        self.lines = []
        self.output_mode = output_mode
    def addLine( self, svg_KWs, svg_element, viewInfo ):
        self.lines.append( LineSelection( svg_KWs, svg_element, viewInfo ) )
        self.viewInfo = viewInfo
    def svg_fun_args( self, args ):
        if self.output_mode == 'combined_center':
            x1, y1, x2, y2 = self.lines[0].drawing_coordinates()
            x3, y3, x4, y4 = self.lines[1].drawing_coordinates()
            args.append( [0.25*(x1 + x2 + x3 + x4), 0.25*(y1 + y2 + y3 + y4)] )
        else:
            raise NotImplementedError, "output_mode %s not implemented" % self.output_mode
    def updateValues( self, doc ):
        changed = any([ line.updateValues( doc ) for line in self.lines ])
        self.viewInfo = self.lines[0].viewInfo
        return changed

        
class PlacementClick:
    def __init__(self, x, y, condensed_args=False):
        self.x = x
        self.y = y
        self.condensed_args = condensed_args
    def svg_fun_args( self, args ):
        if self.condensed_args:
            args.append( [self.x, self.y] )
        else:
            args.extend( [self.x, self.y] )
    def add_properties_to_dimension_object( self, obj, category='Placement Clicks' ):
        i = 1
        while hasattr( obj, 'click%i_x' % i ):
            i = i + 1
        self.x_name = 'click%i_x' % i
        self.y_name = 'click%i_y' % i
        obj.addProperty("App::PropertyFloat", self.x_name, category)
        obj.addProperty("App::PropertyFloat", self.y_name, category)
        setattr( obj, self.x_name, self.x )
        setattr( obj, self.y_name, self.y )
    def get_values_from_dimension_object( self, obj, KWs ):
        self.x = getattr( obj, self.x_name )
        self.y = getattr( obj, self.y_name )
    def updatePosition( self, obj, x, y):
        self.x = x
        self.y = y 
        setattr( obj, self.x_name, self.x )
        setattr( obj, self.y_name, self.y )


class Proxy_DimensionViewObject_prototype:
    def __init__(self, vobj, iconPath):
        self.iconPath = iconPath
        vobj.Proxy = self
    def getIcon(self):
        return self.iconPath
    def attach(self, vobj):
        pass
    #def claimChildren(self):
    #    FreeCAD.Console.PrintMessage('claimChildren called\n')
    #    return []
    #def setupContextMenu(self, ViewObject, menu):
    #    ''' for playing around in an iPythonConsole:
    #    from PySide import *
    #    app = QtGui.QApplication([])
    #    menu = QtGui.QMenu()
    #    '''
    #    action = menu.addAction('animate')
    #    action.triggered.connect( self.animateAction )
    #
    #    moveMenu = menu.addMenu('move')
    #    action = moveMenu.addAction('top')
    #    action.triggered.connect( self.moveTop ) 
    #def animateAction( self ):
    #    pass
    #def moveTop ( self):
    #    pass
