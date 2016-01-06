
from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *
from linearDimension import linearDimensionSVG_points, linearDimensionSVG_parallels,  linearDimension_parallels_hide_non_parallel, LinearDimensionCommand
import copy

d = DimensioningProcessTracker() 

def linearDimension_stack_SVG( selections, mouse_x, mouse_y, KWs ):
    ref = selections[0]
    svg_codes = []
    if len(ref) == 4:
        reference_type = 'line'
        x1,y1,x2,y2 = ref
        offset_d = numpy.array([x2-x1,y2-y1])
        offset_d = offset_d / numpy.linalg.norm(offset_d)
        mouse_diff = [mouse_x - x1, mouse_y - y1]
        if numpy.dot(offset_d , mouse_diff) < 0:
            offset_d = -offset_d
    else: 
        reference_type = 'point'
        x,y = ref
        mouse_diff_x = mouse_x - x
        mouse_diff_y = mouse_y - y
        if abs(mouse_diff_x) > abs(mouse_diff_y):
            offset_d = numpy.array([1.0,0]) if mouse_diff_x > 0 else  numpy.array([-1.0,0])
        else:
            offset_d = numpy.array([0,1.0]) if mouse_diff_y > 0 else  numpy.array([0,-1.0])
    dx, dy = offset_d * 10**-6 #for converting point selections into tiny lines ... #wont effect dimension value, only dimenion gap
    if reference_type == 'point':
        line1 = [ x-dx, y-dy, x+dx, y+dy ]
    else:
        line1 = ref
    for i,s in enumerate(selections[1:]):
        SVG_args = []
        if len(s) == 2: #then point
            x,y = s
            SVG_args = [ line1, [ x-dx, y-dy, x+dx, y+dy ] ]
        else: #another line selected
            SVG_args = [ line1, s]
        base_point = line1[0:2] if numpy.dot(offset_d, line1[0:2]) > numpy.dot(offset_d, line1[2:4]) else line1[2:4]
        if KWs['stack_offset0'] <> 0:
            offset = KWs['stack_offset0'] + i*KWs['stack_offset']
        else:
            mouse_diff = [mouse_x - base_point[0], mouse_y - base_point[1]]
            offset = numpy.dot(offset_d , mouse_diff) + i*KWs['stack_offset']
        x3 = base_point[0] + offset_d[0]*offset
        y3 = base_point[1] + offset_d[1]*offset
        SVG_args = SVG_args + [x3,y3]
        SVG_KWs = copy.copy(KWs)
        SVG_KWs['autoPlaceText'] = True
        del SVG_KWs['stack_offset0'], SVG_KWs['stack_offset']
        svg_code =  linearDimensionSVG_parallels( *SVG_args, **SVG_KWs) 
        if svg_code <> None:
            svg_codes.append( svg_code )
    if len(svg_codes) > 0:
        return '\n'.join(svg_codes)
    else:
        return '<g></g>'


d.dialogWidgets.append( unitSelectionWidget )
d.registerPreference( 'stack_offset0', 0, 'initial gap (0 for mouse)', increment = 1.0)
d.registerPreference( 'stack_offset',  7, 'gap', increment  = 1.0 )
d.registerPreference( 'textFormat_linear')
d.registerPreference( 'arrow_scheme')
d.registerPreference( 'comma_decimal_place')
d.registerPreference( 'gap_datum_points') 
d.registerPreference( 'dimension_line_overshoot')
d.registerPreference( 'arrowL1')
d.registerPreference( 'arrowL2')
d.registerPreference( 'arrowW')
d.registerPreference( 'strokeWidth')
d.registerPreference( 'lineColor')
d.registerPreference( 'textRenderer')
d.registerPreference( 'autoPlaceOffset')

def linearDimension_stack_preview(mouse_x, mouse_y):
    selections = d.selections + [ PlacementClick( mouse_x, mouse_y ) ] if not isinstance(d.selections[-1], PlacementClick) else d.selections
    d.dimensionConstructorKWs['scale'] = d.viewScale*d.unitConversionFactor
    return linearDimension_stack_SVG( *selections_to_svg_fun_args_linear_stack(selections), KWs = d.dimensionConstructorKWs )

def linearDimension_stack_clickHandler( x, y ):
    d.selections.append( PlacementClick( x, y ) )
    return 'createDimension:%s' % findUnusedObjectName('dimStack')

def stack_selectDimensioningPoint( event, referer, elementXML, elementParms, elementViewObject ):
    viewInfo = selectionOverlay.DrawingsViews_info[elementViewObject.Name]
    if len(d.selections) == 0:
        if isinstance(referer, selectionOverlay.PointSelectionGraphicsItem):
            d.selections.append( PointSelection( elementParms, elementXML, viewInfo ) )
            d.selections[-1].condensed_args = True
            selectionOverlay.hideSelectionGraphicsItems(
                lambda gi: isinstance(gi,  selectionOverlay.LineSelectionGraphicsItem)
                )
        else:
            d.selections.append( LineSelection( elementParms, elementXML, viewInfo ) )
            linearDimension_parallels_hide_non_parallel( elementParms, elementViewObject)
        d.viewScale = 1 / elementXML.rootNode().scaling()
    else:
        if isinstance(referer,selectionOverlay.PointSelectionGraphicsItem):
            d.selections.append( PointSelection( elementParms, elementXML, viewInfo ) )
            d.selections[-1].condensed_args = True
        else:
            d.selections.append( LineSelection( elementParms, elementXML, viewInfo ) )
        if len(d.selections) == 2:
            previewDimension.initializePreview( d, linearDimension_stack_preview, linearDimension_stack_clickHandler )


def selections_to_svg_fun_args_linear_stack( selections ):
    args = []
    for s in selections:
        s.svg_fun_args( args )
    return args[:-2], args[-2], args[-1]

class Proxy_linearDimension_stack( Proxy_DimensionObject_prototype ):
    def dimensionProcess( self ):
        return d
    def generate_viewResult( self, KWs ):
        return linearDimension_stack_SVG( *selections_to_svg_fun_args_linear_stack(self.selections), KWs=KWs )
d.ProxyClass = Proxy_linearDimension_stack


maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)
line_maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
line_maskPen.setWidth(2.0)
line_maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
line_maskHoverPen.setWidth(2.0)
line_maskBrush = QtGui.QBrush() #clear

class LinearDimensionStackCommand(LinearDimensionCommand):
    def __init__(self):
        self.iconPath = ':/dd/icons/linearDimensionStack.svg'
        self.onClickFun = stack_selectDimensioningPoint
        self.toolTip = 'Add Linear Dimension Stack'
        self.d = d
FreeCADGui.addCommand('dd_linearDimensionStack', LinearDimensionStackCommand())
