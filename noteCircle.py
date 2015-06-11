
from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *

d = DimensioningProcessTracker()

def noteCircleSVG( start_x, start_y, radialLine_x=None, radialLine_y=None, tail_x=None, tail_y=None,
                   noteCircleText= '0', strokeWidth=0.5, lineColor='blue', noteCircle_radius=4.5, noteCircle_fill='white',
                   textRenderer=defaultTextRenderer):
    XML_body = [ ]
    if radialLine_x <> None and radialLine_y <> None:
        XML_body.append( svgLine(radialLine_x, radialLine_y, start_x, start_y, lineColor, strokeWidth) )
        if tail_x <> None and tail_y <> None:
            XML_body.append( svgLine(radialLine_x, radialLine_y, tail_x, radialLine_y, lineColor, strokeWidth) )
            XML_body.append(' <circle cx ="%f" cy ="%f" r="%f" stroke="%s" fill="%s" /> ' % (tail_x, radialLine_y, noteCircle_radius, lineColor, noteCircle_fill) )
            XML_body.append( textRenderer( tail_x - 1.5, radialLine_y + 1.5, noteCircleText ) )
    return '<g> %s </g>' % '\n'.join(XML_body)

d.registerPreference( 'strokeWidth')
d.registerPreference( 'lineColor' )
d.registerPreference( 'noteCircle_radius', 4.5, increment=0.5, label='radius')
d.registerPreference( 'noteCircle_fill', RGBtoUnsigned(255, 255, 255), kind='color', label='fill' )
class NoteCircleText_widget:
    def __init__(self):
        self.counter = 1
    def valueChanged( self, arg1):
        d.noteCircleText = '%i' % arg1
        self.counter = arg1 + 1
    def generateWidget( self, dimensioningProcess ):
        self.spinbox = QtGui.QSpinBox()
        self.spinbox.setValue(self.counter)
        d.noteCircleText = '%i' % self.counter
        self.spinbox.valueChanged.connect(self.valueChanged)
        self.counter = self.counter + 1
        return DimensioningTaskDialog_generate_row_hbox('no.', self.spinbox)
d.dialogWidgets.append( NoteCircleText_widget() )



def noteCircle_preview(mouseX, mouseY):
    args = d.args + [ mouseX, mouseY ] if len(d.args) < 6 else d.args
    return noteCircleSVG( *args, noteCircleText=d.noteCircleText, **d.dimensionConstructorKWs )

def noteCircle_clickHandler( x, y ):
    d.args = d.args + [ x, y ]
    d.stage = d.stage + 1
    if d.stage == 3 :
        return 'createDimension:%s' % findUnusedObjectName('dim')

def selectFun( event, referer, elementXML, elementParms, elementViewObject ):
    x,y = elementParms['x'], elementParms['y']
    d.args = [x,y]
    d.stage = 1
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview( d, noteCircle_preview, noteCircle_clickHandler)

maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)

class NoteCircle:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, dialogTitle='Add Note Circle', dialogIconPath=os.path.join( iconPath , 'noteCircle.svg' ), endFunction=self.Activated )
        #d.SVGFun = noteCircleSVG
        selectionOverlay.generateSelectionGraphicsItems(
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim') and not obj.Name.startswith('center')],
            selectFun,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene,
            doPoints=True, doMidPoints=True, doSelectViewObjectPoints = True, 
            pointWid=1.0,
            maskPen=maskPen,
            maskHoverPen=maskHoverPen,
            maskBrush = maskBrush
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)

    def GetResources(self):
        return {
            'Pixmap' : os.path.join( iconPath , 'noteCircle.svg' ) ,
            'MenuText': 'Notation',
            'ToolTip': 'Creates a notation indicator'
            }

FreeCADGui.addCommand('dd_noteCircle', NoteCircle())
