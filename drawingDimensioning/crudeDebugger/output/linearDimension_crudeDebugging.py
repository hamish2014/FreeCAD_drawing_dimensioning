from drawingDimensioning.crudeDebugger import crudeDebuggerPrint

crudeDebuggerPrint('''linearDimension.py:1  	from dimensioning import * ''')
from dimensioning import *
crudeDebuggerPrint('''linearDimension.py:2  	from dimensioning import __dir__ # not imported with * directive ''')
from dimensioning import __dir__ # not imported with * directive
crudeDebuggerPrint('''linearDimension.py:3  	import selectionOverlay, previewDimension ''')
import selectionOverlay, previewDimension
crudeDebuggerPrint('''linearDimension.py:4  	from dimensionSvgConstructor import linearDimensionSVG ''')
from dimensionSvgConstructor import linearDimensionSVG

crudeDebuggerPrint('''linearDimension.py:6  	dimensioning = DimensioningProcessTracker() ''')
dimensioning = DimensioningProcessTracker()

def selectDimensioningPoint( event, referer, elementXML, elementParms, elementViewObject ):
    crudeDebuggerPrint('''linearDimension.py:9  	    x, y = elementParms['x'], elementParms['y'] ''')
    x, y = elementParms['x'], elementParms['y']
    crudeDebuggerPrint('''linearDimension.py:10  	    referer.lockSelection() ''')
    referer.lockSelection()
    crudeDebuggerPrint('''linearDimension.py:11  	    if dimensioning.stage == 0: #then selectPoint1 ''')
    if dimensioning.stage == 0: #then selectPoint1
        crudeDebuggerPrint('''linearDimension.py:12  	        dimensioning.point1 =  x,y ''')
        dimensioning.point1 =  x,y
        crudeDebuggerPrint('''linearDimension.py:13  	        debugPrint(2, 'point1 set to x=%3.1f y=%3.1f' % (x,y)) ''')
        debugPrint(2, 'point1 set to x=%3.1f y=%3.1f' % (x,y))
        crudeDebuggerPrint('''linearDimension.py:14  	        dimensioning.stage = 1 ''')
        dimensioning.stage = 1
    else:
        crudeDebuggerPrint('''linearDimension.py:16  	        dimensioning.point2 =  x,y ''')
        dimensioning.point2 =  x,y
        crudeDebuggerPrint('''linearDimension.py:17  	        debugPrint(2, 'point2 set to x=%3.1f y=%3.1f' % (x,y)) ''')
        debugPrint(2, 'point2 set to x=%3.1f y=%3.1f' % (x,y))
        crudeDebuggerPrint('''linearDimension.py:18  	        dimensioning.stage = 2 ''')
        dimensioning.stage = 2 
        crudeDebuggerPrint('''linearDimension.py:19  	        dimensioning.dimScale = 1/elementXML.rootNode().scaling() ''')
        dimensioning.dimScale = 1/elementXML.rootNode().scaling()
        crudeDebuggerPrint('''linearDimension.py:20  	        selectionOverlay.hideSelectionGraphicsItems() ''')
        selectionOverlay.hideSelectionGraphicsItems()
        crudeDebuggerPrint('''linearDimension.py:21  	        previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview ) ''')
        previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )

def clickFunPreview( x, y ):
    crudeDebuggerPrint('''linearDimension.py:24  	    if dimensioning.stage == 2 : ''')
    if dimensioning.stage == 2 :
        crudeDebuggerPrint('''linearDimension.py:25  	        dimensioning.point3 = x, y ''')
        dimensioning.point3 = x, y
        crudeDebuggerPrint('''linearDimension.py:26  	        debugPrint(2, 'point3 set to x=%3.1f y=%3.1f' % (x,y)) ''')
        debugPrint(2, 'point3 set to x=%3.1f y=%3.1f' % (x,y))
        crudeDebuggerPrint('''linearDimension.py:27  	        dimensioning.stage = 3 ''')
        dimensioning.stage = 3
        crudeDebuggerPrint('''linearDimension.py:28  	        return None, None ''')
        return None, None
    else:
        crudeDebuggerPrint('''linearDimension.py:30  	        p1,p2,p3 = dimensioning.point1,  dimensioning.point2,  dimensioning.point3 ''')
        p1,p2,p3 = dimensioning.point1,  dimensioning.point2,  dimensioning.point3
        crudeDebuggerPrint('''linearDimension.py:31  	        XML = linearDimensionSVG( p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], ''')
        XML = linearDimensionSVG( p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], 
                                  x, y, scale=dimensioning.dimScale)
        crudeDebuggerPrint('''linearDimension.py:33  	        return findUnusedObjectName('dim'), XML ''')
        return findUnusedObjectName('dim'), XML

def hoverFunPreview( x, y ):
    crudeDebuggerPrint('''linearDimension.py:36  	    p1, p2 = dimensioning.point1, dimensioning.point2 ''')
    p1, p2 = dimensioning.point1, dimensioning.point2 
    crudeDebuggerPrint('''linearDimension.py:37  	    if dimensioning.stage == 2 : ''')
    if dimensioning.stage == 2 :
        crudeDebuggerPrint('''linearDimension.py:38  	        return linearDimensionSVG( p1[0], p1[1], p2[0], p2[1], x, y, **dimensioning.svg_preview_KWs ) ''')
        return linearDimensionSVG( p1[0], p1[1], p2[0], p2[1], x, y, **dimensioning.svg_preview_KWs )
    else:
        crudeDebuggerPrint('''linearDimension.py:40  	        return  linearDimensionSVG( p1[0], p1[1], p2[0], p2[1], ''')
        return  linearDimensionSVG( p1[0], p1[1], p2[0], p2[1],
                                    dimensioning.point3[0], dimensioning.point3[1], 
                                    x, y, scale=dimensioning.dimScale,  **dimensioning.svg_preview_KWs )

crudeDebuggerPrint('''linearDimension.py:44  	maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) ) ''')
maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
crudeDebuggerPrint('''linearDimension.py:45  	maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) ) ''')
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
crudeDebuggerPrint('''linearDimension.py:46  	maskPen.setWidth(0.0) ''')
maskPen.setWidth(0.0)
crudeDebuggerPrint('''linearDimension.py:47  	maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) ) ''')
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
crudeDebuggerPrint('''linearDimension.py:48  	maskHoverPen.setWidth(0.0) ''')
maskHoverPen.setWidth(0.0)

class linearDimension:
    "this class will create a line after the user clicked 2 points on the screen"
    def Activated(self):
        crudeDebuggerPrint('''linearDimension.py:53  	        V = getDrawingPageGUIVars() ''')
        V = getDrawingPageGUIVars()
        crudeDebuggerPrint('''linearDimension.py:54  	        dimensioning.activate(V) ''')
        dimensioning.activate(V)
        crudeDebuggerPrint('''linearDimension.py:55  	        selectionOverlay.generateSelectionGraphicsItems( ''')
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim')], 
            selectDimensioningPoint ,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            doPoints=True, 
            pointWid=2.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush
            )
        
    def GetResources(self): 
        crudeDebuggerPrint('''linearDimension.py:68  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'linearDimension.svg' ) , 
            'MenuText': 'Linear Dimension', 
            'ToolTip': 'Creates a linear dimension'
            } 

crudeDebuggerPrint('''linearDimension.py:74  	FreeCADGui.addCommand('linearDimension', linearDimension()) ''')
FreeCADGui.addCommand('linearDimension', linearDimension())