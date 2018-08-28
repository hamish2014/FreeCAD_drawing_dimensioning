from crudeDebugger import crudeDebuggerPrint

crudeDebuggerPrint('''circularDimension.py:1  	from dimensioning import * ''')
from dimensioning import *
crudeDebuggerPrint('''circularDimension.py:2  	from dimensioning import __dir__ # not imported with * directive ''')
from dimensioning import __dir__ # not imported with * directive
crudeDebuggerPrint('''circularDimension.py:3  	import selectionOverlay, previewDimension ''')
import selectionOverlay, previewDimension
crudeDebuggerPrint('''circularDimension.py:4  	from dimensionSvgConstructor import circularDimensionSVG ''')
from dimensionSvgConstructor import circularDimensionSVG

crudeDebuggerPrint('''circularDimension.py:6  	dimensioning = DimensioningProcessTracker() ''')
dimensioning = DimensioningProcessTracker()

def selectFun(  event, referer, elementXML, elementParms, elementViewObject ):
    crudeDebuggerPrint('''circularDimension.py:9  	    x,y = elementParms['x'], elementParms['y'] ''')
    x,y = elementParms['x'], elementParms['y']
    crudeDebuggerPrint('''circularDimension.py:10  	    dimensioning.point1 = x, y ''')
    dimensioning.point1 = x, y
    crudeDebuggerPrint('''circularDimension.py:11  	    debugPrint(2, 'center selected at x=%3.1f y=%3.1f' % (x,y)) ''')
    debugPrint(2, 'center selected at x=%3.1f y=%3.1f' % (x,y))
    crudeDebuggerPrint('''circularDimension.py:12  	    dimensioning.radius = elementParms['r'] ''')
    dimensioning.radius = elementParms['r']
    crudeDebuggerPrint('''circularDimension.py:13  	    dimensioning.dimScale = 1/elementXML.rootNode().scaling() ''')
    dimensioning.dimScale = 1/elementXML.rootNode().scaling()
    crudeDebuggerPrint('''circularDimension.py:14  	    dimensioning.stage = 1 ''')
    dimensioning.stage = 1
    crudeDebuggerPrint('''circularDimension.py:15  	    selectionOverlay.hideSelectionGraphicsItems() ''')
    selectionOverlay.hideSelectionGraphicsItems()
    crudeDebuggerPrint('''circularDimension.py:16  	    previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview ) ''')
    previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )

def clickFunPreview( x, y ):
    crudeDebuggerPrint('''circularDimension.py:19  	    if dimensioning.stage == 1: ''')
    if dimensioning.stage == 1:
        crudeDebuggerPrint('''circularDimension.py:20  	        dimensioning.point2 = x,y ''')
        dimensioning.point2 = x,y
        crudeDebuggerPrint('''circularDimension.py:21  	        debugPrint(2, 'dimension radial direction point set to x=%3.1f y=%3.1f' % (x,y)) ''')
        debugPrint(2, 'dimension radial direction point set to x=%3.1f y=%3.1f' % (x,y))
        crudeDebuggerPrint('''circularDimension.py:22  	        dimensioning.stage = 2 ''')
        dimensioning.stage = 2
        crudeDebuggerPrint('''circularDimension.py:23  	        return None, None ''')
        return None, None
    elif dimensioning.stage == 2:
        crudeDebuggerPrint('''circularDimension.py:25  	        dimensioning.point3 = x, y ''')
        dimensioning.point3 = x, y
        crudeDebuggerPrint('''circularDimension.py:26  	        debugPrint(2, 'radius dimension tail defining point set to x=%3.1f y=%3.1f' % (x,y)) ''')
        debugPrint(2, 'radius dimension tail defining point set to x=%3.1f y=%3.1f' % (x,y))
        crudeDebuggerPrint('''circularDimension.py:27  	        dimensioning.stage = 3 ''')
        dimensioning.stage = 3
        crudeDebuggerPrint('''circularDimension.py:28  	        return None, None ''')
        return None, None
    else:
        crudeDebuggerPrint('''circularDimension.py:30  	        XML = circularDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius, ''')
        XML = circularDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius,
                                    dimensioning.point2[0], dimensioning.point2[1], 
                                    dimensioning.point3[0], dimensioning.point3[1], 
                                    x, y, dimScale=dimensioning.dimScale)
        crudeDebuggerPrint('''circularDimension.py:34  	        return findUnusedObjectName('dim'), XML ''')
        return findUnusedObjectName('dim'), XML

def hoverFunPreview( x, y):
    crudeDebuggerPrint('''circularDimension.py:37  	    if dimensioning.stage == 1: ''')
    if dimensioning.stage == 1:
        crudeDebuggerPrint('''circularDimension.py:38  	        return circularDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius, x, y, dimScale=dimensioning.dimScale, **dimensioning.svg_preview_KWs ) ''')
        return circularDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius, x, y, dimScale=dimensioning.dimScale, **dimensioning.svg_preview_KWs )
    elif dimensioning.stage == 2:
        crudeDebuggerPrint('''circularDimension.py:40  	        return circularDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius, ''')
        return circularDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius, 
                                     dimensioning.point2[0], dimensioning.point2[1], x, y, dimScale=dimensioning.dimScale, **dimensioning.svg_preview_KWs )
    else: 
        crudeDebuggerPrint('''circularDimension.py:43  	        return circularDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius, ''')
        return circularDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius, 
                                     dimensioning.point2[0], dimensioning.point2[1], 
                                     dimensioning.point3[0], dimensioning.point3[1], 
                                     x, y, dimScale=dimensioning.dimScale,**dimensioning.svg_preview_KWs )
    

crudeDebuggerPrint('''circularDimension.py:49  	maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) ) ''')
maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
crudeDebuggerPrint('''circularDimension.py:50  	maskPen.setWidth(2.0) ''')
maskPen.setWidth(2.0)
crudeDebuggerPrint('''circularDimension.py:51  	maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) ) ''')
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
crudeDebuggerPrint('''circularDimension.py:52  	maskHoverPen.setWidth(2.0) ''')
maskHoverPen.setWidth(2.0)

class circularDimension:
    def Activated(self):
        crudeDebuggerPrint('''circularDimension.py:56  	        V = getDrawingPageGUIVars() ''')
        V = getDrawingPageGUIVars()
        crudeDebuggerPrint('''circularDimension.py:57  	        dimensioning.activate(V) ''')
        dimensioning.activate(V)
        crudeDebuggerPrint('''circularDimension.py:58  	        selectionOverlay.generateSelectionGraphicsItems( ''')
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim')], 
            selectFun ,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            doCircles=True, doFittedCircles=True, 
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = QtGui.QBrush() #clear
            )
    def GetResources(self): 
        crudeDebuggerPrint('''circularDimension.py:69  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'circularDimension.svg' ) , 
            'MenuText': 'Circular Dimension', 
            'ToolTip': 'Creates a circular dimension'
            } 

crudeDebuggerPrint('''circularDimension.py:75  	FreeCADGui.addCommand('circularDimension', circularDimension()) ''')
FreeCADGui.addCommand('circularDimension', circularDimension())